# Use non-GUI backend during tests (safe on CI)
import matplotlib
matplotlib.use("Agg", force=True)
from pathlib import Path
import mdsa_tools.Viz as vz


def test_visualize_reduction_largebins_saves_file(tmp_path, small_embedding):
    out = tmp_path / "viz_continuous.png"
    vz.visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=None,      # triggers continuous colormap branch
        savepath=out,        # function expects a file path here
        title="Test Continuous",
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False,
    )

    assert out.exists(), "visualize_reduction did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"


def test_visualize_reduction_saves_file(tmp_path, small_embedding, less_than_256_bin_colormappings):
    out = tmp_path / "viz_discrete.png"
    vz.visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=less_than_256_bin_colormappings,  # triggers discrete colormap branch
        savepath=out,
        title="Test Discrete",
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False,
    )

    assert out.exists(), "visualize_reduction did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"


def test_replicatemap_from_labels_saves_png(tmp_path, simple_labels_and_frames):
    labels, frame_list = simple_labels_and_frames
    out = tmp_path 

    vz.replicatemap_from_labels(
        labels=labels,
        frame_list=frame_list,
        savepath=out,   
        title="Replicate Map Test",
        xlabel="Frame",
        ylabel="Replicate",
        cmap=None,
    )

    assert out.exists(), "replicatemap_from_labels did not create the output file"
    assert out.stat().st_size > 0, "output image is empty"



def test_continuous_colorbar_branch(tmp_path, small_embedding):
    out = tmp_path / "viz_auto_continuous.png"
    vz.visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=None,
        savepath=out,
        title=None,
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False,
    )

    assert out.exists()

def test_discrete_colorbar_branch(tmp_path, small_embedding,less_than_256_bin_colormappings):
    out = tmp_path / "viz_auto_discrete.png"
    vz.visualize_reduction(
        embedding_coordinates=small_embedding,
        color_mappings=less_than_256_bin_colormappings,
        savepath=out,
        title=None,
        cmap=None,
        axis_one_label=None,
        axis_two_label=None,
        cbar_label=None,
        gridvisible=False,
    )
    
    assert out.exists()

def test_plot_silhouette_scores(tmp_path,kvals_and_silscores):
    kvals,scores=kvals_and_silscores
    out_prefix = tmp_path    
    
    best_k = vz.plot_sillohette_scores(
        cluster_range=kvals,
        silhouette_scores=scores,
        outfile_path=str(out_prefix),
        title="Sil scores",
        xlabel="k",
        ylabel="score",
    )

    assert best_k==5

def test_plot_elbow_scores(tmp_path,kvals_and_inertiascores):
    k_vals, inertia_scores=kvals_and_inertiascores
    out_prefix = tmp_path / "elbow_test"  
    
    best_k = vz.plot_elbow_scores(
        cluster_range=k_vals,
        inertia_scores=inertia_scores,
        outfile_path=str(out_prefix),
        title="Elbow Test",
        xlabel="k",
        ylabel="Inertia"
    )

    # Verify the returned optimal k
    assert best_k == 5 

def test_plot_elbow_scores(tmp_path,kvals_and_inertiascores):
    k_vals, inertia_scores=kvals_and_inertiascores
    out_prefix = tmp_path / "elbow_test"  
    
    best_k = vz.plot_elbow_scores(
        cluster_range=k_vals,
        inertia_scores=inertia_scores,
        outfile_path=str(out_prefix),
        title="Elbow Test",
        xlabel="k",
        ylabel="Inertia"
    )

    # Verify the returned optimal k
    assert best_k == 5 

###############################
#Moving into MDcircos Creation#
###############################

def test_MDcircos_creation(tmp_path,rankedweights_df):
    vz.create_MDcircos_from_weightsdf(rankedweights_df,str(tmp_path))
    return

#nice to see the submodules are working as intended
def test_extract_properties_from_weightsdf(rankedweights_df):
    vz.extract_properties_from_weightsdf(rankedweights_df)
    return



import matplotlib.pyplot as plt


def test_add_continuous_colorbar_runs(emptyplotting_space):
    fig, ax = emptyplotting_space
    scatter = ax.scatter([0, 1, 2], [0, 1, 2], c=[0.1, 0.2, 0.3])
    cbar = vz.add_continuous_colorbar(scatter, labels=[0.1, 0.2, 0.3], cbar_label="val", ax=ax)
    assert cbar is not None
    plt.close(fig)


def test_add_discrete_colorbar_runs(emptyplotting_space):
    fig, ax = emptyplotting_space
    labels = ["A", "B", "A"]
    scatter = ax.scatter([0, 1, 2], [0, 1, 2], c=[0, 1, 0])
    cbar = vz.add_discrete_colorbar(scatter, labels, cbar_label="cats", ax=ax)
    assert cbar is not None
    plt.close(fig)


def test_set_ticks_runs(emptyplotting_space):
    fig, ax = emptyplotting_space
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 200)
    vz.set_ticks(ax=ax)  # should adjust ticks, not error
    plt.close(fig)


def test_create_2d_color_mappings_returns_colors():
    labels = [0, 0, 1, 2]
    colors = vz.create_2d_color_mappings(labels)
    assert len(colors) == len(labels)


def test_rmsd_lineplots(tmp_path,rmsd_df):
    out = tmp_path / "rmsd"
    vz.rmsd_lineplots(rmsd_df, outfilepath=str(out))



def test_contour_embedding_space(tmp_path,small_embedding):
    out = tmp_path / "contour.png"
    vz.contour_embedding_space(str(out), small_embedding, levels=5)
    


def test_make_MDCircos_object_small_and_large():
    small = vz.make_MDCircos_object([1, 2, 3])
    assert small is not None
    large = vz.make_MDCircos_object(list(range(60)))
    assert large is not None


def test_get_Circos_coordinates_and_mdcircos_graph(tmp_path):
    circle = vz.make_MDCircos_object(["1", "2"])
    arc = vz.get_Circos_coordinates("1", circle)
    assert isinstance(arc, tuple)
    weights = {"1-2": 0.5}
    outprefix = str(tmp_path / "circos")
    vz.mdcircos_graph(circle, weights, savepath=outprefix)
   


