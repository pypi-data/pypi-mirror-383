import numpy as np
import mdtraj as md
from mdsa_tools.Cpptraj_import import cpptraj_hbond_import

import os


file='./GCU_HBond_Matrix.dat'
topology='../PDBs/5JUP_N2_GCU_nowat.prmtop'

importer_instance=cpptraj_hbond_import(file,topology)
rep=importer_instance.create_systems_rep()
print(rep.shape)
np.savez_compressed(f'GCU_full_sampling',rep=rep)

del importer_instance,rep,topology,file

file='./CGU_HBond_Matrix.dat'
topology='../PDBs/5JUP_N2_CGU_nowat.prmtop'

importer_instance=cpptraj_hbond_import(file,topology)
rep=importer_instance.create_systems_rep()
print(rep.shape)
np.savez_compressed(f'CGU_full_sampling',rep=rep)
