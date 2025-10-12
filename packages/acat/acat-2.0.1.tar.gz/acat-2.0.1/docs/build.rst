Building things
===============

Operate adsorbate
-----------------

.. automodule:: acat.build.action
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: add_adsorbate, add_adsorbate_to_site, add_adsorbate_to_label, remove_adsorbate_from_site, remove_adsorbates_from_sites, remove_adsorbates_too_close

The add_adsorbate function
~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: add_adsorbate
               
    **Example 1**

    To add a NO molecule to a bridge site consists of one Pt and one 
    Ni on the fcc111 surface of a bimetallic truncated octahedron:

        >>> from acat.build import add_adsorbate 
        >>> from ase.cluster import Octahedron
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', length=7, cutoff=2)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Pt' 
        >>> add_adsorbate(atoms, adsorbate='NO', site='bridge',
        ...               surface='fcc111', composition='NiPt',
        ...               surrogate_metal='Ni')
        >>> view(atoms)

    Output: 
    
    .. image:: ../images/add_adsorbate_1.png 
       :scale: 70 %
       :align: center

    **Example 2**

    To add a N atom to a Ti-Ti bridge site on an anatase TiO2(101) 
    surface. The code automatically identifies the sites occupied by 
    surface oxygens and then adds the adsorbate to an unoccupied 
    bridge site:

        >>> from acat.build import add_adsorbate
        >>> from acat.settings import CustomSurface
        >>> from ase.spacegroup import crystal
        >>> from ase.build import surface
        >>> from ase.visualize import view
        >>> a, c = 3.862, 9.551
        >>> anatase = crystal(['Ti', 'O'], basis=[(0 ,0, 0), (0, 0, 0.208)],
        ...                   spacegroup=141, cellpar=[a, a, c, 90, 90, 90])
        >>> anatase_101_atoms = surface(anatase, (1, 0, 1), 4, vacuum=5)
        >>> anatase_101 = CustomSurface(anatase_101_atoms, n_layers=4)
        >>> # Suppose we have a surface structure resulting from some
        >>> # perturbation of the reference TiO2(101) surface structure
        >>> atoms = anatase_101_atoms.copy()
        >>> atoms.rattle(stdev=0.2)
        >>> add_adsorbate(atoms, adsorbate='N', site='bridge',
        ...               surface=anatase_101, composition='TiTi')
        >>> view(atoms) 

    Output:

    .. image:: ../images/add_adsorbate_2.png
       :scale: 80 %
       :align: center

The add_adsorbate_to_site function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: add_adsorbate_to_site

    **Example 1**

    To add CO to all fcc sites of an icosahedral nanoparticle:

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.build import add_adsorbate_to_site
        >>> from ase.cluster import Icosahedron
        >>> from ase.visualize import view
        >>> atoms = Icosahedron('Pt', noshells=5)
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms)
        >>> fcc_sites = cas.get_sites(site='fcc')
        >>> for site in fcc_sites:
        ...     add_adsorbate_to_site(atoms, adsorbate='CO', site=site)
        >>> view(atoms)

    Output:

    .. image:: ../images/add_adsorbate_to_site_1.png
       :align: center

    **Example 2**

    To add a bidentate CH3OH to the (54, 57, 58) site on a Pt fcc111 
    surface slab and rotate to the orientation of a neighbor site:

        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from acat.adsorption_sites import get_adsorption_site
        >>> from acat.build import add_adsorbate_to_site 
        >>> from acat.utilities import get_mic
        >>> from ase.build import fcc111
        >>> from ase.visualize import view
        >>> atoms = fcc111('Pt', (4, 4, 4), vacuum=5.)
        >>> i, site = get_adsorption_site(atoms, indices=(54, 57, 58),
        ...                               surface='fcc111',
        ...                               return_index=True)
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc111')
        >>> sites = sas.get_sites()
        >>> nbsites = sas.get_neighbor_site_list(neighbor_number=1)
        >>> nbsite = sites[nbsites[i][0]] # Choose the first neighbor site
        >>> ori = get_mic(site['position'], nbsite['position'], atoms.cell)
        >>> add_adsorbate_to_site(atoms, adsorbate='CH3OH', site=site, 
        ...                       orientation=ori)
        >>> view(atoms)

    Output:

    .. image:: ../images/add_adsorbate_to_site_2.png
       :scale: 70 %
       :align: center

    **Example 3**

    We can also generate symmetric surface slabs with adsorbates by
    setting both_sides=True. Below is a more advanced example for 
    generating a symmetric 5-layer rutile TiO2(110) surface slab with 
    N adsorbed at all cus sites:

        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.build import add_adsorbate_to_site
        >>> from acat.settings import CustomSurface
        >>> from ase.spacegroup import crystal
        >>> from ase.build import surface
        >>> from ase.visualize import view
        >>> from collections import Counter
        >>> a, c = 4.584, 2.953
        >>> rutile = crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0)],
        ...                  spacegroup=136, cellpar=[a, a, c, 90, 90, 90])
        >>> rutile_110_atoms = surface(rutile, (1,1,0), layers=5)
        >>> # Remove the oxygens above the top surface
        >>> indices = [a.index for a in rutile_110_atoms if a.position[2] < 14.]
        >>> rutile_110_atoms = rutile_110_atoms[indices]
        >>> rutile_110_atoms.center(vacuum=5., axis=2)
        >>> rutile_110_atoms *= (2,3,1)
        >>> rutile_110 = CustomSurface(rutile_110_atoms, n_layers=5)
        >>> sac = SlabAdsorbateCoverage(rutile_110_atoms, surface=rutile_110, both_sides=True)
        >>> # Get all ontop sites which half are cus sites
        >>> ontop_sites = sac.get_sites(site='ontop')
        >>> # Get all 3fold sites occupied by oxygen
        >>> occupied_3fold_sites = sac.get_sites(occupied=True, site='3fold')
        >>> # Cus sites are then the atoms that contribute 4 times to these sites
        >>> occurences = [i for st in occupied_3fold_sites for i in st['indices']]
        >>> cus_indices = [(i,) for i, count in Counter(occurences).items() if count == 4]
        >>> for site in ontop_sites:
        ...     if site['indices'] in cus_indices:
        ...         add_adsorbate_to_site(rutile_110_atoms, adsorbate='N', site=site)
        >>> view(rutile_110_atoms)

    Output:

    .. image:: ../images/add_adsorbate_to_site_3.png
       :scale: 70 %
       :align: center

The add_adsorbate_to_label function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: add_adsorbate_to_label

    **Example**

    To add a NH molecule to a site with bimetallic label 14 (an 
    hcp CuCuAu site) on a bimetallic fcc110 surface slab:

        >>> from acat.build import add_adsorbate_to_label 
        >>> from ase.build import fcc110
        >>> from ase.visualize import view
        >>> atoms = fcc110('Cu', (3, 3, 8), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Au'
        ... atoms.center(axis=2)
        >>> add_adsorbate_to_label(atoms, adsorbate='NH', 
        ...                        label=14, surface='fcc110', 
        ...                        composition_effect=True,
        ...                        surrogate_metal='Cu')
        >>> view(atoms)

    Output:

    .. image:: ../images/add_adsorbate_to_label.png
       :scale: 70 %
       :align: center

The remove_adsorbate_from_site function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: remove_adsorbate_from_site

    **Example 1**

    To remove a CO molecule from a fcc111 surface slab with one 
    CO and one OH:

        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.build import add_adsorbate_to_site 
        >>> from acat.build import remove_adsorbate_from_site
        >>> from ase.build import fcc111
        >>> from ase.visualize import view
        >>> atoms = fcc111('Pt', (6, 6, 4), 4, vacuum=5.)
        >>> atoms.center(axis=2) 
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc111')
        >>> sites = sas.get_sites()
        >>> add_adsorbate_to_site(atoms, adsorbate='OH', site=sites[0])
        >>> add_adsorbate_to_site(atoms, adsorbate='CO', site=sites[-1])
        >>> sac = SlabAdsorbateCoverage(atoms, sas)
        >>> occupied_sites = sac.get_sites(occupied=True)
        >>> CO_site = next((s for s in occupied_sites if s['adsorbate'] == 'CO'))
        >>> remove_adsorbate_from_site(atoms, site=CO_site)
        >>> view(atoms)

    .. image:: ../images/remove_adsorbate_from_site.png
       :scale: 60 %

The remove_adsorbates_from_sites function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: remove_adsorbates_from_sites

    **Example 1**

    To remove all CO species from a fcc111 surface slab covered 
    with both CO and OH:

        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.build.adlayer import min_dist_coverage_pattern
        >>> from acat.build import remove_adsorbates_from_sites
        >>> from ase.build import fcc111
        >>> from ase.visualize import view
        >>> slab = fcc111('Pt', (6, 6, 4), 4, vacuum=5.)
        >>> slab.center(axis=2)
        >>> atoms = min_dist_coverage_pattern(slab, adsorbate_species=['OH','CO'],
        ...                                   surface='fcc111',
        ...                                   min_adsorbate_distance=5.)
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc111')
        >>> sac = SlabAdsorbateCoverage(atoms, sas)
        >>> occupied_sites = sac.get_sites(occupied=True)
        >>> CO_sites = [s for s in occupied_sites if s['adsorbate'] == 'CO']
        >>> remove_adsorbates_from_sites(atoms, sites=CO_sites)
        >>> view(atoms)

    Output:

    .. image:: ../images/remove_adsorbates_from_sites_1.png
       :scale: 60 %

    **Example 2**

    To remove O species from all cus sites on a rutile TiO2(110) 
    surface slab:

        >>> from acat.adsorbate_coverage import SlabAdsorbateCoverage
        >>> from acat.build import remove_adsorbates_from_sites
        >>> from acat.settings import CustomSurface
        >>> from ase.spacegroup import crystal
        >>> from ase.build import surface
        >>> from ase.visualize import view
        >>> from collections import Counter
        >>> a, c = 4.584, 2.953
        >>> rutile = crystal(['Ti', 'O'], basis=[(0, 0, 0), (0.3, 0.3, 0)],
        ...                  spacegroup=136, cellpar=[a, a, c, 90, 90, 90])
        >>> rutile_110_atoms = surface(rutile, (1,1,0), layers=5)
        >>> rutile_110_atoms.center(vacuum=5., axis=2)
        >>> rutile_110_atoms *= (2,3,1)
        >>> rutile_110 = CustomSurface(rutile_110_atoms, n_layers=5)
        >>> sac = SlabAdsorbateCoverage(rutile_110_atoms, surface=rutile_110)
        >>> # Get all ontop sites which half are cus sites
        >>> ontop_sites = sac.get_sites(site='ontop')
        >>> # Get all 3fold sites occupied by oxygen
        >>> occupied_3fold_sites = sac.get_sites(occupied=True, site='3fold')
        >>> # Cus sites are then the atoms that contribute 4 times to these sites
        >>> occurences = [i for st in occupied_3fold_sites for i in st['indices']]
        >>> cus_indices = [(i,) for i, count in Counter(occurences).items() if count == 4]
        >>> # Remove O from all cus sites
        >>> cus_sites = [s for s in ontop_sites if s['indices'] in cus_indices]
        >>> remove_adsorbates_from_sites(rutile_110_atoms, sites=cus_sites)
        >>> view(rutile_110_atoms)

    Output:

    .. image:: ../images/remove_adsorbates_from_sites_2.png
       :scale: 70 %

The remove_adsorbates_too_close function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: remove_adsorbates_too_close

    **Example**

    To remove unphysically close adsorbates on the edges of a Marks 
    decahedron with 0.75 ML ordered CO coverage:

        >>> from acat.build.adlayer import special_coverage_pattern
        >>> from acat.build import remove_adsorbates_too_close
        >>> from ase.cluster import Decahedron
        >>> from ase.visualize import view
        >>> atoms = Decahedron('Pt', p=4, q=3, r=1)
        >>> atoms.center(vacuum=5.)
        >>> pattern = special_coverage_pattern(atoms, adsorbate='CO', 
        ...                                    coverage=0.75)
        >>> remove_adsorbates_too_close(pattern, min_adsorbate_distance=1.)
        >>> view(pattern)

    Output:

    .. image:: ../images/remove_adsorbates_too_close.png

Generate adsorbate overlayer patterns
-------------------------------------

.. automodule:: acat.build.adlayer
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: RandomPatternGenerator, SystematicPatternGenerator, OrderedPatternGenerator, special_coverage_pattern, max_dist_coverage_pattern, min_dist_coverage_pattern

The RandomPatternGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: RandomPatternGenerator

        .. automethod:: run

    **Example 1**

    The following example illustrates how to stochastically generate 
    100 unique adsorbate overlayer patterns with one more adsorbate 
    chosen from CO, OH, CH3 and CHO, based on 10 Pt fcc111 surface 
    slabs with random C and O coverages, where CH3 is forbidden to be
    added to ontop and bridge sites:

        >>> from acat.build.adlayer import RandomPatternGenerator as RPG
        >>> from acat.build.adlayer import min_dist_coverage_pattern
        >>> from ase.build import fcc111
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> slab = fcc111('Pt', (6, 6, 4), 4, vacuum=5.)
        >>> slab.center(axis=2)
        >>> images = []
        >>> for _ in range(10):
        ...     atoms = slab.copy()
        ...     image = min_dist_coverage_pattern(atoms, adsorbate_species=['C','O'],
        ...                                       surface='fcc111',
        ...                                       min_adsorbate_distance=5.)
        ...     images.append(image)
        >>> rpg = RPG(images, adsorbate_species=['CO','OH','CH3','CHO'],
        ...           species_probabilities={'CO': 0.3, 'OH': 0.3, 
        ...                                  'CH3': 0.2, 'CHO': 0.2},
        ...           min_adsorbate_distance=1.5, 
        ...           surface='fcc111',
        ...           composition_effect=False, 
        ...           species_forbidden_sites={'CH3': ['ontop','bridge']})
        >>> rpg.run(num_gen=100, action='add', unique=True)
        >>> images = read('patterns.traj', index=':') 
        >>> view(images)

    Output:

    .. image:: ../images/RandomPatternGenerator1.gif
       :scale: 60 %
       :align: center

    **Example 2**

    The following example illustrates how to generate 20 unique coverage 
    patterns, each adding 4 adsorbates (randomly chosen from H, OH and 
    H2O) onto a fcc100 Ni2Cu surface slab on both top and bottom 
    interfaces (:download:`bulk water <../tests/water_bulk.xyz>` in 
    between) with probabilities of 0.25, 0.25, 0.5, respectively, and a 
    minimum adsorbate distance of 2.5 Angstrom:

        >>> from acat.build.adlayer import RandomPatternGenerator as RPG
        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from ase.io import read
        >>> from ase.build import fcc100
        >>> from ase.visualize import view
        >>> water_bulk = read('water_bulk.xyz')
        >>> water_bulk.center(vacuum=11., axis=2)
        >>> slab = fcc100('Ni', (4, 4, 8), vacuum=9.5, periodic=True)
        >>> for atom in slab:
        ...     if atom.index % 3 == 0:
        ...         atom.symbol = 'Cu'
        >>> slab.translate(-slab.cell[2] / 2)
        >>> slab.wrap()
        >>> atoms = slab + water_bulk
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc100',
        ...                           composition_effect=True,
        ...                           both_sides=True,
        ...                           surrogate_metal='Ni')
        >>> rpg = RPG(atoms, adsorbate_species=['H','OH','OH2'],
        ...           species_probabilities={'H': 0.25, 'OH': 0.25, 'OH2': 0.5},
        ...           min_adsorbate_distance=2.5,
        ...           adsorption_sites=sas,
        ...           surface='fcc100')
        >>> rpg.run(num_gen=20, action='add', num_act=4, unique=True)
        >>> images = read('patterns.traj', index=':')
        >>> view(images) 

    Output:

    .. image:: ../images/RandomPatternGenerator2.gif
       :scale: 60 %
       :align: center

    **Example 3**

    The following example illustrates how to generate 20 random
    adsorbate overlayer patterns with 5 adsorbates: 1 CO, 2 OH and 
    2 N, on 10 quaternary cuboctahedral nanoalloys with random 
    chemical orderings. The minimum adsorbate distance is set to 3 
    Angstrom and duplicate patterns are allowed (very unlikely for 
    nanoparticles):

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.build.adlayer import RandomPatternGenerator as RPG
        >>> from acat.build.ordering import RandomOrderingGenerator as ROG
        >>> from ase.cluster import Octahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', length=5, cutoff=2)
        >>> atoms.center(vacuum=5.)
        >>> rog = ROG(atoms, elements=['Ni', 'Cu', 'Pt', 'Au'])
        >>> rog.run(num_gen=10)
        >>> particles = read('orderings.traj', index=':')
        >>> rpg = RPG(particles, adsorbate_species=['CO','OH','N'],
        ...           min_adsorbate_distance=3.,
        ...           composition_effect=True,
        ...           surrogate_metal='Ni')
        >>> rpg.run(num_gen=20, action='add', num_act=5, unique=False,
        ...         add_species_composition={'CO': 1, 'OH': 2, 'N': 2})
        >>> images = read('patterns.traj', index=':')
        >>> view(images)

    Output:

    .. image:: ../images/RandomPatternGenerator3.gif

The SystematicPatternGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: SystematicPatternGenerator

        .. automethod:: run

    **Example 1**

    The following example illustrates how to add CO to all unique sites on 
    a cuboctahedral bimetallic nanoparticle with a minimum adsorbate
    distance of 2 Angstrom:

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.build.adlayer import SystematicPatternGenerator as SPG
        >>> from ase.cluster import Octahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Cu', length=7, cutoff=3)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Au' 
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms, composition_effect=True,
        ...                              surrogate_metal='Cu')
        >>> spg = SPG(atoms, adsorbate_species='CO',
        ...           min_adsorbate_distance=2., 
        ...           adsorption_sites=cas,
        ...           composition_effect=True) 
        >>> spg.run(action='add')
        >>> images = read('patterns.traj', index=':') 
        >>> view(images)

    Output:

    .. image:: ../images/SystematicPatternGenerator1.gif                     

    **Example 2**

    The following example illustrates how to enumerate all unique coverage
    patterns consists of 3 adsorbates: 1 C, 1 N and 1 O on a bimetallic 
    bcc111 surface slab with a minimum adsorbate distance of 2 Angstrom 
    (here only generate a maximum of 100 unique patterns):

        >>> from acat.build.adlayer import SystematicPatternGenerator as SPG
        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from ase.io import read
        >>> from ase.build import bcc111
        >>> from ase.visualize import view
        >>> atoms = bcc111('Fe', (2, 2, 12), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Mo'
        >>> atoms.center(axis=2)
        >>> sas = SlabAdsorptionSites(atoms, surface='bcc111',
        ...                           ignore_sites='3fold',
        ...                           composition_effect=True)
        >>> spg = SPG(atoms, adsorbate_species=['C','N','O'],
        ...           min_adsorbate_distance=2.,
        ...           adsorption_sites=sas,
        ...           surface='bcc111',
        ...           composition_effect=True)
        >>> spg.run(max_gen_per_image=100, action='add', num_act=3,
        ...         add_species_composition={'C': 1, 'N': 1, 'O': 1}) 
        >>> images = read('patterns.traj', index=':')
        >>> view(images)

    Output:

    .. image:: ../images/SystematicPatternGenerator2.gif
       :scale: 40 %
       :align: center

    **Example 3**

    The following example illustrates how to enumerate all unique sites
    on a ( :download:`Cu2O(111) surface slab <../tests/Cu2O_111.xyz>` )
    that considers the lattice-O effect on the local environment of each 
    site. Here we will also enumerate all unique orientations of a 
    multidentate SO2 adsorbate at these unique sites:

        >>> from acat.build.adlayer import SystematicPatternGenerator as SPG
        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from acat.settings import CustomSurface
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = read('Cu2O_111.xyz')
        >>> Cu2O_111 = CustomSurface(atoms, n_layers=4)
        >>> sas = SlabAdsorptionSites(atoms, surface=Cu2O_111)
        >>> spg = SPG(atoms, adsorbate_species='SO2',
        ...           min_adsorbate_distance=1.5,
        ...           adsorption_sites=sas,
        ...           smart_skip=False, # Set this to False for oxides
        ...           enumerate_orientations=True,
        ...           trajectory='Cu2O_111_SO2_unique_configs.traj')
        >>> spg.run(action='add', num_act=1, unique=True)
        >>> images = read('Cu2O_111_SO2_unique_configs.traj', index=':')
        >>> view(images) 

    Output:

    .. image:: ../images/SystematicPatternGenerator3.gif
       :scale: 80 %
       :align: center

The OrderedPatternGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: OrderedPatternGenerator

        .. automethod:: get_site_groups

        .. automethod:: run

    **Example 1**                                                             

    The following example illustrates how to generate 50 unique 
    ordered adlayer patterns on a fcc111 NiCu surface slab with 
    possible adsorbates of C, N, O, OH with a repeating distance 
    of 5.026 Angstrom, where each structure is limited to have at 
    most 2 different adsorbate species, and the neighbor sites 
    around each occupied site must be removed: 

        >>> from acat.build.adlayer import OrderedPatternGenerator as OPG 
        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from ase.io import read
        >>> from ase.build import fcc111
        >>> from ase.visualize import view
        >>> atoms = fcc111('Ni', (4, 4, 4), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Cu'
        >>> atoms.center(axis=2)
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc111',
        ...                           allow_6fold=False,
        ...                           ignore_sites='bridge',
        ...                           surrogate_metal='Ni')
        >>> opg = OPG(atoms, adsorbate_species=['C', 'N', 'O', 'OH'],
        ...           surface='fcc111',
        ...           repeating_distance=5.026,
        ...           max_species=2,
        ...           adsorption_sites=sas,
        ...           remove_site_shells=1)
        >>> opg.run(max_gen=50, unique=True)
        >>> images = read('patterns.traj', index=':')
        >>> view(images)

    Output:

    .. image:: ../images/OrderedPatternGenerator1.gif                     
       :scale: 60 %
       :align: center

    **Example 2**                                                             

    The following example illustrates how to generate 50 unique 
    ordered adlayer patterns on a fcc100 NiCu surface slab with 
    possible adsorbates of C, N, O, OH with a repeating distance 
    of 5.026 Angstrom, where each structure is limited to have at 
    most 2 different adsorbate species, the 1st and 2nd neighbor 
    sites around each occupied site must be removed, and the sites
    are sorted according to the diagonal vector: 

        >>> from acat.build.adlayer import OrderedPatternGenerator as OPG
        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from ase.io import read
        >>> from ase.build import fcc100
        >>> from ase.visualize import view
        >>> atoms = fcc100('Ni', (4, 4, 4), vacuum=5.)
        ... for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Cu'
        >>> atoms.center(axis=2)
        >>> diagonal_vec = atoms[63].position - atoms[48].position
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc100',
        ...                           allow_6fold=False,
        ...                           ignore_sites=None,
        ...                           surrogate_metal='Ni')
        >>> opg = OPG(atoms, adsorbate_species=['C', 'N', 'O', 'OH'],
        ...           surface='fcc100',
        ...           repeating_distance=5.026,
        ...           max_species=2,
        ...           sorting_vector=diagonal_vec,
        ...           adsorption_sites=sas,
        ...           remove_site_shells=2)
        >>> opg.run(max_gen=50, unique=True)
        >>> images = read('patterns.traj', index=':')
        >>> view(images)

    Output:

    .. image:: ../images/OrderedPatternGenerator2.gif                     
       :scale: 60 %
       :align: center

The special_coverage_pattern function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: special_coverage_pattern

    **Example 1**

    To add a 0.5 ML CO adlayer pattern on a cuboctahedron:

        >>> from acat.build.adlayer import special_coverage_pattern as scp
        >>> from ase.cluster import Octahedron
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Au', length=9, cutoff=4)
        >>> atoms.center(vacuum=5.)
        >>> pattern = scp(atoms, adsorbate_species='CO', coverage=0.5)
        >>> view(pattern)

    Output:

    .. image:: ../images/special_coverage_pattern_1.png

    **Example 2**

    To add a 0.5 ML CO adlayer pattern on a fcc111 surface slab:

        >>> from acat.build.adlayer import special_coverage_pattern as scp
        >>> from ase.build import fcc111
        >>> from ase.visualize import view
        >>> atoms = fcc111('Cu', (8, 8, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> pattern = scp(atoms, adsorbate_species='CO',
        ...               coverage=0.5, surface='fcc111')
        >>> view(pattern)

    Output:

    .. image:: ../images/special_coverage_pattern_2.png

The max_dist_coverage_pattern function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: max_dist_coverage_pattern

    **Example 1**

    To add 0.33 ML CO to all fcc and hcp sites on an icosahedron:

        >>> from acat.build.adlayer import max_dist_coverage_pattern as maxdcp
        >>> from ase.cluster import Icosahedron
        >>> from ase.visualize import view
        >>> atoms = Icosahedron('Au', noshells=5)
        >>> atoms.center(vacuum=5.)
        >>> pattern = maxdcp(atoms, adsorbate_species='CO', 
        ...                  coverage=0.33, site_types=['fcc','hcp'])
        >>> view(pattern)

    Output:

    .. image:: ../images/max_dist_coverage_pattern_1.png
       :scale: 55 %
       :align: center

    **Example 2**

    To add N and O (3 : 1 ratio) to all 3fold sites on a bcc110 surface 
    slab: 

        >>> from acat.build.adlayer import max_dist_coverage_pattern as maxdcp
        >>> from ase.build import bcc110
        >>> from ase.visualize import view
        >>> atoms = bcc110('Mo', (8, 8, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> pattern = maxdcp(atoms, adsorbate_species=['N','O'],
        ...                  species_probabilities={'N': 0.75, 'O':0.25},
        ...                  coverage=1, site_types='3fold', surface='bcc110')
        >>> view(pattern)

    Output:

    .. image:: ../images/max_dist_coverage_pattern_2.png
       :scale: 55 %
       :align: center

The min_dist_coverage_pattern function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autofunction:: min_dist_coverage_pattern

    **Example 1**

    To add CO randomly onto a cuboctahedron with a minimum adsorbate 
    distance of 5 Angstrom:

        >>> from acat.build.adlayer import min_dist_coverage_pattern as mindcp
        >>> from ase.cluster import Octahedron
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Au', length=9, cutoff=4)
        >>> atoms.center(vacuum=5.)
        >>> pattern = mindcp(atoms, adsorbate_species='CO', 
        ...                  min_adsorbate_distance=5.)
        >>> view(pattern)

    Output:

    .. image:: ../images/min_dist_coverage_pattern_1.png

    **Example 2**

    To add C, N, O randomly onto a hcp0001 surface slab with probabilities 
    of 0.25, 0.25, 0.5, respectively, and a minimum adsorbate distance of 
    2 Angstrom:

        >>> from acat.build.adlayer import min_dist_coverage_pattern as mindcp
        >>> from ase.build import hcp0001
        >>> from ase.visualize import view
        >>> atoms = hcp0001('Ru', (8, 8, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> pattern = mindcp(atoms, adsorbate_species=['C','N','O'],
        ...                  species_probabilities={'C': 0.25, 
        ...                                         'N': 0.25, 
        ...                                         'O': 0.5},
        ...                  surface='hcp0001',
        ...                  min_adsorbate_distance=2.)
        >>> view(pattern)

    Output:

    .. image:: ../images/min_dist_coverage_pattern_2.png

    **Example 3**

    To add H, OH and H2O randomly onto a fcc100 Ni2Cu surface slab on both top 
    and bottom interfaces ( :download:`bulk water <../tests/water_bulk.xyz>` 
    in between) with probabilities of 0.25, 0.25, 0.5, respectively, and a 
    minimum adsorbate distance of 2 Angstrom:

        >>> from acat.build.adlayer import min_dist_coverage_pattern as mindcp                       
        >>> from ase.io import read
        >>> from ase.build import fcc100 
        >>> from ase.visualize import view
        >>> water_bulk = read('water_bulk.xyz')
        >>> water_bulk.center(vacuum=11., axis=2)
        >>> slab = fcc100('Ni', (4, 4, 8), vacuum=9.5, periodic=True)
        >>> for atom in slab:
        ...     if atom.index % 3 == 0:
        ...         atom.symbol = 'Cu'
        >>> slab.translate(-slab.cell[2] / 2)
        >>> slab.wrap()
        >>> atoms = slab + water_bulk
        >>> pattern = mindcp(atoms, adsorbate_species=['H','OH','OH2'],
        ...                  species_probabilities={'H': 0.25,
        ...                                         'OH': 0.25,
        ...                                         'OH2': 0.5},
        ...                  surface='fcc100',
        ...                  min_adsorbate_distance=2.,
        ...                  both_sides=True,
        ...                  surrogate_metal='Ni')
        >>> view(pattern) 

    Output:

    .. image:: ../images/min_dist_coverage_pattern_3.png

Generate alloy chemical orderings
---------------------------------

.. automodule:: acat.build.ordering
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: SymmetricClusterOrderingGenerator, SymmetricSlabOrderingGenerator, RandomOrderingGenerator

The SymmetricClusterOrderingGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: SymmetricClusterOrderingGenerator

        .. automethod:: get_sorted_indices

        .. automethod:: get_groups

        .. automethod:: run

    **Example 1**

    To generate 100 symmetric chemical orderings for truncated
    octahedral NiPt nanoalloys with spherical symmetry:

        >>> from acat.build.ordering import SymmetricClusterOrderingGenerator as SCOG
        >>> from ase.cluster import Octahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', length=8, cutoff=3)
        >>> scog = SCOG(atoms, elements=['Ni', 'Pt'], symmetry='spherical')
        >>> scog.run(max_gen=100, verbose=True)
        >>> images = read('orderings.traj', index=':') 
        >>> view(images)

    Output:

        | 10 symmetry-equivalent groups classified
        | 100 symmetric chemical orderings generated 

    .. image:: ../images/SymmetricClusterOrderingGenerator1.gif
       :scale: 60 %
       :align: center

    **Example 2**
               
    To systematically generate 50 symmetric chemical orderings for 
    quaternary truncated octahedral Ni0.4Cu0.3Pt0.2Au0.1 nanoalloys 
    with mirror circular symmetry:

        >>> from acat.build.ordering import SymmetricClusterOrderingGenerator as SCOG
        >>> from ase.cluster import Octahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', 7, 2)
        >>> scog = SCOG(atoms, elements=['Ni', 'Cu', 'Pt', 'Au'],
        ...             symmetry='mirror_circular',
        ...             composition={'Ni': 0.4, 'Cu': 0.3, 'Pt': 0.2, 'Au': 0.1})
        >>> scog.run(max_gen=50, mode='systematic', verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 25 symmetry-equivalent groups classified
        | 50 symmetric chemical orderings generated

    .. image:: ../images/SymmetricClusterOrderingGenerator2.gif
       :scale: 60 %
       :align: center

    **Example 3**

    To stochastically generate 50 symmetric chemical orderings for 
    quaternary truncated octahedral Ni0.4Cu0.3Pt0.2Au0.1 nanoalloys 
    with mirror circular symmetry:

        >>> from acat.build.ordering import SymmetricClusterOrderingGenerator as SCOG
        >>> from ase.cluster import Octahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', 7, 2)
        >>> scog = SCOG(atoms, elements=['Ni', 'Cu', 'Pt', 'Au'],
        ...             symmetry='mirror_circular',
        ...             composition={'Ni': 0.4, 'Cu': 0.3, 'Pt': 0.2, 'Au': 0.1})
        >>> scog.run(max_gen=50, mode='stochastic', verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 25 symmetry-equivalent groups classified
        | 50 symmetric chemical orderings generated

    .. image:: ../images/SymmetricClusterOrderingGenerator3.gif
       :scale: 60 %
       :align: center

    **Example 4**

    Sometimes it is also useful to get the structure of each group. 
    For instance, to visualize the concentric shells of a truncated 
    octahedral nanoparticle:

        >>> from acat.build.ordering import SymmetricClusterOrderingGenerator as SCOG
        >>> from ase.cluster import Octahedron
        >>> from ase.visualize import view
        >>> atoms = Octahedron('Ni', 12, 5)
        >>> scog = SCOG(atoms, elements=['Ni', 'Pt'], symmetry='concentric')
        >>> groups = scog.get_groups()
        >>> images = [atoms[g] for g in groups]
        >>> view(images)

    Output:

    .. image:: ../images/SymmetricClusterOrderingGenerator4.gif
       :scale: 60 %
       :align: center

The SymmetricSlabOrderingGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: SymmetricSlabOrderingGenerator

        .. automethod:: get_groups

        .. automethod:: run

    **Example 1**

    To stochastically generate 20 chemical orderings with vertical 
    mirror plane symmetry w.r.t. the bisect vector [11.200, 6.467] 
    for binary NixPt1-x fcc111 surface slabs without duplicates:

        >>> from acat.build.ordering import SymmetricSlabOrderingGenerator as SSOG
        >>> from ase.build import fcc111
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> import numpy as np
        >>> atoms = fcc111('Ni', (4, 4, 5), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> ssog = SSOG(atoms, elements=['Ni', 'Pt'],
        ...             symmetry='vertical_mirror',
        ...             bisect_vector=np.array([11.200, 6.467]))
        >>> ssog.run(max_gen=20, mode='stochastic', unique=True, verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 50 symmetry-equivalent groups classified           
        | 20 symmetric chemical orderings generated 

    .. image:: ../images/SymmetricSlabOrderingGenerator1.gif
       :scale: 60 %
       :align: center

    **Example 2**

    To stochastically generate 50 chemical orderings with 
    translational symmetry for ternary NixPtyAu1-x-y fcc111 
    surface slabs:

        >>> from acat.build.ordering import SymmetricSlabOrderingGenerator as SSOG 
        >>> from ase.build import fcc111
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = fcc111('Ni', (6, 6, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> ssog = SSOG(atoms, elements=['Ni', 'Pt', 'Au'],
        ...             symmetry='translational',
        ...             repeating_size=(3, 3)) 
        >>> ssog.run(max_gen=50, mode='stochastic', verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 16 symmetry-equivalent groups classified           
        | 50 symmetric chemical orderings generated 

    .. image:: ../images/SymmetricSlabOrderingGenerator2.gif
       :scale: 60 %
       :align: center

    **Example 3**
               
    To systematically generate 50 chemical orderings with 
    translational symmetry for Ni0.75Pt0.25 fcc110 surface  
    slabs:

        >>> from acat.build.ordering import SymmetricSlabOrderingGenerator as SSOG 
        >>> from ase.build import fcc110
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = fcc110('Ni', (4, 4, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> ssog = SSOG(atoms, elements=['Ni', 'Pt'],
        ...             symmetry='translational', 
        ...             composition={'Ni': 0.75, 'Pt': 0.25},
        ...             repeating_size=(2, 2)) 
        >>> ssog.run(max_gen=50, mode='systematic', verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 16 symmetry-equivalent groups classified
        | 50 symmetric chemical orderings generated

    .. image:: ../images/SymmetricSlabOrderingGenerator3.gif
       :scale: 60 %
       :align: center

    **Example 4**

    To stochastically generate 50 chemical orderings with 
    translational symmetry for Ni0.75Pt0.25 fcc110 surface 
    slabs:

        >>> from acat.build.ordering import SymmetricSlabOrderingGenerator as SSOG 
        >>> from ase.build import fcc110
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = fcc110('Ni', (4, 4, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> ssog = SSOG(atoms, elements=['Ni', 'Pt'],
        ...             symmetry='translational',
        ...             composition={'Ni': 0.75, 'Pt': 0.25},
        ...             repeating_size=(2, 2)) 
        >>> ssog.run(max_gen=50, mode='stochastic', verbose=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

        | 16 symmetry-equivalent groups classified
        | 50 symmetric chemical orderings generated

    .. image:: ../images/SymmetricSlabOrderingGenerator4.gif
       :scale: 60 %
       :align: center

The RandomOrderingGenerator class
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. autoclass:: RandomOrderingGenerator       

        .. automethod:: randint_with_sum

        .. automethod:: random_split_indices

        .. automethod:: run

    **Example 1**

    To generate 50 random chemical orderings for icosahedral 
    Ni0.5Pt0.2Au0.3 nanoalloys:

        >>> from acat.build.ordering import RandomOrderingGenerator as ROG
        >>> from ase.cluster import Icosahedron
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = Icosahedron('Ni', noshells=4)
        >>> rog = ROG(atoms, elements=['Ni', 'Pt', 'Au'], 
        ...           composition={'Ni': 0.5, 'Pt': 0.2, 'Au': 0.3})
        >>> rog.run(num_gen=50)
        >>> images = read('orderings.traj', index=':') 
        >>> view(images)

    Output:

    .. image:: ../images/RandomOrderingGenerator1.gif
       :scale: 60 %
       :align: center

    **Example 2**

    To generate 50 random chemical orderings for Pt0.5Au0.5 
    fcc111 surface slabs without duplicates:

        >>> from acat.build.ordering import RandomOrderingGenerator as ROG 
        >>> from ase.build import fcc111
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> atoms = fcc111('Ni', (4, 4, 4), vacuum=5.)
        >>> atoms.center(axis=2)
        >>> rog = ROG(atoms, elements=['Pt', 'Au'],
        ...           composition={'Pt': 0.5, 'Au': 0.5})
        >>> rog.run(num_gen=50, unique=True)
        >>> images = read('orderings.traj', index=':')
        >>> view(images)

    Output:

    .. image:: ../images/RandomOrderingGenerator2.gif
       :scale: 60 %
       :align: center

    **Example 3**

    Although the code is written for metal alloys, it can also
    be used to generate random mixed metal oxides with some
    simple work around. Below is an example of generating 50
    random equiatomic anatase Ti0.2Pt0.2Pd0.2Ag0.2Au0.2O2(101) 
    high-entropy oxide surfaces:

        >>> from acat.build.ordering import RandomOrderingGenerator as ROG
        >>> from ase.spacegroup import crystal
        >>> from ase.build import surface
        >>> from ase.io import read
        >>> from ase.visualize import view
        >>> a, c = 3.862, 9.551
        >>> TiO2 = crystal(['Ti', 'O'], basis=[(0 ,0, 0), (0, 0, 0.208)],
        ...                spacegroup=141, cellpar=[a, a, c, 90, 90, 90])
        >>> atoms = surface(TiO2, (1, 0, 1), 4, vacuum=5)
        >>> atoms *= (1,2,1)
        >>> atoms.center(axis=2)
        >>> # Distinguish metal and oxygen atoms
        >>> metal_ids, oxygen_ids = [], []
        >>> for i, atom in enumerate(atoms):
        ...     if atom.symbol == 'O':
        ...         oxygen_ids.append(i)
        ...     else:
        ...         metal_ids.append(i)
        >>> metal_atoms, oxygen_atoms = atoms[metal_ids], atoms[oxygen_ids]
        >>> # Prepare sorted_ids for sorting atomic indices back to original order
        >>> sorted_ids = [0] * len(atoms)
        >>> for k, v in enumerate(metal_ids + oxygen_ids):
        ...     sorted_ids[v] = k
        >>> rog = ROG(metal_atoms, elements=['Ti','Pt','Pd','Ag','Au'],
        ...           composition={'Ti':0.2,'Pt':0.2,'Pd':0.2,'Ag':0.2,'Au':0.2})
        >>> rog.run(num_gen=50)
        >>> metal_images = read('orderings.traj', index=':')
        >>> images = [(a + oxygen_atoms)[sorted_ids] for a in metal_images]
        >>> view(images)

    Output:

    .. image:: ../images/RandomOrderingGenerator3.gif
       :scale: 60 %
       :align: center
