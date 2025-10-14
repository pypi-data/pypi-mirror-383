from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
import os
import pandas as pd

'''preliminary reduction with pca



'''

#basically a neat helper function for masking our systems the way we want to 
def make_replicate_ids(n400=20, n800=10, systems=2):
    chunks = []
    cur = 1
    for _ in range(systems):
        chunks.append(np.repeat(np.arange(cur, cur + n400, dtype=np.int32), 400))
        cur += n400
        chunks.append(np.repeat(np.arange(cur, cur + n800, dtype=np.int32), 800))
        cur += n800
    return np.concatenate(chunks)

replicate_ids = make_replicate_ids()  # 60 uniques, length 6400

from mdsa_tools.Viz import visualize_reduction

rep_lengths_one = (list(np.arange(0,400))*20 + list(np.arange(0,800))*10)

persys_frame_distributions=rep_lengths_one*2

'''preliminary reduction with pca



'''

shaving_mask_shorts = ([False]*200 + [True]*400)*20
shaving_mask_longs = ([False]*200 + [True]*800)*10
system_mask=shaving_mask_shorts + shaving_mask_longs

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')

full_sampling_GCU=full_sampling_GCU[system_mask]
full_sampling_CGU=full_sampling_CGU[system_mask]



#Just out of curiosity try just gcu
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(systems_representations=all_systems)
Systems_Analyzer.replicates_to_featurematrix()
PCA_df=Systems_Analyzer.create_PCA_ranked_weights()
PCA_df=PCA_df.sort_values(by='PC1_magnitude',ascending=False)
PCA_df_new=PCA_df.head(20)
PCA_df_new.to_csv('/Users/luis/Desktop/workspacetwo/new_sampling/top20_1in10_PC1.csv')

PC1_ordered_weights_orig = pd.read_csv('/Users/luis/Desktop/workspacetwo/manuscript_explorations/PC1_ordered_weights.csv')

res_indexes_orig=PC1_ordered_weights_orig[['Comparisons']]
res_indexes_new=PCA_df_new[['Comparisons']]

orig_only = res_indexes_orig[~res_indexes_orig['Comparisons'].isin(res_indexes_new['Comparisons'])]
new_only  = res_indexes_new[~res_indexes_new['Comparisons'].isin(res_indexes_orig['Comparisons'])]

print("Entries only in original:")
print(orig_only)

print("\nEntries only in new:")
print(new_only)

os._exit(0)

system_labels = 16000*[1] + 16000*[2] 

import colorcet as cc
palette = cc.glasbey[:60]  # list of hex colors

UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=16000,min_dist=.5) #PCA

visualize_reduction(UMAP_coordinates,
color_mappings=system_labels,cmap=cm.plasma_r,
savepath=f'./starting_over/syslabels_3200n_.5min.png',
title='UMAP Dimensional Reduction with per-system highlighting',
cbar_label='System',
gridvisible=False)#each system

visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
savepath=f'./starting_over/crawlspace_3200n_.5min.png',
title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
gridvisible=False)#all reps

visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
savepath=f'./starting_over/repid_3200n_.5min.png',
title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
gridvisible=False)#all reps
os._exit(0)

'''
Sigh ofcourse I didnt do the actual 16000 clustering and did cross-replicate shit instead i fucking hate myself so rerunning above
'''
X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations(method="PCA")


visualize_reduction(
    X_pca,
    color_mappings=replicate_ids,
    cmap=palette,
    savepath='./starting_over/PCA_byrep_',
    title='PCA Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False
)

visualize_reduction(
    X_pca,
    color_mappings=persys_frame_distributions,
    cmap=cm.magma_r,
    savepath='./starting_over/PCA_byframe_',
    title='PCA Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False
)

visualize_reduction(
    X_pca,
    color_mappings=system_labels,
    cmap=cm.plasma_r,
    savepath='./starting_over/PCA_bysystem_',
    title='PCA Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False
)


'''UMAP section
Now we can iterate to create multiple versions of our UMAP 
'''

for i in range (1,7):
    '''15 neighbors for thoroughness without changing distance'''  
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=15,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./starting_over/syslabels_15n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./starting_over/crawlspace_15n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./starting_over/repid_15n_.5min__{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps


    '''399 neighbors for thoroughness without changing distance'''
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=399,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./starting_over/syslabels_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./starting_over/crawlspace_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./starting_over/repid_399n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps



    '''799 neighbors for thoroughness without changing distance'''
    UMAP_coordinates=Systems_Analyzer.reduce_systems_representations(method='UMAP',n_components=2,n_neighbors=799,min_dist=.5) #PCA

    visualize_reduction(UMAP_coordinates,
    color_mappings=system_labels,cmap=cm.plasma_r,
    savepath=f'./starting_over/syslabels_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-system highlighting',
    cbar_label='System',
    gridvisible=False)#each system

    visualize_reduction(UMAP_coordinates,color_mappings=persys_frame_distributions,cmap=cm.magma_r,
    savepath=f'./starting_over/crawlspace_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps

    visualize_reduction(UMAP_coordinates,color_mappings=replicate_ids,cmap=palette,
    savepath=f'./starting_over/repid_799n_.5min_{i}.png',
    title='UMAP Dimensional Reduction with per-replicate frame highlighting',cbar_label='Frame Number',
    gridvisible=False)#all reps


