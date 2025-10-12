#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Operators that work on slabs. Allowed compositions are respected.
Identical indexing of the slabs are assumed for the cut-splice operator."""
import random
from operator import itemgetter
from collections import Counter
from itertools import permutations
import numpy as np
from ase.ga.offspring_creator import OffspringCreator


def permute2(atoms):
    i1 = random.choice(range(len(atoms)))
    sym1 = atoms[i1].symbol
    i2 = random.choice([a.index for a in atoms if a.symbol != sym1])
    atoms[i1].symbol = atoms[i2].symbol
    atoms[i2].symbol = sym1


def replace_element(atoms, element_out, element_in):
    syms = np.array(atoms.get_chemical_symbols())
    syms[syms == element_out] = element_in
    atoms.set_chemical_symbols(syms)


def get_add_remove_lists(**kwargs):
    to_add, to_rem = [], []
    for s, amount in kwargs.items():
        if amount > 0:
            to_add.extend([s] * amount)
        elif amount < 0:
            to_rem.extend([s] * abs(amount))
    return to_add, to_rem


def get_minority_element(atoms):
    counter = Counter(atoms.get_chemical_symbols())
    return sorted(counter.items(), key=itemgetter(1), reverse=False)[0][0]


def minority_element_segregate(atoms, layer_tag=1):
    """Move the minority alloy element to the layer specified by the layer_tag,
    Atoms object should contain atoms with the corresponding tag."""
    sym = get_minority_element(atoms)
    layer_indices = set([a.index for a in atoms if a.tag == layer_tag])
    minority_indices = set([a.index for a in atoms if a.symbol == sym])
    change_indices = minority_indices - layer_indices
    in_layer_not_sym = list(layer_indices - minority_indices)
    random.shuffle(in_layer_not_sym)
    if len(change_indices) > 0:
        for i, ai in zip(change_indices, in_layer_not_sym):
            atoms[i].symbol = atoms[ai].symbol
            atoms[ai].symbol = sym


def same_layer_comp(atoms):
    unique_syms, comp = np.unique(sorted(atoms.get_chemical_symbols()),
                                  return_counts=True)
    l = get_layer_comps(atoms)
    sym_dict = dict((s, int(np.array(c) / len(l)))
                    for s, c in zip(unique_syms, comp))
    for la in l:
        correct_by = sym_dict.copy()
        lcomp = dict(
            zip(*np.unique([atoms[i].symbol for i in la], return_counts=True)))
        for s, num in lcomp.items():
            correct_by[s] -= num
        to_add, to_rem = get_add_remove_lists(**correct_by)
        for add, rem in zip(to_add, to_rem):
            ai = random.choice([i for i in la if atoms[i].symbol == rem])
            atoms[ai].symbol = add


def get_layer_comps(atoms, eps=1e-2):
    lc = []
    old_z = np.inf
    for z, ind in sorted([(a.z, a.index) for a in atoms]):
        if abs(old_z - z) < eps:
            lc[-1].append(ind)
        else:
            lc.append([ind])
        old_z = z

    return lc


def get_ordered_composition(syms, pools=None):
    if pools is None:
        pool_index = dict((sym, 0) for sym in set(syms))
    else:
        pool_index = {}
        for sym in set(syms):
            for i, pool in enumerate(pools):
                if sym in pool:
                    pool_index[sym] = i
    syms = [(sym, pool_index[sym], c) if sym in pool 
            else (sym, 10000, c) for sym, c in 
            zip(*np.unique(syms, return_counts=True))]
    unique_syms, pn, comp = zip(
        *sorted(syms, key=lambda k: (k[1] - k[2], k[0])))
    return (unique_syms, pn, comp)


def dummy_func(*args):
    return


class SlabOperator(OffspringCreator):
    def __init__(self, verbose=False, num_muts=1,
                 allowed_compositions=None,
                 distribution_correction_function=None,
                 filter_function=None,
                 element_pools=None):
        OffspringCreator.__init__(self, verbose, num_muts=num_muts)

        self.allowed_compositions = allowed_compositions
        self.element_pools = element_pools
        if self.element_pools is not None:
            if not any(isinstance(i, list) for i in self.element_pools):
                self.element_pools = [self.element_pools]
        if distribution_correction_function is None:
            self.dcf = dummy_func
        else:
            self.dcf = distribution_correction_function
        self.ff = filter_function
        # Number of different elements i.e. [2, 1] if len(element_pools) == 2
        # then 2 different elements in pool 1 is allowed but only 1 from pool 2

    def get_symbols_to_use(self, syms):
        """Get the symbols to use for the offspring candidate. The returned
        list of symbols will respect self.allowed_compositions"""
        if self.allowed_compositions is None:
            return syms

        unique_syms, counts = np.unique(syms, return_counts=True)
        comp, unique_syms = zip(*sorted(zip(counts, unique_syms),
                                        reverse=True))

        for cc in self.allowed_compositions:
            comp += (0,) * (len(cc) - len(comp))
            if comp == tuple(sorted(cc)):
                return syms

        comp_diff = self.get_closest_composition_diff(comp)
        to_add, to_rem = get_add_remove_lists(
            **dict(zip(unique_syms, comp_diff)))
        for add, rem in zip(to_add, to_rem):
            tbc = [i for i in range(len(syms)) if syms[i] == rem]
            ai = random.choice(tbc)
            syms[ai] = add
        return syms

    def get_add_remove_elements(self, syms):
        if self.element_pools is None or self.allowed_compositions is None:
            return [], []
        unique_syms, pool_number, comp = get_ordered_composition(
            syms, self.element_pools)
        stay_comp, stay_syms = [], []
        add_rem = {}
        per_pool = len(self.allowed_compositions[0]) / len(self.element_pools)
        pool_count = np.zeros(len(self.element_pools), dtype=int)
        for pn, num, sym in zip(pool_number, comp, unique_syms):
            pool_count[pn] += 1
            if pool_count[pn] <= per_pool:
                stay_comp.append(num)
                stay_syms.append(sym)
            else:
                add_rem[sym] = -num
        # collect elements from individual pools

        diff = self.get_closest_composition_diff(stay_comp)
        add_rem.update(dict((s, c) for s, c in zip(stay_syms, diff)))
        return get_add_remove_lists(**add_rem)

    def get_closest_composition_diff(self, c):
        comp = np.array(c)
        mindiff = 1e10
        allowed_list = list(self.allowed_compositions)
        random.shuffle(allowed_list)
        for ac in allowed_list:
            diff = self.get_composition_diff(comp, ac)
            numdiff = sum([abs(i) for i in diff])
            if numdiff < mindiff:
                mindiff = numdiff
                ccdiff = diff
        return ccdiff

    def get_composition_diff(self, c1, c2):
        difflen = len(c1) - len(c2)
        if difflen > 0:
            c2 += (0,) * difflen
        return np.array(c2) - c1

    def get_possible_mutations(self, a):
        unique_syms, comp = np.unique(sorted(a.get_chemical_symbols()),
                                      return_counts=True)
        min_num = min([i for i in np.ravel(list(self.allowed_compositions))
                       if i > 0])
        muts = set()
        for i, n in enumerate(comp):
            if n != 0:
                muts.add((unique_syms[i], n))
            if n % min_num >= 0:
                for j in range(1, n // min_num):
                    muts.add((unique_syms[i], min_num * j))
        return list(muts)

    def get_all_element_mutations(self, a):
        """Get all possible mutations for the supplied atoms object given
        the element pools."""
        muts = []
        symset = set(a.get_chemical_symbols())
        for sym in symset:
            for pool in self.element_pools:
                if sym in pool:
                    muts.extend([(sym, s) for s in pool if s not in symset])
        return muts

    def finalize_individual(self, indi):
        atoms_string = ''.join(indi.get_chemical_symbols())
        indi.info['key_value_pairs']['atoms_string'] = atoms_string
        return OffspringCreator.finalize_individual(self, indi)


class CutSpliceSlabCrossover(SlabOperator):
    def __init__(self, allowed_compositions=None, 
                 element_pools=None, 
                 allowed_indices=None, 
                 verbose=False,
                 num_muts=1, 
                 tries=1000, 
                 min_ratio=0.25,
                 distribution_correction_function=None,
                 filter_function=None):
        SlabOperator.__init__(self, verbose, num_muts,
                              allowed_compositions,
                              distribution_correction_function,
                              element_pools=element_pools,
                              filter_function=filter_function)

        self.allowed_indices = allowed_indices
        self.tries = tries
        self.min_ratio = min_ratio
        self.descriptor = 'CutSpliceSlabCrossover'

    def get_new_individual(self, parents):
        f0, m0 = parents
        if self.allowed_indices is None:
            f, m = f0.copy(), m0.copy()
        else:
            if any(isinstance(i, list) for i in self.allowed_indices):
                self.allowed_indices = random.choice(self.allowed_indices)
            f, m = f0[self.allowed_indices], m0[self.allowed_indices]

        fail = True
        while fail:
            indi = self.initialize_individual(f, self.operate(f, m)) 
            if self.allowed_indices is None:
                tmp = indi
            else:
                tmp = f0.copy()
                tmp.symbols[self.allowed_indices] = indi.symbols
            if (self.ff is None) or self.ff(tmp):
                fail = False
                info = indi.info.copy()
                indi = tmp.copy()
                indi.info = info

        indi.info['data']['parents'] = [i.info['confid'] for i in parents]
        parent_message = ': Parents {0} {1}'.format(f.info['confid'],
                                                    m.info['confid'])
        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def operate(self, f, m):
        child = f.copy()
        fp = f.positions
        ma = np.max(fp.transpose(), axis=1)
        mi = np.min(fp.transpose(), axis=1)

        for _ in range(self.tries):
            # Find center point of cut
            rv = [random.random() for _ in range(3)]  # random vector
            midpoint = (ma - mi) * rv + mi

            # Determine cut plane
            theta = random.random() * 2 * np.pi  # 0,2pi
            phi = random.random() * np.pi  # 0,pi
            e = np.array((np.sin(phi) * np.cos(theta),
                          np.sin(theta) * np.sin(phi),
                          np.cos(phi)))

            # Cut structures
            d2fp = np.dot(fp - midpoint, e)
            fpart = d2fp > 0
            ratio = float(np.count_nonzero(fpart)) / len(f)
            if ratio < self.min_ratio or ratio > 1 - self.min_ratio:
                continue
            syms = np.where(fpart, f.get_chemical_symbols(),
                            m.get_chemical_symbols())
            dists2plane = abs(d2fp)

            # Correct the composition
            # What if only one element pool is represented in the offspring
            to_add, to_rem = self.get_add_remove_elements(syms)

            # Change elements closest to the cut plane
            for add, rem in zip(to_add, to_rem):
                tbc = [(dists2plane[i], i)
                       for i in range(len(syms)) if syms[i] == rem]
                ai = sorted(tbc)[0][1]
                syms[ai] = add

            child.set_chemical_symbols(syms)
            break

        self.dcf(child)

        return child


class RandomCompositionMutation(SlabOperator):
    """Change the current composition to another of the allowed compositions.
    The allowed compositions should be input in the same order as the element pools,
    for example:
    element_pools = [['Au', 'Cu'], ['In', 'Bi']]
    allowed_compositions = [(6, 2), (5, 3)]
    means that there can be 5 or 6 Au and Cu, and 2 or 3 In and Bi.
    """

    def __init__(self, verbose=False, num_muts=1, 
                 element_pools=None,
                 allowed_compositions=None,
                 allowed_indices=None,
                 distribution_correction_function=None, 
                 filter_function=None):
        SlabOperator.__init__(self, verbose, num_muts,
                              allowed_compositions,
                              distribution_correction_function,
                              element_pools=element_pools,
                              filter_function=filter_function)
        self.allowed_indices = allowed_indices

        self.descriptor = 'RandomCompositionMutation'

    def get_new_individual(self, parents):
        f0 = parents[0]
        if self.allowed_indices is None: 
            f = f0.copy()
        else:
            if any(isinstance(i, list) for i in self.allowed_indices):
                self.allowed_indices = random.choice(self.allowed_indices)
            f = f0[self.allowed_indices]

        parent_message = ': Parent {0}'.format(f.info['confid'])

        if self.allowed_compositions is None:
            if len(set(f.get_chemical_symbols())) == 1:
                if self.element_pools is None:
                    # We cannot find another composition without knowledge of
                    # other allowed elements or compositions
                    return None, self.descriptor + parent_message

        # Do the operation
        fail = True
        while fail:
            indi = self.initialize_individual(f, self.operate(f))
            if self.allowed_indices is None:
                tmp = indi
            else:
                tmp = f0.copy()
                tmp.symbols[self.allowed_indices] = indi.symbols
            if (self.ff is None) or self.ff(tmp):
                fail = False
                info = indi.info.copy()
                indi = tmp.copy()
                indi.info = info

        if 'data' in f.info:
            if 'groups' in f.info['data']:
                indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [i.info['confid'] for i in parents]

        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def operate(self, atoms):
        allowed_comps = self.allowed_compositions
        if allowed_comps is None:
            n_elems = len(set(atoms.get_chemical_symbols()))
            n_atoms = len(atoms)
            allowed_comps = [c for c in permutations(range(1, n_atoms), n_elems)
                             if sum(c) == n_atoms]

        # Sorting the composition to have the same order as in element_pools
        syms = atoms.get_chemical_symbols()
        unique_syms, _, comp = get_ordered_composition(syms, self.element_pools)

        # Choose the composition to change to
        for i, allowed in enumerate(allowed_comps):
            if comp == tuple(allowed):
                allowed_comps = np.delete(allowed_comps, i, axis=0)
                break
        chosen = random.randint(0, len(allowed_comps) - 1)
        comp_diff = self.get_composition_diff(comp, allowed_comps[chosen])

        # Get difference from current composition
        to_add, to_rem = get_add_remove_lists(
            **dict(zip(unique_syms, comp_diff)))

        # Correct current composition
        syms = atoms.get_chemical_symbols()
        for add, rem in zip(to_add, to_rem):
            tbc = [i for i in range(len(syms)) if syms[i] == rem]
            ai = random.choice(tbc)
            syms[ai] = add

        atoms.set_chemical_symbols(syms)
        self.dcf(atoms)

        return atoms


class RandomSlabMutation(SlabOperator):
    def __init__(self, verbose=False, num_muts=1,
                 element_pools=None,
                 element_probabilities=None,
                 allowed_indices=None,
                 distribution_correction_function=None,
                 filter_function=None,
                 from_element=None,
                 to_element=None):
        SlabOperator.__init__(self, verbose, num_muts, None,
                              distribution_correction_function,
                              filter_function=filter_function,
                              element_pools=element_pools)
        self.element_probabilities = element_probabilities
        self.allowed_indices = allowed_indices
        self.from_element = from_element
        self.to_element = to_element

        self.descriptor = 'RandomSlabMutation'

    def get_new_individual(self, parents, return_mutated_elements=False):
        f0 = parents[0]
        if (self.allowed_indices is None) and (self.element_pools is None):
            f = f0.copy()
        else:
            if self.allowed_indices is None:
                self.allowed_indices = list(range(len(f0)))
            else:
                if any(isinstance(i, list) for i in self.allowed_indices):
                    self.allowed_indices = random.choice(self.allowed_indices) 
            if self.element_pools is not None:
                flat_pool = {e for pool in self.element_pools for e in pool}
                self.allowed_indices = [i for i in self.allowed_indices if 
                                        f0[i].symbol in flat_pool]
            f = f0[self.allowed_indices]

        indi = self.initialize_individual(f, f)
        fail = True
        while fail:
            if return_mutated_elements:
                indi, mutated_elements = self.operate(
                        indi, self.element_pools, True)
            else:
                indi = self.operate(indi, self.element_pools, False)
                mutated_elements = None
            if self.allowed_indices is None:
                tmp = indi
            else:
                tmp = f0.copy()
                tmp.symbols[self.allowed_indices] = indi.symbols
            if (self.ff is None) or self.ff(tmp):
                fail = False
                info = indi.info.copy()
                indi = tmp.copy()
                indi.info = info

        if 'data' in f.info:
            if 'groups' in f.info['data']:
                indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [i.info['confid'] for i in parents]
        parent_message = ': Parent {0}'.format(f.info['confid'])

        if return_mutated_elements:
            return (self.finalize_individual(indi),
                    self.descriptor + parent_message,
                    mutated_elements)

        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def operate(self, atoms, element_pools, return_mutated_elements=False):
        # Do the operation
        for _ in range(self.num_muts):
            if self.from_element is None:
                tbm = random.choice(range(len(atoms)))
                tbm_sym = atoms[tbm].symbol
            else:
                tbm_sym = self.from_element
                options = [i for i in range(len(atoms)) if atoms[i].symbol == tbm_sym]
                tbm = random.choice(options)
            if element_pools is not None:
                to_element_pool = list({e for pool in element_pools for e in pool 
                                       if (tbm_sym in pool) and (e != tbm_sym)})
            else:
                to_element_pool = [e for e in set(atoms.symbols) if e != tbm_sym]
            if self.to_element is None:
                if (self.element_probabilities is None) or any(
                e not in self.element_probabilities for e in to_element_pool):
                    sym = random.choice(to_element_pool)
                else:
                    composition_rsv = {k: v for k, v in self.element_probabilities.items() 
                                       if k in to_element_pool}
                    composition_rsv_p = np.array(list(composition_rsv.values()))
                    sym = np.random.choice(np.array(list(composition_rsv.keys())), 
                                           p=composition_rsv_p/composition_rsv_p.sum())
            else:
                sym = self.to_element
            atoms[tbm].symbol = sym 
        self.dcf(atoms)

        if return_mutated_elements:
            return atoms, [tbm_sym, sym]

        return atoms


class RandomSlabPermutation(SlabOperator):
    def __init__(self, verbose=False, num_muts=1,
                 element_pools=None,
                 allowed_indices=None,
                 distribution_correction_function=None,
                 filter_function=None):
        SlabOperator.__init__(self, verbose, num_muts, None,
                              distribution_correction_function,
                              filter_function=filter_function,
                              element_pools=element_pools)
        self.allowed_indices = allowed_indices

        self.descriptor = 'RandomSlabPermutation'

    def get_new_individual(self, parents):
        f0 = parents[0]
        if (self.allowed_indices is None) and (self.element_pools is None): 
            f = f0.copy()
        else:
            if self.allowed_indices is None:
                self.allowed_indices = list(range(len(f0)))
            else:
                if any(isinstance(i, list) for i in self.allowed_indices):
                    allowed_indices = [idxs for idxs in self.allowed_indices if 
                                       len(set(f0[idxs].get_chemical_symbols())) > 1]
                    if not allowed_indices:
                        return None, '{0} not possible in {1}'.format(self.descriptor,
                                                                      f0.info['confid'])
                    self.allowed_indices = random.choice(allowed_indices)
            if self.element_pools is not None:
                element_pools = [pool for pool in self.element_pools if not                
                                 set(pool).isdisjoint(set(f0.symbols))]
                element_pool = random.choice([pool for pool in element_pools if not
                        set(f0.symbols[self.allowed_indices]).isdisjoint(set(pool))])
                self.allowed_indices = [i for i in self.allowed_indices if 
                                        f0[i].symbol in element_pool]       
            f = f0[self.allowed_indices]

        # Permutation only makes sense if two different elements are present
        if len(set(f.get_chemical_symbols())) == 1:
            if self.allowed_indices is None: 
                f = f0.copy()
            else:
                f = f0[self.allowed_indices]
            if len(set(f.get_chemical_symbols())) == 1:
                return None, '{0} not possible in {1}'.format(self.descriptor,
                                                              f.info['confid'])

        indi = self.initialize_individual(f, f)
        fail = True
        while fail:
            indi = self.operate(indi)
            if self.allowed_indices is None:
                tmp = indi
            else:
                tmp = f0.copy()
                tmp.symbols[self.allowed_indices] = indi.symbols
            if (self.ff is None) or self.ff(tmp):
                fail = False
                info = indi.info.copy()
                indi = tmp.copy()
                indi.info = info

        if 'data' in f.info:
            if 'groups' in f.info['data']:
                indi.info['data']['groups'] = f.info['data']['groups']
        indi.info['data']['parents'] = [i.info['confid'] for i in parents]
        parent_message = ': Parent {0}'.format(f.info['confid'])

        return (self.finalize_individual(indi),
                self.descriptor + parent_message)

    def operate(self, atoms):
        # Do the operation
        for _ in range(self.num_muts):
            permute2(atoms)
        self.dcf(atoms)

        return atoms
