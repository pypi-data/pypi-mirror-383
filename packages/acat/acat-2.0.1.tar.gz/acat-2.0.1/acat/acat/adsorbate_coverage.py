#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .settings import (adsorbate_elements,
                       site_heights,
                       adsorbate_formulas)
from .adsorption_sites import (ClusterAdsorptionSites, 
                               SlabAdsorptionSites)
from .utilities import (neighbor_shell_list, 
                        get_adj_matrix,
                        get_mic)
from ase.geometry import find_mic
from ase.formula import Formula
from collections import defaultdict, Counter
from operator import attrgetter
from copy import deepcopy
import networkx as nx
import numpy as np
import random


class ClusterAdsorbateCoverage(object):
    """Child class of `ClusterAdsorptionSites` for identifying adsorbate 
    coverage on a nanoparticle. Support common nanoparticle shapes 
    including: Mackay icosahedron, (truncated) octahedron and (Marks) 
    decahedron.

    The information of each occupied site stored in the dictionary is 
    updated with the following new keys:

    **'occupied'**: 1 if the site is occupied, otherwise 0.
 
    **'adsorbate'**: the name of the adsorbate that occupies this site.
 
    **'adsorbate_indices'**: the indices of the adosorbate atoms that occupy
    this site. If the adsorbate is multidentate, these atoms might
    occupy multiple sites.
 
    **'bonding_index'**: the index of the atom that directly bonds to the
    site (closest to the site).
 
    **'fragment'**: the name of the fragment that occupies this site. Useful
    for multidentate species.
 
    **'fragment_indices'**: the indices of the fragment atoms that occupy
    this site. Useful for multidentate species.
 
    **'bond_length'**: the distance between the bonding atom and the site.
 
    **'dentate'**: dentate number.
 
    **'label'**: the updated label with the name of the occupying adsorbate
    if label_occupied_sites is set to True.

    Parameters
    ----------
    atoms : ase.Atoms object
        The atoms object must be a non-periodic nanoparticle with at 
        least one adsorbate attached to it. Accept any ase.Atoms object. 
        No need to be built-in.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or its pickle file path, default None
        `ClusterAdsorptionSites` object of the nanoparticle. Initialize a 
        `ClusterAdsorptionSites` object if not specified.
        If this is not provided, the arguments for identifying adsorption 
        sites can still be passed in by **kwargs.

    subtract_heights : dict, default None
        A dictionary that contains the height to be subtracted from the bond 
        length when allocating a type of site to an adsorbate. Default is to 
        allocate the site that is closest to the adsorbate's binding atom 
        without subtracting height. Useful for ensuring the allocated site 
        for each adsorbate is consistent with the site to which the adsorbate
        was added.                                                           

    label_occupied_sites : bool, default False
        Whether to assign a label to the occupied each site. The string 
        of the occupying adsorbate is concatentated to the numerical 
        label that represents the occupied site.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.    

    Example
    -------
    The following example illustrates the most important use of a
    `ClusterAdsorbateCoverage` object - getting occupied adsorption sites:

    .. code-block:: python

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.adsorbate_coverage import ClusterAdsorbateCoverage
        >>> from acat.build import add_adsorbate_to_site
        >>> from ase.cluster import Octahedron
        >>> atoms = Octahedron('Ni', length=7, cutoff=2)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Pt'
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms, composition_effect=True,
        ...                              surrogate_metal='Ni') 
        >>> sites = cas.get_sites()
        >>> for s in sites:
        ...     if s['site'] == 'fcc':
        ...         add_adsorbate_to_site(atoms, adsorbate='CO', site=s)
        >>> cac = ClusterAdsorbateCoverage(atoms, adsorption_sites=cas,
        ...                                label_occupied_sites=True)
        >>> occupied_sites = cac.get_sites(occupied=True)
        >>> print(occupied_sites[0])

    Output:

    .. code-block:: python

        {'site': 'fcc', 'surface': 'fcc111', 
         'position': array([ 6.17333333,  7.93333333, 11.45333333]), 
         'normal': array([-0.57735027, -0.57735027, -0.57735027]), 
         'indices': (0, 2, 4), 'composition': 'PtPtPt', 
         'subsurf_index': None, 'subsurf_element': None, 'label': '21CO', 
         'bonding_index': 201, 'bond_length': 1.3, 'adsorbate': 'CO', 
         'fragment': 'CO', 'adsorbate_indices': (201, 202), 'occupied': 1, 
         'dentate': 1, 'fragment_indices': (201, 202)}

    """

    def __init__(self, atoms, 
                 adsorption_sites=None, 
                 subtract_heights=None,
                 label_occupied_sites=False,
                 adsorbate_indices=None,
                 dmax=2.5, **kwargs):

        atoms = atoms.copy()
        for dim in range(3):
            if np.linalg.norm(atoms.cell[dim]) == 0:
                atoms.cell[dim][dim] = np.ptp(atoms.positions[:, dim]) + 10.

        self.atoms = atoms 
        self.positions = atoms.positions
        self.symbols = atoms.symbols
        if adsorbate_indices is None:
            self.nonmetal_ids = [a.index for a in atoms if 
                                 a.symbol in adsorbate_elements]
        else:
            self.nonmetal_ids = adsorbate_indices
        if self.nonmetal_ids:
            self.ads_atoms = atoms[self.nonmetal_ids]
        else:
            self.ads_atoms = None
        self.cell = atoms.cell
        self.pbc = atoms.pbc

        self.subtract_heights = subtract_heights
        if subtract_heights is not None:
            self.subtract_heights = site_heights
            for k, v in subtract_heights.items():
                self.subtract_heights[k] = v      
        self.label_occupied_sites = label_occupied_sites
        self.dmax = dmax
        self.kwargs = {'allow_6fold': False, 'composition_effect': False,
                       'ignore_sites': None, 'label_sites': False} 
        self.kwargs.update(kwargs)

        if adsorption_sites:
            if isinstance(adsorption_sites, str):      
                import pickle      
                with open(adsorption_sites, 'rb') as f:
                    cas = pickle.load(f)
            else:
                cas = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(cas)
        else:
            cas = ClusterAdsorptionSites(atoms, **self.kwargs)    
        self.__dict__.update(self.kwargs)
        self.adsorption_sites = cas
        self.cas = cas
        self.metals = cas.metals
        self.metal_ids = cas.metal_ids
        self.surf_ids = [self.metal_ids[i] for i in cas.surf_ids]
        self.label_dict = cas.label_dict
        self.hetero_site_list = deepcopy(cas.site_list)

        if self.nonmetal_ids:                                     
            self.make_ads_neighbor_list()
            self.ads_adj_matrix = self.get_ads_connectivity()
            self.identify_adsorbates()
        else:
            self.ads_list = []
        self.label_list = ['0'] * len(self.hetero_site_list)
        self.populate_hetero_site_list()

        if self.nonmetal_ids:
            self.labels = self.get_occupied_labels()
        else:
            self.labels = []

    def identify_adsorbates(self):

        G = nx.Graph()
        adscm = self.ads_adj_matrix

        # Cut all intermolecular H-H bonds except intramolecular               
        # H-H bonds in e.g. H2
        hids = [a.index for a in self.ads_atoms if a.symbol == 'H']
        for hi in hids:
            conns = np.where(adscm[hi] == 1)[0]
            hconns = [i for i in conns if self.ads_atoms.symbols[i] == 'H']
            if hconns and len(conns) > 1:
                adscm[hi,hconns] = 0
      
        if adscm.size != 0:
            np.fill_diagonal(adscm, 1)
            rows, cols = np.where(adscm == 1)

            edges = zip([self.nonmetal_ids[row] for row in rows.tolist()], 
                        [self.nonmetal_ids[col] for col in cols.tolist()])
            G.add_edges_from(edges)                        
            SG = (G.subgraph(c) for c in nx.connected_components(G))
 
            adsorbates = []
            for sg in SG:
                nodes = sorted(list(sg.nodes))
                adsorbates += [nodes]
        else:
            adsorbates = [self.nonmetal_ids]

        self.ads_list = adsorbates

    def get_updated_connectivity(self):
        """Get the adjacency matrix of slab + adsorbates."""

        nbslist = neighbor_shell_list(self.atoms, 0.3, neighbor_number=1)
        return get_adj_matrix(nbslist)                          

    def get_ads_connectivity(self):
        """Get the adjacency matrix for adsorbate atoms."""

        return get_adj_matrix(self.ads_nblist) 

    def get_site_connectivity(self):
        """Get the adjacency matrix for adsorption sites."""

        sl = self.hetero_site_list
        conn_mat = []
        for i, sti in enumerate(sl):
            conn_x = []
            for j, stj in enumerate(sl): 
                overlap = len(set(sti['indices']).intersection(stj['indices']))
                if i == j:
                    conn_x.append(0.)
                elif overlap > 0:
                    if self.allow_6fold: 
                        if '6fold' in [sti['site'], stj['site']]: 
                            if overlap == 3:                            
                                conn_x.append(1.)
                            else:
                                conn_x.append(0.)
                        else:
                            conn_x.append(1.)
                    else:
                        conn_x.append(1.)                     
                else:
                    conn_x.append(0.)
            conn_mat.append(conn_x)   

        return np.asarray(conn_mat) 

    def populate_hetero_site_list(self):
        """Find all the occupied sites, identify the adsorbate coverage
        of those sites and collect in a heterogeneous site list."""

        hsl = self.hetero_site_list
        ll = self.label_list
        ads_list = self.ads_list
        ndentate_dict = {} 

        for adsid in self.nonmetal_ids:            
            if self.symbols[adsid] == 'H':
                if [adsid] not in ads_list:
                    rest = [s for x in ads_list for s in x 
                            if (adsid in x and s != adsid)]
                    if not (self.symbols[rest[0]] == 'H' and len(rest) == 1):
                        continue

            adspos = self.positions[adsid]
            if self.subtract_heights is not None:
                dls = np.linalg.norm(np.asarray([s['position'] + s['normal'] * 
                                     self.subtract_heights[s['site']] - adspos 
                                     for s in hsl]), axis=1)
                stid = np.argmin(dls)
                st = hsl[stid]
                bl = np.linalg.norm(st['position'] - adspos)
            else:
                dls = np.linalg.norm(np.asarray([s['position'] - adspos 
                                     for s in hsl]), axis=1)
                stid = np.argmin(dls)
                st, bl = hsl[stid], dls[stid]
            bl = round(bl, 8)
            if bl > self.dmax:
                continue
            if st['normal'][2] > 0:
                if (bl > 0.75) and (st['position'][2] > adspos[2]):
                    continue
            else:
                if (bl > 0.75) and (st['position'][2] < adspos[2]):
                    continue

            adsids = next((l for l in ads_list if adsid in l), None)
            adsi = tuple(sorted(adsids))

            if 'occupied' in st:
                if bl >= st['bond_length']:
                    continue
                elif self.symbols[adsid] != 'H':
                    if adsi in ndentate_dict:
                        ndentate_dict[adsi] -= 1 
            st['bonding_index'] = adsid
            st['bond_length'] = bl

            symbols = ''.join(list(Formula(str(self.symbols[adsids]))))
            adssym = next((k for k, v in adsorbate_formulas.items() 
                           if v == symbols), None)
            if adssym is None:
                adssym = next((k for k, v in adsorbate_formulas.items()
                               if sorted(v) == sorted(symbols)), symbols)

            st['adsorbate'] = adssym
            st['fragment'] = adssym
            st['adsorbate_indices'] = adsi 
            if adsi in ndentate_dict:
                ndentate_dict[adsi] += 1
            else:
                ndentate_dict[adsi] = 1
            st['occupied'] = 1            

        # Get dentate numbers and coverage  
        self.n_occupied, n_surf_occupied, self.n_subsurf_occupied = 0, 0, 0
        for st in hsl:
            if 'occupied' not in st:
                st['bonding_index'] = st['bond_length'] = None
                st['adsorbate'] = st['fragment'] = None
                st['adsorbate_indices'] = None
                st['occupied'] = st['dentate'] = 0
                st['fragment_indices'] = None
                continue
            self.n_occupied += 1
            if st['site'] == '6fold':
                self.n_subsurf_occupied += 1
            else:
                n_surf_occupied += 1
            adsi = st['adsorbate_indices']
            if adsi in ndentate_dict:              
                st['dentate'] = ndentate_dict[adsi]
            else:
                st['dentate'] = 0
        self.coverage = n_surf_occupied / len(self.surf_ids)

        # Identify bidentate fragments and assign labels 
        self.multidentate_fragments = []
        self.monodentate_adsorbate_list = []
        self.multidentate_labels = []
        multidentate_adsorbate_dict = {}
        for j, st in enumerate(hsl):
            if st['occupied']:
                adssym = st['adsorbate']
                if st['dentate'] > 1:
                    bondid = st['bonding_index']
                    bondsym = self.symbols[bondid]
                    conns = [self.nonmetal_ids[k] for k in np.where(self.ads_adj_matrix[
                             self.nonmetal_ids.index(bondid)] == 1)[0].tolist()]
                    hnnlen = len([i for i in conns if self.atoms[i].symbol == 'H'])
                    fsym = self.atoms[bondid].symbol
                    if hnnlen == 1:
                        fsym += 'H'
                    elif hnnlen > 1:
                        fsym += 'H{}'.format(hnnlen)
                    st['fragment'] = fsym
                    flen = hnnlen + 1
                    adsids = st['adsorbate_indices']
                    ibond = adsids.index(bondid)
                    fsi = adsids[ibond:ibond+flen]
                    st['fragment_indices'] = fsi
                    if adsids not in multidentate_adsorbate_dict:
                        multidentate_adsorbate_dict[adsids] = adssym
                else:
                    st['fragment_indices'] = st['adsorbate_indices']
                    self.monodentate_adsorbate_list.append(adssym)

                if self.label_occupied_sites:
                    if st['label'] is None:
                        signature = [st['site'], st['surface']] 
                        if self.composition_effect:
                            signature.append(st['composition'])
                        stlab = self.label_dict['|'.join(signature)]
                    else:
                        stlab = st['label']                         
                    label = str(stlab) + st['fragment']
                    st['label'] = label
                    ll[j] = label
                    if st['dentate'] > 1:                    
                        self.multidentate_fragments.append(label)
                        if bondid == adsids[0]:
                            mdlabel = str(stlab) + adssym
                            self.multidentate_labels.append(mdlabel)
            else:
                if self.label_occupied_sites and (st['label'] is None):
                    signature = [st['site'], st['morphology']]
                    if self.composition_effect:
                        signature.append(st['composition'])
                    st['label'] = self.label_dict['|'.join(signature)] 

        self.multidentate_adsorbate_list = list(multidentate_adsorbate_dict.values())
        self.adsorbate_list = self.monodentate_adsorbate_list + \
                              self.multidentate_adsorbate_list 

    def get_site(self, indices=None):
        """Get information of an adsorption site.
        
        Parameters
        ----------
        indices : list or tuple, default None
            The indices of the atoms that contribute to the site. 
            Return a random site if the indices are not provided.        

        """

        if indices is None:
            st = random.choice(self.hetero_site_list)
        else:
            indices = indices if is_list_or_tuple(indices) else [indices]
            indices = tuple(sorted(indices))
            st = next((s for s in self.hetero_site_list if 
                       s['indices'] == indices), None)
        return st

    def get_sites(self, occupied=None, **kwargs):
        """Get information of all sites.
                                                                     
        Parameters                                                   
        ----------                                                   
        occupied : bool or None, default None
            Set to True to return only the occupied sites.
            Set to False to return only the unoccupied sites.
            Set to None to return all sites.

        """                                                          

        kwargs['return_site_indices'] = True
        all_sites = self.hetero_site_list
        target_stids = self.cas.get_sites(**kwargs)
        target_sites = [all_sites[si] for si in target_stids]
        if occupied is True:
            target_sites = [s for s in target_sites if s['occupied']]
        elif occupied is False:
            target_sites = [s for s in target_sites if not s['occupied']]

        return target_sites

    def get_unique_sites(self, occupied=False, **kwargs):           
        """Get all symmetry-inequivalent adsorption sites (one
        site for each type). Note that this method does not
        consider the change in site's local environment caused 
        by adsorbates. To get unique sites with adsorbate effects,
        please use acat.build.adlayer.SystematicPatternGenerator.

        Parameters
        ----------
        occupied : bool or None, default False
            Set to True to return only the occupied unique sites.
            Set to False to return only the unoccupied unique sites.
            Set to None to return all unique sites.

        """

        kwargs['return_site_indices'] = True
        all_sites = self.hetero_site_list
        unq_stids = self.cas.get_unique_sites(**kwargs)
        unq_sites = [all_sites[si] for si in unq_stids]
        if occupied is True:
            unq_sites = [s for s in unq_sites if s['occupied']]
        elif occupied is False:
            unq_sites = [s for s in unq_sites if not s['occupied']]

        return unq_sites

    def get_adsorbates(self, adsorbate_species=None, fragmentation=True):
        """Get a list of tuples that contains each adsorbate (string)
        and the corresponding adsorbate indices (tuple) in ascending
        order.

        Parameters
        ----------
        adsorbate_species : list of strs, default None
            The available adsorbate species. If the adsorbate is not
            one of the available species, return the fragment instead.

        """

        adsorbates = []
        adsorbate_ids = set()
        for st in self.hetero_site_list:
            if st['occupied']:
                if adsorbate_species is not None:
                    if st['adsorbate'] not in adsorbate_species:
                        if fragmentation:
                            fragi = st['fragment_indices']
                            adsorbates.append((st['fragment'], fragi))
                            adsorbate_ids.update(fragi)
                        continue
                adsi = st['adsorbate_indices']
                if not set(adsi).issubset(adsorbate_ids):
                    adsorbates.append((st['adsorbate'], adsi))
                    adsorbate_ids.update(adsi)

        return sorted(adsorbates, key=lambda x: x[1])

    def get_fragments(self):
        """Get a list of tuples that contains each fragment (string)
        and the corresponding fragment indices (tuple) in ascending
        order."""

        fragments = []
        for st in self.hetero_site_list:
            if st['occupied']:
                fragi = st['fragment_indices']
                fragments.append((st['fragment'], fragi))

        return sorted(fragments, key=lambda x: x[1])        

    def make_ads_neighbor_list(self, dx=.2, neighbor_number=1):
        self.ads_nblist = neighbor_shell_list(self.ads_atoms, dx, 
                                              neighbor_number, mic=False)

    def get_occupied_labels(self, fragmentation=True):
        """Get a list of labels of all occupied sites. The label consists
        of a numerical part that represents site, and a character part
        that represents the occupying adsorbate.

        Parameters
        ----------
        fragmentation : bool, default True
            Whether to cut multidentate species into fragments. This ensures 
            that multidentate species with different orientations have 
            different labels.

        """

        if not self.label_occupied_sites:
            return self.atoms[self.nonmetal_ids].get_chemical_formula(mode='hill')

        ll = self.label_list
        labs = [lab for lab in ll if lab != '0']
        if not fragmentation:
            mf = self.multidentate_fragments
            mdlabs = self.multidentate_labels
            c1, c2 = Counter(labs), Counter(mf)
            diff = list((c1 - c2).elements())
            labs = diff + mdlabs                   

        return sorted(labs)

    def get_graph(self, atom_wise=False,
                  fragmentation=True, 
                  subsurf_effect=False, 
                  full_effect=False,
                  return_adj_matrix=False,
                  connect_dentates=True,
                  dx=0.5):                                         
        """Get the graph representation of the nanoparticle with adsorbates.

        Parameters
        ----------
        atom_wise : bool, default False
            Whether to treat each adsorbate as an atom-wise subgraph. If not, 
            treat each adsorbate fragment as a unity (molecule-wise, which may
            not preserve atomic indices).

        fragmentation : bool, default True
            Whether to cut multidentate species into fragments. This ensures 
            that multidentate species with different orientations have 
            different graphs.

        subsurf_effect : bool, default False
            Take subsurface atoms into consideration when generating graph. 

        full_effect : bool, default False
            Take the whole catalyst into consideration when generating graph.

        return_adj_matrix : bool, default False
            Whether to return adjacency matrix instead of the networkx.Graph 
            object.

        connect_dentates : bool, default True
            Whether to add edges between the fragments of multidentate species.

        dx : float, default 0.5
            Buffer to calculate nearest neighbor pairs. Only relevent when
            atom_wise=True.

        """

        # Molecule-wise
        if not atom_wise:
            hsl = self.hetero_site_list
            hcm = self.cas.get_connectivity().copy()
            if full_effect:
                surf_ids = self.metal_ids
            else:
                if subsurf_effect:
                    surf_ids = self.surf_ids + self.cas.get_subsurface()
                else:
                    surf_ids = self.surf_ids
            surf_metal_ids = [i for i, idx in enumerate(self.metal_ids) if idx in surf_ids]
            surfhcm = hcm[surf_metal_ids]
            symbols = self.symbols[self.metal_ids]
            nrows, ncols = surfhcm.shape
 
            newrows, frag_list, adsi_list = [], [], []
            multi_conns = defaultdict(list)
            ohsl = [st for st in hsl if st['occupied']]
            for st in sorted(ohsl, key=lambda x: x['fragment_indices']):
                adsi = st['adsorbate_indices']
                if not fragmentation and st['dentate'] > 1: 
                    if st['bonding_index'] != adsi[0]:
                        continue
                si = [i for i, idx in enumerate(self.metal_ids) if idx in st['indices']]
                newrow = np.zeros(ncols)
                newrow[si] = 1
                newrows.append(newrow)
 
                if fragmentation:                
                    frag_list.append(st['fragment'])
                    if st['dentate'] > 1 and connect_dentates:
                        bondid = st['bonding_index']
                        all_conns = [self.nonmetal_ids[j] for j in np.where(self.ads_adj_matrix[
                                     self.nonmetal_ids.index(bondid)] == 1)[0].tolist()]
                        conns = [c for c in all_conns if c not in st['fragment_indices']]
                        i = len(newrows) - 1
                        if i not in multi_conns:
                            multi_conns[bondid].append([i])
                        for k, v in multi_conns.items():
                            if k in conns:
                                multi_conns[k].append([i, v[0][0]])
                else:
                    frag_list.append(st['adsorbate'])
 
            links = []
            if newrows:
                surfhcm = np.vstack((surfhcm, np.asarray(newrows)))
                if multi_conns:
                    links = [sorted(c) for cs in multi_conns.values() for c in cs if len(c) > 1]
 
            shcm = surfhcm[:,surf_metal_ids]
            if return_adj_matrix:
                if newrows:
                    dd = len(newrows)
                    small_mat = np.zeros((dd, dd))
                    if links:
                        for (i, j) in links:
                            small_mat[i,j] = 1
                            small_mat[j,i] = 1
                    return np.hstack((shcm, np.vstack((shcm[-dd:].T, small_mat))))
                else:
                    return shcm
 
            G = nx.Graph()               
            # Add nodes from fragment list
            G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                               for i in range(nrows)] + 
                             [(j + nrows, {'symbol': frag_list[j]})
                               for j in range(len(frag_list))])
 
            # Add edges from surface adjacency matrix
            shcm = shcm * np.tri(*shcm.shape, k=-1)
            rows, cols = np.where(shcm == 1)
            edges = zip(rows.tolist(), cols.tolist())
            G.add_edges_from(edges)
            if links:
                for (i, j) in links:
                    G.add_edge(i + len(surf_ids), j + len(surf_ids))
        # Atom-wise
        else:
            nblist = neighbor_shell_list(self.atoms, dx=dx, 
                                         neighbor_number=1, mic=False)
            cm = get_adj_matrix(nblist)
            if full_effect:
                surf_ids = self.metal_ids
                surf_ads_ids = list(range(len(self.atoms)))
            else:
                if subsurf_effect:
                    surf_ids = self.surf_ids + self.cas.get_subsurface()
                else:
                    surf_ids = self.surf_ids
                ads_ids = set()
                for st in self.hetero_site_list:
                    if st['occupied']:
                        ads_ids.update(list(st['adsorbate_indices']))
                surf_ads_ids = sorted(surf_ids + list(ads_ids))
            shcm = cm[surf_ads_ids][:,surf_ads_ids]
            symbols = self.symbols[surf_ads_ids]
            if return_adj_matrix:
                return shcm
 
            G = nx.Graph()                                                  
            G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                              for i in range(len(symbols))])
            rows, cols = np.where(shcm == 1)
            edges = zip(rows.tolist(), cols.tolist())
            G.add_edges_from(edges)

        return G

    def get_coverage(self):
        """Get the adsorbate coverage (ML) of the surface."""

        return self.coverage

    def get_subsurf_coverage(self):
        """Get the adsorbate coverage (ML) of the subsurface."""

        nsubsurf = len(self.cas.get_subsurface())
        return self.n_subsurf_occupied / nsubsurf


class SlabAdsorbateCoverage(object):
    """Child class of `SlabAdsorptionSites` for identifying adsorbate 
    coverage on a surface slab. Support 20 common surfaces: fcc100, 
    fcc111, fcc110, fcc211, fcc221, fcc311, fcc322, fcc331, fcc332, 
    bcc100, bcc111, bcc110, bcc210, bcc211, bcc310, hcp0001, 
    hcp10m10t, hcp10m10h, hcp10m11, hcp10m12.

    The information of each occupied site stored in the dictionary is 
    updated with the following new keys:

    **'occupied'**: 1 if the site is occupied, otherwise 0.

    **'adsorbate'**: the name of the adsorbate that occupies this site.

    **'adsorbate_indices'**: the indices of the adosorbate atoms that occupy
    this site. If the adsorbate is multidentate, these atoms might
    occupy multiple sites.

    **'bonding_index'**: the index of the atom that directly bonds to the
    site (closest to the site).

    **'fragment'**: the name of the fragment that occupies this site. Useful
    for multidentate species.

    **'fragment_indices'**: the indices of the fragment atoms that occupy
    this site. Useful for multidentate species.

    **'bond_length'**: the distance between the bonding atom and the site.

    **'dentate'**: dentate number.

    **'label'**: the updated label with the name of the occupying adsorbate
    if label_occupied_sites is set to True.

    Parameters
    ----------
    atoms : ase.Atoms object
        The atoms object must be a non-periodic nanoparticle with at 
        least one adsorbate attached to it. Accept any ase.Atoms object. 
        No need to be built-in.

    adsorption_sites : acat.adsorption_sites.SlabAdsorptionSites object or its pickle file path, default None
        `SlabAdsorptionSites` object of the nanoparticle. Initialize a         
        `SlabAdsorptionSites` object if not specified.
        If this is not provided, the arguments for identifying adsorption 
        sites can still be passed in by **kwargs.

    subtract_heights : dict, default None
        A dictionary that contains the height to be subtracted from the bond 
        length when allocating a type of site to an adsorbate. Default is to 
        allocate the site that is closest to the adsorbate's binding atom 
        without subtracting height. Useful for ensuring the allocated site 
        for each adsorbate is consistent with the site to which the adsorbate 
        was added.                                                             

    label_occupied_sites : bool, default False
        Whether to assign a label to the occupied each site. The string 
        of the occupying adsorbate is concatentated to the numerical 
        label that represents the occupied site.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    Examples
    --------
    The following example illustrates the most important use of a
    `SlabAdsorbateCoverage` object - getting occupied adsorption sites:

    .. code-block:: python

        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.build import add_adsorbate
        >>> from ase.build import fcc211
        >>> atoms = fcc211('Cu', (3, 3, 4), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Au'
        >>> atoms.center(axis=2)
        >>> add_adsorbate(atoms, adsorbate='CH3OH', surface='fcc211',
        ...               indices=(5, 7, 8), surrogate_metal='Cu')
        >>> sac = SlabAdsorbateCoverage(atoms, surface='fcc211', 
        ...                             label_occupied_sites=True)
        >>> occupied_sites = sac.get_sites(occupied=True)
        >>> print(occupied_sites)

    Output:

    .. code-block:: python

        [{'site': 'bridge', 'surface': 'fcc211', 'morphology': 'step', 
          'position': array([ 5.21058618,  5.74347483, 13.10576981]), 
          'normal': array([-0.33333333,  0.        ,  0.94280904]), 
          'indices': (1, 2), 'composition': None, 'subsurf_index': None, 
          'subsurf_element': None, 'label': '4OH', 'bonding_index': 40, 
          'bond_length': 1.11154558, 'adsorbate': 'CH3OH', 'fragment': 'OH', 
          'adsorbate_indices': (36, 37, 38, 39, 40, 41), 'occupied': 1, 
          'dentate': 2, 'fragment_indices': (40, 41)}, 
         {'site': 'bridge', 'surface': 'fcc211', 'morphology': 'sc-tc-h', 
          'position': array([ 1.04211724,  5.10531096, 12.73732573]), 
          'normal': array([-0.33333333,  0.        ,  0.94280904]), 
          'indices': (1, 5), 'composition': None, 'subsurf_index': None, 
          'subsurf_element': None, 'label': '6CH3', 'bonding_index': 36, 
          'bond_length': 0.78070973, 'adsorbate': 'CH3OH', 'fragment': 'CH3', 
          'adsorbate_indices': (36, 37, 38, 39, 40, 41), 'occupied': 1, 
          'dentate': 2, 'fragment_indices': (36, 37, 38, 39)}]

    The following example illustrates the use of `SlabAdsorbateCoverage` 
    to get all unoccupied symmetry-inequivalent adsorption sites on an 
    anatase TiO2(101) surface which is not directly implemented in ACAT:

    .. code-block:: python

        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.settings import CustomSurface
        >>> from ase.spacegroup import crystal
        >>> from ase.build import surface
        >>> a, c = 3.862, 9.551
        >>> anatase = crystal(['Ti', 'O'], basis=[(0 ,0, 0), (0, 0, 0.208)],
        ...                   spacegroup=141, cellpar=[a, a, c, 90, 90, 90])
        >>> anatase_101_atoms = surface(anatase, (1, 0, 1), 4, vacuum=5)
        >>> anatase_101 = CustomSurface(anatase_101_atoms, n_layers=4)
        >>> # Suppose we have a surface structure resulting from some
        >>> # perturbation of the reference TiO2(101) surface structure
        >>> atoms = anatase_101_atoms.copy()
        >>> atoms.rattle(stdev=0.2)
        >>> sac = SlabAdsorbateCoverage(atoms, surface=anatase_101,
        ...                             ignore_sites=['4fold'])
        >>> unq_unoccupied_sites = sac.get_unique_sites(occupied=False)
        >>> print(unq_unoccupied_sites) 

    Output:

    .. code-block:: python

        [{'site': '3fold', 'surface': CustomSurface, 'morphology': 'sc-tc', 
          'position': array([ 3.62687221,  1.94117703, 15.78133729]), 
          'normal': array([0.48335322, 0.        , 0.87542542]), 'indices': (36, 36, 38), 
          'composition': None, 'subsurf_index': None, 'subsurf_element': None, 'label': None, 
          'bonding_index': None, 'bond_length': None, 'adsorbate': None, 'fragment': None, 
          'adsorbate_indices': None, 'occupied': 0, 'dentate': 0, 'fragment_indices': None}, 
         {'site': 'bridge', 'surface': CustomSurface, 'morphology': 'sc-tc', 
          'position': array([ 3.24293684,  2.91921014, 15.99332154]), 
          'normal': array([0.3520727 , 0.        , 0.92537315]), 'indices': (36, 38), 
          'composition': None, 'subsurf_index': None, 'subsurf_element': None, 'label': None, 
          'bonding_index': None, 'bond_length': None, 'adsorbate': None, 'fragment': None, 
          'adsorbate_indices': None, 'occupied': 0, 'dentate': 0, 'fragment_indices': None}]

    """

    def __init__(self, atoms, 
                 adsorption_sites=None, 
                 subtract_heights=None,
                 label_occupied_sites=False,
                 adsorbate_indices=None,
                 dmax=2.5, **kwargs):

        atoms = atoms.copy()
        ptp = np.ptp(atoms.positions[:, 2]) 
        if np.linalg.norm(atoms.cell[2]) - ptp < 10.:
            atoms.cell[2][2] = ptp + 10.

        self.atoms = atoms 
        self.positions = atoms.positions
        self.symbols = atoms.symbols
        if adsorbate_indices is None:
            self.nonmetal_ids = [a.index for a in atoms if 
                                 a.symbol in adsorbate_elements]
        else:
            self.nonmetal_ids = adsorbate_indices
        if self.nonmetal_ids:
            self.ads_atoms = atoms[self.nonmetal_ids]
        else:
            self.ads_atoms = None
        self.cell = atoms.cell
        self.pbc = atoms.pbc

        self.subtract_heights = subtract_heights
        if subtract_heights is not None:
            self.subtract_heights = site_heights
            for k, v in subtract_heights.items():
                self.subtract_heights[k] = v      
        self.label_occupied_sites = label_occupied_sites
        self.dmax = dmax
        self.kwargs = {'allow_6fold': False, 'composition_effect': False,
                       'ignore_sites': None, 'label_sites': False} 
        self.kwargs.update(kwargs)

        if adsorption_sites:                           
            if isinstance(adsorption_sites, str):      
                import pickle      
                with open(adsorption_sites, 'rb') as f:
                    sas = pickle.load(f)
            else:
                sas = adsorption_sites
            for k in self.kwargs.keys():
                self.kwargs[k] = attrgetter(k)(sas)
        else:
            sas = SlabAdsorptionSites(atoms, **self.kwargs)
        self.__dict__.update(self.kwargs)
        self.adsorption_sites = sas
        self.sas = sas
        self.metals = sas.metals
        self.metal_ids = sas.metal_ids
        self.surf_ids = [self.metal_ids[i] for i in sas.surf_ids]
        try:
            self.subsurf_ids = [self.metal_ids[i] for i in sas.subsurf_ids]
            self.adj_matrix = sas.adj_matrix
            self.label_dict = sas.label_dict 
        except:
            self.subsurf_ids = []
            self.adj_matrix = None
            self.label_dict = {}
        self.hetero_site_list = deepcopy(sas.site_list)
 
        if self.nonmetal_ids:                                     
            self.make_ads_neighbor_list()
            self.ads_adj_matrix = self.get_ads_connectivity()
            self.identify_adsorbates()
        else:
            self.ads_list = []
        self.label_list = ['0'] * len(self.hetero_site_list)
        self.populate_hetero_site_list()

        if self.nonmetal_ids:
            self.labels = self.get_occupied_labels() 
        else:
            self.labels = []

    def identify_adsorbates(self):

        G = nx.Graph()
        adscm = self.ads_adj_matrix

        # Cut all intermolecular H-H bonds except intramolecular        
        # H-H bonds in e.g. H2
        hids = [a.index for a in self.ads_atoms if a.symbol == 'H']
        for hi in hids:
            conns = np.where(adscm[hi] == 1)[0]
            hconns = [i for i in conns if self.ads_atoms.symbols[i] == 'H']
            if hconns and len(conns) > 1:
                adscm[hi,hconns] = 0

        if adscm.size != 0:
            np.fill_diagonal(adscm, 1)
            rows, cols = np.where(adscm == 1)

            edges = zip([self.nonmetal_ids[row] for row in rows.tolist()], 
                        [self.nonmetal_ids[col] for col in cols.tolist()])
            G.add_edges_from(edges)                        
            SG = (G.subgraph(c) for c in nx.connected_components(G))
 
            adsorbates = []
            for sg in SG:
                nodes = sorted(list(sg.nodes))
                adsorbates += [nodes]
        else:
            adsorbates = [self.nonmetal_ids]

        self.ads_list = adsorbates

    def get_updated_connectivity(self):
        """Get the adjacency matrix of slab + adsorbates."""

        nbslist = neighbor_shell_list(self.atoms, 0.3, neighbor_number=1)
        return get_adj_matrix(nbslist)                           

    def get_ads_connectivity(self):
        """Get the adjacency matrix for adsorbate atoms."""

        return get_adj_matrix(self.ads_nblist) 

    def get_site_connectivity(self):
        """Get the adjacency matrix for adsorption sites."""

        sl = self.hetero_site_list
        conn_mat = []
        for i, sti in enumerate(sl):
            conn_x = []
            for j, stj in enumerate(sl):
                overlap = len(set(sti['indices']).intersection(stj['indices']))
                if i == j:
                    conn_x.append(0.)
                elif overlap > 0:
                    if self.allow_6fold:         
                        if 'subsurf' in [sti['morphology'], stj['morphology']]: 
                            if overlap == 3:
                                conn_x.append(1.)
                            else:
                                conn_x.append(0.)
                        else:
                            conn_x.append(1.)
                    else:
                        conn_x.append(1.) 
                else:
                    conn_x.append(0.)
            conn_mat.append(conn_x)   

        return np.asarray(conn_mat) 

    def populate_hetero_site_list(self):
        """Find all the occupied sites, identify the adsorbate coverage
        of those sites and collect in a heterogeneous site list."""

        hsl = self.hetero_site_list
        ll = self.label_list
        ads_list = self.ads_list
        ndentate_dict = {}

        for adsid in self.nonmetal_ids:
            if self.symbols[adsid] == 'H':
                if [adsid] not in ads_list:
                    rest = [s for x in ads_list for s in x 
                            if (adsid in x and s != adsid)]
                    if not (self.symbols[rest[0]] == 'H' and len(rest) == 1):
                        continue

            adspos = self.positions[adsid]
            if self.subtract_heights is not None:
                _, dls = find_mic(np.asarray([s['position'] + s['normal'] * 
                                  self.subtract_heights[s['site']] - adspos 
                                  for s in hsl]), cell=self.cell, pbc=True)
                stid = np.argmin(dls)
                st = hsl[stid]
                bl = get_mic(st['position'], adspos, self.cell, 
                             return_squared_distance=True)**0.5
            else:
                _, dls = find_mic(np.asarray([s['position'] - adspos for s in hsl]), 
                                  cell=self.cell, pbc=True)
                stid = np.argmin(dls)
                st, bl = hsl[stid], dls[stid] 
            bl = round(bl, 8)
            if bl > self.dmax:
                continue
            if st['normal'][2] > 0:
                if (bl > 0.75) and (st['position'][2] > adspos[2]):
                    continue
            else:
                if (bl > 0.75) and (st['position'][2] < adspos[2]):
                    continue

            adsids = next((l for l in ads_list if adsid in l), None)
            adsi = tuple(sorted(adsids))
            if 'occupied' in st:
                if bl >= st['bond_length']:
                    continue
                elif self.symbols[adsid] != 'H':
                    if adsi in ndentate_dict:
                        ndentate_dict[adsi] -= 1
            st['bonding_index'] = adsid
            st['bond_length'] = bl

            symbols = ''.join(list(Formula(str(self.symbols[adsids]))))
            adssym = next((k for k, v in adsorbate_formulas.items() 
                           if v == symbols), None)
            if adssym is None:
                adssym = next((k for k, v in adsorbate_formulas.items()
                               if sorted(v) == sorted(symbols)), symbols)

            st['adsorbate'] = adssym
            st['fragment'] = adssym
            st['adsorbate_indices'] = adsi 
            if adsi in ndentate_dict:
                ndentate_dict[adsi] += 1
            else:
                ndentate_dict[adsi] = 1
            st['occupied'] = 1        

        # Get dentate numbers and coverage  
        self.n_occupied, n_surf_occupied, n_subsurf_occupied = 0, 0, 0
        for st in hsl:
            if 'occupied' not in st:
                st['bonding_index'] = st['bond_length'] = None
                st['adsorbate'] = st['fragment'] = None
                st['adsorbate_indices'] = None
                st['occupied'] = st['dentate'] = 0
                st['fragment_indices'] = None
                continue
            self.n_occupied += 1
            if ('morphology' in st) and (st['morphology'] == 'subsurf'):
                n_subsurf_occupied += 1
            else:
                n_surf_occupied += 1
            adsi = st['adsorbate_indices']
            if adsi in ndentate_dict:              
                st['dentate'] = ndentate_dict[adsi]
            else:
                st['dentate'] = 0
        self.coverage = n_surf_occupied / len(self.surf_ids)
        if len(self.subsurf_ids) == 0:
            self.subsurf_coverage = 0.
        else:
            self.subsurf_coverage = n_subsurf_occupied / len(self.subsurf_ids)

        # Identify bidentate fragments and assign labels 
        self.multidentate_fragments = []
        self.monodentate_adsorbate_list = []
        self.multidentate_labels = []
        multidentate_adsorbate_dict = {}
        for j, st in enumerate(hsl):
            if st['occupied']:
                adssym = st['adsorbate']
                if st['dentate'] > 1:
                    bondid = st['bonding_index']
                    bondsym = self.symbols[bondid] 
                    conns = [self.nonmetal_ids[k] for k in np.where(self.ads_adj_matrix[
                             self.nonmetal_ids.index(bondid)] == 1)[0].tolist()]
                    hnnlen = len([i for i in conns if self.atoms[i].symbol == 'H'])
                    fsym = self.atoms[bondid].symbol
                    if hnnlen == 1:
                        fsym += 'H'
                    elif hnnlen > 1:
                        fsym += 'H{}'.format(hnnlen)
                    st['fragment'] = fsym 
                    flen = hnnlen + 1
                    adsids = st['adsorbate_indices']
                    ibond = adsids.index(bondid)
                    fsi = adsids[ibond:ibond+flen]
                    st['fragment_indices'] = fsi
                    if adsids not in multidentate_adsorbate_dict:
                        multidentate_adsorbate_dict[adsids] = adssym
                else:
                    st['fragment_indices'] = st['adsorbate_indices'] 
                    self.monodentate_adsorbate_list.append(adssym)

                if self.label_occupied_sites:
                    if st['label'] is None:
                        signature = [st['site'], st['morphology']]   
                        if self.composition_effect:
                            signature.append(st['composition'])
                        stlab = self.label_dict['|'.join(signature)]
                    else:
                        stlab = st['label']
                    label = str(stlab) + st['fragment']
                    st['label'] = label
                    ll[j] = label
                    if st['dentate'] > 1:                    
                        self.multidentate_fragments.append(label)
                        if bondid == adsids[0]:
                            mdlabel = str(stlab) + adssym
                            self.multidentate_labels.append(mdlabel)
            else:
                if self.label_occupied_sites and (st['label'] is None):
                    signature = [st['site'], st['morphology']]
                    if self.composition_effect:
                        signature.append(st['composition'])
                    st['label'] = self.label_dict['|'.join(signature)] 

        self.multidentate_adsorbate_list = list(multidentate_adsorbate_dict.values())
        self.adsorbate_list = self.monodentate_adsorbate_list + \
                              self.multidentate_adsorbate_list 

    def get_site(self, indices=None):
        """Get information of an adsorption site.
        
        Parameters
        ----------
        indices : list or tuple, default None
            The indices of the atoms that contribute to the site.
            Return a random site if the indices are not provided.   

        """

        if indices is None:
            st = random.choice(self.hetero_site_list)
        else:
            indices = indices if is_list_or_tuple(indices) else [indices]
            indices = tuple(sorted(indices))
            st = next((s for s in self.hetero_site_list if 
                       s['indices'] == indices), None)
        return st

    def get_sites(self, occupied=None, **kwargs):
        """Get information of all sites.
                                                                     
        Parameters                                                   
        ----------                                                   
        occupied : bool or None, default None
            Set to True to return only the occupied sites.
            Set to False to return only the unoccupied sites.
            Set to None to return all sites.

        """                                                          

        kwargs['return_site_indices'] = True
        all_sites = self.hetero_site_list
        target_stids = self.sas.get_sites(**kwargs)
        target_sites = [all_sites[si] for si in target_stids]
        if occupied is True:
            target_sites = [s for s in target_sites if s['occupied']]
        elif occupied is False:
            target_sites = [s for s in target_sites if not s['occupied']]

        return target_sites

    def get_unique_sites(self, occupied=False, **kwargs):           
        """Get all symmetry-inequivalent adsorption sites (one
        site for each type). Note that this method does not
        consider the change in site's local environment caused
        by adsorbates. To get unique sites with adsorbate effects,
        please use acat.build.adlayer.SystematicPatternGenerator.

        Parameters
        ----------
        occupied : bool or None, default False
            Set to True to return only the occupied unique sites.
            Set to False to return only the unoccupied unique sites.
            Set to None to return all unique sites.

        """

        kwargs['return_site_indices'] = True
        all_sites = self.hetero_site_list
        unq_stids = self.sas.get_unique_sites(**kwargs)
        unq_sites = [all_sites[si] for si in unq_stids]
        if occupied is True:
            unq_sites = [s for s in unq_sites if s['occupied']]
        elif occupied is False:
            unq_sites = [s for s in unq_sites if not s['occupied']]

        return unq_sites

    def get_adsorbates(self, adsorbate_species=None, fragmentation=True):
        """Get a list of tuples that contains each adsorbate (string)
        and the corresponding adsorbate indices (tuple) in ascending
        order.

        Parameters
        ----------
        adsorbate_species : list of strs, default None
            The available adsorbate species. If the adsorbate is not
            one of the available species, return the fragment instead.

        """

        adsorbates = []
        adsorbate_ids = set()
        for st in self.hetero_site_list:
            if st['occupied']:
                if adsorbate_species is not None:
                    if st['adsorbate'] not in adsorbate_species:
                        if fragmentation:
                            fragi = st['fragment_indices']
                            adsorbates.append((st['fragment'], fragi))
                            adsorbate_ids.update(fragi)
                        continue
                adsi = st['adsorbate_indices']
                if not set(adsi).issubset(adsorbate_ids):
                    adsorbates.append((st['adsorbate'], adsi))
                    adsorbate_ids.update(adsi)

        return sorted(adsorbates, key=lambda x: x[1])

    def get_fragments(self):
        """Get a list of tuples that contains each fragment (string)
        and the corresponding fragment indices (tuple) in ascending
        order."""

        fragments = []
        for st in self.hetero_site_list:
            if st['occupied']:
                fragi = st['fragment_indices']
                fragments.append((st['fragment'], fragi))

        return sorted(fragments, key=lambda x: x[1])        

    def make_ads_neighbor_list(self, dx=.2, neighbor_number=1):
        self.ads_nblist = neighbor_shell_list(self.ads_atoms, dx, 
                                              neighbor_number, mic=True)

    def get_occupied_labels(self, fragmentation=True):
        """Get a list of labels of all occupied sites. The label consists
        of a numerical part that represents site, and a character part
        that represents the occupying adsorbate.

        Parameters
        ----------
        fragmentation : bool, default True
            Whether to cut multidentate species into fragments. This ensures 
            that multidentate species with different orientations have 
            different labels.

        """

        if not self.label_occupied_sites:
            return self.atoms[self.nonmetal_ids].get_chemical_formula(mode='hill')

        ll = self.label_list
        labs = [lab for lab in ll if lab != '0']
        if not fragmentation:
            mf = self.multidentate_fragments
            mdlabs = self.multidentate_labels
            c1, c2 = Counter(labs), Counter(mf)
            diff = list((c1 - c2).elements())
            labs = diff + mdlabs                   

        return sorted(labs)

    def get_graph(self, atom_wise=False,
                  fragmentation=True, 
                  subsurf_effect=False,
                  full_effect=False,
                  return_adj_matrix=False,
                  connect_dentates=True,
                  dx=0.5):                                         
        """Get the graph representation of the nanoparticle with adsorbates.

        Parameters
        ----------
        atom_wise : bool, default False
            Whether to treat each adsorbate as an atom-wise subgraph. If not, 
            treat each adsorbate fragment as a unity (molecule-wise, which may
            not preserve the atomic indices).

        fragmentation : bool, default True
            Whether to cut multidentate species into fragments. This ensures 
            that multidentate species with different orientations have 
            different graphs.

        subsurf_effect : bool, default False
            Take subsurface atoms into consideration when generating graph. 

        full_effect : bool, default False
            Take the whole catalyst into consideration when generating graph.

        return_adj_matrix : bool, default False
            Whether to return adjacency matrix instead of the networkx.Graph 
            object.

        connect_dentates : bool, default True
            Whether to add edges between the fragments of multidentate species.

        dx : float, default 0.5
            Buffer to calculate nearest neighbor pairs. Only relevent when
            atom_wise=True.

        """

        # Molecule-wise
        if not atom_wise:
            hsl = self.hetero_site_list
            hcm = self.adj_matrix.copy()
            if full_effect:
                surf_ids = self.metal_ids
            else:
                if subsurf_effect:
                    surf_ids = self.surf_ids + self.subsurf_ids
                else:
                    surf_ids = self.surf_ids
            surf_metal_ids = [i for i, idx in enumerate(self.metal_ids) if idx in surf_ids]
            surfhcm = hcm[surf_metal_ids]
            symbols = self.symbols[self.metal_ids]
            nrows, ncols = surfhcm.shape       
 
            newrows, frag_list, adsi_list = [], [], []
            multi_conns = defaultdict(list)
            ohsl = [st for st in hsl if st['occupied']]
            for st in sorted(ohsl, key=lambda x: x['fragment_indices']):
                adsi = st['adsorbate_indices']
                if not fragmentation and st['dentate'] > 1: 
                    if st['bonding_index'] != adsi[0]:
                        continue
                si = [i for i, idx in enumerate(self.metal_ids) if idx in st['indices']]
                newrow = np.zeros(ncols)
                newrow[si] = 1
                newrows.append(newrow)
 
                if fragmentation:                
                    frag_list.append(st['fragment'])
                    if st['dentate'] > 1 and connect_dentates:
                        bondid = st['bonding_index']
                        all_conns = [self.nonmetal_ids[j] for j in np.where(self.ads_adj_matrix[
                                     self.nonmetal_ids.index(bondid)] == 1)[0].tolist()]
                        conns = [c for c in all_conns if c not in st['fragment_indices']]
                        i = len(newrows) - 1
                        if i not in multi_conns:
                            multi_conns[bondid].append([i])
                        for k, v in multi_conns.items():
                            if k in conns:
                                multi_conns[k].append([i, v[0][0]])
                else:
                    frag_list.append(st['adsorbate'])
 
            links = []
            if newrows:
                surfhcm = np.vstack((surfhcm, np.asarray(newrows)))
                if multi_conns:
                    links = [sorted(c) for cs in multi_conns.values() for c in cs if len(c) > 1]
 
            shcm = surfhcm[:,surf_metal_ids]
            if return_adj_matrix:
                if newrows:
                    dd = len(newrows)
                    small_mat = np.zeros((dd, dd))
                    if links:
                        for (i, j) in links:
                            small_mat[i,j] = 1
                            small_mat[j,i] = 1
                    return np.hstack((shcm, np.vstack((shcm[-dd:].T, small_mat))))
                else:
                    return shcm
 
            G = nx.Graph()               
            # Add nodes from fragment list
            G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                               for i in range(nrows)] + 
                             [(j + nrows, {'symbol': frag_list[j]})
                               for j in range(len(frag_list))])
 
            # Add edges from surface adjacency matrix
            shcm = shcm * np.tri(*shcm.shape, k=-1)
            rows, cols = np.where(shcm == 1)
            edges = zip(rows.tolist(), cols.tolist())
            G.add_edges_from(edges)
            if links:
                for (i, j) in links:
                    G.add_edge(i + len(surf_ids), j + len(surf_ids))
        # Atom-wise
        else:
            nblist = neighbor_shell_list(self.atoms, dx=dx, 
                                         neighbor_number=1, mic=True)
            cm = get_adj_matrix(nblist)
            if full_effect:
                surf_ids = self.metal_ids
                surf_ads_ids = list(range(len(self.atoms)))
            else:
                if subsurf_effect:
                    surf_ids = self.surf_ids + self.subsurf_ids
                else:
                    surf_ids = self.surf_ids
                ads_ids = set()                                       
                for st in self.hetero_site_list:
                    if st['occupied']:
                        ads_ids.update(list(st['adsorbate_indices']))
                surf_ads_ids = sorted(surf_ids + list(ads_ids))
            shcm = cm[surf_ads_ids][:,surf_ads_ids]
            symbols = self.symbols[surf_ads_ids]
            if return_adj_matrix:
                return shcm

            G = nx.Graph()                                                  
            G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                              for i in range(len(symbols))])
            rows, cols = np.where(shcm == 1)
            edges = zip(rows.tolist(), cols.tolist())
            G.add_edges_from(edges)

        return G

    def get_coverage(self):
        """Get the adsorbate coverage (ML) of the surface."""

        return self.coverage

    def get_subsurf_coverage(self):
        """Get the adsorbate coverage (ML) of the subsurface."""

        return self.subsurf_coverage


def enumerate_updated_sites(atoms, adsorption_sites=None,
                            surface=None, morphology=None,
                            occupied=None, subtract_heights=None,
                            label_occupied_sites=False,
                            adsorbate_indices=None,
                            dmax=2.5, **kwargs):
    """A function that enumerates all updated (occupied/unoccupied) 
    adsorption sites of the input catalyst structure after adding 
    adsorbates. The function is generalized for both periodic and 
    non-periodic systems (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object or acat.adsorption_sites.SlabAdsorptionSites object or the corresponding pickle file path, default None
        The built-in adsorption sites class. If this is not provided, 
        the arguments for identifying adsorption sites can still be 
        passed in by **kwargs.

    surface : str, default None
        The surface type (crystal structure + Miller indices)
        If the structure is a periodic surface slab, this is required.
        If the structure is a nanoparticle, the function enumerates
        only the sites on the specified surface.
        For periodic slabs, a user-defined customized surface object 
        can also be used, but note that the identified site types will 
        only include 'ontop', 'bridge', '3fold' and '4fold'.

    morphology : str, default None
        The function enumerates only the sites of the specified
        local surface morphology. Only available for surface slabs.

    occupied : bool or None, default None
        Set to True to return only the occupied sites.
        Set to False to return only the unoccupied sites.
        Set to None to return all sites.

    subtract_heights : dict, default None
        A dictionary that contains the height to be subtracted from the 
        bond length when allocating a type of site to an adsorbate. 
        Default is to allocate the site that is closest to the adsorbate's 
        binding atom without subtracting height. Useful for ensuring the 
        allocated site for each adsorbate is consistent with the site to 
        which the adsorbate was added.                                                           

    label_occupied_sites : bool, default False
        Whether to assign a label to the occupied each site. The string 
        of the occupying adsorbate is concatentated to the numerical 
        label that represents the occupied site.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    Example
    -------
    This is an example of enumerating all occupied sites on a truncated 
    octahedral nanoparticle:

    .. code-block:: python

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.adsorbate_coverage import enumerate_updated_sites
        >>> from acat.build import add_adsorbate_to_site
        >>> from ase.cluster import Octahedron
        >>> atoms = Octahedron('Ni', length=7, cutoff=2)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Pt'
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms, composition_effect=True,
        ...                              surrogate_metal='Ni') 
        >>> sites = cas.get_sites()
        >>> for s in sites:
        ...     if s['site'] == 'ontop':
        ...         add_adsorbate_to_site(atoms, adsorbate='OH', site=s)
        >>> sites = enumerate_updated_sites(atoms, adsorption_sites=cas,
        ...                                 occupied=True) 
        >>> print(sites[0])

    Output:

    .. code-block:: python

        {'site': 'ontop', 'surface': 'edge', 
         'position': array([ 6.76,  6.76, 12.04]), 
         'normal': array([-0.70710678, -0.70710678, -0.        ]), 
         'indices': (0,), 'composition': 'Pt', 'subsurf_index': None, 
         'subsurf_element': None, 'label': None, 'bonding_index': 201, 
         'bond_length': 1.8, 'adsorbate': 'OH', 'fragment': 'OH', 
         'adsorbate_indices': (201, 202), 'occupied': 1, 'dentate': 1, 
         'fragment_indices': (201, 202)}

    """

    if True not in atoms.pbc:
        cac = ClusterAdsorbateCoverage(atoms, adsorption_sites,
                                       subtract_heights,
                                       label_occupied_sites,
                                       adsorbate_indices,
                                       dmax, **kwargs)
        all_sites = cac.hetero_site_list
        if surface is not None:
            all_sites = [s for s in all_sites if s['surface'] == surface]
        if occupied is not None:
            all_sites = [s for s in all_sites if s['occupied'] == occupied]

    else:
        kwargs['surface'] = surface
        sac = SlabAdsorbateCoverage(atoms, adsorption_sites,
                                    subtract_heights,
                                    label_occupied_sites,
                                    adsorbate_indices,
                                    dmax, **kwargs)
        all_sites = sac.hetero_site_list
        if morphology is not None:
            all_sites = [s for s in all_sites if s['morphology'] == morphology] 
        if occupied is not None:
            all_sites = [s for s in all_sites if s['occupied'] == occupied]

    return all_sites

