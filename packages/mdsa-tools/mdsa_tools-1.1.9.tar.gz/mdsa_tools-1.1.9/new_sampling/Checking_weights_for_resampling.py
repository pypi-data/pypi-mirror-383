from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
import os
shaving_mask_shorts = ([False]*200 + [True]*400)*20
shaving_mask_longs = ([False]*200 + [True]*800)*10
system_mask=shaving_mask_shorts + shaving_mask_longs # So we make sure we are sampling correctly

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')

full_sampling_GCU=full_sampling_GCU[system_mask]
full_sampling_CGU=full_sampling_CGU[system_mask]


#Just out of curiosity try just gcu
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(systems_representations=all_systems)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations(method="PCA")
new_sampling_df=Systems_Analyzer.create_PCA_ranked_weights()
sorted_new_sampling_df=new_sampling_df.sort_values('PC1_magnitude',ascending=False)
print(sorted_new_sampling_df.head(20))