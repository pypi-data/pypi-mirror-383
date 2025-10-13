"""
Comapre analytic force and torque expressions to integrated Maxwell stress tensor
"""

import numpy as np
import matplotlib.pyplot as plt
import miepy
from math import factorial
from tqdm import tqdm
from scipy import constants

nm = 1e-9

Ag = miepy.materials. Ag()
# Ag = miepy.constant_material(4**2 + 0.01j)
radius = 75*nm
source = miepy.sources.rhc_polarized_plane_wave(amplitude=2)
separations = np.linspace(2*radius + 10*nm, 2*radius + 700*nm, 50)

spheres = miepy.spheres([[separations[0]/2,0,0], [-separations[0]/2,0,0]], radius, Ag)
mie = miepy.gmt(spheres, source, 600*nm, 2)

analytic_force = np.zeros((3,) + separations.shape)
analytic_torque = np.zeros_like(analytic_force)

mst_force = np.zeros_like(analytic_force)
mst_torque = np.zeros_like(analytic_force)

for i, separation in enumerate(tqdm(separations)):
    mie.update_position(np.array([[separation/2,0,0], [-separation/2,0,0]]))
    analytic_force[:,i] = mie.force_on_particle(0).squeeze()
    analytic_torque[:,i] = mie.torque_on_particle(0).squeeze()

    mst_force[:,i], mst_torque[:,i] = map(np.squeeze, 
            miepy.forces._gmt_force_and_torque_from_mst(mie, 0, sampling=30))

fig, axes = plt.subplots(nrows=2, ncols=3, figsize=plt.figaspect(2/3)*2)

for i in range(3):
    comp = ['x', 'y', 'z'][i]

    axes[0,i].plot(separations/nm, mst_force[i], 'o', color=f'C{i}', label='Numerical Stress Tensor')
    axes[1,i].plot(separations/nm, mst_torque[i], 'o', color=f'C{i}', label='Numerical Stress Tensor')

    axes[0,i].plot(separations/nm, analytic_force[i], color=f'C{i}', label='Analytic Equation')
    axes[1,i].plot(separations/nm, analytic_torque[i], color=f'C{i}', label='Analytic Equation')

    axes[0,i].set_title(label=f'F{comp}', weight='bold')
    axes[1,i].set_title(label=f'T{comp}', weight='bold')

for ax in axes.flatten():
    ax.axhline(y=0, color='black', linestyle='--')
    ax.legend()

for ax in axes[1]:
    ax.set_xlabel('separation (nm)')

axes[0,0].set_ylabel('force (N)')
axes[1,0].set_ylabel('torque (mN)')

plt.tight_layout()
plt.show()
