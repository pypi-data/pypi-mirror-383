from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
import os


#umap below
#Pipeline setup assumed as in: Data Generation
redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=False)
redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=False)
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]


#For the paper we move forward with systems representations
Systems_Analyzer = systems_analysis(all_systems)
Systems_Analyzer.replicates_to_featurematrix()
#######################################################################################
#ALL of the examples of looking at worm behavior in same file bc of randomness of UMAP#
#######################################################################################
PCA_coordinates,_,_=Systems_Analyzer.reduce_systems_representations(method='PCA',n_components=2,n_neighbors=100,min_dist=.5) #PCA


def make_replicate_ids(n80=20, n160=10, systems=2):
    chunks = []
    cur = 1
    for _ in range(systems):
        chunks.append(np.repeat(np.arange(cur, cur + n80, dtype=np.int32), 80))
        cur += n80
        chunks.append(np.repeat(np.arange(cur, cur + n160, dtype=np.int32), 160))
        cur += n160
    return np.concatenate(chunks)

replicate_ids = make_replicate_ids()  # 60 uniques, length 6400

from mdsa_tools.Viz import visualize_reduction
# one system: 20×(1..80) then 10×(1..160)
rep_lengths_one = [80]*20 + [160]*10
one_system = np.concatenate([np.arange(1, L+1, dtype=np.int32) for L in rep_lengths_one])

# both systems: repeat that whole sequence twice → 6400 total
persys_frame_distributions = np.tile(one_system, 2)

import colorcet as cc
palette = cc.glasbey[:60]  # list of hex colors

visualize_reduction(
    PCA_coordinates,
    color_mappings=replicate_ids,
    cmap=palette,
    savepath='./umap_exmples/PCA_byrep',
    title='PCA Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False
)



###############
#worm behavior#
###############

from mdsa_tools.Viz import visualize_reduction

system_labels=(([1]*3200)+[2]*3200)

for i in range (1,7):
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=15,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./umap_exmples/syslabels_15n_point5mindist_run_3200_{i}',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./umap_exmples/crawlspace_15n_point5mindist_crawlspace_3200{i}',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./umap_exmples/repid_crawlspace_15n_point5mindist_crawlspace_{i}',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps


