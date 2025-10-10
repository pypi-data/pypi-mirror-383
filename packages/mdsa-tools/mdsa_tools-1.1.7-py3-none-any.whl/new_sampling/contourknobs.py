
from mdsa_tools.Analysis import systems_analysis
import numpy as np
import matplotlib.cm as cm
from mdsa_tools.Viz import visualize_reduction
import os

from mdsa_tools.Analysis import systems_analysis as sa
from mdsa_tools.Viz import contour_embedding_space

#Pipeline setup assumed as in: Data Generation
#redone_CCU_GCU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_GCU_Trajectory_array.npy',allow_pickle=True)
#redone_CCU_CGU_fulltraj=np.load('/Users/luis/Downloads/redone_unrestrained_CCU_CGU_Trajectory_array.npy',allow_pickle=True)

shaving_mask_shorts = ([False]*200 + [True]*400)*20
shaving_mask_longs = ([False]*200 + [True]*800)*10
system_mask=shaving_mask_shorts + shaving_mask_longs

full_sampling_GCU = np.load('/Users/luis/Downloads/full_sampling_CGU.npy')
full_sampling_CGU = np.load('/Users/luis/Downloads/full_sampling_GCU.npy')

redone_CCU_GCU_fulltraj=full_sampling_GCU[system_mask]
redone_CCU_CGU_fulltraj=full_sampling_CGU[system_mask]



#Just out of curiosity try just gcu
all_systems=[redone_CCU_GCU_fulltraj,redone_CCU_CGU_fulltraj]
Systems_Analyzer = systems_analysis(systems_representations=all_systems)
Systems_Analyzer.replicates_to_featurematrix()
X_pca,_,_= Systems_Analyzer.reduce_systems_representations()

levels_list = [5, 10, 15]
thresh_list = [0, 0.05, 0.1]
bw_adjust_list = [0.3, 0.5, 1.0]
grid_options = [False, True]

for i, levels in enumerate(levels_list, start=1):
    for thresh in thresh_list:
        for bw in bw_adjust_list:
            for grid in grid_options:
                
                # Optional: create a descriptive file name
                outfile = (
                    f"./contourknobs_fullsampling/"
                    f"contour_lvl{levels}_thr{thresh}_bw{bw}_grid{grid}_{i}.png"
                )

                contour_embedding_space(
                    outfile_path=outfile,
                    embeddingspace_coordinates=X_pca,  
                    levels=levels,
                    thresh=thresh,
                    bw_adjust=bw,
                    title=f"Contour Map: lvl={levels}, thr={thresh}, bw={bw}, grid={grid}",
                    xlabel="Component 1",
                    ylabel="Component 2",
                    gridvisible=grid
                )

                print(f"Saved: {outfile}")