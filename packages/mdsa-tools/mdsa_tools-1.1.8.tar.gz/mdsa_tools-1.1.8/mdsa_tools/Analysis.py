'''
High-level wrapper for storing and running common analyses over systems of
residue–residue adjacency matrices (e.g., H-bond networks).

You can follow the provided pipeline end-to-end, or call individual, modular
steps (flattening → feature matrix → dimensionality reduction → clustering).
For example, you might cluster arbitrary n-dimensional feature matrices, or
pull H-bond values via ``systems_analysis.extract_hbond_values()`` and use
those in replicate maps instead of k-means cluster assignments.

See Also
--------
mdsa_tools.Viz.visualize_reduction : Plot PCA/UMAP embeddings.
mdsa_tools.Data_gen_hbond.create_system_representations : Build residue–residue H-bond adjacency matrices.
numpy.linalg.svd : Linear algebra used under the hood.
'''
from mdsa_tools.Data_gen_hbond import TrajectoryProcessor
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import numpy as np
import os
from sklearn.decomposition import PCA
import pandas as pd
import umap
import os

class systems_analysis:
    '''
    Container for systems-level analyses on residue–residue adjacency matrices.

    This class assumes each “system representation” is a 3D array with shape
    ``(n_frames, n_residues, n_residues)`` where a single frame contains a
    residue×residue adjacency matrix (e.g., H-bond counts/weights). Many methods
    operate on a *feature matrix* constructed by flattening/stacking per-frame
    upper triangles.

    Parameters
    ----------
    systems_representations : list of np.ndarray
        ``[array_1, ..., array_m]``, each of shape
        ``(n_frames, n_residues, n_residues)``. The only permitted difference
        across arrays is ``n_frames``; all systems should share the same residue
        dimension. Index metadata are expected in row/column 0.
    replicate_distribution : array-like of int or None, optional
        Optional labels or indices describing how frames are distributed
        across replicates/systems. If ``None``, defaults to
        ``np.arange(0, systems_representations[0].shape[0])``.

    Attributes
    ----------
    num_systems : int
        Number of systems provided (``len(systems_representations)``).
    systems_representations : list of np.ndarray
        Original input, retained for convenience.
    indexes : np.ndarray
        Derived from ``systems_representations[0][0, 0, 1:]``. These are used to
        label residue–residue comparisons when generating feature names.
    feature_matrix : np.ndarray or None
        Cached 2D feature matrix produced by ``replicates_to_featurematrix``.
    replicate_distribution : np.ndarray
        Distribution vector set from the provided argument or default.

    Notes
    -----
    * Many operations expect systems of the same residue size.
    * Designed for comparative analyses but also works with a single system.
    * The class focuses on simple, modular wrappers around common steps
      (flattening, reduction, clustering) for downstream use.
    '''
    
    def __init__(self,systems_representations=None,replicate_distribution=None):
        '''
        Initialize the analysis container.

        Parameters
        ----------
        systems_representations : list of np.ndarray
            List of system arrays, each shaped ``(n_frames, n_residues, n_residues)``.
        replicate_distribution : array-like of int or None, optional
            Optional frame-level indexing/labels for downstream bookkeeping.

        Returns
        -------
        None
        '''
        
        self.num_systems=len(systems_representations) #this is useful later on for when we are doing system_specific operations
        self.systems_representations=systems_representations
        self.indexes = systems_representations[0][0, 0, 1:] #bc list then 3d array
        self.feature_matrix=None
        if replicate_distribution is not None:
            self.replicate_distribution=replicate_distribution
            
        if replicate_distribution is None:
            self.replicate_distribution=np.arange(0,systems_representations[0].shape[0])
        
        return


    #pre-processing
    def replicates_to_featurematrix(self,arrays=None)->np.ndarray:
        """Construct a flattened, per-frame feature matrix from one or more
        systems of residue×residue adjacency matrices.

        Parameters
        ----------
        arrays : list of np.ndarray or None
            ``[array_1, ..., array_m]`` where each array has shape
            ``(n_frames, n_residues, n_residues)``. If ``None``, uses
            ``self.systems_representations``.
            The only axis allowed to differ across arrays is ``n_frames``.

        Returns
        -------
        np.ndarray
            Shape ``(sum(n_frames), n_features)``, where ``n_features`` equals the
            number of unique residue–residue pairs from the *upper triangle*
            (excluding the diagonal) of the per-frame matrix. Each row corresponds
            to a single frame across all systems.

        Notes
        -----
        * Index row/column ``0`` are dropped (``[1:, 1:]``) under the assumption
          they hold metadata (residue indices).
        * Only the upper triangle is used to avoid duplicate symmetric entries.
        * The result is cached to ``self.feature_matrix`` for reuse.

        Examples
        --------
        >>> arrays = [sys1, sys2]  # each (n_frames, n_res, n_res)
        >>> X = sa.replicates_to_featurematrix(arrays)  # doctest: +SKIP
        """
        arrays = arrays if arrays is not None else self.systems_representations
        
        #Concatenate arrays and define list to hold reformatted arrays
        try:
            concatenated_array=np.concatenate((arrays))
        except(ValueError, TypeError):
            print("its really best if you input a list but the program will move on with the assumption you have given just a single arrray as input")
            concatenated_array=np.asarray(arrays)

        final_frames=[]
        frame_num, n_residues, _ = concatenated_array.shape

        # Get indices for upper triangle (excluding diagonal)
        triu_idx = np.triu_indices(n_residues - 1, k=1)  # -1 due to [1:,1:] slice below


        final_frames = []
        for i in range(frame_num):
            current_frame = np.copy(concatenated_array[i, 1:, 1:])
            # Extract upper triangle only
            flattened = current_frame[triu_idx]
            final_frames.append(flattened)

        final_frames = np.vstack(final_frames).astype(np.float32)
        self.feature_matrix=final_frames#set global var as well

        return final_frames

    def extract_hbond_values(self,residues,systems_array=None,mode="sum"):
        '''Aggregate per-frame H-bond values over a chosen residue set.

        Parameters
        ----------
        residues : list of int
            Residue indices to retain (e.g., a surface or motif). All pairwise
            combinations among these residues are used.
        systems_array : np.ndarray or None, shape ``(n_frames, n_res, n_res)``
            Averaged array or a single 3D trajectory array. If ``None``, all
            systems in ``self.systems_representations`` are concatenated.
        mode : {'sum','average'}, default='sum'
            Aggregation across the upper triangle for each frame.

        Returns
        -------
        np.ndarray
            Shape ``(n_frames,)`` containing the aggregated value per frame.

        Notes
        -----
        * Index/label row/column ``0`` are dropped before aggregation.
        * Only the upper triangle is aggregated to avoid double counting.

        Examples
        --------
        >>> vals = sa.extract_hbond_values([12, 47, 91], mode='average')  # doctest: +SKIP
        '''
        if systems_array is not None:
            systems_array=systems_array
        if systems_array is None:
            systems_array=np.concatenate(self.systems_representations)


        # making it a static function felt like too big a jump but this toy attribute feels neat
        # grabbing filter function from datagen with a simplenamespace
        from types import SimpleNamespace
        fake_self = SimpleNamespace(
            system_representation=systems_array,
            create_system_representations=lambda: None,
        )

        filtered = TrajectoryProcessor.create_filtered_representations(
            fake_self, residues_to_keep=residues, systems_representation=systems_array
        )
        

        if mode == "average":
            systems_array,residues
            filtered_array=filtered[:,1:,1:]        
            ta_labels = np.mean(np.triu(filtered_array, k=1), axis=(1, 2)) #accounting for symmetry
        
        if mode == "sum":      
            systems_array,residues
            filtered_array=filtered[:,1:,1:]
            ta_labels = np.sum(np.triu(filtered_array, k=1), axis=(1, 2)) #accounting for symmetry
        
        return ta_labels

    #Analyses
    def perform_kmeans(self, outfile_path=None, max_clusters=None, data=None, k=None):
        '''
        Run KMeans clustering on a feature matrix, either:
        (a) sweeping K to select optima by silhouette and elbow criteria, or
        (b) fitting once at a fixed K.

        Parameters
        ----------
        outfile_path : str or pathlib.Path or None, optional
            Directory where per-K label arrays are saved (via ``np.save``) when
            sweeping K (i.e., when ``k is None``). One file is written per value of K.
            If ``None``, nothing is written to disk. Default is ``None``.
        max_clusters : int or None, optional
            Upper bound on the number of clusters to consider when sweeping K.
            Effective only when ``k is None``. The exact K range is determined by
            :meth:`perform_clust_opt` (typically ``2..max_clusters`` inclusive).
            Default is ``10``.
        data : array-like of shape (n_samples, n_features) or None, optional
            Feature matrix to cluster. If ``None``, uses ``self.feature_matrix``.
        k : int or None, optional
            If provided, fit a single KMeans model with exactly ``k`` clusters and
            return its labels and centers. If ``None``, perform a sweep over K and
            return the best solutions under the silhouette and elbow criteria.

        Returns
        -------
        cluster_labels : ndarray of shape (n_samples,), dtype=int
            (Only when ``k`` is not ``None``) Cluster assignment for each sample,
            with labels in ``[0, k-1]``.
        cluster_centers : ndarray of shape (k, n_features)
            (Only when ``k`` is not ``None``) Centroids of the fitted model.
        optimal_k_silhouette_labels : ndarray of shape (n_samples,), dtype=int
            (Only when ``k`` is ``None``) Labels for the K chosen by the silhouette
            criterion.
        optimal_k_elbow_labels : ndarray of shape (n_samples,), dtype=int
            (Only when ``k`` is ``None``) Labels for the K chosen by the elbow
            (inertia) criterion.
        centers_sillohuette : ndarray of shape (k_silhouette, n_features)
            (Only when ``k`` is ``None``) Centers corresponding to
            ``optimal_k_silhouette_labels``.
        centers_elbow : ndarray of shape (k_elbow, n_features)
            (Only when ``k`` is ``None``) Centers corresponding to
            ``optimal_k_elbow_labels``.

        Notes
        -----
        - When ``k`` is provided, this method fits ``sklearn.cluster.KMeans`` with
          ``init='random'``, ``n_init=k``, and ``random_state=0`` for reproducibility.
        - When ``k`` is ``None``, selection of the optimal K and any per-K saving
          behavior are delegated to :meth:`perform_clust_opt`, which is expected to
          return the label arrays and centers for the silhouette- and elbow-selected
          solutions.

        Examples
        --------
        Fit a fixed-K model:

        >>> labels, centers = obj.perform_kmeans(k=5)

        Sweep K (saving per-K labels):

        >>> sil_labels, elbow_labels, sil_centers, elbow_centers = \
        ...     obj.perform_kmeans(outfile_path="results/kmeans", max_clusters=12)
        '''
        
        max_clusters = max_clusters if max_clusters is not None else 10
        data = data if data is not None else self.feature_matrix
        # IMPORTANT: If None, do not save anything downstream.
        outfile_path = outfile_path if outfile_path is not None else None
        k = k if k is not None else None

        if k is None:
            optimal_k_silhouette_labels, optimal_k_elbow_labels, centers_sillohuette, centers_elbow = \
                self.perform_clust_opt(outfile_path=outfile_path, data=data, max_clusters=max_clusters)

        if k is not None:
            kmeans = KMeans(n_clusters=k, init='random', n_init=k, random_state=0)
            kmeans.fit(data)
            cluster_centers, inertia, cluster_labels = kmeans.cluster_centers_, kmeans.inertia_, kmeans.labels_
            return cluster_labels, cluster_centers

        return optimal_k_silhouette_labels, optimal_k_elbow_labels, centers_sillohuette, centers_elbow    
   
    def reduce_systems_representations(self,feature_matrix=None,
                                        method=None,
                                        n_components=None,
                                        min_dist=None,
                                        n_neighbors=None):
        '''
        Reduce the dimensionality of the per-frame feature matrix using PCA or UMAP.

        Parameters
        ----------
        feature_matrix : np.ndarray or None
            If provided, use this matrix; otherwise prefer ``self.feature_matrix``.
            If neither is set, calls ``replicates_to_featurematrix()`` to create it.
        method : {'PCA','UMAP'}, optional
            Reduction method. Default ``'PCA'``.
        n_components : int, optional
            Target dimensionality (default ``2``).
        min_dist : float, optional
            UMAP parameter controlling cluster tightness (default ``0.5``).
        n_neighbors : int, optional
            UMAP parameter controlling local vs global structure (default ``900``).

        Returns
        -------
        If method == 'PCA':
            (X_pca, weights, explained_variance_ratio_) : tuple
                ``X_pca`` has shape ``(n_samples, n_components)``.
                ``weights`` are component loadings (``n_components × n_features``).
                ``explained_variance_ratio_`` is length ``n_components``.
        If method == 'UMAP':
            embedding : np.ndarray
                Shape ``(n_samples, n_components)``.

        Notes
        -----
        * PCA uses ``sklearn.decomposition.PCA``.
        * UMAP uses ``umap.UMAP`` with provided parameters.

        Examples
        --------
        >>> X, W, evr = sa.reduce_systems_representations(method='PCA', n_components=2)  # doctest: +SKIP
        >>> U = sa.reduce_systems_representations(method='UMAP', n_components=2)         # doctest: +SKIP
        '''
        
        if feature_matrix is not None:
            feature_matrix = feature_matrix 
        if self.feature_matrix is not None:
            feature_matrix=self.feature_matrix
        if self.feature_matrix is None:
            self.replicates_to_featurematrix()
            feature_matrix=self.feature_matrix

        n_components=n_components if n_components is not None else 2
        method = method if method is not None else 'PCA'
        min_dist = min_dist if min_dist is not None else .5
        n_neighbors= n_neighbors if n_neighbors is not None else 900

        if method=='PCA':
        
            X_pca,weights,explained_variance_ratio_=self.run_PCA(feature_matrix,n_components)
            return X_pca,weights,explained_variance_ratio_
            
        if method=='UMAP':

            # Initialize UMAP
            reducer = umap.UMAP(n_components=n_components,n_neighbors=n_neighbors,min_dist=.5)
            embedding = reducer.fit_transform(feature_matrix)

            return embedding
            
            
        elif method != 'PCA' and method != 'UMAP':
            print('No valid method supplied for dimensional reduction ')
        
    def cluster_embeddingspace(self, reduced_coordinates=None, outfile_path=None, num_systems=None, val_metric=None):
        '''
        (Deprecated) Cluster each system independently in a reduced embedding space.

        ...
        '''
        # IMPORTANT: If None, downstream won't save.
        outfile_path = outfile_path if outfile_path is not None else None
        num_systems = num_systems if num_systems is not None else self.num_systems
        val_metric = val_metric if val_metric is not None else 'sillohuette'

        if reduced_coordinates is None:
            reduced_coordinates, _, _ = self.reduce_systems_representations()

        individual_systems = np.array_split(reduced_coordinates, num_systems, axis=0)
        print(individual_systems[0].shape)
        candidate_states_per_system = []
        for i in individual_systems:
            optimal_k_silhouette_labels, optimal_k_elbow_labels, centers_sillohuette, centers_elbow = \
                self.perform_clust_opt(outfile_path, data=i)
            if val_metric == 'sillohuette':
                candidate_states_per_system.append((optimal_k_silhouette_labels, centers_sillohuette))
            if val_metric == 'elbow':
                candidate_states_per_system.append((optimal_k_elbow_labels, centers_elbow))

        return candidate_states_per_system

    def create_pearsontest_for_kmeans_distributions(self,labels,coordinates,cluster_centers):

        '''Compute pairwise Pearson correlations between per-cluster distance
        distributions (to their respective KMeans centroids).

        Parameters
        ----------
        labels : array-like of int
            Cluster assignment for each sample (length ``n_samples``).
        coordinates : np.ndarray, shape (n_samples, n_features)
            Coordinates of samples in some space (e.g., embedding or feature space).
        cluster_centers : np.ndarray, shape (k, n_features)
            Coordinates of cluster centers.

        Returns
        -------
        correlation_df : pandas.DataFrame
            Long-form table of pairwise Pearson correlations between *equal-length* samples
            drawn from per-cluster distance distributions (truncated to the shortest length
            across clusters). Columns:
              - ``cluster_i`` (int): first cluster id
              - ``cluster_j`` (int): second cluster id
              - ``pearson_r`` (float): correlation coefficient
              - ``p_value`` (float): two-sided p-value

        Notes
        -----
        Distances are Euclidean from each point to its assigned center. Because cluster
        sizes differ, distributions are truncated to the minimum cluster size before
        computing correlations.

        Examples
        --------
        >>> df = sa.create_pearsontest_for_kmeans_distributions(labels, X, C)  # doctest: +SKIP
        '''
        distances = np.linalg.norm(coordinates - cluster_centers[labels], axis=1) #euclidean distances to centroid

        #extracting everything by the group its a part of
        dist_by_cluster = {}
        for cluster_id in np.unique(labels):
            dist_by_cluster[int(cluster_id)] = distances[labels == cluster_id]

        #find minimum distance
        lengths = [len(i) for i in dist_by_cluster.values()]
        #print(lengths)
        shortest_length = min(lengths)
        #print(shortest_length)


        #form final list
        final_distributions=[]
        for i in dist_by_cluster.values():
            current_distribution=i[0:shortest_length,]
            final_distributions.append(current_distribution)
        
        from scipy.stats import pearsonr
        import pandas as pd
        
        correlations = []

        for i in range(len(final_distributions)):
            for j in range(i + 1,len(final_distributions)):
                r_value, p_value = pearsonr(final_distributions[i], final_distributions[j])
                correlations.append({
                    "cluster_i": i,
                    "cluster_j": j,
                    "pearson_r": r_value,
                    "p_value": p_value
                })

        correlation_df = pd.DataFrame(correlations)
        

        return correlation_df
       
    def create_PCA_ranked_weights(self,outfile_path=None, weights=None, indexes=None):
        '''Create a ranked table of PCA feature weights for the first two principal components.

        Parameters
        ----------
        outfile_path : str or pathlib.Path, optional
            Directory where outputs may be written. If ``None``, uses the current working directory.
        weights : np.ndarray, shape = (n_components, n_features), optional
            PCA component loadings (rows = components, columns = features). If ``None``, this
            function calls ``reduce_systems_representations()`` to compute PCA (default n=2)
            and uses the returned ``weights``.
        indexes : array-like of int, optional
            Residue indices used to label pairwise comparisons. If ``None``, uses ``self.indexes``.
            These indices define the order used to generate upper-triangle residue–residue
            comparison labels (e.g., "12-47").

        Returns
        -------
        pandas.DataFrame
            A table mapping each feature (upper-triangle residue pair) to its PCA weights and
            magnitudes with columns:

            * ``Comparisons``     — 'i-j' residue pair label (str)
            * ``PC1_Weights``     — raw loading for PC1 (float)
            * ``PC2_Weights``     — raw loading for PC2 (float)
            * ``PC1_magnitude``   — (PC1_Weights)**2 (float)
            * ``PC2_magnitude``   — (PC2_Weights)**2 (float)
            * ``PC1_mag_norm``    — min–max normalized PC1_magnitude to [0, 1] (float)  [*optional if postprocessed*]
            * ``PC2_mag_norm``    — min–max normalized PC2_magnitude to [0, 1] (float)  [*optional if postprocessed*]

        Notes
        -----
        Only the upper triangle (excluding the diagonal) of the residue–residue matrix is used,
        so each row corresponds to a unique residue pair. The function assumes at least two
        principal components are available.

        Examples
        --------
        >>> df = sa.create_PCA_ranked_weights()  # doctest: +SKIP
        '''
        if weights is None:
            _,weights,_ =self.reduce_systems_representations()
        if weights is not None:
            weights=weights

        outfile_path = outfile_path if outfile_path is not None else os.getcwd()
        indexes=indexes if indexes is not None else self.indexes

        # grab only upper triangle
        triu_idx = np.triu_indices(len(indexes), k=1)

        # Generate comparison labels (no array values needed)
        comparisons = [f"{str(int(indexes[i]))}-{str(int(indexes[j]))}" for i, j in zip(*triu_idx)]
        dataframe={
            'Comparisons':comparisons,
            'PC1_Weights':weights[0],
            'PC2_Weights':weights[1],
            'PC1_magnitude':weights[0]**2,
            'PC2_magnitude':weights[1]**2,
        
        }

        dataframe=pd.DataFrame(dataframe).round(3)
        
        return dataframe


    #Algorithm wrappers 
    #Algorithm wrappers 
    def perform_clust_opt(self, outfile_path, max_clusters=None, data=None, k=None):
        """Sweep K for KMeans and pick “best” K by silhouette and elbow, or fit a single K.

        Parameters
        ----------
        outfile_path : str or pathlib.Path or None
            If provided, per-K label arrays are saved via ``np.save`` as
            ``"<outfile_path>kluster_labels_{K}clust.npy"`` and selection plots
            are delegated to ``mdsa_tools.Viz``. If ``None``, nothing is written
            and elbow selection falls back to a simple heuristic.
        max_clusters : int, optional
            Upper bound (inclusive) for the K sweep (default ``10``). The sweep
            runs from ``K=2`` through ``K=max_clusters``.
        data : np.ndarray or None, shape (n_samples, n_features), optional
            Feature matrix to cluster. If ``None``, uses ``self.feature_matrix``.
        k : int or None, optional
            If set, skip the sweep and fit one KMeans at exactly ``k`` clusters.

        Returns
        -------
        If ``k`` is None:
            optimal_k_silhouette_labels : np.ndarray of int, shape (n_samples,)
                Labels for the silhouette-selected K.
            optimal_k_elbow_labels : np.ndarray of int, shape (n_samples,)
                Labels for the elbow-selected K.
            centers_sillohuette : np.ndarray, shape (K_sil, n_features)
                Cluster centers for the silhouette-selected K. (Legacy spelling kept.)
            centers_elbow : np.ndarray, shape (K_elb, n_features)
                Cluster centers for the elbow-selected K.
        If ``k`` is not None:
            cluster_labels : np.ndarray of int, shape (n_samples,)
                Labels from the single KMeans run.
            cluster_centers : np.ndarray, shape (k, n_features)
                Cluster centers from the single KMeans run.

        Notes
        -----
        * Silhouette uses ``sklearn.metrics.silhouette_score`` on the provided
          feature space (no precomputed distance matrix).
        * Elbow choice:
            - If ``outfile_path`` is provided, the decision is delegated to
              ``mdsa_tools.Viz.plot_elbow_scores`` (with plotting).
            - If not, and too few points exist to fit a curve, falls back to the
              argmin of inertia over the available Ks.
        * ``KMeans(init='random', n_init=K, random_state=0)`` is used for reproducibility.
        * The variable/name ``sillohuette`` is spelled as-is to preserve legacy usage.

        Examples
        --------
        >>> labels_sil, labels_elb, C_sil, C_elb = sa.perform_clust_opt(None, max_clusters=8, data=X)  # doctest: +SKIP
        >>> labels, centers = sa.perform_clust_opt(None, data=X, k=3)                                   # doctest: +SKIP
        """

        data = data if data is not None else self.feature_matrix
        # IMPORTANT: Do not coerce to CWD; None means "no saving".
        outfile_path = outfile_path if outfile_path is not None else None
        max_clusters = max_clusters if max_clusters is not None else 10
        k = k if k is not None else None

        if k is not None:
            kmeans = KMeans(n_clusters=k, init='random', n_init=k, random_state=0)
            kmeans.fit(data)
            cluster_centers, inertia, cluster_labels = kmeans.cluster_centers_, kmeans.inertia_, kmeans.labels_
            return cluster_labels, cluster_centers

        inertia_scores, silhouette_scores, all_labels, centers = [], [], [], []
        inertia_Ks = []
        cluster_range = range(2, max_clusters + 1)

        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, init='random', n_init=k, random_state=0)
            kmeans.fit(data)
            cluster_centers, inertia, cluster_labels = kmeans.cluster_centers_, kmeans.inertia_, kmeans.labels_
            sil_score = silhouette_score(data, cluster_labels)

            centers.append(cluster_centers)
            silhouette_scores.append(sil_score)
            all_labels.append(cluster_labels)

            if not (max_clusters == 3 and k == 3):
                inertia_scores.append(inertia)
                inertia_Ks.append(k)

            # Only save if a directory/path was provided
            if outfile_path is not None:
                # Keeping your original path style; just gated.
                np.save(f"{outfile_path}kluster_labels_{k}clust", cluster_labels)

        # Choose optimal Ks
        if outfile_path is not None:
            from mdsa_tools.Viz import plot_elbow_scores, plot_sillohette_scores
            optimal_sillohuette = plot_sillohette_scores(cluster_range, silhouette_scores, outfile_path)
            if len(inertia_scores) < 3:
                optimal_elbow = inertia_Ks[int(np.argmin(np.asarray(inertia_scores)))]
            else:
                optimal_elbow = plot_elbow_scores(inertia_Ks, inertia_scores, outfile_path)
        else:
            # No plotting: simple, deterministic fallbacks
            optimal_sillohuette = int(np.argmax(np.asarray(silhouette_scores))) + 2  # offset for range start at 2
            optimal_elbow = inertia_Ks[int(np.argmin(np.asarray(inertia_scores)))] if len(inertia_scores) > 0 else 2

        optimal_k_silhouette_labels = all_labels[optimal_sillohuette - 2]
        optimal_k_elbow_labels = all_labels[optimal_elbow - 2]
        centers_sillohuette = centers[optimal_sillohuette - 2]
        centers_elbow = centers[optimal_elbow - 2]

        return optimal_k_silhouette_labels, optimal_k_elbow_labels, centers_sillohuette, centers_elbow
        
    def run_PCA(self,feature_matrix,n):
        '''Run Principal Components Analysis (PCA) and return transformed
        coordinates, component loadings, and explained variance ratios.

        Parameters
        ----------
        feature_matrix : np.ndarray
            Shape ``(n_samples, n_features)``. Typically produced by
            ``replicates_to_featurematrix()``.
        n : int
            Number of components to retain (default ``2`` in upstream callers).

        Returns
        -------
        X_pca : np.ndarray, shape (n_samples, n)
            Transformed coordinates in the principal-component space.
        weights : np.ndarray, shape (n, n_features)
            PCA component loadings (rows = components, columns = original features).
        explained_variances : np.ndarray, shape (n,)
            Fraction of variance explained by each selected component.

        Notes
        -----
        Thin wrapper around ``sklearn.decomposition.PCA``; fits on the provided
        feature matrix and returns the transformed coordinates, component loadings,
        and explained-variance ratios.

        Examples
        --------
        >>> X_pca, W, evr = sa.run_PCA(feature_matrix, 2)  # doctest: +SKIP
        >>> X_pca.shape                                     # doctest: +SKIP
        (feature_matrix.shape[0], 2)
        '''

        pca=PCA(n_components=n)
        pca.fit(feature_matrix)
        X_pca = pca.transform(feature_matrix)
        weights = pca.components_
        explained_variances = pca.explained_variance_ratio_

        print("X_pca shape (new data):",X_pca.shape)
        print(f"the total explained variance{np.sum(explained_variances)}")
        print(f"the total explained variance of PC's is {explained_variances}")
        print("weights shape:", weights.shape) 
        
        return X_pca,weights,explained_variances

if __name__ == '__main__':

    print('testing testing 1 2 3')