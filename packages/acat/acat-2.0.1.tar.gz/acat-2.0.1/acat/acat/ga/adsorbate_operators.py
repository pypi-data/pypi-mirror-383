#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Adsorbate procreation operators that adds an adsorbate to the surface of 
a particle or given structure."""
from ..settings import (adsorbate_elements, 
                        site_heights)
from ..utilities import (custom_warning, 
                         is_list_or_tuple, 
                         atoms_too_close_after_addition)
from ..adsorption_sites import (ClusterAdsorptionSites, 
                                SlabAdsorptionSites)
from ..adsorbate_coverage import (ClusterAdsorbateCoverage, 
                                  SlabAdsorbateCoverage)
from ..build.action import (add_adsorbate_to_site, 
                            remove_adsorbate_from_site, 
                            remove_adsorbates_from_sites)
from ase.ga.offspring_creator import OffspringCreator
from ase.formula import Formula
from ase import Atoms
from operator import attrgetter
from itertools import chain
from copy import deepcopy
import numpy as np
import warnings
import random
warnings.formatwarning = custom_warning


class AdsorbateOperator(OffspringCreator):
    """Base class for all operators that add, move or remove adsorbates.

    Don't use this operator directly!"""

    def __init__(self, adsorbate_species, species_probabilities=None, num_muts=1):        
        OffspringCreator.__init__(self, num_muts=num_muts)

        self.adsorbate_species = adsorbate_species if is_list_or_tuple(
                                 adsorbate_species) else [adsorbate_species]
        self.species_probabilities = species_probabilities
        if self.species_probabilities is not None:
            assert len(self.species_probabilities.keys()) == len(self.adsorbate_species)

        self.descriptor = 'AdsorbateOperator'

    @classmethod
    def initialize_individual(cls, parent, indi=None):
        indi = OffspringCreator.initialize_individual(parent, indi=indi)
        if 'unrelaxed_adsorbates' in parent.info['data']:
            unrelaxed = list(parent.info['data']['unrelaxed_adsorbates'])
        else:
            unrelaxed = []
        indi.info['data']['unrelaxed_adsorbates'] = unrelaxed
        
        return indi
        
    def get_new_individual(self, parents):
        raise NotImplementedError

    def add_adsorbate(self, atoms, hetero_site_list, heights, 
                      adsorbate_species=None, 
                      min_adsorbate_distance=2., 
                      tilt_angle=0.):
        """Adds the adsorbate in self.adsorbate to the supplied atoms
        object at the first free site in the specified site_list. A site
        is free if no other adsorbates can be found in a sphere of radius
        min_adsorbate_distance around the chosen site.

        Parameters
        ----------
        atoms : ase.Atoms object
            The atoms object that the adsorbate will be added to.

        hetero_site_list : list
            A list of dictionaries, each dictionary contains site 
            information given by acat.adsorbate_coverage module.

        heights : dict
            A dictionary that contains the adsorbate height for each site 
            type.

        adsorbate_species : str or list of strs, default None
            One or a list of adsorbate species to be added to the surface.
            Use self.adsorbate_species if not specified.

        min_adsorbate_distance : float, default 2.
            The radius of the sphere inside which no other adsorbates 
            should be found.
        
        tilt_angle : float, default 0.
            Tilt the adsorbate with an angle (in degrees) relative to the 
            surface normal.

        """

        if adsorbate_species is None:
            adsorbate_species = self.adsorbate_species
        elif not is_list_or_tuple(adsorbate_species): 
            adsorbate_species = [adsorbate_species]
        i = 0
        too_close = True
        while too_close:
            if i >= len(hetero_site_list):
                return False

            site = hetero_site_list[i]
            if site['occupied']:
                i += 1
                continue

            # Allow only single-atom species to enter subsurf 6fold sites
            this_site = site['site']
            if this_site == '6fold':
                tmp_adsorbate_species = [s for s in adsorbate_species if len(s) == 1]
                if tmp_adsorbate_species:
                    adsorbate_spcies = tmp_adsorbate_species

            # Add a random adsorbate to the correct position
            if (self.species_probabilities is None) or sum(
            self.species_probabilities[a] for a in adsorbate_species) == 0.:
                adsorbate = random.choice(adsorbate_species)
            else:
                probs = [self.species_probabilities[a] for a in adsorbate_species]
                adsorbate = random.choices(k=1, population=adsorbate_species,
                                           weights=probs)[0]                   
            height = heights[this_site]
            atoms = atoms.copy()
            add_adsorbate_to_site(atoms, adsorbate, site, height, 
                                  tilt_angle=tilt_angle)

            nads = len(list(Formula(adsorbate)))
            ads_atoms = atoms[[a.index for a in atoms if 
                               a.symbol in adsorbate_elements]]
            if atoms_too_close_after_addition(ads_atoms, nads, 
            cutoff=min_adsorbate_distance, mic=(True in atoms.pbc)):
                atoms = atoms[:-nads]
                i += 1
                continue    
            too_close = False 

        # Setting the indices of the unrelaxed adsorbates for the cut-
        # relax-paste function to be executed in the calculation script.
        # There it should also reset the parameter to [], to indicate
        # that the adsorbates have been relaxed.
        ads_indices = sorted([len(atoms) - k - 1 for k in range(nads)])
        
        if 'unrelaxed_adsorbates' not in atoms.info['data']:
            atoms.info['data']['unrelaxed_adsorbates'] = []
        atoms.info['data']['unrelaxed_adsorbates'].append(ads_indices)
        
        return atoms

    def remove_adsorbate(self, atoms, hetero_site_list, return_site_index=False,
                         fragmentation=True): 
        """Removes an adsorbate from the atoms object at the first occupied
        site in hetero_site_list. If no adsorbates can be found, one will be
        added instead.

        Parameters
        ----------
        atoms : ase.Atoms object
            The atoms object that the adsorbate will be added to

        hetero_site_list : list
            A list of dictionaries, each dictionary contains site 
            information given by acat.adsorbate_coverage module.

        return_site_index : bool, default False
            Whether to return the site index of the hetero_site_list instead
            of the site. Useful for moving or replacing adsorbate.

        """

        i = 0
        occupied = False
        while not occupied:
            if i >= len(hetero_site_list):
                if return_site_index:
                    return False
                warnings.warn('Removal not possible, will add instead')
                return self.add_adsorbate(atoms, hetero_site_list, site_heights)

            site = hetero_site_list[i]
            if not site['occupied']:
                i += 1
                continue
            # Remove adsorbate from the correct position. Remove the fragment
            # with priority if it is one of the given adsorbate species
            if fragmentation:
                rm_frag = (site['fragment'] in self.adsorbate_species)
            else:
                if site['adsorbate'] not in self.adsorbate_species:
                    i += 1
                    continue
                rm_frag = False
            remove_adsorbate_from_site(atoms, site, remove_fragment=rm_frag)

            if return_site_index:
                return i
            occupied = True

        return atoms

    def get_all_adsorbate_indices(self, atoms):
        from asap3 import FullNeighborList

        ac = atoms.copy()
        ads_ind = [a.index for a in ac if 
                   a.symbol in adsorbate_elements]
        mbl = 1.5  # max_bond_length
        nl = FullNeighborList(rCut=mbl / 2., atoms=ac)

        adsorbates = []
        while len(ads_ind) != 0:
            i = int(ads_ind[0])
            mol_ind = self._get_indices_in_adsorbate(ac, nl, i)
            for ind in mol_ind:
                if int(ind) in ads_ind:
                    ads_ind.remove(int(ind))
            adsorbates.append(sorted(mol_ind))
        return adsorbates

    def get_adsorbate_indices(self, atoms, position):
        """Returns the indices of the adsorbate at the supplied position."""
        dmin = 1000.
        for a in atoms:
            if a.symbol in adsorbate_elements:
                d = np.linalg.norm(a.position - position)
                if d < dmin:
                    dmin = d
                    ind = a.index

        for ads in self.get_all_adsorbate_indices(atoms):
            if ind in ads:
                return ads[:]
        
    def _get_indices_in_adsorbate(self, atoms, neighborlist,
                                  index, molecule_indices=None):
        """Internal recursive function that help
        determine adsorbate indices."""
        if molecule_indices is None:
            molecule_indices = []
        mi = molecule_indices
        nl = neighborlist
        mi.append(index)
       # neighbors, _ = nl.get_neighbors(index)
        neighbors = nl[index]

        for n in neighbors:
            if int(n) not in mi:
                if atoms[int(n)].symbol in adsorbate_elements:
                    mi = self._get_indices_in_adsorbate(atoms, nl, n, mi)
        return mi


class AddAdsorbate(AdsorbateOperator):
    """
    Use this operator to add adsorbates to the surface.
    The surface is allowed to change during the algorithm run.

    There is no limit of adsorbate species. You can either provide one
    species or a list of species.

    Site and surface preference can be supplied. If both are supplied site
    will be considered first.

    Supplying a tilt angle will tilt the adsorbate with an angle relative
    to the standard perpendicular to the surface.

    The operator is generalized for both periodic and non-periodic systems 
    (distinguished by atoms.pbc).

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of adding onto the surface.
        Adding adsorbate species with equal probability if not specified.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    min_adsorbate_distance : float, default 2.
        The radius of the sphere inside which no other adsorbates 
        should be found.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    site_preference : str or list of strs, defualt None
        The site type(s) that has higher priority to attach adsorbates.

    surface_preference : str, default None
        The surface type that has higher priority to attach adsorbates.
        Please only use this for nanoparticles.

    max_coverage : float, default None
        The maximum allowed coverage on the surface. Coverage is defined
        as (number of surface occupied sites / number of surface atoms).
        The maximum coverage is solely governed by min_adsorbate_distance 
        if max_coverage is not specified.

    tilt_angle : float, default 0.
        Tilt the adsorbate with an angle (in degrees) relative to the 
        surface normal.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 species_probabilities=None,
                 max_species=None,
                 heights=site_heights,
                 min_adsorbate_distance=2.,
                 adsorption_sites=None,
                 site_preference=None,
                 surface_preference=None,
                 max_coverage=None,
                 tilt_angle=None,
                 subtract_heights=False,
                 fragmentation=True,
                 catalyst_indices=None,
                 num_muts=1,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species,
                                   species_probabilities,
                                   num_muts=num_muts)
        self.descriptor = 'AddAdsorbate'

        if max_species is None:                                                             
            self.max_species = None
        else:
            self.max_species = min([max_species, len(set(self.adsorbate_species))])
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.min_adsorbate_distance = min_adsorbate_distance
        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)

        self.site_preference = site_preference
        if site_preference is not None:
            if not is_list_or_tuple(site_preference):
                self.site_preference = [site_preference]
        self.surface_preference = surface_preference

        self.max_coverage = max_coverage        
        self.tilt_angle = tilt_angle or 0.
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 1
        self.dmax = dmax

    def get_new_individual(self, parents):
        """Returns the new individual as an atoms object."""
        f = parents[0]

        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]

        for atom in f:
            indi.append(atom)

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = SlabAdsorptionSites(indi, **self.kwargs)
            sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax,
                                        adsorbate_indices=adsorbate_indices)
        else:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = ClusterAdsorptionSites(indi, **self.kwargs)
            sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax,
                                           adsorbate_indices=adsorbate_indices)
        ads_sites = sac.hetero_site_list

        if self.max_species is None:
            options = self.adsorbate_species.copy()
        else:
            occupied_specs = list({st['adsorbate'] for st in ads_sites if st['occupied']
                                   and (st['adsorbate'] in self.adsorbate_species)})
            diff = self.max_species - len(occupied_specs)
            if diff == 0:
                options = occupied_specs
            elif diff > 0:
                others = [sp for sp in self.adsorbate_species if sp not in occupied_specs]
                if (self.species_probabilities is None) or sum(
                self.species_probabilities[osp] for osp in others) == 0.:
                    dspecs = random.sample(others, diff)
                else:
                    probs = [self.species_probabilities[osp] for osp in others]
                    dspecs = random.choices(k=diff, population=others, weights=probs) 
                options = occupied_specs + dspecs
            else:
                options = occupied_specs
                warnings.warn('The number of adsorbate species exceeds ' +
                              'the maximum allowed number.')
 
        for i in range(self.num_muts):
            # Make sure the coverage does not exceed maximum coverage
            if self.max_coverage is not None:
                if sac.coverage >= self.max_coverage:
                    if i == 0:
                        warnings.warn('Addition not possible, will remove instead')
                        indi = self.remove_adsorbate(indi, ads_sites, 
                                                     fragmentation=self.fragmentation)
                    break

            random.shuffle(ads_sites)
            if self.surface_preference is not None:
                def func(x):
                    return x['surface'] == self.surface_preference
                ads_sites.sort(key=func, reverse=True)

            if self.site_preference is not None:
                def func(x):
                    return x['site'] in self.site_preference
                ads_sites.sort(key=func, reverse=True)

            nindi = self.add_adsorbate(indi, ads_sites, self.heights, 
                                       options, self.min_adsorbate_distance,
                                       tilt_angle=self.tilt_angle)
            if not nindi:
                warnings.warn('Addition not possible, will remove instead')
                indi = self.remove_adsorbate(indi, ads_sites, 
                                             fragmentation=self.fragmentation)
                break

            indi = nindi
            if self.catalyst_indices is None:                              
                adsorbate_indices = None
            else:
                adsorbate_indices = [a.index for a in indi if 
                                     a.index not in self.catalyst_indices]
            if True in indi.pbc:
                sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                            self.subtract_heights, dmax=self.dmax,
                                            adsorbate_indices=adsorbate_indices)
            else:
                sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                               self.subtract_heights, dmax=self.dmax,
                                               adsorbate_indices=adsorbate_indices)
            ads_sites = sac.hetero_site_list                          
        
        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                sac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = sac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0}'.format(f.info['confid']))


class RemoveAdsorbate(AdsorbateOperator):
    """This operator removes an adsorbate from the surface. It works
    exactly (but doing the opposite) as the AddAdsorbate operator.

    The operator is generalized for both periodic and non-periodic systems 
    (distinguished by atoms.pbc).

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be removed from the surface.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    site_preference : str or list of strs, defualt None
        The site type(s) that has higher priority to detach adsorbates.

    surface_preference : str, default None
        The surface type that has higher priority to detach adsorbates.
        Please only use this for nanoparticles.

    min_coverage : float, default None
        The minimum allowed coverage on the surface. Coverage is defined
        as (number of surface occupied sites / number of surface atoms).
        The minimum coverage is 0 if min_coverage is not specified.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 adsorption_sites=None,
                 site_preference=None,
                 surface_preference=None,
                 min_coverage=None,
                 subtract_heights=False,
                 fragmentation=True,
                 catalyst_indices=None,
                 num_muts=1,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species,
                                   num_muts=num_muts)
        self.descriptor = 'RemoveAdsorbate'

        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)

        self.site_preference = site_preference
        if site_preference is not None:
            if not is_list_or_tuple(site_preference):
                self.site_preference = [site_preference]

        self.min_coverage = min_coverage
        self.surface_preference = surface_preference
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 1
        self.dmax = dmax

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]

        for atom in f:
            indi.append(atom)

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = SlabAdsorptionSites(indi, **self.kwargs)
            sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax,
                                        adsorbate_indices=adsorbate_indices)
        else:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = ClusterAdsorptionSites(indi, **self.kwargs)
            sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax,
                                           adsorbate_indices=adsorbate_indices)
        ads_sites = sac.hetero_site_list

        for _ in range(self.num_muts):
            # Make sure the coverage is not lower than the minimum coverage
            if self.min_coverage is not None:
                if sac.coverage <= self.min_coverage:
                    break

            random.shuffle(ads_sites)
            if self.surface_preference is not None:
                def func(x):
                    return x['surface'] == self.surface_preference
                ads_sites.sort(key=func, reverse=True)

            if self.site_preference is not None:
                def func(x):
                    return x['site'] in self.site_preference
                ads_sites.sort(key=func, reverse=True)

            indi = self.remove_adsorbate(indi, ads_sites, fragmentation=self.fragmentation)

            if self.catalyst_indices is None:
                adsorbate_indices = None
            else:
                adsorbate_indices = [a.index for a in indi if 
                                     a.index not in self.catalyst_indices]
            if True in indi.pbc:
                sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                            self.subtract_heights, dmax=self.dmax,
                                            adsorbate_indices=adsorbate_indices)
            else:
                sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                               self.subtract_heights, dmax=self.dmax,
                                               adsorbate_indices=adsorbate_indices)
            ads_sites = sac.hetero_site_list               
            # Make sure there are still adsorbates to remove
            if not any(st for st in ads_sites if st['occupied']):
                break          
 
        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                sac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = sac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0}'.format(f.info['confid']))


class MoveAdsorbate(AdsorbateOperator):                                           
    """This operator removes an adsorbate from the surface and adds it
    again to a different site, i.e. effectively moving the adsorbate.

    The operator is generalized for both periodic and non-periodic systems 
    (distinguished by atoms.pbc).

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    min_adsorbate_distance : float, default 2.
        The radius of the sphere inside which no other adsorbates 
        should be found.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    site_preference_from : str or list of strs, defualt None
        The site type(s) that has higher priority to detach adsorbates.

    surface_preference_from : str, default None
        The surface type that has higher priority to detach adsorbates.
        Please only use this for nanoparticles.

    site_preference_to : str or list of strs, defualt None
        The site type(s) that has higher priority to attach adsorbates.

    surface_preference_to : str, default None
        The surface type that has higher priority to attach adsorbates.
        Please only use this for nanoparticles.

    tilt_angle : float, default 0.
        Tilt the adsorbate with an angle (in degrees) relative to the 
        surface normal.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added.

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 heights=site_heights,
                 min_adsorbate_distance=2.,
                 adsorption_sites=None,
                 site_preference_from=None,
                 surface_preference_from=None,
                 site_preference_to=None,
                 surface_preference_to=None,
                 tilt_angle=None,
                 subtract_heights=False,
                 fragmentation=True,
                 catalyst_indices=None,
                 num_muts=1,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species,
                                   num_muts=num_muts)
        self.descriptor = 'MoveAdsorbate'

        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.min_adsorbate_distance = min_adsorbate_distance
        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)

        self.site_preference_from = site_preference_from
        if site_preference_from is not None:
            if not is_list_or_tuple(site_preference_from):
                self.site_preference_from = [site_preference_from]
        self.surface_preference_from = surface_preference_from
        self.site_preference_to = site_preference_to
        if site_preference_to is not None:
            if not is_list_or_tuple(site_preference_to):
                self.site_preference_to = [site_preference_to]
        self.surface_preference_to = surface_preference_to
        self.tilt_angle = tilt_angle or 0.
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 1
        self.dmax = dmax

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]

        for atom in f:
            indi.append(atom)

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = SlabAdsorptionSites(indi, **self.kwargs)
            sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax,
                                        adsorbate_indices=adsorbate_indices)
        else:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = ClusterAdsorptionSites(indi, **self.kwargs) 
            sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax,
                                           adsorbate_indices=adsorbate_indices)
        ads_sites = sac.hetero_site_list

        for _ in range(self.num_muts):
            random.shuffle(ads_sites)
            if self.surface_preference_from is not None:
                def func(x):
                    return x['surface'] == self.surface_preference_from
                ads_sites.sort(key=func, reverse=True)

            if self.site_preference_from is not None:
                def func(x):
                    return x['site'] in self.site_preference_from
                ads_sites.sort(key=func, reverse=True)

            removed = self.remove_adsorbate(indi, ads_sites,
                                            return_site_index=True,
                                            fragmentation=self.fragmentation)
            if (removed is False) or (self.fragmentation is False):
                removed_species = random.choice(self.adsorbate_species)
            else:
                removed_species = ads_sites[removed]['fragment']
                if not removed_species:
                    removed_species = random.choice(self.adsorbate_species)
            random.shuffle(ads_sites)

            if self.surface_preference_to is not None:
                def func(x):
                    return x['surface'] == self.surface_preference_to
                ads_sites.sort(key=func, reverse=True)

            if self.site_preference_to is not None:
                def func(x):
                    return x['site'] in self.site_preference_to
                ads_sites.sort(key=func, reverse=True)

            nindi = self.add_adsorbate(indi, ads_sites, 
                                       self.heights, removed_species,
                                       self.min_adsorbate_distance,
                                       tilt_angle=self.tilt_angle)
            if not nindi:
                break

            indi = nindi
            if self.catalyst_indices is None:
                adsorbate_indices = None
            else:
                adsorbate_indices = [a.index for a in indi if 
                                     a.index not in self.catalyst_indices]
            if True in indi.pbc:
                sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                            self.subtract_heights, dmax=self.dmax,
                                            adsorbate_indices=adsorbate_indices)
            else:
                sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                               self.subtract_heights, dmax=self.dmax,
                                               adsorbate_indices=adsorbate_indices)
            ads_sites = sac.hetero_site_list                          

        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                sac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = sac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0}'.format(f.info['confid']))


class ReplaceAdsorbate(AdsorbateOperator):                                           
    """This operator removes an adsorbate from the surface and adds another
    species to the same site, i.e. effectively replacing the adsorbate.

    The operator is generalized for both periodic and non-periodic systems 
    (distinguished by atoms.pbc).

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    species_probabilities : dict, default None
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of replacing an adsorbate on the 
        surface. Choosing adsorbate species with equal probability if 
        not specified.

    max_species : int, default None
        The maximum allowed adsorbate species (excluding vacancies) for a
        single structure. Allow all adsorbate species if not specified.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    min_adsorbate_distance : float, default 2.
        The radius of the sphere inside which no other adsorbates 
        should be found.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    site_preference : str or list of strs, defualt None
        The site type(s) that has higher priority to replace adsorbates.

    surface_preference : str, default None
        The surface type that has higher priority to replace adsorbates.
        Please only use this for nanoparticles.

    tilt_angle : float, default 0.
        Tilt the adsorbate with an angle (in degrees) relative to the 
        surface normal.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    num_muts : int, default 1
        The number of times to perform this operation.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 species_probabilities=None,
                 max_species=None,
                 heights=site_heights,
                 min_adsorbate_distance=2.,
                 adsorption_sites=None,
                 site_preference=None,
                 surface_preference=None,
                 tilt_angle=None,
                 subtract_heights=False,
                 fragmentation=True,
                 catalyst_indices=None,
                 num_muts=1,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species,
                                   species_probabilities,
                                   num_muts=num_muts)
        self.descriptor = 'ReplaceAdsorbate'

        if max_species is None:                                                    
            self.max_species = None
        else:
            self.max_species = min([max_species, len(set(self.adsorbate_species))])
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.min_adsorbate_distance = min_adsorbate_distance
        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)

        self.site_preference = site_preference
        if site_preference is not None:
            if not is_list_or_tuple(site_preference):
                self.site_preference = [site_preference]
        self.surface_preference = surface_preference

        self.tilt_angle = tilt_angle or 0.
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 1
        self.dmax = dmax

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]

        for atom in f:
            indi.append(atom)

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = SlabAdsorptionSites(indi, **self.kwargs)
            sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax,
                                        adsorbate_indices=adsorbate_indices)
        else:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = ClusterAdsorptionSites(indi, **self.kwargs) 
            sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax,
                                           adsorbate_indices=adsorbate_indices)
        ads_sites = sac.hetero_site_list

        for _ in range(self.num_muts):
            random.shuffle(ads_sites)
            if self.surface_preference is not None:
                def func(x):
                    return x['surface'] == self.surface_preference
                ads_sites.sort(key=func, reverse=True)

            if self.site_preference is not None:
                def func(x):
                    return x['site'] in self.site_preference
                ads_sites.sort(key=func, reverse=True)

            removed = self.remove_adsorbate(indi, ads_sites,
                                            return_site_index=True,
                                            fragmentation=self.fragmentation)
            if removed is False:
                removed = random.choice(range(len(ads_sites)))
                removed_species = 'x'
            else:
                removed_species = ads_sites[removed]['fragment']
            ads_sites[removed]['occupied'] = 0
            other_specs = [s for s in self.adsorbate_species if
                           s != removed_species]
            if self.max_species is None:
                options = other_specs
            else:
                occupied_specs = list({st['adsorbate'] for st in ads_sites if st['occupied'] 
                                       and (st['adsorbate'] in self.adsorbate_species)})
                diff = self.max_species - len(occupied_specs)
                if diff == 0:
                    options = [s for s in occupied_specs if s in other_specs]
                    if len(options) == 0:
                        warnings.warn('The number of adsorbate species will likely exceed ' +
                                      'the maximum allowed number due to new adsorbate species.')
                        options = other_specs
                elif diff > 0:
                    options = other_specs
                else:
                    options = other_specs
                    warnings.warn('The number of adsorbate species exceeds ' +
                                  'the maximum allowed number.')

            nindi = self.add_adsorbate(indi, [ads_sites[removed]], 
                                       self.heights, options,
                                       self.min_adsorbate_distance,
                                       tilt_angle=self.tilt_angle)
            if not nindi:
                break

            indi = nindi
            if self.catalyst_indices is None:
                adsorbate_indices = None
            else:
                adsorbate_indices = [a.index for a in indi if 
                                     a.index not in self.catalyst_indices]
            if True in indi.pbc:
                sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                            self.subtract_heights, dmax=self.dmax,
                                            adsorbate_indices=adsorbate_indices)
            else:
                sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                               self.subtract_heights, dmax=self.dmax,
                                               adsorbate_indices=adsorbate_indices)
            ads_sites = sac.hetero_site_list                          

        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                sac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = sac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0}'.format(f.info['confid']))


class ReplaceAdsorbateSpecies(AdsorbateOperator):                                           
    """This operator replace all adsorbates of a certain species with 
    another species at the same sites. Add an adsorbate if there is no
    adsorbate present on the surface.

    The operator is generalized for both periodic and non-periodic systems 
    (distinguished by atoms.pbc).

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    species_probabilities : dict, default None                         
        A dictionary that contains keys of each adsorbate species and 
        values of their probabilities of replacing an adsorbate on the 
        surface. Choosing adsorbate species with equal probability if 
        not specified.

    replace_vacancy : bool, default False
        Whether to allow replacing adsorbates with vacancies, i.e., 
        effectively removing all adsorbates of a certain species.
        Note that if you want to specify species_probabilties, you
        then need to also provide the probability for vacancy
        replacement using the keyword 'vacancy'.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    tilt_angle : float, default 0.
        Tilt the adsorbate with an angle (in degrees) relative to the 
        surface normal.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 replace_vacancy=False,
                 species_probabilities=None,
                 heights=site_heights,
                 adsorption_sites=None,
                 tilt_angle=None,
                 subtract_heights=False,
                 fragmentation=True,
                 catalyst_indices=None,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species,
                                   species_probabilities)
        self.descriptor = 'ReplaceAdsorbateSpecies'

        assert len(set(self.adsorbate_species)) > 1
        self.replace_vacancy = replace_vacancy
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)

        self.tilt_angle = tilt_angle or 0.
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 1
        self.dmax = dmax

    def get_new_individual(self, parents):
        f = parents[0]

        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [f.info['confid']]
        if 'groups' in f.info['data']:
            indi.info['data']['groups'] = f.info['data']['groups']
        for atom in f:
            indi.append(atom)

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = SlabAdsorptionSites(indi, **self.kwargs)
            sac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax,
                                        adsorbate_indices=adsorbate_indices)
        else:
            if self.adsorption_sites is not None:
                sas = deepcopy(self.adsorption_sites)
                sas.update(indi)
            else:
                sas = ClusterAdsorptionSites(indi, **self.kwargs) 
            sac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax,
                                           adsorbate_indices=adsorbate_indices)

        ads_sites = sac.hetero_site_list
        specs = [t[0] for t in sac.get_adsorbates(
                 self.adsorbate_species, self.fragmentation)]
        # Add adsorbate if no adsorbate is present
        if not specs:
            indi = self.add_adsorbate(indi, ads_sites, self.heights)
            warnings.warn('{0} not possible in {1}, will add instead!'.format(
                          self.descriptor, f.info['confid']))
        else:
            spec = random.choice(specs)
            all_specs = self.adsorbate_species.copy()
            if self.replace_vacancy:
                if 'vacancy' not in all_specs:
                    all_specs.append('vacancy')
         
            other_specs = [sp for sp in all_specs if sp != spec]
            if (self.species_probabilities is None) or sum(
            self.species_probabilities.values()) == 0.:
                to_spec = random.choice(other_specs)
            else:
                probs = []
                for osp in other_specs:
                    if (osp == 'vacancy') and ('vacancy' not in self.species_probabilities):
                        vs = self.species_probabilities.values()
                        prob = sum(vs) / len(vs)
                    else:
                        prob = self.species_probabilities[osp]
                    probs.append(prob)
                to_spec = random.choices(k=1, population=other_specs, weights=probs)[0]  
         
            rmsites, rmstids = [], []
            rmfrags = True
            for i, st in enumerate(ads_sites):
                if self.fragmentation and (st['fragment'] in self.adsorbate_species):
                    if st['fragment'] == spec:
                        rmsites.append(st) 
                        rmstids.append(i)
                else:
                    if st['adsorbate'] == spec:
                        rmsites.append(st)
                        rmstids.append(i)
                        rmfrags = False
            remove_adsorbates_from_sites(indi, sites=rmsites, remove_fragments=rmfrags)
         
            if to_spec != 'vacancy':
                for i, st in enumerate(ads_sites):
                    if i in rmstids:
                        height = self.heights[st['site']]
#                        height = st['bond_length']
                        add_adsorbate_to_site(indi, to_spec, st, height, tilt_angle=self.tilt_angle) 

        if self.catalyst_indices is None:
            adsorbate_indices = None
        else:
            adsorbate_indices = [a.index for a in indi if 
                                 a.index not in self.catalyst_indices]
        if True in indi.pbc:
            nsac = SlabAdsorbateCoverage(indi, sas, subtract_heights=
                                         self.subtract_heights, dmax=self.dmax,
                                         adsorbate_indices=adsorbate_indices)
        else:
            nsac = ClusterAdsorbateCoverage(indi, sas, subtract_heights=
                                            self.subtract_heights, dmax=self.dmax,
                                            adsorbate_indices=adsorbate_indices)

        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                nsac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = nsac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0}'.format(f.info['confid']))

        
class CutSpliceCrossoverWithAdsorbates(AdsorbateOperator):
    """Crossover that cuts two particles with adsorbates through a plane 
    in space and merges two halfes from different particles together 
    (only returns one of them). The indexing of the atoms is not 
    preserved. Please only use this operator if the particle is allowed 
    to change shape.

    It keeps the correct composition by randomly assigning elements in
    the new particle. If some of the atoms in the two particle halves
    are too close, the halves are moved away from each other perpendicular
    to the cutting plane.

    The complexity of crossover with adsorbates makes this operator not 
    robust enough. The adsorption site identification will fail once the
    nanoparticle shape becomes too irregular after crossover. 

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    blmin : dict
        Dictionary of minimum distance between atomic numbers.
        e.g. {(28,29): 1.5}
    
    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    keep_composition : bool, default True
        Should the composition be the same as in the parents.

    fix_coverage : bool, default False 
        Should the adsorbate coverage be the same as in the parents.

    min_adsorbate_distance : float, default 2.
        The radius of the sphere inside which no other adsorbates 
        should be found.

    rotate_vectors : list, default None
        A list of vectors that the part of the structure that is cut
        is able to rotate around, the size of rotation is set in
        rotate_angles. Default None meaning no rotation is performed.

    rotate_angles : list, default None
        A list of angles that the structure cut can be rotated. The 
        vector being rotated around is set in rotate_vectors. Default 
        None meaning no rotation is performed.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species, blmin, 
                 heights=site_heights,
                 keep_composition=True,
                 fix_coverage=False, 
                 min_adsorbate_distance=2.,
                 rotate_vectors=None, 
                 rotate_angles=None,
                 subtract_heights=False,
                 fragmentation=True,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species)
        self.descriptor = 'CutSpliceCrossoverWithAdsorbates'

        self.blmin = blmin
        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.keep_composition = keep_composition
        self.fix_coverage = fix_coverage
        self.min_adsorbate_distance = min_adsorbate_distance
        self.rvecs = rotate_vectors
        self.rangs = rotate_angles
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.min_inputs = 2
        self.dmax = dmax

        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        self.__dict__.update(self.kwargs)
        
    def get_new_individual(self, parents):
        f, m = parents

        if self.fix_coverage:
            # Count number of adsorbates
            adsorbates_in_parents = len(self.get_all_adsorbate_indices(f))
            
        indi = self.initialize_individual(f)
        indi.info['data']['parents'] = [i.info['confid'] for i in parents]
        
        fna = self.get_atoms_without_adsorbates(f)
        mna = self.get_atoms_without_adsorbates(m)
        fna_geo_mid = np.average(fna.get_positions(), 0)
        mna_geo_mid = np.average(mna.get_positions(), 0)
        
        if self.rvecs is not None:
            if not isinstance(self.rvecs, list):
                warnings.warn('Rotation vectors are not a list, skipping rotation')
            else:
                vec = random.choice(self.rvecs)
                try:
                    angle = random.choice(self.rangs)
                except TypeError:
                    angle = self.rangs
                f.rotate(angle, vec, center=fna_geo_mid)
                vec = random.choice(self.rvecs)
                try:
                    angle = random.choice(self.rangs)
                except TypeError:
                    angle = self.rangs
                m.rotate(angle, vec, center=mna_geo_mid)
                
        theta = random.random() * 2 * np.pi  # 0,2pi
        phi = random.random() * np.pi  # 0,pi
        e = np.asarray((np.sin(phi) * np.cos(theta),
                        np.sin(theta) * np.sin(phi),
                        np.cos(phi)))
        eps = 0.0001
        
        # Move each particle to origo with their respective geometrical
        # centers, without adsorbates
        common_mid = (fna_geo_mid + mna_geo_mid) / 2.
        f.translate(-common_mid)
        m.translate(-common_mid)
        
        off = 1
        while off != 0:
            fna = self.get_atoms_without_adsorbates(f)
            mna = self.get_atoms_without_adsorbates(m)

            # Get the signed distance to the cutting plane
            # We want one side from f and the other side from m
            fmap = [np.dot(x, e) for x in fna.get_positions()]
            mmap = [-np.dot(x, e) for x in mna.get_positions()]
            ain = sorted([i for i in chain(fmap, mmap) if i > 0],
                         reverse=True)
            aout = sorted([i for i in chain(fmap, mmap) if i < 0],
                          reverse=True)

            off = len(ain) - len(fna)

            # Translating f and m to get the correct number of atoms
            # in the offspring
            if off < 0:
                # too few
                # move f and m away from the plane
                dist = abs(aout[abs(off) - 1]) + eps
                f.translate(e * dist)
                m.translate(-e * dist)
            elif off > 0:
                # too many
                # move f and m towards the plane
                dist = abs(ain[-abs(off)]) + eps
                f.translate(-e * dist)
                m.translate(e * dist)
            eps /= 5.

        fna = self.get_atoms_without_adsorbates(f)
        mna = self.get_atoms_without_adsorbates(m)
        
        # Determine the contributing parts from f and m
        tmpf, tmpm = Atoms(), Atoms()
        for atom in fna:
            if np.dot(atom.position, e) > 0:
                atom.tag = 1
                tmpf.append(atom)
        for atom in mna:
            if np.dot(atom.position, e) < 0:
                atom.tag = 2
                tmpm.append(atom)

        # Place adsorbates from f and m in tmpf and tmpm
        f_ads = self.get_all_adsorbate_indices(f)
        m_ads = self.get_all_adsorbate_indices(m)
        for ads in f_ads:
            if np.dot(f[ads[0]].position, e) > 0:
                for i in ads:
                    f[i].tag = 1
                    tmpf.append(f[i])
        for ads in m_ads:
            pos = m[ads[0]].position
            if np.dot(pos, e) < 0:
                # If the adsorbate will sit too close to another adsorbate
                # (below self.min_adsorbate_distance) do not add it.
                dists = [np.linalg.norm(pos - a.position)
                         for a in tmpf if a.tag == 1]
                for d in dists:
                    if d < self.min_adsorbate_distance:
                        break
                else:
                    for i in ads:
                        m[i].tag = 2
                        tmpm.append(m[i])
                
        tmpfna = self.get_atoms_without_adsorbates(tmpf)
        tmpmna = self.get_atoms_without_adsorbates(tmpm)
                
        # Check that the correct composition is employed
        if self.keep_composition:
            opt_sm = sorted(fna.numbers)
            tmpf_numbers = list(tmpfna.numbers)
            tmpm_numbers = list(tmpmna.numbers)
            cur_sm = sorted(tmpf_numbers + tmpm_numbers)
            # correct_by: dictionary that specifies how many
            # of the atom_numbers should be removed (a negative number)
            # or added (a positive number)
            correct_by = dict([(j, opt_sm.count(j)) for j in set(opt_sm)])
            for n in cur_sm:
                correct_by[n] -= 1
            correct_in = random.choice([tmpf, tmpm])
            to_add, to_rem = [], []
            for num, amount in correct_by.items():
                if amount > 0:
                    to_add.extend([num] * amount)
                elif amount < 0:
                    to_rem.extend([num] * abs(amount))
            for add, rem in zip(to_add, to_rem):
                tbc = [a.index for a in correct_in if a.number == rem]
                if len(tbc) == 0:
                    pass
                ai = random.choice(tbc)
                correct_in[ai].number = add
                
        # Move the contributing apart if any distance is below blmin
        maxl = 0.
        for sv, min_dist in self.get_vectors_below_min_dist(tmpf + tmpm):
            lsv = np.linalg.norm(sv)  # length of shortest vector
            d = [-np.dot(e, sv)] * 2
            d[0] += np.sqrt(np.dot(e, sv)**2 - lsv**2 + min_dist**2)
            d[1] -= np.sqrt(np.dot(e, sv)**2 - lsv**2 + min_dist**2)
            l = sorted([abs(i) for i in d])[0] / 2. + eps
            if l > maxl:
                maxl = l
        tmpf.translate(e * maxl)
        tmpm.translate(-e * maxl)
        
        # Translate particles halves back to the center
        tmpf.translate(common_mid)
        tmpm.translate(common_mid)

        # Put the two parts together
        for atom in chain(tmpf, tmpm):
            indi.append(atom)

        pcas = ClusterAdsorptionSites(indi, **self.kwargs) 
        pcac = ClusterAdsorbateCoverage(indi, pcas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax)
        pads_sites = pcac.hetero_site_list       

        adsi_dict = {}
        for st in pads_sites:
            if st['occupied']:
                si = st['indices']
                adsi_dict[si] = {}
                adsi_dict[si]['height'] = self.heights[st['site']]
                adsi_dict[si]['fragment'] = st['fragment']
                adsi_dict[si]['fragment_indices'] = st['fragment_indices']

        indi = pcas.atoms                
        indi.positions = pcas.ref_atoms.positions
        cas = ClusterAdsorptionSites(indi, **self.kwargs) 

        nori = len(indi) 
        for st in cas.site_list:
            si = st['indices']
            if si in adsi_dict:
                adsorbate = adsi_dict[si]['fragment']
                height = adsi_dict[si]['height']    
                add_adsorbate_to_site(indi, adsorbate, st, height)

                # Make sure no adsorbates too close to each other 
                # after each adsorbate addition
                nads = len(adsi_dict[si]['fragment_indices'])
                ads_atoms = indi[[a.index for a in indi if 
                                  a.symbol in adsorbate_elements]]
                if atoms_too_close_after_addition(ads_atoms, nads,
                self.min_adsorbate_distance, mic=False):
                    indi = indi[:-nads]                               

        # Add adsorbate if no adsorbate is present
        if len(indi) == nori:
            st = random.choice(cas.site_list)
            ads_spec = random.choice(self.adsorbate_species)
            add_adsorbate_to_site(indi, ads_spec, site=st, 
                                  height=self.heights[st['site']])

        cac = ClusterAdsorbateCoverage(indi, cas, subtract_heights=
                                       self.subtract_heights, dmax=self.dmax)
        ads_sites = cac.hetero_site_list

        if self.fix_coverage:
            # Remove or add adsorbates as needed
            adsorbates_in_child = self.get_all_adsorbate_indices(indi)
            diff = len(adsorbates_in_child) - adsorbates_in_parents
            if diff < 0:
                # Add adsorbates
                for _ in range(abs(diff)):
                    self.add_adsorbate(indi, ads_sites, site_heights,
                                       self.adsorbate_species,
                                       self.min_adsorbate_distance)
            elif diff > 0:
                # Remove adsorbates
                tbr = random.sample(adsorbates_in_child, diff)  # to be removed
                for adsorbate_indices in sorted(tbr, reverse=True):
                    for i in adsorbate_indices[::-1]:
                        indi.pop(i)                
            cac = ClusterAdsorbateCoverage(indi, cas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax)

        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                cac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = cac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        return (self.finalize_individual(indi),
                self.descriptor + ': {0} {1}'.format(f.info['confid'],
                                                     m.info['confid']))

    def get_numbers(self, atoms):
        """Returns the atomic numbers of the atoms object
        without adsorbates"""
        ac = atoms.copy()
        del ac[[a.index for a in ac
                if a.symbol in adsorbate_elements]]
        return ac.numbers
        
    def get_atoms_without_adsorbates(self, atoms):
        ac = atoms.copy()
        del ac[[a.index for a in ac
                if a.symbol in adsorbate_elements]]
        return ac
        
    def get_vectors_below_min_dist(self, atoms):
        """Generator function that returns each vector (between atoms)
        that is shorter than the minimum distance for those atom types
        (set during the initialization in blmin)."""
        ap = atoms.get_positions()
        an = atoms.numbers
        for i in range(len(atoms)):
            pos = atoms[i].position
            for j, d in enumerate([np.linalg.norm(k - pos) for k in ap[i:]]):
                if d == 0:
                    continue
                min_dist = self.blmin[tuple(sorted((an[i], an[j + i])))]
                if d < min_dist:
                    yield atoms[i].position - atoms[j + i].position, min_dist


class SimpleCutSpliceCrossoverWithAdsorbates(AdsorbateOperator):
    """Crossover that divides two particles through a plane in space and
    merges the symbols of two halves from different particles with 
    adosrbates together (only returns one of them). The indexing of the 
    atoms is preserved. Please only use this operator with other operators 
    that also preserves the indexing.

    It keeps the correct composition by randomly assigning elements in
    the new particle.

    Parameters
    ----------
    adsorbate_species : str or list of strs 
        One or a list of adsorbate species to be added to the surface.

    heights : dict, default acat.settings.site_heights
        A dictionary that contains the adsorbate height for each site 
        type. Use the default height settings if the height for a site 
        type is not specified.

    keep_composition : bool, default True
        Boolean that signifies if the composition should be the same 
        as in the parents.

    fix_coverage : bool, default False 
        Should the adsorbate coverage be the same as in the parents.

    min_adsorbate_distance : float, default 2.
        The radius of the sphere inside which no other adsorbates 
        should be found.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        Provide the built-in adsorption sites class to accelerate the 
        genetic algorithm. Make sure all the operators used with this
        operator preserve the indexing of the atoms.

    subtract_heights : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorbate_species,
                 heights=site_heights,
                 keep_composition=True,
                 fix_coverage=False, 
                 min_adsorbate_distance=2.,
                 adsorption_sites=None, 
                 subtract_heights=False,
                 fragmentation=True,
                 dmax=2.5, **kwargs):
        AdsorbateOperator.__init__(self, adsorbate_species)
        self.descriptor = 'SimpleCutSpliceCrossoverWithAdsorbates'

        self.heights = site_heights 
        for k, v in heights.items():
            self.heights[k] = v
        self.keep_composition = keep_composition
        self.fix_coverage = fix_coverage
        self.min_adsorbate_distance = min_adsorbate_distance
        self.kwargs = {'allow_6fold': False, 'composition_effect': False, 
                       'ignore_sites': None, 'label_sites': False}
        self.kwargs.update(kwargs)
        if adsorption_sites is not None:
            if isinstance(adsorption_sites, str):
                import pickle
                with open(adsorption_sites, 'rb') as f:
                    self.adsorption_sites = pickle.load(f)
            else:
                self.adsorption_sites = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(self.adsorption_sites)
        else:
            self.adsorption_sites = None
        self.__dict__.update(self.kwargs)
        if subtract_heights:
            self.subtract_heights = self.heights
        else:
            self.subtract_heights = None
        self.fragmentation = fragmentation
        self.min_inputs = 2
        self.dmax = dmax
        
    def get_new_individual(self, parents):
        f, m = parents        
        indi = f.copy()

        if self.fix_coverage:
            # Count number of adsorbates
            adsorbates_in_parents = len(self.get_all_adsorbate_indices(f))

        theta = random.random() * 2 * np.pi  # 0,2pi
        phi = random.random() * np.pi  # 0,pi
        e = np.array((np.sin(phi) * np.cos(theta),
                      np.sin(theta) * np.sin(phi),
                      np.cos(phi)))
        eps = 0.0001
        
        f.translate(-f.get_center_of_mass())
        m.translate(-m.get_center_of_mass())
        
        # Get the signed distance to the cutting plane
        # We want one side from f and the other side from m
        mids, fids, rmids = [], [], []
        for i, x in enumerate(f.get_positions()):
            if np.dot(x, e) > 0:
                if f[i].symbol in adsorbate_elements:
                    rmids.append(i)
                else:
                    mids.append(i)
            else:
                if f[i].symbol not in adsorbate_elements:
                    fids.append(i)

        # Change half of f symbols to the half of m symbols
        for i in mids:
            indi[i].symbol = m[i].symbol

        # Check that the correct composition is employed
        if self.keep_composition:
            opt_sm = sorted([a.number for a in f if a.symbol 
                             not in adsorbate_elements])
            tmpf_numbers = list(indi.numbers[fids])
            tmpm_numbers = list(indi.numbers[mids])
            cur_sm = sorted(tmpf_numbers + tmpm_numbers)
            # correct_by: dictionary that specifies how many
            # of the atom_numbers should be removed (a negative number)
            # or added (a positive number)
            correct_by = dict([(j, opt_sm.count(j)) for j in set(opt_sm)])
            for n in cur_sm:
                correct_by[n] -= 1
            correct_ids = random.choice([fids, mids])
            to_add, to_rem = [], []
            for num, amount in correct_by.items():
                if amount > 0:
                    to_add.extend([num] * amount)
                elif amount < 0:
                    to_rem.extend([num] * abs(amount))
            for add, rem in zip(to_add, to_rem):
                tbc = [i for i in correct_ids if indi[i].number == rem]
                if len(tbc) == 0:
                    pass
                ai = random.choice(tbc)
                indi[ai].number = add

        # Place adsorbates from half of m and remove adsorbates from
        # half of f
        if self.adsorption_sites is not None:
            cas = deepcopy(self.adsorption_sites)
            cas.update(indi)
        else:
            cas = ClusterAdsorptionSites(indi, **self.kwargs) 
        fcac = ClusterAdsorbateCoverage(indi, cas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax)
        fhsl = fcac.hetero_site_list
        mcac = ClusterAdsorbateCoverage(m, cas, subtract_heights=
                                        self.subtract_heights, dmax=self.dmax)
        mhsl = mcac.hetero_site_list

        rmset = set(rmids)
        rmsites = []
        for st in fhsl:
            if st['occupied']:
                if not set(st['fragment_indices']).isdisjoint(rmset):
                    rmsites.append(st)

        # Remove fragments if every fragment is one of the given adsorbate species
        rmfrags = all(st['fragment'] in self.adsorbate_species for st in rmsites)
        remove_adsorbates_from_sites(indi, sites=rmsites, remove_fragments=rmfrags) 

        mset = set(mids)
        adsi_dict = {}
        for st in mhsl:
            if st['occupied']:
                si = st['indices']
                if set(si).issubset(mset):
                    si = st['indices']
                    adsi_dict[si] = {}
                    adsi_dict[si]['height'] = self.heights[st['site']]
                    adsi_dict[si]['fragment'] = st['fragment']
                    adsi_dict[si]['fragment_indices'] = st['fragment_indices']        

        nori = len(indi) 
        for st in cas.site_list:
            si = st['indices']
            if si in adsi_dict:
                adsorbate = adsi_dict[si]['fragment']
                height = adsi_dict[si]['height']    
                add_adsorbate_to_site(indi, adsorbate, st, height)

                # Make sure no adsorbates too close to each other 
                # after each adsorbate addition
                nads = len(adsi_dict[si]['fragment_indices'])
                ads_atoms = indi[[a.index for a in indi if 
                                  a.symbol in adsorbate_elements]]
                if atoms_too_close_after_addition(ads_atoms, nads,
                self.min_adsorbate_distance, mic=False):
                    indi = indi[:-nads]                               

        # Add adsorbate if no adsorbate is present
        if len(indi) == nori:
            st = random.choice(cas.site_list)
            ads_spec = random.choice(self.adsorbate_species)
            add_adsorbate_to_site(indi, ads_spec, site=st, 
                                  height=self.heights[st['site']])

        cac = ClusterAdsorbateCoverage(indi, cas, subtract_heights=
                                       self.subtract_heights, dmax=self.dmax)
        ads_sites = cac.hetero_site_list

        if self.fix_coverage:
            # Remove or add adsorbates as needed
            adsorbates_in_child = self.get_all_adsorbate_indices(indi)
            diff = len(adsorbates_in_child) - adsorbates_in_parents
            if diff < 0:
                # Add adsorbates
                for _ in range(abs(diff)):
                    self.add_adsorbate(indi, ads_sites, site_heights,
                                       self.adsorbate_species,
                                       self.min_adsorbate_distance)
            elif diff > 0:
                # Remove adsorbates
                tbr = random.sample(adsorbates_in_child, diff)  # to be removed
                for adsorbate_indices in sorted(tbr, reverse=True):
                    for i in adsorbate_indices[::-1]:
                        indi.pop(i)                
            cac = ClusterAdsorbateCoverage(indi, cas, subtract_heights=
                                           self.subtract_heights, dmax=self.dmax)

        indi = self.initialize_individual(f, indi)
        indi.info['data']['parents'] = [i.info['confid'] for i in parents] 
        indi.info['data']['operation'] = 'crossover'
        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = [t[0] for t in 
                cac.get_adsorbates(self.adsorbate_species, self.fragmentation)]
        if 'fragments' in f.info['data']:
            adsorbate_tuples = cac.get_adsorbates(self.adsorbate_species, self.fragmentation)
            adsorbates = [t[0] for t in adsorbate_tuples]
            adsid_set = set(i for t in adsorbate_tuples for i in t[1])
            indi.info['data']['fragments'] = adsorbates + \
                    [a.symbol for a in indi if (a.symbol in adsorbate_elements) 
                     and (a.index not in adsid_set)]

        parent_message = ':Parents {0} {1}'.format(f.info['confid'],
                                                   m.info['confid'])
        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def get_numbers(self, atoms):
        """Returns the atomic numbers of the atoms object
        without adsorbates"""
        ac = atoms.copy()
        del ac[[a.index for a in ac
                if a.symbol in adsorbate_elements]]
        return ac.numbers

    def get_atoms_without_adsorbates(self, atoms):
        ac = atoms.copy()
        del ac[[a.index for a in ac
                if a.symbol in adsorbate_elements]]
        return ac


class CatalystAdsorbateCrossover(AdsorbateOperator):                                   
    """Crossover that divides two particles or two slabs by the catalyst-
    adsorbates interfaces and exchange all adsorbates (only returns one 
    of them). The indexing of the atoms is preserved. Please only use 
    this operator with other operators that also preserves the indexing.

    The composition or the coverage is fixed if it is preserved by all 
    other operators being used.

    Parameters
    ----------
    group_by_sites : bool, default False
        If atoms.info['data']['groups'] is used, please set this to True
        if the groups is for adsorption sites, so that the offspring will
        inheritate the site groups. The default is grouping by slab atoms.

    catalyst_indices : list of ints, default None
        The atomic indices of catalyst atoms. Only metal atoms are treated
        as part of the catalyst by default. Useful when the indexing is
        preserved during the run, and there are non-metal elements in the
        catalyst, e.g. metal oxides.

    """

    def __init__(self, group_by_sites=False, catalyst_indices=None):
        AdsorbateOperator.__init__(self, adsorbate_species='X')
        self.descriptor = 'CatalystAdsorbateCrossover'

        self.group_by_sites = group_by_sites
        self.catalyst_indices = catalyst_indices
        self.min_inputs = 2
        
    def get_new_individual(self, parents, return_both=False):
        f, m = parents        
        indi = f.copy()
        if self.catalyst_indices is None:
            cat_ids = [a.index for a in indi if a.symbol not in adsorbate_elements]
        else:
            cat_ids = self.catalyst_indices
        indi.symbols[cat_ids] = m.symbols[cat_ids]

        indi = self.initialize_individual(f, indi)
        if 'groups' in f.info['data']:
            if self.group_by_sites:
                indi.info['data']['groups'] = f.info['data']['groups']
            else:
                indi.info['data']['groups'] = m.info['data']['groups']
        if 'adsorbates' in f.info['data']:
            indi.info['data']['adsorbates'] = f.info['data']['adsorbates']
        if 'fragments' in f.info['data']:
            indi.info['data']['fragments'] = f.info['data']['fragments']
        indi.info['data']['parents'] = [i.info['confid'] for i in parents] 
        indi.info['data']['operation'] = 'crossover'
        parent_message = ':Parents {0} {1}'.format(f.info['confid'],
                                                   m.info['confid'])
        if return_both:
            indi2 = m.copy()
            if self.catalyst_indices is None:
                cat_ids = [a.index for a in indi2 if a.symbol not in adsorbate_elements]
            else:
                cat_ids = self.catalyst_indices
            indi2.symbols[cat_ids] = f.symbols[cat_ids]
         
            indi2 = self.initialize_individual(m, indi2)
            if 'groups' in m.info['data']:
                if self.group_by_sites:
                    indi2.info['data']['groups'] = m.info['data']['groups']
                else:
                    indi2.info['data']['groups'] = f.info['data']['groups']
            if 'adsorbates' in m.info['data']:
                indi2.info['data']['adsorbates'] = m.info['data']['adsorbates']
            if 'fragments' in m.info['data']:
                indi2.info['data']['fragments'] = m.info['data']['fragments']
            indi2.info['data']['parents'] = [i.info['confid'] for i in parents]
            indi2.info['data']['operation'] = 'crossover'
            return ([self.finalize_individual(indi), self.finalize_individual(indi2)],
                    self.descriptor + parent_message)

        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

