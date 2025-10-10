# tests/test_analysis.py
import numpy as np
import os

def test_feature_matrix_shape(analyzer):
    fm = analyzer.feature_matrix
    assert fm.shape[0] == 18  

def test_proper_PCA_reduction_output(analyzer):
    X_pca, weights, var_ratio = analyzer.reduce_systems_representations(method="PCA")
    assert X_pca.shape[0] == analyzer.feature_matrix.shape[0]
    assert isinstance(var_ratio, np.ndarray) and var_ratio.shape[0] == 2
    assert weights.shape[1] == analyzer.feature_matrix.shape[1]

def test_proper_UMAP_reduction_output(analyzer):
    umap_coordinates = analyzer.reduce_systems_representations(method="UMAP",n_neighbors=5)
    assert umap_coordinates.shape[0] == analyzer.feature_matrix.shape[0]
    assert umap_coordinates.shape[1] == 2

def test_system_clustering(analyzer):
    optimal_k_silhouette_labels, optimal_k_elbow_labels, centers_silhouette, centers_elbow = analyzer.perform_kmeans(max_clusters=5)

    assert optimal_k_silhouette_labels.shape[0] == analyzer.feature_matrix.shape[0], "silhouette clustering labels dont match n_samples"
    assert optimal_k_elbow_labels.shape[0] == analyzer.feature_matrix.shape[0], "elbow clustering labels dont match n_samples"

    assert centers_silhouette.shape[1] == analyzer.feature_matrix.shape[1], "silhouette cluster centers wrong dimension"
    assert centers_elbow.shape[1] == analyzer.feature_matrix.shape[1], "elbow cluster centers wrong dimension"

    assert centers_silhouette.shape[0] >= 2, "silhouette clustering found too few clusters"
    assert centers_elbow.shape[0] >= 2, "elbow clustering found too few clusters"
    
def test_pca_ranked_weights(analyzer):
    analyzer.reduce_systems_representations(method='UMAP')
    ranked_weights = analyzer.create_PCA_ranked_weights()
    assert ranked_weights.shape[0] == analyzer.feature_matrix.shape[1], "incorrect number of comparisons in ranked_weights creation"
    for col in ["Comparisons","PC1_Weights","PC2_Weights","PC1_magnitude","PC2_magnitude"]:
        assert col in ranked_weights.columns
    
    features = analyzer.feature_matrix.shape[1]
    assert (ranked_weights["PC1_magnitude"].values >= 0).all()
    assert (ranked_weights["PC2_magnitude"].values >= 0).all()
    assert ranked_weights["PC1_Weights"].shape[0] == features
    assert ranked_weights["PC2_Weights"].shape[0] == features

    # check comparisons look like “i-j” (important for MDCircos use later on)
    assert ranked_weights["Comparisons"].str.contains(r"^\d+-\d+$").all()

    return

def test_replicates_to_featurematrix_accepts_single_array(analysis_systems):
    from mdsa_tools.Analysis import systems_analysis as sas
    single_array=analysis_systems[0]
    analyzer = sas([single_array])
    Feature_Matrix = analyzer.replicates_to_featurematrix()
    assert np.count_nonzero(Feature_Matrix) > 0

def test_perform_clust_opt_fixed_k_returns_shapes(tmp_path, analyzer):
    Feature_Matrix = analyzer.replicates_to_featurematrix()
    labels, centers = analyzer.perform_clust_opt(outfile_path=str(tmp_path) + os.sep, data=Feature_Matrix, k=2)
    assert labels.shape[0] == Feature_Matrix.shape[0]
    assert centers.shape == (2, Feature_Matrix.shape[1])

def test_perform_kmeans_k_path(tmp_path, analyzer):
    Fm = analyzer.feature_matrix
    labels, centers = analyzer.perform_kmeans(outfile_path=str(tmp_path) + os.sep, data=Fm, k=2)
    assert labels.shape[0] == Fm.shape[0]
    assert centers.shape[0] == 2

def test_perform_kmeans_k_path(tmp_path, analyzer):
    X = analyzer.feature_matrix
    labels, centers = analyzer.perform_kmeans(outfile_path=str(tmp_path) + os.sep, data=X, k=2)
    assert labels.shape[0] == X.shape[0]
    assert centers.shape[0] == 2


def test_create_pearsontest_for_kmeans_distributions_shape(analyzer):
    coords = np.array([[0, 0], [0, 1], [5, 5], [5, 6]], dtype=float)
    labels = np.array([0, 0, 1, 1])
    centers = np.array([[0, 0.5], [5, 5.5]])
    df = analyzer.create_pearsontest_for_kmeans_distributions(labels, coords, centers)
    assert list(df.columns) == ["cluster_i", "cluster_j", "pearson_r", "p_value"]
    assert len(df) == 1



