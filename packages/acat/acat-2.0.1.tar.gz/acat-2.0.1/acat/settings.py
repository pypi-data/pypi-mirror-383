#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ase.formula import Formula
from ase.build import molecule
from ase.parallel import parprint
from ase.geometry import get_layers
from ase import Atoms
import numpy as np


# Adsorbate elements must be different from catalyst elements
adsorbate_elements = ['H', 'C', 'N', 'O', 'F', 'S', 'Cl', 'X']

# Adsorbate height on different sites
site_heights = {'ontop': 1.8, 
                'bridge': 1.5, 
                'shortbridge': 1.5,
                'longbridge': 1.5,
                'fcc': 1.3, 
                'hcp': 1.3,
                '3fold': 1.3, 
                '4fold': 1.3,
                '5fold': 1.5,
                '6fold': 0.,}

# The default adsorbate list already contains most common adsorbate 
# species. If you want to add any species, make sure you always sort 
# the indices of the atoms in the same order as the symbols, by adding 
# entries in the adsorbate_molecule function. 

# Adsorbate nomenclature: first element always starts from bonded index 
# or the bonded element if multi-dentate.
# Hydrogen is not considered as a bonding element except for H and H2.
# The hydrogens should always follow the atom that they bond to.
# This is different from ASE's nomenclature, e.g. water should be 'OH2',
# hydrogen peroxide should be 'OHOH'

# Monodentate (vertical)                            
monodentate_adsorbate_list = ['H','C','N','O','S',
                              'CH','NH','OH','SH','CO','NO','CN','CS','NS',
                              'CH2','NH2','OH2','SH2','COH','NOH',
                              'CH3','NH3','OCH',
                              'OCH2',
                              'OCH3',]

                              # You may want to put some monodentate species here
# Multidentate (lateral)      # as potential multidentate species on rugged surfaces
multidentate_adsorbate_list = ['H2','C2','N2','O2','S2','OS',
                               'CO2','NO2','O2N','N2O','SO2','O2S','CS2','NS2','CHN','CHO','NHO','COS','C3','O3',
                               'CHOH','CH2O','COOH','CHOO','OHOH',
                               'CH3O','CH2OH','CH3S','CH2CO',
                               'CH3OH','CHOOH','CH3CO',
                               'CH3COOH',
                               'CHCHCHCHCHCH',]

adsorbate_list = monodentate_adsorbate_list + multidentate_adsorbate_list
adsorbate_formulas = {k: ''.join(list(Formula(k))) for k in adsorbate_list}

# Add entries and make your own adsorbate molecules
def adsorbate_molecule(adsorbate):
    # The ase.build.molecule module has many issues.       
    # Adjust positions, angles and indexing for your needs.
    if adsorbate == 'CO':
        ads = molecule(adsorbate)[::-1]
    elif adsorbate == 'C2':
        ads = molecule('C2H2')
        del ads[-2:]
        ads.rotate(90, 'x')
    elif adsorbate in ['H2','N2','O2','S2']:
        ads = molecule(adsorbate)
        ads.rotate(90, 'x')
    elif adsorbate == 'NS':
        ads = molecule('CS')
        ads[0].symbol = 'N'
    elif adsorbate == 'OS':
        ads = molecule('SO')
        ads.rotate(90, 'x')
    elif adsorbate == 'OH2':
        ads = molecule('H2O')
        ads.rotate(180, 'y')
    elif adsorbate == 'CH2':
        ads = molecule('NH2')
        ads[0].symbol = 'C'
        ads.rotate(180, 'y')
    elif adsorbate in ['NH2','SH2']:
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'COH':
        ads = molecule('H2COH')
        del ads[-2:]
        ads.rotate(90, 'y')
    elif adsorbate == 'NOH':
        ads = molecule('H2COH')
        ads[0].symbol = 'N'
        del ads[-2:]
        ads.rotate(90, 'y')
    elif adsorbate == 'CO2':     
        ads = molecule(adsorbate)
        ads.rotate(90, 'x')
        ads.rotate(90, '-z')
    elif adsorbate in ['CS2','N2O']:
        ads = molecule(adsorbate)[[1,0,2]]
        ads.rotate(90, 'x')
    elif adsorbate == 'NS2':
        ads = molecule('CS2')[[1,0,2]]
        ads[0].symbol = 'N'
        ads.rotate(90, 'x')
    elif adsorbate == 'NO2':
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'O2N':
        ads = molecule('NO2')[::-1]
        ads.rotate(180, 'x')
        ads.rotate(180, 'y')
    elif adsorbate == 'O2S':
        ads = molecule('SO2')[::-1]
        ads.rotate(180, 'x')
        ads.rotate(180, 'y')
    elif adsorbate == 'SO2':
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate == 'CHN':
        ads = molecule('HCN')[[0,2,1]]
        ads.rotate(90, 'x')
        ads.rotate(90, '-z')
    elif adsorbate == 'CHO':
        ads = molecule('HCO')[[0,2,1]]
        ads.rotate(90, '-z')
    elif adsorbate == 'NHO':
        ads = molecule('HCO')[[0,2,1]]
        ads[0].symbol = 'N'
        ads.rotate(90, '-z')
    elif adsorbate == 'COS':
        ads = molecule('OCS')[[1,0,2]]
        ads.rotate(90, 'x')
    elif adsorbate == 'C3':
        ads = molecule('C3H4_D2d')
        del ads[-4:]
        ads.rotate(90, 'x')
    elif adsorbate == 'O3':
        ads = molecule(adsorbate)[[1,0,2]]
        ads.rotate(180, 'y')
    elif adsorbate == 'CH3':
        ads = molecule('CH3O')[[0,2,3,4]]
        ads.rotate(90, '-x')
    elif adsorbate == 'NH3':
        ads = molecule(adsorbate)
        ads.rotate(180, 'y')
    elif adsorbate in ['OOH','O2H']:
        ads = Atoms('OOH', positions=[
                    [0.        , 0.        , 0.10409395],
                    [1.22309921, 0.0632367 , 0.73652894],
                    [1.88101424, 0.09544209, 0.        ]])
    elif adsorbate == 'OCH2':
        ads = molecule('H2CO')
        ads.rotate(180, 'y')
    elif adsorbate == 'OCH3':
        ads = molecule('CH3O')[[1,0,2,3,4]]
        ads.rotate(90, '-x')
    elif adsorbate == 'CH2O':
        ads = molecule('H2CO')[[1,2,3,0]]
        ads.rotate(90, 'y')
        ads.rotate(180, '-z')
    elif adsorbate in ['CH3O','CH3S']:
        ads = molecule(adsorbate)[[0,2,3,4,1]]
        ads.rotate(30, 'y')
        ads.rotate(90, 'z')
    elif adsorbate == 'CH2CO':
        ads = molecule('H2CCO')[[0,2,3,1,4]]
        ads.rotate(90, 'y')
        ads.rotate(180, 'z')
    elif adsorbate == 'CHOH':
        ads = molecule('H2COH')
        del ads[-1]
        ads = ads[[0,3,1,2]]
    elif adsorbate == 'OHOH':
        ads = molecule('H2O2')[[0,2,1,3]]
        ads.rotate(90, '-z')
    elif adsorbate == 'CH2OH':
        ads = molecule('H2COH')[[0,3,4,1,2]]
    elif adsorbate == 'CH3OH':
        ads = molecule(adsorbate)[[0,2,4,5,1,3]]
        ads.rotate(-30, 'y')
        ads.rotate(90, '-z')
    elif adsorbate == 'CHOOH':
        ads = molecule('HCOOH')[[1,4,2,0,3]]
    elif adsorbate == 'CH3CO':
        ads = molecule(adsorbate)[[0,2,3,4,1,5]]
        ads.rotate(180, 'z')
    elif adsorbate == 'COOH':
        ads = Atoms('COOH', positions=[
                    (1.478221, 1.560435, 1.876707),
                    (2.124981, 0.480334, 2.067106),
                    (1.025178, 2.173870, 2.970078),
                    (0.550955, 3.006358, 2.725701),])
        ads.positions -= np.array([1.478221, 1.560435, 1.876707])
        ads.rotate(57, 'z')
    elif adsorbate == 'CHOO':
        ads = molecule('HCOOH')
        del ads[-2]
        ads = ads[[1,3,2,0]]
        ads.rotate(90, 'x')
        ads.rotate(7.5, 'y')
    elif adsorbate == 'CH3COOH':
        ads = molecule('CH3COOH')[[4,5,6,7,0,1,2,3]]
        ads.rotate(180, 'x')
    elif adsorbate == 'CHCHCHCHCHCH':
        ads = molecule('C6H6')[[0,6,1,7,2,8,3,9,4,10,5,11]] 
    elif adsorbate == 'X':
        ads = Atoms('X', positions=[[0, 0, 0]])
    else:
        try:
            ads = molecule(adsorbate)
        except:
            parprint('Molecule {} is not implemented. '.format(adsorbate) + 
                     'Use ase.Atoms to represent the adsorbate instead')
            return 
    return ads


class CustomSurface(object):

    """A customized surface class for general adsorption site identification 
    of any given surface structure. A reference surface structure is provided 
    to represent a certain type of surface with a certain size. For example, 
    a (4x4x4) rutile TiO2(101) surface can be used as the reference for any 
    (4x4x4) (101) surface with the same rutile crystal structure (even if it
    has different lattice constants).

    Parameters
    ----------
    ref_atoms : ase.Atoms object
        The reference surface structure. Accept any ase.Atoms object. 
        No need to be built-in.

    n_layers : int
        Number of layers in the slab structure given by ref_atoms.
        The top-most layer will be identified as the surface. Each
        layer can have multiple planes representing different
        morphologies such as step/terrace/corner.

    tol : float, default 0.3
        The maximum distance in Angstrom along the z direction for
        counting two atoms as belonging to the same plane.

    """

    def __init__(self, ref_atoms, n_layers=None, tol=0.3):
        self._ref_atoms = ref_atoms[[a.index for a in ref_atoms if 
                                    a.symbol not in adsorbate_elements]]
        self._n_layers = n_layers
        self._tol = tol
        if self._n_layers is not None:
            planes = get_layers(self._ref_atoms, (0,0,1), tolerance=self._tol)[0]
            quotient, remainder = divmod(len(np.unique(planes)), self._n_layers)
            self._n_morphs = int(quotient)
            assert remainder == 0, 'The total number of planes is not a multiple of n_layers'
            assert self.n_morphs <= 3, 'Too many identified planes in each layer'
            if self._n_morphs == 1:
                self._n_steps = 0
                self._n_terraces = np.count_nonzero(planes==np.max(planes))
                self._n_corners = 0
            elif self._n_morphs == 2:
                self._n_steps = np.count_nonzero(planes==np.max(planes))
                self._n_terraces = np.count_nonzero(planes==np.max(planes)-1)
                self._n_corners = 0
            elif self._n_morphs == 3:
                self._n_steps = np.count_nonzero(planes==np.max(planes))
                self._n_terraces = np.count_nonzero(planes==np.max(planes)-1)
                self._n_corners = np.count_nonzero(planes==np.max(planes)-2)
        else:
            self._n_morphs, self._n_steps = None, None
            self._n_terraces, self._n_corners = None, None

    @property
    def ref_atoms(self):
        return self._ref_atoms

    @property
    def n_layers(self):
        return self._n_layers

    @property
    def tol(self):
        return self._tol

    @property
    def n_morphs(self):
        return self._n_morphs

    @property
    def n_steps(self):
        return self._n_steps

    @property
    def n_terraces(self):
        return self._n_terraces

    @property
    def n_corners(self):
        return self._n_corners


