import matplotlib.cm as cm
import os
import pandas as pd
from mdsa_tools.subdomain_explorations import MSM_Modeller as msm
import numpy as np
from mdsa_tools.Analysis import systems_analysis

from mdsa_tools.Viz import visualize_reduction
persys_frame_list=((([80] * 20) + ([160] * 10)))
persys_frame_short=([80] * 20) 
persys_frame_long= ([160] * 10)

# Pipeline setup assumed as in earlier analyses
X_pca=np.load('X_PCA_both_sys_embeddingspace.npy')
GCU_coordinates=X_pca[0:3200,:]
CGU_coordinates=X_pca[3200:,:]

GCU_opt_labels=np.load('klust/GCU_coordinates_kluster_labels_5clust.npy')
CGU_opt_labels=np.load('klust/CGU_coordinates_kluster_labels_2clust.npy')
GCU_sil_centers=np.load('./klust/GCU_sil_centers.npy')
CGU_sil_centers=np.load('./klust/CGU_sil_centers.npy')

# --------- GCU (as you had it) ----------
b = np.arange(3200) 
only_long  = (1600 <= b) 
only_short = (1600 > b) 

only_short_labels=GCU_opt_labels[only_short]
only_long_labels=GCU_opt_labels[only_long]

current_coordinates_short=X_pca[0:3200,:][only_short,:]
current_coordinates_long=X_pca[0:3200,:][only_long,:]

print(only_short_labels.shape)
print(only_long_labels.shape)
print(current_coordinates_short.shape)
print(current_coordinates_long.shape)

onlyshort_modeler=msm(only_short_labels,GCU_sil_centers,current_coordinates_short,persys_frame_short)
onlylong_modeler=msm(only_long_labels,GCU_sil_centers,current_coordinates_long,persys_frame_long)

onlyshort_results_shrinking=onlyshort_modeler.evaluate_cohesion_shrinkingwindow(step_size=20)
onlyshort_results_sliding=onlyshort_modeler.evaluate_cohesion_slidingwindow(step_size=20)

onlylong_results_shrinking=onlylong_modeler.evaluate_cohesion_shrinkingwindow(step_size=20)
onlylong_results_sliding=onlylong_modeler.evaluate_cohesion_slidingwindow(step_size=20)

onlyshort_results_shrinking.to_csv(f'./rmsd_df/GCU_5klust_onlyshort_results_shrinking.csv',float_format='%.2f')
onlyshort_results_sliding.to_csv(f'./rmsd_df/GCU_5klust_onlyshort_results_sliding.csv',float_format='%.2f')
onlylong_results_shrinking.to_csv(f'./rmsd_df/GCU_5klust_onlylong_shrinkingresults.csv',float_format='%.2f')
onlylong_results_sliding.to_csv(f'./rmsd_df/GCU_5klust_onlylong_slidingresults.csv',float_format='%.2f')

from mdsa_tools.Viz import rmsd_lineplots
rmsd_lineplots(onlyshort_results_shrinking,outfilepath='./rmsd_df/GCU_onlyshort_results_shrinking',cmap=cm.plasma)
rmsd_lineplots(onlyshort_results_sliding,outfilepath='./rmsd_df/GCU_onlyshort_results_sliding',cmap=cm.plasma)
rmsd_lineplots(onlylong_results_shrinking,outfilepath='./rmsd_df/GCU_onlylong_results_shrinking',cmap=cm.plasma)
rmsd_lineplots(onlylong_results_sliding,outfilepath='./rmsd_df/GCU_onlylong_results_sliding',cmap=cm.plasma)

# --------- CGU (added; mirrors GCU) ----------
b2 = np.arange(3200)
only_long_CGU  = (1600 <= b2)
only_short_CGU = (1600 > b2)

only_short_labels_CGU = CGU_opt_labels[only_short_CGU]
only_long_labels_CGU  = CGU_opt_labels[only_long_CGU]

current_coordinates_short_CGU = X_pca[3200:,:][only_short_CGU,:]
current_coordinates_long_CGU  = X_pca[3200:,:][only_long_CGU,:]

print(only_short_labels_CGU.shape)
print(only_long_labels_CGU.shape)
print(current_coordinates_short_CGU.shape)
print(current_coordinates_long_CGU.shape)

onlyshort_modeler_CGU = msm(only_short_labels_CGU, CGU_sil_centers, current_coordinates_short_CGU, persys_frame_short)
onlylong_modeler_CGU  = msm(only_long_labels_CGU,  CGU_sil_centers, current_coordinates_long_CGU,  persys_frame_long)

onlyshort_results_shrinking_CGU = onlyshort_modeler_CGU.evaluate_cohesion_shrinkingwindow(step_size=20)
onlyshort_results_sliding_CGU   = onlyshort_modeler_CGU.evaluate_cohesion_slidingwindow(step_size=20)

onlylong_results_shrinking_CGU  = onlylong_modeler_CGU.evaluate_cohesion_shrinkingwindow(step_size=20)
onlylong_results_sliding_CGU    = onlylong_modeler_CGU.evaluate_cohesion_slidingwindow(step_size=20)

onlyshort_results_shrinking_CGU.to_csv('./rmsd_df/CGU_2klust_onlyshort_results_shrinking.csv', float_format='%.2f')
onlyshort_results_sliding_CGU.to_csv('./rmsd_df/CGU_2klust_onlyshort_results_sliding.csv',   float_format='%.2f')
onlylong_results_shrinking_CGU.to_csv('./rmsd_df/CGU_2klust_onlylong_shrinkingresults.csv',  float_format='%.2f')
onlylong_results_sliding_CGU.to_csv('./rmsd_df/CGU_2klust_onlylong_slidingresults.csv',      float_format='%.2f')

rmsd_lineplots(onlyshort_results_shrinking_CGU,outfilepath='./rmsd_df/CGU_onlyshort_results_shrinking',cmap=cm.plasma)
rmsd_lineplots(onlyshort_results_sliding_CGU,outfilepath='./rmsd_df/CGU_onlyshort_results_sliding',cmap=cm.plasma)
rmsd_lineplots(onlylong_results_shrinking_CGU,outfilepath='./rmsd_df/CGU_onlylong_results_shrinking',cmap=cm.plasma)
rmsd_lineplots(onlylong_results_sliding_CGU,outfilepath='./rmsd_df/CGU_onlylong_results_sliding',cmap=cm.plasma)
