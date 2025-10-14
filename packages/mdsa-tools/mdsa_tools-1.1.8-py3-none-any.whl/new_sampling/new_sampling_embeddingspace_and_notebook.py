from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.subdomain_explorations import MSM_Modeller as msm
from mdsa_tools.Viz import replicatemap_from_labels

frame_list=(([600]*20 + [1000]*10) * 2)
system_labels=(([1]*22000)+[2]*22000)
colormappings=[np.arange(0,np.max(i),1) for i in frame_list]
timeseries=np.concatenate(colormappings)

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')
print(full_sampling_GCU.shape,full_sampling_CGU.shape)

#Just out of curiosity try just gcu
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(systems_representations=all_systems,replicate_distribution=frame_list)
Systems_Analyzer.replicates_to_featurematrix()
UMAP_coordinates=Systems_Analyzer.reduce_systems_representations()
cluster_solodf=Systems_Analyzer.create_PCA_ranked_weights(outfile_path="./1_in_10_total_df")

PC1_magnitude_table=cluster_solodf.sort_values('PC1_magnitude',ascending=False)
PC2_magnitude_table=cluster_solodf.sort_values('PC2_magnitude',ascending=False)

PC1_magnitude_table.to_csv('./1_in_10_total_df_PC1_orderdf.csv')
PC2_magnitude_table.to_csv('./1_in_10_total_df_PC2_orderdf.csv')

optimal_k_silhouette_labels_GCU,optimal_k_elbow_labels_GCU,centers_sillohuette_GCU,centers_elbow_GCU=Systems_Analyzer.perform_kmeans(data=X_pca[0:22000,:],outfile_path='./embeddingspace/klust/GCU_')
optimal_k_silhouette_labels_CGU,optimal_k_elbow_labels_CGU,centers_sillohuette_CGU,centers_elbow_CGU=Systems_Analyzer.perform_kmeans(data=X_pca[22000:,:],outfile_path='./embeddingspace/klust/CGU_')

from mdsa_tools.Viz import visualize_reduction

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
