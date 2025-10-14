from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
import os
import pandas as pd

#Pipeline setup assumed as in: Data Generation
redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)

from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
import os

'''preliminary reduction with pca
'''

#basically a neat helper function for masking our systems the way we want to 
def make_replicate_ids(n400=20, n800=10, systems=2):
    chunks = []
    cur = 1
    for _ in range(systems):
        chunks.append(np.repeat(np.arange(cur, cur + n400, dtype=np.int32), 80))
        cur += n400
        chunks.append(np.repeat(np.arange(cur, cur + n800, dtype=np.int32), 160))
        cur += n800
    return np.concatenate(chunks)

replicate_ids = make_replicate_ids()  # 60 uniques, length 6400

from mdsa_tools.Viz import visualize_reduction

rep_lengths_one = (list(np.arange(0,80))*20 + list(np.arange(0,160))*10)

persys_frame_distributions=rep_lengths_one*2

'''preliminary reduction with pca

'''

#Just out of curiosity try just gcu
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]
Systems_Analyzer = systems_analysis(systems_representations=all_systems)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_,_= Systems_Analyzer.reduce_systems_representations()

system_labels = 3200*[1] + 3200*[2] 

import colorcet as cc
palette = cc.glasbey[:60]  # list of hex colors


#True yellow false is black
#ignore first half
start_mask = [True]*1600 + ([False]*20 + [True]*140)*10
end_mask = [True]*1600 + ([True]*140 + [False]*20)*10


visualize_reduction(X_pca[0:3200,:],color_mappings=start_mask,title='long only GCU first20ns of every trajectory',savepath='./2framepernscohesion/long_only_GCUfirst20ns_10frame',gridvisible=True)
visualize_reduction(X_pca[3200:,:],color_mappings=start_mask,title='long only CGU first 20ns of every trajectory',savepath='./2framepernscohesion/long_only_CGUfirst20ns_10frame',gridvisible=True)

visualize_reduction(X_pca[0:3200,:],color_mappings=end_mask,title='long only GCU last 20ns of every trajectory',savepath='./2framepernscohesion/long_only_GCUlast20ns_10frame',gridvisible=True)
visualize_reduction(X_pca[3200:,:],color_mappings=end_mask,title='long only CGU last 20ns of every trajectory',savepath='./2framepernscohesion/long_only_CGUlast20ns_10frame',gridvisible=True)

os._exit(0)

'''UMAP section
Now we can iterate to create multiple versions of our UMAP 
'''

for i in range (1,7):
    '''15 neighbors for thoroughness without changing distance'''  
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=15,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./orig_sampling/syslabels_15n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./orig_sampling/crawlspace_15n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./orig_sampling/repid_15n_.5min__{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps


    '''399 neighbors for thoroughness without changing distance'''
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=79,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./orig_sampling/syslabels_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./orig_sampling/crawlspace_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./orig_sampling/repid_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps



    '''799 neighbors for thoroughness without changing distance'''
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=3200,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./orig_sampling/syslabels_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./orig_sampling/crawlspace_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./orig_sampling/repid_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps


