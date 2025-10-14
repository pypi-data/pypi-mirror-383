'''
The Visualization module stores all of the different operations for the various graphs we create.

It is not a larger object but a series of complimentary functions including helpers that make different color bars
depending on values etc.

For the most part we expect a max of around 256 bins but, if you have more bins in any labelling (colorcoding)of your graphs it auto switches
to a continous colorbar and goes based on sample index.



See Also
--------
mdsa_tools.Analysis : A lot of the results you will probably visualize

mdsa_tools.Data_gen_hbond.create_system_representations : Build residue–residue H-bond adjacency matrices.


'''


import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pycircos.pycircos as py
import seaborn as sns
from matplotlib.colors import BoundaryNorm
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
import pandas as pd


# Miscellaneous tools
def add_continuous_colorbar(scatter, labels, cbar_label=None, ax=None, cmap=None,
                            extend="neither", format=None):
    """
    Add a continuous colorbar to a scatter plot.

    Works for numeric labels directly; for non-numeric labels, maps unique
    values to an ordinal numeric sequence and normalizes over that range.

    Parameters
    ----------
    scatter : matplotlib.collections.PathCollection
        The scatter object returned by `Axes.scatter(...)`.

    labels : array-like or None
        Values to color by. If None, uses an index-based gradient.

    cbar_label : str or None, default=None
        Colorbar label.

    ax : matplotlib.axes.Axes or None, default=None
        Target axes. Defaults to `plt.gca()`.

    cmap : str or matplotlib.colors.Colormap or None, default=None
        Colormap name or object. Defaults to `cm.inferno`.

    extend : {'neither', 'both', 'min', 'max'}, default='neither'
        Colorbar extension behavior.

    format : str or matplotlib.ticker.Formatter or None, default=None
        Formatting for colorbar tick labels.

    Returns
    -------
    matplotlib.colorbar.Colorbar
        The created colorbar.

    Notes
    -----
    This function also applies the computed `Normalize` and `Colormap` to the
    provided scatter so the colorbar reflects the actual plotted data.
    """
    if ax is None:
        ax = plt.gca()

    cmap_obj = plt.get_cmap(cmap or cm.inferno)

    # Build numeric values
    if labels is None:
        n = scatter.get_offsets().shape[0]
        vals = np.arange(n, dtype=float)
    else:
        vals = np.asarray(labels)

    if not np.issubdtype(vals.dtype, np.number):
        _, inv = np.unique(vals, return_inverse=True)
        vals = inv.astype(float)

    finite = np.isfinite(vals)
    if not finite.any():
        vmin, vmax = 0.0, 1.0
    else:
        vmin = float(np.nanmin(vals[finite]))
        vmax = float(np.nanmax(vals[finite]))
        if vmin == vmax:
            pad = 0.5 if vmin == 0 else 0.01 * abs(vmin)
            vmin, vmax = vmin - pad, vmax + pad

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    # Ensure scatter uses this norm/cmap/data
    scatter.set_norm(norm)
    scatter.set_cmap(cmap_obj)
    scatter.set_array(vals)

    mappable = ScalarMappable(norm=norm, cmap=cmap_obj)
    mappable.set_array(vals)
    cbar = plt.colorbar(mappable, ax=ax, extend=extend, format=format)
    if cbar_label:
        cbar.set_label(cbar_label, fontsize=10)
    return cbar

def add_discrete_colorbar(scatter, labels, cbar_label=None, ax=None, cmap=None):
    """
    Add a discrete (categorical) colorbar to a scatter plot.

    Maps the unique `labels` to integer IDs and shows a tick per category.
    For large cardinality (N > 100) it sparsifies ticks every 10 to improve readability.

    Parameters
    ----------
    scatter : matplotlib.collections.PathCollection
        The scatter object returned by `Axes.scatter(...)`.

    labels : array-like
        Categorical labels per point. Converted to strings for tick labels.

    cbar_label : str or None, default=None
        Colorbar label.

    ax : matplotlib.axes.Axes or None, default=None
        Target axes. Defaults to `plt.gca()`.

    cmap : str or matplotlib.colors.Colormap or None, default=None
        Colormap name or object. Defaults to `cm.inferno`.

    Returns
    -------
    matplotlib.colorbar.Colorbar
        The created colorbar.

    Notes
    -----
    Sets the scatter's `norm` to a `BoundaryNorm` over integer bins matching
    the number of unique categories so colors align with discrete tick marks.
    """
    if ax is None:
        ax = plt.gca()

    labels = np.asarray(labels)
    uniques, label_ids = np.unique(labels, return_inverse=True)
    N = len(uniques)

    cmap = cmap if cmap is not None else cm.inferno
    bounds = np.arange(-0.5, N + 0.5, 1)
    norm = BoundaryNorm(bounds, cmap.N)

    scatter.set_cmap(cmap)
    scatter.set_array(label_ids)
    scatter.set_norm(norm)

    cbar = plt.colorbar(scatter, ax=ax, boundaries=bounds,
                        ticks=np.arange(N), pad=0.02, shrink=0.8)
    cbar.set_label(cbar_label or 'Value', fontsize=10)

    if N > 100:
        tick_positions = np.arange(N)[::10]
        tick_labels = [str(u) for u in uniques][::10]
        cbar.set_ticks(tick_positions)
        cbar.set_ticklabels(tick_labels)
        return cbar

    cbar.set_ticklabels([str(u) for u in uniques])
    return cbar

def set_ticks(ax=None):
    """
    Set x and y ticks for an axis depending on range.

    If the axis span exceeds 100 units, ticks are placed every 10 units;
    otherwise, Matplotlib's default tick locator is preserved.

    Parameters
    ----------
    ax : matplotlib.axes.Axes or None, default=None
        Axis to apply tick settings. Defaults to the current axis.

    Returns
    -------
    None
        Modifies the axis in place.
    """
    if ax is None:
        ax = plt.gca()

    xmin, xmax = ax.get_xlim()
    if xmax - xmin > 100:
        ax.set_xticks(np.arange(np.floor(xmin), np.ceil(xmax) + 1, 10))

    ymin, ymax = ax.get_ylim()
    if ymax - ymin > 100:
        ax.set_yticks(np.arange(np.floor(ymin), np.ceil(ymax) + 1, 10))
    return

# Replicate maps
def replicatemap_from_labels(labels, frame_list,
                             savepath=None,
                             title=None,
                             xlabel=None, ylabel=None,
                             cbar_label=None,
                             cmap=None) -> None:
    """
    Plot a "replicate × frame" map of discrete labels and save to disk.

    Parameters
    ----------
    labels : array-like of shape (n_total_frames,)
        Label per frame (e.g., k-means cluster or any discrete annotation),
        concatenated across replicates in the same order as `frame_list`.

    frame_list : array-like of shape (n_replicates,)
        Number of frames in each replicate, in the exact concatenation order
        used to build `labels`.

    savepath : str or None, default=None
        Directory or path *prefix* where the plot is saved. If None, uses
        `os.getcwd()`. The file name appended is ``'replicate_map.png'``
        (i.e., saved at ``f"{savepath}replicate_map.png"``).

    title : str or None, default=None
        Figure title; if None, a default is used.

    xlabel, ylabel : str or None, default=None
        Axis labels. If omitted, defaults are used.

    cbar_label : str or None, default=None
        Label for the colorbar.

    cmap : str or matplotlib.colors.Colormap or None, default=None
        Colormap for the label values. Defaults to ``cm.magma_r``.

    Returns
    -------
    None
        The figure is saved to disk and closed. Nothing is returned.

    Notes
    -----
    - Uses a small square marker per (replicate, frame) and a discrete colorbar
      for low/medium cardinality labels; switches to a continuous colorbar when
      unique label count is very large (>= 1000).
    - Replicate index is placed on the y-axis (top row is replicate 0) and the
      axis is inverted for a top-down visual.

    Examples
    --------
    >>> labels = [0]*100 + [1]*120 + [2]*90
    >>> frames = [100, 120, 90]
    >>> replicatemap_from_labels(labels, frames, savepath="/tmp/")
    """
    cmap = cmap if cmap is not None else cm.magma_r
    savepath = savepath if savepath is not None else os.getcwd()

    iterator = 0
    final_coordinates = []

    for i in range(len(frame_list)):
        current_frame_length = frame_list[i]
        current_replicate_coordinates = np.full(shape=(current_frame_length,), fill_value=i)
        frame_positions = np.arange(current_frame_length)
        frame_values = labels[iterator:iterator + current_frame_length]
        replicate_block = np.stack([current_replicate_coordinates, frame_positions, frame_values], axis=1)
        final_coordinates.append(replicate_block)
        iterator += current_frame_length

    final_coordinates = np.vstack(final_coordinates)

    y_spacing_factor = 1
    x_spacing_factor = 1

    scatter = plt.scatter(
        x=final_coordinates[:, 1] * x_spacing_factor,
        y=final_coordinates[:, 0] * y_spacing_factor,
        c=final_coordinates[:, 2],
        s=1,
        marker='s',
        cmap=cmap,
        alpha=1)

    # Choose colorbar style
    if np.unique(final_coordinates).shape[0] >= 1000:
        add_continuous_colorbar(scatter, final_coordinates[:, 2], cbar_label, plt.gca(), cmap=cmap)
    else:
        add_discrete_colorbar(scatter, final_coordinates[:, 2], cbar_label, plt.gca(), cmap=cmap)

    # Style
    plt.grid(visible=False)
    currentaax = plt.gca()
    for spine in currentaax.spines.values():
        spine.set_visible(False)

    ax = plt.gca()
    ax.invert_yaxis()
    ax.set_title('Clusters per frame', fontsize=20, weight='bold', family='monospace', style='italic')

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.tight_layout()
    plt.savefig(f'{savepath}_replicate_map.png', dpi=800)
    plt.close()
    return

# K-means Cross-validation metrics
def plot_sillohette_scores(cluster_range, silhouette_scores, outfile_path=None,
                           title=None, xlabel=None, ylabel=None):
    """
    Plot silhouette scores over k, mark the maximum, and save.

    Parameters
    ----------
    cluster_range : array-like
        Candidate k values.

    silhouette_scores : array-like
        Silhouette score per k (same length/order as `cluster_range`).

    outfile_path : str, default='sillohette_method.png'
        Path prefix or filename to save the figure. The code appends the suffix
        ``'sillohuette_plot'`` (note spelling) to this string.

    title, xlabel, ylabel : str or None
        Optional figure/axis labels.

    Returns
    -------
    int
        k with maximum silhouette score.

    Notes
    -----
    The filename suffix used in saving is ``'sillohuette_plot'`` for historical reasons.
    """
    outfile_path = outfile_path if outfile_path is not None else os.getcwd()

    optimal_k_sil = cluster_range[np.argmax(silhouette_scores)]
    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, silhouette_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k_sil, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k_sil}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Silhouette Score')
    plt.title(title if title is not None else 'Silhouette Score for optimal K')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'sillohuette_plot', dpi=300)
    plt.close()
    return optimal_k_sil

def plot_elbow_scores(cluster_range, inertia_scores, outfile_path=None,
                      title=None, xlabel=None, ylabel=None):
    """
    Plot inertia over k, estimate the elbow via the second derivative, and save.

    Parameters
    ----------
    cluster_range : array-like
        Candidate k values.

    inertia_scores : array-like
        KMeans inertia per k (same length/order as `cluster_range`).

    outfile_path : str, default='elbow_method.png'
        Path prefix or filename to save the figure. The code appends the suffix
        ``'elbow_plot'`` to this string.

    title, xlabel, ylabel : str or None
        Optional figure/axis labels.

    Returns
    -------
    int
        Estimated elbow k (argmin of the second difference + 1).
    """
    outfile_path=outfile_path if outfile_path is not None else os.getcwd()
    diff = np.diff(inertia_scores)
    diff2 = np.diff(diff)
    optimal_k = cluster_range[np.argmin(diff2) + 1]

    plt.figure(figsize=(8, 5))
    plt.plot(cluster_range, inertia_scores, marker='o', linestyle='-')
    plt.axvline(optimal_k, color='red', linestyle='--', linewidth=2, label=f'Optimal k = {optimal_k}')

    plt.xlabel(xlabel if xlabel is not None else 'Number of Clusters (k)')
    plt.ylabel(ylabel if ylabel is not None else 'Inertia (Sum of Squared Distances)')
    plt.title(title if title is not None else 'Elbow Method for Optimal k')
    plt.legend()
    plt.grid(True)
    plt.savefig(outfile_path + 'elbow_plot', dpi=300)
    plt.close()

    return optimal_k

# Circos plots
def get_Circos_coordinates(residue, gcircle):
    """
    Create chord endpoints anchored at the middle of a residue arc.

    Parameters
    ----------
    residue : str or int
        Residue arc identifier present in `gcircle`. If int, it will be looked
        up as a string (e.g., `'42'`).

    gcircle : py.Gcircle
        A PyCircos `Gcircle` object that already contains arcs.

    Returns
    -------
    tuple
        A 4-tuple `(arc_id, start_pos, end_pos, radial)` suitable for
        `Gcircle.chord_plot(...)`, where start and end positions are the arc
        midpoint and the radial anchor is 550.

    Notes
    -----
    Assumes the arc exists in `gcircle._garc_dict`. This is a convenience
    wrapper to place chords at arc midpoints for a tidy symmetric look.

    Examples
    --------
    >>> arc = get_Circos_coordinates('45', circle)
    >>> # later: circle.chord_plot(arc, other_arc, linewidth=1.5, facecolor='k')
    """
    arc = gcircle._garc_dict[str(residue)]
    mid_position = arc.size * 0.5
    raxis_position = 550
    return (residue, mid_position, mid_position, raxis_position)

def make_MDCircos_object(residue_indexes):
    """
    Build a PyCircos `Gcircle` with arcs for the provided residues.

    Arc sizing, label size, and figure size are coarsely adapted to the number
    of residues to keep visuals legible for both small and large sets.

    Parameters
    ----------
    residue_indexes : list of (str or int)
        Residue identifiers to add as arcs. Stored as strings internally.

    Returns
    -------
    py.Gcircle
        A `Gcircle` with arcs added and `set_garcs()` already called.

    Notes
    -----
    For small sets (<= 50 residues) a compact 6×6 figure is used; for larger
    sets a 10×10 figure with narrower labels and bigger arc sizes is used.
    """
    if len(residue_indexes) <= 50:
        circle = py.Gcircle(figsize=(6, 6))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',
                    edgecolor='#000000',
                    label=str(index),
                    label_visible=True,
                    labelposition=40,
                    labelsize=6,
                    size=10,
                    interspace=0,
                    linewidth=.1
                )
            )
        circle.set_garcs()

    if len(residue_indexes) > 50:
        circle = py.Gcircle(figsize=(10, 10))
        plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)

        for index in residue_indexes:
            circle.add_garc(
                py.Garc(
                    arc_id=str(index),
                    facecolor='#FFFFFF',
                    edgecolor='#000000',
                    label=str(index),
                    label_visible=True,
                    labelposition=30,
                    labelsize=2,
                    size=100,
                    interspace=4,
                    linewidth=.1
                )
            )

    circle.set_garcs()
    return circle

def mdcircos_graph(empty_circle, residue_dict, savepath=os.getcwd()+'mdcircos_graph',
                   scale_factor=5, colormap=cm.magma_r):
    """
    Draw chords on a PyCircos circle from pairwise weights and save images.

    Creates a chord diagram on `empty_circle` using `residue_dict` where keys
    are residue pair strings ``'i-j'`` and values are magnitudes (signed allowed).
    Saves the main diagram as ``savepath + '.png'`` and a separate colorbar image
    as ``savepath + '_colorbar.png'``.

    Parameters
    ----------
    empty_circle : py.Gcircle
        A `Gcircle` that already has arcs for all residues referenced by keys
        in `residue_dict`.

    residue_dict : dict[str, float]
        Mapping from pair key ``'i-j'`` to a numeric magnitude (used for both
        chord color and line width after normalization).

    savepath : str, default=os.getcwd()+'mdcircos_graph'
        Output *prefix* for image files.

    scale_factor : float, default=5
        Multiplier for the normalized chord linewidths.

    colormap : str or matplotlib.colors.Colormap, default=cm.magma_r
        Colormap used for chord colors and the separate colorbar.

    Returns
    -------
    None
        Saves figure(s) to disk and closes the colorbar figure.

    Notes
    -----
    - Colors are min-max normalized over the raw (signed) values; widths use
      min-max over absolute values for aesthetics.
    - Pair keys are split on the first '-' to look up per-residue arc anchors.

    Examples
    --------
    >>> circle = make_MDCircos_object(['10','20','30'])
    >>> weights = {'10-20': 0.4, '20-30': -0.2}
    >>> mdcircos_graph(circle, weights, savepath='/tmp/example')
    """
    import matplotlib.pyplot as plt
    from matplotlib import cm
    from matplotlib.colors import Normalize
    import numpy as np

    # Normalize the colors based on the values provided
    vals = list(residue_dict.values())
    vmin, vmax = min(vals), max(vals)
    color_norm = Normalize(vmin=vmin, vmax=vmax)
    cmap = colormap if colormap is not None else cm.plasma
    hex_color_map = {k: cmap(color_norm(v)) for k, v in residue_dict.items()}

    # Width normalization on the absolute values via min–max
    abs_vals = [abs(v) for v in vals if v != 0]
    min_abs, max_abs = min(abs_vals), max(abs_vals)
    denom = max_abs - min_abs if max_abs != min_abs else 1.0

    width_norm = {k: (abs(v) - min_abs) / denom for k, v in residue_dict.items()}

    # Draw chords
    for key, value in residue_dict.items():
        if value == 0:
            continue
        res1, res2 = key.split('-')
        arc1 = get_Circos_coordinates(res1, empty_circle)
        arc2 = get_Circos_coordinates(res2, empty_circle)
        color = hex_color_map[key]
        lw = width_norm[key] * scale_factor
        empty_circle.chord_plot(arc1, arc2, linewidth=lw, facecolor=color, edgecolor=color)

    empty_circle.figure.savefig(savepath + ".png", dpi=300, bbox_inches="tight")

    # Separate colorbar
    fig_cb, ax_cb = plt.subplots(figsize=(1.5, 4))
    sm = cm.ScalarMappable(cmap=cmap, norm=color_norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, cax=ax_cb)
    ticks = np.linspace(vmin, vmax, num=6)
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f"{t:.2f}" for t in ticks])
    cbar.set_label("Directional Difference")
    fig_cb.savefig(savepath + "_colorbar.png", dpi=300, bbox_inches="tight")
    plt.close(fig_cb)

def extract_properties_from_weightsdf(pca_table):
    """
    Parse a Systems Analysis weights table into residue IDs and per-PC weight mappings.

    Parameters
    ----------
    pca_table : pandas.DataFrame
        Must contain at least:
        - 'Comparisons' : str, residue pair keys like ``'i-j'``.
        - 'PC1_magnitude' : float
        - 'PC2_magnitude' : float

    Returns
    -------
    residues : list of str
        Unique residue IDs encountered in 'Comparisons', in first-appearance order.

    PC1_weight_dict : dict[str, float]
        Mapping ``'i-j'`` -> PC1 magnitude.

    PC2_weight_dict : dict[str, float]
        Mapping ``'i-j'`` -> PC2 magnitude.

    Notes
    -----
    Keys are preserved exactly; inverse pairs (``'i-j'`` vs ``'j-i'``) are not merged.
    """
    comps = pca_table['Comparisons'].astype(str)
    sides = comps.str.split('-', n=1, expand=True)
    residues = (sides.stack().str.strip().dropna().unique())
    residues = [str(x) for x in residues]
    PC1_weight_dict = pca_table.set_index('Comparisons')['PC1_magnitude'].to_dict()
    PC2_weight_dict = pca_table.set_index('Comparisons')['PC2_magnitude'].to_dict()
    return residues, PC1_weight_dict, PC2_weight_dict

def create_MDcircos_from_weightsdf(PCA_ranked_weights, outfilepath=None):
    """
    Create and save MD-circos diagrams for PC1 and PC2 magnitudes from a weights table.

    Parameters
    ----------
    PCA_ranked_weights : pandas.DataFrame
        Must include 'Comparisons', 'PC1_magnitude', and 'PC2_magnitude' columns.

    outfilepath : str or None, default=None
        Output *prefix* directory/path. If None, uses `os.getcwd()`. The function
        appends the stems:
            - 'PC1_magnitudeviz'
            - 'PC2_magnitudeviz'
        before adding file extensions.

    Returns
    -------
    None
        Saves the figures and colorbars to disk.

    Notes
    -----
    Both PC1 and PC2 visualizations share the same arc layout constructed from
    the residue IDs present in 'Comparisons'.
    """
    outfilepath = outfilepath if outfilepath is not None else os.getcwd()
    
    res_indexes, PC1_magnitude_dict, PC2_magnitude_dict = extract_properties_from_weightsdf(PCA_ranked_weights)
    pc1_circos_object = make_MDCircos_object(res_indexes)
    pc2_circos_object = make_MDCircos_object(res_indexes)
    mdcircos_graph(pc1_circos_object, PC1_magnitude_dict, outfilepath + 'PC1_magnitudeviz')
    mdcircos_graph(pc2_circos_object, PC2_magnitude_dict, outfilepath + 'PC2_magnitudeviz')
    return

# Embedding-space visualizations
def create_2d_color_mappings(
    labels=([80] * 20) + ([160] * 10),
    colors_list=('purple', 'orange', 'green', 'yellow', 'blue',
                 'red', 'pink', 'cyan', 'grey', 'brown'),
):
    """
    Produce a list of colors for 2-D scatter points given discrete labels.

    Parameters
    ----------
    labels : array-like of shape (n_samples,), default=([80]*20)+([160]*10)
        Discrete labels per sample (e.g., cluster IDs).

    colors_list : sequence of str, default=('purple','orange','green','yellow',
                                            'blue','red','pink','cyan','grey','brown')
        Palette to cycle through for unique labels.

    Returns
    -------
    list[str]
        A color per sample.

    Examples
    --------
    >>> labels = [0, 0, 1, 2, 2, 2]
    >>> colors = create_2d_color_mappings(labels)
    """
    label_dict = {}
    i = 0
    for label in labels:
        if label not in label_dict:
            label_dict[label] = colors_list[i % len(colors_list)]
            i += 1
    return [label_dict[i] for i in labels]

def visualize_reduction(embedding_coordinates,
                        cbar_type=None,
                        color_mappings=None,
                        savepath=os.getcwd(),
                        title=None,
                        cmap=None,
                        axis_one_label=None,
                        axis_two_label=None,
                        cbar_label=None,
                        gridvisible=False,
                        color_palette=None):
    """
    Plot a 2-D embedding (e.g., PCA/UMAP) as a scatter with optional coloring and colorbar,
    and save the figure to disk.

    Parameters
    ----------
    embedding_coordinates : array-like of shape (n_samples, 2)
        The 2D coordinates to plot.

    cbar_type : {'discrete', 'continuous'} or None, default=None
        Desired colorbar behavior. If None, defaults to 'discrete'.
        When 'discrete' is selected but the number of unique values in `color_mappings`
        is large (>= 250), the function automatically falls back to a continuous colorbar.

    color_mappings : array-like of shape (n_samples,) or None, default=None
        Values used to color points.
        - If provided (non-empty) and treated as *categorical* (i.e., `cbar_type='discrete'`
          and < 250 unique values), a discrete colorbar is drawn.
        - If provided but either `cbar_type='continuous'` or >= 250 unique values,
          a continuous colorbar is drawn.
        - If None or empty, points are colored by their index (0..n_samples-1)
          with a continuous colorbar.

    savepath : str, default=os.getcwd()
        Full output path **including filename**. No extension is appended automatically.
        The figure is saved at 500 DPI.

    title : str or None, default='Dimensional Reduction of Systems'
        Figure title.

    cmap : str or matplotlib.colors.Colormap or sequence, default=cm.magma_r
        Base colormap. If a sequence is passed, it is converted to a Colormap.
        Ignored when `color_palette` is provided.

    axis_one_label : str or None, default='Embedding Space Axis 1'
        X-axis label.

    axis_two_label : str or None, default='Embedding Space Axis 2'
        Y-axis label.

    cbar_label : str or None, default='Value'
        Colorbar label.

    gridvisible : bool, default=False
        If True, show a background grid.

    color_palette : sequence of color specs or matplotlib.colors.Colormap, default=None
        User-supplied palette that overrides `cmap`.
        - With categorical coloring: builds a ListedColormap from the sequence.
        - With continuous coloring or when `color_mappings` is None: builds a
          LinearSegmentedColormap from the sequence.
        - If a Colormap object is supplied, it is used directly.

    Returns
    -------
    None
        Saves the plot to `savepath` and closes the figure.

    Notes
    -----
    - Figure size is 16×12 inches at 300 DPI (saved at 500 DPI).
    - Axes spines are hidden; tick density is coarsened via `set_ticks`.
    - Automatically switches from discrete to continuous colorbar when
      unique categories >= 250 to keep the legend readable.
    """
     
    is_categorical = color_mappings is not None and len(color_mappings) > 0
    cbar_type=cbar_type if cbar_type is not None else 'discrete'

    def _as_colormap(seq_or_cmap, categorical):
        if isinstance(seq_or_cmap, mcolors.Colormap):
            return seq_or_cmap
        # treat lists/tuples/arrays of colors as a user palette
        seq = list(seq_or_cmap)
        return (mcolors.ListedColormap(seq)
                if categorical
                else mcolors.LinearSegmentedColormap.from_list('custom_palette', seq))

    # If user supplies a dedicated palette, it overrides cmap
    if color_palette is not None:
        cmap = _as_colormap(color_palette, is_categorical)
    # Back-compat: if user passed a list/tuple/ndarray to `cmap`, make it a proper Colormap
    elif isinstance(cmap, (list, tuple, np.ndarray)):
        cmap = _as_colormap(cmap, is_categorical)


    labels_font_dict = {
        'family': 'monospace',
        'size': 20,
        'weight': 'bold',
        'style': 'italic',
        'color': 'black',
    }

    fig = plt.figure(figsize=(16, 12), dpi=300)
    ax = plt.gca()

    if color_mappings is not None:
        if cbar_type == 'discrete' and len(np.unique(color_mappings)) < 250:
            scatter = ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                                c=color_mappings, cmap=cmap, alpha=0.6)
            add_discrete_colorbar(scatter, color_mappings, cbar_label, plt.gca(), cmap=cmap)
        
        if cbar_type == 'discrete' and len(np.unique(color_mappings)) > 250:
            scatter = ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                                c=color_mappings, cmap=cmap, alpha=0.6)
            add_continuous_colorbar(scatter, color_mappings, cbar_label, plt.gca(), cmap=cmap)

    if color_mappings is None:#default for no colormaps is values
        if cbar_type == 'discrete':
            print('Too many bins for discrete colormappings, transitioning to continous')
        values = np.arange(embedding_coordinates.shape[0])
        scatter = ax.scatter(embedding_coordinates[:, 0], embedding_coordinates[:, 1],
                             c=values, cmap=cmap, alpha=0.6)
        add_continuous_colorbar(scatter, values, cbar_label, plt.gca(), cmap=cmap)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.grid(visible=gridvisible)
    set_ticks(ax=plt.gca())
    ax.set_title(title, fontdict=labels_font_dict)
    ax.set_xlabel(axis_one_label, fontdict=labels_font_dict)
    ax.set_ylabel(axis_two_label, fontdict=labels_font_dict)
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')

    plt.tight_layout()
    plt.savefig(savepath, dpi=500)
    plt.close()
    return

# RMSD lineplots
def rmsd_lineplots(pandasdf=None, title='RMSD plot',
                   xgroupvar='window',
                   ygroupvar='rmsd',
                   xlab="window",
                   ylab="rmsd",
                   groupingvar='cluster',
                   cmap=cm.inferno_r,
                   cmap_is_colormap=True,
                   legendtitle='Cluster',
                   outfilepath=os.getcwd()):
    """
    Create a grouped line plot of RMSD (or similar metric) over a window variable.

    Parameters
    ----------
    pandasdf : pandas.DataFrame or None, default=None
        Data with at least the columns specified by `xgroupvar`, `ygroupvar`, and `groupingvar`.

    title : str, default='RMSD plot'
        Plot title.

    xgroupvar : str, default='window'
        Column used for the x-axis.

    ygroupvar : str, default='rmsd'
        Column used for the y-axis.

    xlab : str, default='window'
        X-axis label.

    ylab : str, default='rmsd'
        Y-axis label.

    groupingvar : str, default='cluster'
        Column used to form separate lines (and legend entries).

    cmap : str or matplotlib.colors.Colormap, default=cm.inferno_r
        Palette/colormap to use.

    cmap_is_colormap : bool, default=True
        If True, interpret `cmap` as a Matplotlib colormap.

    legendtitle : str, default='Cluster'
        Legend title.

    outfilepath : str, default=os.getcwd()
        Output *prefix* for the saved figure. The function appends ``'_rmsdlineplot'``.

    Returns
    -------
    None
        Saves the line plot and closes the figure.
    """
    if cmap_is_colormap:
        n_colors = pandasdf[groupingvar].nunique()
        cmap = [cmap(i) for i in np.linspace(0, 1, n_colors)]

    # if cmap_is_string, just pass it through (Seaborn handles it)
    # if both False, cmap will be used as-is

    plt.figure(figsize=(10, 8))
    sns.lineplot(
        data=pandasdf,
        x=xgroupvar,
        y=ygroupvar,
        hue=groupingvar,
        palette=cmap
    )

    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # show ticks where theres actually have windows
    unique_x = np.sort(pd.to_numeric(pandasdf[xgroupvar], errors="coerce").dropna().unique())
    ax.set_xticks(unique_x)                          # ticks exactly at your windows
    ax.set_xlim(unique_x.min(), unique_x.max())      # trim extra space
    ax.minorticks_off()                              # no half-step minor ticks

    # (optional) pretty integer labels if they’re whole numbers
    ax.set_xticklabels([str(int(x)) if float(x).is_integer() else f"{x:g}" for x in unique_x])

    plt.legend(title=legendtitle, bbox_to_anchor=(1.0, 1), loc="upper left")
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(title)
    plt.savefig(outfilepath + '_rmsdlineplot', dpi=800)
    plt.close()
    return

# Contour plots
def contour_embedding_space(outfile_path, embeddingspace_coordinates, levels=10, thresh=0, bw_adjust=.5,
                            title=None, xlabel=None, ylabel=None, gridvisible=False):
    """
    Plot a density contour map over 2-D embedding coordinates and save to disk.

    Parameters
    ----------
    outfile_path : str or None
        Output path (file name). If None, uses current working directory.

    embeddingspace_coordinates : array-like of shape (n_samples, 2)
        The 2-D embedding coordinates (e.g., PCA/UMAP).

    levels : int, default=10
        Number of contour levels.

    thresh : float, default=0
        Only draw contours where estimated density is greater than this threshold.

    bw_adjust : float, default=0.5
        Bandwidth adjustment factor for KDE.

    title : str or None, default=None
        Plot title.

    xlabel, ylabel : str or None, default=None
        Axis labels.

    gridvisible : bool, default=False
        Whether to show the background grid.

    Returns
    -------
    None
        Saves the contour plot and closes the figure.

    Notes
    -----
    Convenience wrapper over `sns.kdeplot` with filled contours and colorbar.
    """
    outfile_path = outfile_path if outfile_path is not None else os.getcwd()
    gridvisible = gridvisible if gridvisible is not None else False

    sns.kdeplot(
        x=embeddingspace_coordinates[:, 0],
        y=embeddingspace_coordinates[:, 1],
        fill=True,
        cmap="cividis",
        levels=levels,
        thresh=thresh,
        bw_adjust=bw_adjust,
        cbar=True
    )

    ax = plt.gca()
    for spine in ax.spines.values():
        spine.set_visible(False)

    if title:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    if ylabel:
        plt.ylabel(ylabel)

    plt.grid(visible=gridvisible)
    plt.savefig(outfile_path, dpi=800)
    plt.close()
    return

