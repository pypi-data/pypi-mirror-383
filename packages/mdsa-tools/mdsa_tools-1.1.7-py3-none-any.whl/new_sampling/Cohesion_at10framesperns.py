from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
import os

def make_replicate_ids(n400=20, n800=10, systems=1):
    chunks = []
    cur = 1
    for _ in range(systems):
        chunks.append(np.repeat(np.arange(cur, cur + n400, dtype=np.int32), 400))
        cur += n400
        chunks.append(np.repeat(np.arange(cur, cur + n800, dtype=np.int32), 800))
        cur += n800
    return np.concatenate(chunks)
replicate_ids = make_replicate_ids(systems=1)  # 60 uniques, length 6400


from mdsa_tools.Viz import visualize_reduction, replicatemap_from_labels

rep_lengths_one = (list(np.arange(0,400))*20 + list(np.arange(0,800))*10)

persys_frame_distributions=rep_lengths_one*2


'''
prep work above
'''


shaving_mask_shorts = ([False]*200 + [True]*400)*20
shaving_mask_longs = ([False]*200 + [True]*800)*10
system_mask=shaving_mask_shorts + shaving_mask_longs



full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')

full_sampling_GCU=full_sampling_GCU[system_mask]
full_sampling_CGU=full_sampling_CGU[system_mask]




#Just out of curiosity try just gcu
all_systems=[full_sampling_GCU,full_sampling_CGU]
Systems_Analyzer = systems_analysis(systems_representations=all_systems)
Systems_Analyzer.replicates_to_featurematrix()

system_labels = 16000*[1] + 16000*[2] 

X_pca,_ ,_=Systems_Analyzer.reduce_systems_representations(method="PCA")


GCU=X_pca[0:16000,:]
CGU=X_pca[16000:,:]
print(replicate_ids)
print(replicate_ids.shape)
print(len(persys_frame_distributions))
print(full_sampling_GCU.shape)
print(full_sampling_CGU.shape)


GCU_optimal_k_silhouette_labels, GCU_optimal_k_elbow_labels, GCU_centers_sillohuette, GCU_centers_elbow = Systems_Analyzer.perform_kmeans(data=GCU,outfile_path='./klust_10frameperns/GCU_',max_clusters=10)
CGU_optimal_k_silhouette_labels, CGU_optimal_k_elbow_labels, CGU_centers_sillohuette, CGU_centers_elbow = Systems_Analyzer.perform_kmeans(data=CGU,outfile_path='./klust_10frameperns/CGU_',max_clusters=10)

visualize_reduction(embedding_coordinates=GCU,color_mappings=GCU_optimal_k_silhouette_labels,cbar_type='discrete',cmap=cm.magma_r,savepath='./10dramepernscohesion/GCU')
visualize_reduction(embedding_coordinates=CGU,color_mappings=CGU_optimal_k_silhouette_labels,cbar_type='discrete',cmap=cm.magma_r,savepath='./10dramepernscohesion/CGU')

print(GCU_optimal_k_silhouette_labels.shape)
print(CGU_optimal_k_silhouette_labels.shape)
print(len(replicate_ids))
frames_one_system = [400]*20 + [800]*10
replicatemap_from_labels(labels=GCU_optimal_k_silhouette_labels,frame_list=frames_one_system,savepath='./10dramepernscohesion/GCU_replicate_map',title='GCU_replicate_map')
replicatemap_from_labels(labels=CGU_optimal_k_silhouette_labels,frame_list=frames_one_system,savepath='./10dramepernscohesion/CGU_replicate_map',title='CGU_replicate_map')

'''
Now lets evaluate the shorts and longs of both systems
'''

b = np.arange(16000) 
only_short  = (8000 <= b) 
only_long = (8000 > b) 

only_short_labels_GCU,only_long_labels_GCU=GCU_optimal_k_silhouette_labels[only_short],GCU_optimal_k_silhouette_labels[only_long]
only_short_labels_CGU,only_long_labels_CGU=CGU_optimal_k_silhouette_labels[only_short],CGU_optimal_k_silhouette_labels[only_long]

GCU_current_coordinates_short,GCU_current_coordinates_long=X_pca[0:16000,:][only_short,:],X_pca[16000:,:][only_long,:]
CGU_current_coordinates_short,current_coordinates_long=X_pca[16000:,:][only_short,:],X_pca[16000:,:][only_long,:]




from mdsa_tools.subdomain_explorations import MSM_Modeller as msm 

onlyshort_modeler_GCU,onlylong_modeler_GCU=msm(only_short_labels_GCU,GCU_centers_sillohuette,GCU_current_coordinates_short,[400]*20),msm(only_long_labels_GCU,GCU_centers_sillohuette,GCU_current_coordinates_long,[800]*10)
onlyshort_modeler_CGU,onlylong_modeler_CGU=msm(only_short_labels_GCU,GCU_centers_sillohuette,GCU_current_coordinates_short,[400]*20),msm(only_long_labels_GCU,GCU_centers_sillohuette,GCU_current_coordinates_long,[800]*10)

onlyshort_results_shrinkingGCU,onlylong_results_shrinkingGCU=onlyshort_modeler_GCU.evaluate_cohesion_shrinkingwindow(step_size=50),onlylong_modeler_GCU.evaluate_cohesion_shrinkingwindow(step_size=50)
onlyshort_results_shrinkingCGU,onlylong_results_shrinkingCGU=onlyshort_modeler_CGU.evaluate_cohesion_shrinkingwindow(step_size=50),onlylong_modeler_CGU.evaluate_cohesion_shrinkingwindow(step_size=50)


onlyshort_results_shrinkingGCU.to_csv('10dramepernscohesion/onlyshort_results_shrinkingGCU')
onlylong_results_shrinkingGCU.to_csv('10dramepernscohesion/onlylong_results_shrinkingGCU')
onlyshort_results_shrinkingCGU.to_csv('10dramepernscohesion/onlyshort_results_shrinkingCGU')
onlylong_results_shrinkingCGU.to_csv('10dramepernscohesion/onlylong_results_shrinkingCGU')

from mdsa_tools.Viz import rmsd_lineplots

outdir = "./10dramepernscohesion"
os.makedirs(outdir, exist_ok=True)

plot_specs = [
    ("RMSD — GCU (Shorts)", onlyshort_results_shrinkingGCU, "GCU_shorts"),
    ("RMSD — GCU (Longs)",  onlylong_results_shrinkingGCU,  "GCU_longs"),
    ("RMSD — CGU (Shorts)", onlyshort_results_shrinkingCGU, "CGU_shorts"),
    ("RMSD — CGU (Longs)",  onlylong_results_shrinkingCGU,  "CGU_longs"),
]

for title, df, slug in plot_specs:
    rmsd_lineplots(
        pandasdf=df,
        title=title,
        xgroupvar="window",   # adjust if your dataframe uses a different column name
        ygroupvar="rmsd",
        xlab="Window",
        ylab="RMSD",
        groupingvar="cluster",
        cmap=cm.inferno_r,
        cmap_is_colormap=True,
        legendtitle="Cluster",
        outfilepath=os.path.join(outdir, slug+'_50frame')  # function appends its own suffix
    )


persys_frame_list=((([400] * 20) + ([800] * 10)))


modeller_GCU = msm(GCU_optimal_k_silhouette_labels, GCU_centers_sillohuette, X_pca, frame_scale=persys_frame_list)
modeller_CGU = msm(CGU_optimal_k_silhouette_labels, CGU_centers_sillohuette, X_pca, frame_scale=persys_frame_list)


# Transition matrix + stationary states

Tmat_GCU = modeller_GCU.create_transition_probability_matrix()[1:,1:]
Tmat_CGU = modeller_CGU.create_transition_probability_matrix()[1:,1:]

print(Tmat_GCU.shape)
print(Tmat_CGU.shape)

np.savetxt('/Users/luis/Desktop/workspacetwo/new_sampling/10dramepernscohesion/Tmat_GCU.csv',Tmat_GCU,delimiter=',')
np.savetxt('/Users/luis/Desktop/workspacetwo/new_sampling/10dramepernscohesion/Tmat_CGU.csv',Tmat_CGU,delimiter=',')


import matplotlib.pyplot as plt
# Implied timescales
lags=[50,60,70,80,90,100,150,200,250,300,350,400,450,550,650]
its_GCU = modeller_GCU.compute_implied_timescales(lags=[50,60,70,80,90,100,150,200,250,300,350,400,450,550,650])
its_CGU = modeller_CGU.compute_implied_timescales(lags=[50,60,70,80,90,100,150,200,250,300,350,400,450,550,650])

for i in range(len(next(iter(its_GCU.values())))):
    plt.plot(lags, [its_GCU[lag][i] for lag in lags], marker='o')

plt.xlabel("Lag time")
plt.ylabel("Implied timescale")
plt.yscale("log")
plt.title(f"ITS plot: ")
plt.show()

for i in range(len(next(iter(its_CGU.values())))):
    plt.plot(lags, [its_CGU[lag][i] for lag in lags], marker='o')

plt.xlabel("Lag time")
plt.ylabel("Implied timescale")
plt.yscale("log")
plt.title(f"ITS plot: ")
plt.show()