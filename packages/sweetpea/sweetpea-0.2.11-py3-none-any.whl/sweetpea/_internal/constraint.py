"""This module provides constraints for CNF generation."""

import operator as op
from abc import abstractmethod
from copy import deepcopy
from typing import List, Tuple, Any, Union, cast, Dict, Callable, Optional
from itertools import chain, product
from math import ceil
import inspect

from sweetpea._internal.base_constraint import Constraint
from sweetpea._internal.iter import chunk, chunk_list
from sweetpea._internal.block import Block
from sweetpea._internal.cross_block import MultiCrossBlockRepeat
from sweetpea._internal.backend import LowLevelRequest, BackendRequest
from sweetpea._internal.logic import If, Iff, And, Or, Not
from sweetpea._internal.primitive import DerivedFactor, DerivedLevel, Factor, Level, SimpleLevel, ContinuousFactor
from sweetpea._internal.argcheck import argcheck, make_istuple
from sweetpea._internal.weight import combination_weight
from sweetpea._internal.beforestart import BeforeStart

def validate_factor(block: Block, factor: Factor) -> None:
    if not block.has_factor(factor):
        raise ValueError(("A factor with name '{}' wasn't found in the design. "
                          "Are you sure the factor was included, and that the name is spelled "
                          "correctly?").format(factor.name))

def validate_factor_and_level(block: Block, factor: Factor, level: Union[SimpleLevel, DerivedLevel]) -> None:
    validate_factor(block, factor)

    if not level in factor:
        raise ValueError(("A level with name '{}' wasn't found in the '{}' factor").format(
                              level.name,
                              factor.name))


class Consistency(Constraint):
    """This constraint ensures that only one level of each factor is 'on' at a
    time. So for instance in the experiment::

        color = Factor("color", ["red", "blue"])
        text  = Factor("text",  ["red", "blue"])
        design = crossing = [color, text, conFactor]
        experiment   = fully_cross_block(design, crossing, [])

    The first trial is represented by the boolean vars ``[1, 2, 3, 4]``:

    - 1 is true iff the trial is color:red
    - 2 is true iff the trial is color:blue
    - 3 is true iff the trial is text:red
    - 4 is true iff the trial is text:blue

    The second trial is represented by the boolean vars ``[5-8]``, the third by
    ``[9-12]``, the fourth by ``[13-16]``. So this desugaring applies the
    following constraints::

        sum(1, 2) EQ 1
        sum(3, 4) EQ 1
        sum(5, 6) EQ 1
        ...
        sum(15, 16) EQ 1
    """

    def validate(self, block: Block) -> None:
        pass

    @staticmethod
    def apply(block: Block, backend_request: BackendRequest) -> None:
        next_var = 1
        for _ in range(block.trials_per_sample()):
            for f in filter(lambda f: not f.has_complex_window, block.act_design):
                number_of_levels = len(f.levels)
                new_request = LowLevelRequest("EQ", 1, list(range(next_var, next_var + number_of_levels)))
                backend_request.ll_requests.append(new_request)
                next_var += number_of_levels

        for f in filter(lambda f: f.has_complex_window, block.act_design):
            variables_for_factor = block.variables_for_factor(f)
            var_list = list(map(lambda n: n + next_var, range(variables_for_factor)))
            chunks = list(chunk_list(var_list, len(f.levels)))
            backend_request.ll_requests += list(map(lambda v: LowLevelRequest("EQ", 1, v), chunks))
            next_var += variables_for_factor

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        # conformance by construction in combinatoric
        return True

class Cross(Constraint):
    """We represent the fully crossed constraint by allocating additional
    boolean variables to represent each unique state. Only factors in crossing
    will contribute to the number of states (there may be factors in the design
    that aren't in the crossing).

    Continuing with the example from :class:`.Consistency`, we will represent
    the states::

        (color:red, text:red)
        (color:red, text:blue)
        (color:blue, text:red)
        (color:blue, text:blue)

    The steps taken are:

    1. Generate intermediate vars

        Using the fresh var counter, allocate ``numTrials * num_states`` new
        vars

    2. Entangle them with block vars

        Add to the CNF queue: ``toCNF(Iff(newVar, And(levels)))``, e.g., if the
        variable ``1`` indicates ``color:red``, the var ``3`` indicates
        ``text:red``, and the var ``25`` represents ``(color:red, text:red)``,
        do ``toCNF(Iff(25, And([1, 3])))``

    3. 1 hot the *states* e.g., 1 red circle, etc

        Same as :class:`.Consistency` above, collect all the state vars that
        represent each state & enforce that only one of those states is true,
        e.g., ``sum(25, 29, 33, 37) EQ 1`` (and 3 more of these for each of the
        other states).
    """

    def validate(self, block: Block) -> None:
        pass

    @staticmethod
    def apply(block: MultiCrossBlockRepeat, backend_request: BackendRequest) -> None:
        # Treat each crossing seperately, but they're related by shared variables, which
        # are the per-trial, per-level variables of factors used in multiple crossings
        for c in block.crossings:
            fresh = backend_request.fresh

            crossing_size = block.crossing_size(c)
            preamble_size = block.preamble_size(c)
            crossing_weight = block.crossing_weight(c)
            
            # Step 1a: Get a list of the trials that are involved in the crossing. That list
            # omits leading trials that will be present to initialize transitions, and the
            # number of trials may have been reduced by exclusions.
            # crossing_trials = list(filter(lambda t: all(map(lambda f: f.applies_to_trial(t), c)),
            #                               range(1, block.trials_per_sample() + 1)))
            # Modify this to make it depend on block property and preamble_size instead of factor
            crossing_trials = list(range(1+preamble_size, block.trials_per_sample() + 1))

            # Step 1b: For each trial, cross all levels of all factors in the crossing.
            # We exclude any combination that is dsiallowed by implicit or explicit exlcusions.
            level_lists = [list(f.levels) for f in c]
            crossings = [{level.factor: level for level in levels} for levels in product(*level_lists)]
            trial_combinations = list(filter(lambda c: not block.is_excluded_or_inconsistent_combination(c), crossings))
            crossing_combinations = [[block.encode_combination(c, t) for c in trial_combinations] for t in crossing_trials]
            # Each trial is now represented in `crossing_factors` by a list
            # of potential level combinations, where each level combination is represented
            # as tuple of CNF variables.

            # Step 2a: Allocate additional variables to represent each crossing in each trial.
            num_state_vars = len(crossing_combinations) * len(crossing_combinations[0])
            state_vars = list(range(fresh, fresh + num_state_vars))
            fresh += num_state_vars

            # Step 2b: Associate each state variable with its combination in each trial.
            flattened_combinations = list(chain.from_iterable(crossing_combinations))
            iffs = list(map(lambda n: Iff(state_vars[n], And([*flattened_combinations[n]])), range(len(state_vars))))

            # Step 2c: Get weight associated with each combination.
            combination_weights = [combination_weight(tuple(c.values())) for c in trial_combinations]

            # Step 3: Constrain each crossing to occur exactly according to its weight time the
            # crossing weight in each `crossing_size * crossing_weight` set of trials, or at most
            # that much in a last set of trials that is less than `crossing_size * crossing_weight`
            # in length.

            states = list(chunk(state_vars, len(trial_combinations)))
            transposed = cast(List[List[int]], list(map(list, zip(*states))))
            reqss = map(lambda l, w: Cross.__add_weight_constraint(l, w, crossing_size, crossing_weight),
                        transposed,
                        combination_weights)
            backend_request.ll_requests += list(chain.from_iterable(reqss))

            (cnf, new_fresh) = block.cnf_fn(And(iffs), fresh)

            backend_request.cnfs.append(cnf)
            backend_request.fresh = new_fresh

    @staticmethod
    def __add_weight_constraint(variables: List[int],
                                weight: int,
                                crossing_size: int,
                                crossing_weight: int) -> List[LowLevelRequest]:
        """Constrain to a weight of each `crossing_size` sequence of variables, and at
        at most one for an ending sequence that is less than `crossing_size` in length.
        """
        to_add = len(variables)
        reqs = cast(List[LowLevelRequest], [])
        while to_add > 0:
            if (to_add >= (crossing_size * crossing_weight)):
                reqs.append(LowLevelRequest("EQ", weight*crossing_weight, variables[:(crossing_size*crossing_weight)]))
            else:
                reqs.append(LowLevelRequest("LT", weight*crossing_weight+1, variables))
            variables = variables[(crossing_size*crossing_weight):]
            to_add -= crossing_size * crossing_weight
        return reqs

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        # conformance by construction or direct checking in combinatoric
        return True

class Derivation(Constraint):
    """A derivation such as::

        Derivation(4, [[0, 2], [1, 3]])

    where the index of the derived level is ``4``, and ``[[0, 2], [1, 3]]`` is
    the list of dependent indices, represents the logical formula::

        4 iff (0 and 2) or (1 and 3)

    These indicies are used the get the corresponding trial variables.
    Continuing from the example in of processDerivations, the first trial is
    represented by variables ``[1-6]`` (notice this feels like an off-by-one:
    the indicies start from ``0``, but the boolean variables start from ``1``).
    So we would use the indices to map onto the vars as::

        5 iff (1 and 3) or (2 and 4)

    Then we convert to CNF directly, i.e.::

        toCNF(Iff(5, Or(And(1,3), And(2,4))))

    This is then done for all window-sizes, taking into account strides (which
    are specified only in :class:`DerivedLevels <.DerivedLevel>` specified with
    a general :class:`.Window` rather than :class:`.Transition` or
    :class:`.WithinTrial`). We grab window-sized chunks of the variables that
    represent the trials, map the variables using the indices, and then convert
    to CNF. These chunks look like::

        window1: 1  2  3  4  5  6
        window2: 7  8  9  10 11 12

    So, for the second trial (since the window size in this example is ``1``)
    it would be::

        11 iff (7 and 9) or (8 and 10)

    When a dependent_idx has `BeforeStart`, then it should only apply early
    where the corresponding level is not available.

    90% sure this is the correct way to generalize to derivations involving 2+
    levels & various windowsizes. One test is the experiment::

        color = ["r", "b", "g"];
        text = ["r", "b"];
        conFactor;
        fullycross(color, text) + AtMostKInARow 1 conLevel
    """

    def __init__(self,
                 derived_idx: int,
                 dependent_idxs: List[List[object]],
                 factor: DerivedFactor) -> None:
        self.derived_idx = derived_idx
        self.dependent_idxs = dependent_idxs
        self.factor = factor
        # TODO: validation

    def validate(self, block: Block) -> None:
        pass

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        if self.is_complex(block):
            self.__apply_derivation(block, backend_request)
        else:
            # If the index is beyond the grid variables, that means it's a derivation from a complex window.
            # (This is brittle, but I haven't come up with a better way yet.)
            self.__apply_derivation_with_complex_window(block, backend_request)

    def is_complex(self, block: Block):
        return self.derived_idx < block.grid_variables()

    def __apply_derivation(self, block: Block, backend_request: BackendRequest) -> None:
        trial_size = block.variables_per_trial()
        cross_size = block.trials_per_sample()

        iffs = []
        for n in range(cross_size):
            or_clause = Or(list(And(list(map(lambda x: x + (n * trial_size) + 1, l))) for l in self.dependent_idxs))
            iffs.append(Iff(self.derived_idx + (n * trial_size) + 1, or_clause))

        (cnf, new_fresh) = block.cnf_fn(And(iffs), backend_request.fresh)

        backend_request.cnfs.append(cnf)
        backend_request.fresh = new_fresh

    def __apply_derivation_with_complex_window(self, block: Block, backend_request: BackendRequest) -> None:
        trial_size = block.variables_per_trial()
        trial_count = block.trials_per_sample()
        iffs = []
        f = self.factor
        window = f.levels[0].window
        t = 0
        delta = window.start_delta
        for n in range(trial_count):
            if not f.applies_to_trial(n + 1):
                continue
            num_levels = len(f.levels)
            get_trial_size = lambda x: trial_size if x < block.grid_variables() else len(block.decode_variable(x+1)[0].levels)

            # Only keep clauses where all `BeforeStarts` apply and all indices are in range:
            ands = []
            for l in self.dependent_idxs:
                vars = cast(List[int], [])
                ok = True
                for x in l:
                    if isinstance(x, BeforeStart):
                        if x.ready_at <= n:
                            ok = False
                            break
                    else:
                        new_x = x + ((t + delta) * window.stride * get_trial_size(x) + 1)
                        if new_x <= 0:
                            ok = False
                            break
                        vars.append(new_x)
                if ok:
                    ands.append(And(vars))

            or_clause = Or(ands)
            iffs.append(Iff(self.derived_idx + (t * num_levels) + 1, or_clause))
            t += 1
        (cnf, new_fresh) = block.cnf_fn(And(iffs), backend_request.fresh)

        backend_request.cnfs.append(cnf)
        backend_request.fresh = new_fresh

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def uses_factor(self, f: Factor) -> bool:
        return any(list(map(lambda l: l.uses_factor(f), self.factor.levels)))

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        return True


class _KInARow(Constraint):
    def __init__(self, k, level):
        self.k = k
        self.level = level
        self.within_block = False
        self.__validate()

    def __validate(self) -> None:
        who = self.__class__.__name__

        if not isinstance(self.k, int):
            raise ValueError(f"{who}: k must be an integer, received {self.k}")

        if self.k <= 0:
            raise ValueError(f"{who}: k must be greater than 0; if you're trying to exclude a particular level, "
                             f"use the 'Exclude' constraint")

        self.level = filter_level(who, self.level, True)

    def validate(self, block: Block) -> None:
        validate_factor_and_level(block, self.level.get_factor(), self.level)

    def set_within_block(self) -> None:
        self.within_block = True
 
    # NEW:
    def set_within_windows(self, window_len: int):
        self._within_window_len = int(window_len)   # no within_block change

    def uses_factor(self, f: Factor) -> bool:
        if isinstance(self.level, Factor):
            return self.level.uses_factor(f)
        else:
            return self.level.factor.uses_factor(f)

    def desugar(self, replacements: dict) -> List[Constraint]:
        constraints = cast(List[Constraint], [self])

        level = replacements.get(self.level, self.level)

        # Generate the constraint for each level in the factor.
        if isinstance(level, Factor):
            levels = level.levels  # Get the actual levels out of the factor.

            constraints = []
            for l in levels:
                constraint_copy = deepcopy(self)
                constraint_copy.level = l
                constraints.append(constraint_copy)
        elif level != self.level:
            constraint_copy = deepcopy(self)
            constraint_copy.level = level
            constraints = [constraint_copy]

        return constraints

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        # By this point, level should be a level tht has a factor.
        # Block construction is expected to flatten out constraints applied to whole factors so
        # that the constraint is applied to each level of the factor.
        self.apply_to_backend_request(block, (self.level.factor, self.level), backend_request)

    def _build_variable_sublistss(
        self,
        block: Block,
        level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]],
        sublist_length: int
    ) -> List[List[List[int]]]:
        # If window-scoped, we operate over fixed-size windows; otherwise we
        # use the original (global or repeat-scoped) behavior.
        window_len = cast(Optional[int], getattr(self, "_within_window_len", None))

        # When window-scoped, we must not trigger the repeat-only path in build_variable_lists
        base_within_block = self.within_block if window_len is None else False
        var_lists = block.build_variable_lists(level, base_within_block)

        sublistss: List[List[List[int]]] = []
        for var_list in var_lists:
            if window_len:
                # carve into non-overlapping windows; runs must not cross windows
                for start in range(0, len(var_list), window_len):
                    window_vars = var_list[start:start + window_len]
                    raw = [window_vars[i:i + sublist_length] for i in range(0, len(window_vars))]
                    sublistss.append([sl for sl in raw if len(sl) == sublist_length])
            else:
                raw = [var_list[i:i + sublist_length] for i in range(0, len(var_list))]
                sublistss.append([sl for sl in raw if len(sl) == sublist_length])

        return sublistss

    @abstractmethod
    def apply_to_backend_request(self, block: Block, level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]], backend_request: BackendRequest) -> None:
        pass

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        level = self.level
        factor = level.factor
        level_list = sample[factor]

        def check_sequence(start: int, end: int) -> bool:
            counts = []
            count = 0
            for i in range(start, end):
                l = level_list[i]
                if count > 0 and l != level:
                    counts.append(count)
                    count = 0
                elif l == level:
                    count += 1
            if count > 0:
                counts.append(count)
            return self._potential_counts_conform(counts)

        # Window-scoped: check each fixed window
        if hasattr(self, "_within_window_len"):
            win = int(self._within_window_len)
            T = len(level_list)
            if win <= 0 or T == 0:
                return True
            for start in range(0, T, win):
                end = min(start + win, T)
                if not check_sequence(start, end):
                    return False
            return True

        # Repeat-scoped or global
        return all(block.map_block_trial_ranges(self.within_block, check_sequence))

    @abstractmethod
    def _potential_counts_conform(self, counts: List[int]) -> bool:
        pass

    def _potential_counts_conform_individually(self, counts: List[int], fn: Callable[[int, int], bool]) -> bool:
        return all(map(lambda n: fn(n, self.k), counts))


class AtMostKInARow(_KInARow):
    """This desugars pretty directly into the llrequests. The only thing to do
    here is to collect all the boolean vars that match the same level & pair
    them up according to k.

    Continuing with the example from :class:`.Consistency`, say we want
    ``AtMostKInARow 1 ("color", "red")``, then we need to grab all the vars
    which indicate color-red::

        [1, 7, 13, 19]

    and then wrap them up so that we're making requests like::

        sum(1, 7)  LT 2
        sum(7, 13)  LT 2
        sum(13, 19) LT 2

    If it had been ``AtMostKInARow 2 ("color", "red")``, the reqs would have
    been::

        sum(1, 7, 13)  LT 3
        sum(7, 13, 19) LT 3
    """
    def apply_to_backend_request(self, block: Block, level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]], backend_request: BackendRequest) -> None:
        sublistss = self._build_variable_sublistss(block, level, self.k + 1)
        # Build the requests
        for sublists in sublistss:
            backend_request.ll_requests += list(map(lambda l: LowLevelRequest("LT", self.k + 1, l), sublists))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def _potential_counts_conform(self, counts: List[int]) -> bool:
        return self._potential_counts_conform_individually(counts, op.le)


class AtLeastKInARow(_KInARow):
    """This is more complicated that AtMostKInARow. We collect all the boolean
    vars that match the same level & pair them up according to k.

    We want ``AtLeastKInARow 2 ("color", "red")``, then we need to grab all the
    vars which indicate color-red::

        [1, 7, 13, 19]

    and then wrap them up in CNF as follows::

        If(1) Then (7)          --------This is a corner case
        If(And(!1, 7)) Then (13)
        If(And(!7, 13)) Then (19)
        If(19) Then (13)   --------This is a corner case

    If it had been ``AtLeastKInARow 3 ("color", "red")``, the CNF would have
    been::

        If(1) Then (7, 13)          --------This is a corner case
        If(And(!1, 7)) Then (13, 19)
        If(19) Then (7, 13)   --------This is a corner case
    """
    def __init__(self, k, levels):
        super().__init__(k, levels)
        self.max_trials_required = cast(int, None)

    def apply_to_backend_request(self, block: Block, level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]],
                                    backend_request: BackendRequest) -> None:

        # Request sublists for k+1 to allow us to determine the transition
        sublistss = self._build_variable_sublistss(block, level, self.k + 1)
        implications = []
        for sublists in sublistss:
            # Starting corner case
            implications.append(If(sublists[0][0], And(sublists[0][1:-1])))
            for sublist in sublists:
                implications.append(If(And([Not(sublist[0]), sublist[1]]), And(sublist[2:])))
            # Ending corner case
            implications.append(If(Not(sublists[-1][1]), Not(Or(sublists[-1][2:]))))

        (cnf, new_fresh) = block.cnf_fn(And(implications), backend_request.fresh)

        backend_request.cnfs.append(cnf)
        backend_request.fresh = new_fresh

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def _potential_counts_conform(self, counts: List[int]) -> bool:
        return self._potential_counts_conform_individually(counts, op.ge)


class ExactlyK(_KInARow):
    """Requires that if the given level exists at all, it must exist in a trial
    exactly ``k`` times.
    """
    def apply_to_backend_request(self,
                                 block: Block,
                                 level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]],
                                 backend_request: BackendRequest
                                 ) -> None:
        sublistss = block.build_variable_lists(level, self.within_block)

        window_len = cast(Optional[int], getattr(self, "_within_window_len", None))
        if window_len:
            new_sublistss = []
            for sub in sublistss:
                windows = [sub[s:s+window_len] for s in range(0, len(sub), window_len)]
                new_sublistss.extend(windows)
            sublistss = new_sublistss

        for sublists in sublistss:
            backend_request.ll_requests.append(LowLevelRequest("EQ", self.k, sublists))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def _potential_counts_conform(self, counts: List[int]) -> bool:
        return sum(counts) == self.k


class ExactlyKInARow(_KInARow):
    """Requires that if the given level exists at all, it must exist in a
    sequence of exactly K.
    """
    def apply_to_backend_request(self,
                                 block: Block,
                                 level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]],
                                 backend_request: BackendRequest
                                 ) -> None:
        sublistss = self._build_variable_sublistss(block, level, self.k)
        implications = []

        for sublists in sublistss:
            # Handle the regular cases (1 => 2 ^ ... ^ n ^ ~n+1)
            trim = len(sublists) if self.k > 1 else len(sublists) - 1
            for idx, l in enumerate(sublists[:trim]):
                if idx > 0:
                    p_list = [Not(sublists[idx-1][0]), l[0]]
                    p = And(p_list) if len(p_list) > 1 else p_list[0]
                else:
                    p = l[0]

                if idx < len(sublists) - 1:
                    q_list = cast(List[Any], l[1:]) + [Not(sublists[idx+1][-1])]
                    q = And(q_list) if len(q_list) > 1 else q_list[0]
                else:
                    q = And(l[1:]) if len(l[1:]) > 1 else l[self.k - 1]
                implications.append(If(p, q))

            # Handle the tail: if the last element is ON, the previous one must be ON.
            last_run = sublists[-1]
            if len(last_run) > 1:
                tail = list(reversed(last_run))  # [last, ..., first]
                for i in range(len(tail) - 1):
                    implications.append(If(tail[i], tail[i + 1]))

            (cnf, new_fresh) = block.cnf_fn(And(implications), backend_request.fresh)
            backend_request.cnfs.append(cnf)
            backend_request.fresh = new_fresh

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def _potential_counts_conform(self, counts: List[int]) -> bool:
        return self._potential_counts_conform_individually(counts, op.eq)


class ExactlyKMultipleInARow(_KInARow):
    def apply_to_backend_request(
        self,
        block: Block,
        level: Tuple[Factor, Union[SimpleLevel, DerivedLevel]],
        backend_request: BackendRequest
    ) -> None:
    
        k = self.k
        max_len = block.trials_per_sample()
        implications: List[Any] = [] 
        var_lists = block.build_variable_lists(level, self.within_block)
        all_trial_vars = var_lists[0]  # assume non-blocked design for now

        selector_runs: List[Tuple[int, List[int]]] = []  # (selector_var, covered_indices)

        window_len = cast(Optional[int], getattr(self, "_within_window_len", None))

        def encode_segment(segment_vars: List[int]) -> None:
            """Encode 'ON runs must have length ∈ {k, 2k, 3k, ...}' within this segment only."""
            max_len = len(segment_vars)
            if max_len == 0:
                return

            implications: List[Any] = []
            selector_runs: List[Tuple[int, List[int]]] = []  # (selector_var, covered_indices)

            # 1) selectors for all multiples of k within this segment
            for run_len in range(k, max_len + 1, k):
                for start in range(0, max_len - run_len + 1):
                    run_indices = list(range(start, start + run_len))
                    sel_var = backend_request.fresh
                    backend_request.fresh += 1
                    selector_runs.append((sel_var, run_indices))
                    implications.append(If(sel_var, And([all_trial_vars[i] for i in run_indices])))
                    after = start + run_len
                    if after < max_len:
                        implications.append(If(sel_var, Not(all_trial_vars[after])))

            # 2) Ensure every active trial is covered by some selector
            for i in range(max_len):
                covering = [sel for (sel, idxs) in selector_runs if i in idxs]
                if covering:
                    implications.append(If(segment_vars[i], Or(covering)))

            # 3) prevent overlaps
            for i, (sel_a, idxs_a) in enumerate(selector_runs):
                set_a = set(idxs_a)
                for j in range(i + 1, len(selector_runs)):
                    sel_b, idxs_b = selector_runs[j]
                    if set_a.intersection(idxs_b):
                        implications.append(Or([Not(sel_a), Not(sel_b)]))

            if implications:
                cnf, backend_request.fresh = block.cnf_fn(And(implications), backend_request.fresh)
                backend_request.cnfs.append(cnf)

        # Build lists (not repeat-scoped for window behavior)
        base_var_lists = block.build_variable_lists(level, within_block=self.within_block if not hasattr(self, "_within_window_len") else False)


        if hasattr(self, "_within_window_len"):
            win = int(self._within_window_len)
            for var_list in base_var_lists:
                for start in range(0, len(var_list), win):
                    segment = var_list[start:start + win]
                    encode_segment(segment)
        else:
            for var_list in base_var_lists:
                encode_segment(var_list)

    def _potential_counts_conform(self, counts: List[int]) -> bool:
        return all(c % self.k == 0 for c in counts)


def filter_level(who, level, factor_ok: bool = False):
    if factor_ok and isinstance(level, Factor):
        return level
    elif isinstance(level, Level):
        if hasattr(level, 'factor'):
            return level
        raise ValueError(f"{who}: level does not belong to a factor: {level}")
    elif isinstance(level, tuple) and len(level) == 2 and isinstance(level[0], Factor):
        if isinstance(level[1], SimpleLevel) or isinstance(level[1], DerivedLevel):
            if level[1] not in level[0]:
                raise ValueError(f"{who}: level {level[0]} is not in factor {level[1]}")
            return level[1]
        else:
            l = level[0].get_level(level[1])
            if not l:
                raise ValueError(f"{who}: not a level in factor {level[0]}: {level[1]}")
            return l
    else:
        if factor_ok:
            raise ValueError(f"{who}: expected either a Factor, Level, or a tuple of Factor and Level, given {level}")
        else:
            raise ValueError(f"{who}: expected either a Level or a tuple of Factor and Level, given {level}")

class Exclude(Constraint):
    def __init__(self, level):
        level = filter_level("Exclude", level)
        self.factor = level.factor
        self.level = level

    def validate(self, block: Block) -> None:
        validate_factor_and_level(block, self.factor, self.level)

        block.exclude.append((self.factor, self.level))
        # Store the basic factor-level combnations resulting in the derived excluded factor in the block
        if isinstance(self.level, DerivedLevel) and not self.factor.has_complex_window:
            block.excluded_derived.extend(self.extract_simplelevel(block, self.level))

    def uses_factor(self, f: Factor) -> bool:
        return self.factor.uses_factor(f)

    def desugar(self, replacements: dict) -> List:
        level = replacements.get(self.level, self.level)
        return [Exclude(level)]

    def extract_simplelevel(self, block: Block, level: DerivedLevel) -> List[Dict[Factor, SimpleLevel]]:
        """Recursively deciphers the excluded level to a list of combinations
        basic levels."""
        excluded_levels = []
        excluded: List[Tuple[Level, ...]] = [cross for cross in level.get_dependent_cross_product()
                                             if level.window.predicate(*[level.name for level in cross])]
        for excluded_level_tuple in excluded:
            combos: List[Dict[Factor, SimpleLevel]] = [{}]
            for excluded_level in excluded_level_tuple:
                if isinstance(excluded_level, DerivedLevel):
                    result = self.extract_simplelevel(block, excluded_level)
                    newcombos = []
                    valid = True
                    for r in result:
                        for c in combos:
                            for f in c:
                                if f in r:
                                    if c[f] != r[f]:
                                        valid = False
                        if valid:
                            newcombos.append({**r, **c})
                    combos = newcombos
                else:
                    if not isinstance(excluded_level, SimpleLevel):
                        raise ValueError(f"Unexpected level type in exclusion: level {level.name} of type "
                                         f"{type(level).__name__}.")
                    for c in combos:
                        if block.factor_in_crossing(excluded_level.factor) and block.require_complete_crossing:
                            block.errors.add("WARNING: Some combinations have been excluded, this crossing may not be complete!")
                        c[excluded_level.factor] = excluded_level
            excluded_levels.extend(combos)
        return excluded_levels

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        var_lists = block.build_variable_lists((self.factor, self.level))
        for var_list in var_lists:
            backend_request.cnfs.append(And(list(map(lambda n: n * -1, var_list))))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def is_complex_for_combinatoric(self) -> bool:
        return False

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        # conformance by construction in combinatoric for simple factors, but
        # we have to check exlcusions based on complex factors
        #if self.factor.has_complex_window:
        levels = sample[self.factor]
        level = self.level
        for l in levels:
            if l == level:
                return False
        return True

class Pin(Constraint):
    def __init__(self, index, level):
        level = filter_level("Pin", level)
        self.index = index
        self.factor = level.factor
        self.level = level
        self.within_block = False

    def set_within_block(self) -> None:
        self.within_block = True

    def validate(self, block: Block) -> None:
        validate_factor_and_level(block, self.factor, self.level)
        if not block.get_trial_numbers(self.index):
            num_trials = block.trials_per_sample()
            block.errors.add("WARNING: Pin constraint unsatisfiable, because "
                             + str(self.index) + " is out of range for " + str(num_trials) + " trials")

    def uses_factor(self, f: Factor) -> bool:
        return self.factor.uses_factor(f)

    def desugar(self, replacements: dict) -> List:
        level = replacements.get(self.level, self.level)
        p = Pin(self.index, level)
        p.within_block = self.within_block
        return [p]

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        trial_nos = block.get_trial_numbers(self.index, self.within_block)
        if trial_nos:
            for trial_no in trial_nos:
                var = block.get_variable(trial_no+1, (self.factor, self.level))
                backend_request.cnfs.append(And([var]))
        else:
            backend_request.cnfs.append(And([1, -1]))

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def is_complex_for_combinatoric(self) -> bool:
        return True

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        levels = sample[self.factor]
        trial_nos = block.get_trial_numbers(self.index, self.within_block)
        if trial_nos:
            for trial_no in trial_nos:
                if levels[trial_no] != self.level:
                    return False
            return True
        else:
            return False

class Reify(Constraint):
    """The only purpose of this constraint is to make a factor
    non-implied, so that it's exposed to a constraint solver."""
    def __init__(self, factor):
        self.factor = factor

    def validate(self, block: Block) -> None:
        validate_factor(block, self.factor)

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        """Do nothing."""

    def uses_factor(self, f: Factor) -> bool:
        return self.factor.uses_factor(f)

    def is_complex_for_combinatoric(self) -> bool:
        return False

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        return True

    def desugar(self, replacements: dict) -> List:
        factor = replacements.get(self.factor, self.factor)
        return [Reify(factor)]


class MinimumTrials(Constraint):
    def __init__(self, trials):
        self.trials = trials
        who = "MinimumTrials"
        argcheck(who, trials, int, "an integer")
        # TODO: validation

    def is_complex_for_combinatoric(self) -> bool:
        return False

    def validate(self, block: Block) -> None:
        if self.trials <= 0 and not isinstance(self.trials, int):
            raise ValueError("Minimum trials must be a positive integer.")

    def apply(self, block: Block, backend_request: Union[BackendRequest, None]) -> None:
        if block.min_trials:
            block.min_trials = max([block.min_trials, self.trials])
        else:
            block.min_trials = self.trials

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        return True



class ContinuousConstraint(Constraint):
    """This is the class for continuous constraint. 
    Users need to define the continuous factor and the required constraint function for those factors when initializing
    continuous constraints. This is only used to check continuous sampling. 
    """
    def __init__(self, factors, constraint_function):
        self.factors = factors
        self.constraint_function = constraint_function
        who = "ContinuousConstraint"
        # argcheck(who, factors, List[ContinuousFactor], "continuous factors")
        for f in self.factors: 
            if not isinstance(f, ContinuousFactor):
                raise ValueError(f"{who}: expected continuous factor, given {f}")
        #argcheck(who, constraint_function, Callable, "constraint function")
        if not isinstance(constraint_function, Callable):
            raise ValueError(f"{who}: expected constraint function, given {constraint_function}")
        # TODO: validation

    def validate(self, block: Block) -> None:
        sig = inspect.signature(self.constraint_function)
        num_params = len(sig.parameters)
        if len(self.factors ) != num_params:
            raise RuntimeError("The number of factors in the continuous constraint does not match the function for the constraint")
        for f in self.factors:
            if f not in block.continuous_factors:
                raise RuntimeError("Continuous factor {} not defined in the design".format(f))


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return str(self.__dict__)
    # def validate(self, block: Block) -> None:
    #     if self.trials <= 0 and not isinstance(self.trials, int):
    #         raise ValueError("Minimum trials must be a positive integer.")

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        return True

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        """Do nothing."""


class OrderRunsByPermutation(Constraint):
    """
    Given a permutation factor and an inner single-crossing block, pin each window
    (length = preamble + crossing_size) to the permutation chosen by the factor.
    """
    def __init__(self,
                 perm_factor: Factor,
                 inner_block: MultiCrossBlockRepeat,
                 level2perm: Dict[Level, Tuple[int, ...]]):
        self.perm_factor = perm_factor
        self.inner_block = inner_block
        if len(inner_block.crossings) != 1:
            raise ValueError("OrderRunsByPermutation expects an inner block with exactly one crossing.")
        self.inner_cross = inner_block.crossings[0]
        self.cross_size  = inner_block.crossing_size(self.inner_cross)
        self.preamble    = inner_block.preamble_size(self.inner_cross)
        self.run_len     = self.preamble + self.cross_size
        self.level2perm  = level2perm  # {Level: tuple[int]}

    def validate(self, block: Block) -> None:
        validate_factor(block, self.perm_factor)
        # basic sanity
        if self.cross_size <= 0:
            raise ValueError("OrderRunsByPermutation: inner crossing has zero size.")
        for lvl, perm in self.level2perm.items():
            if len(perm) != self.cross_size:
                raise ValueError(f"OrderRunsByPermutation: permutation for {lvl.name} "
                                 f"has length {len(perm)} != crossing size {self.cross_size}.")

    def uses_factor(self, f: Factor) -> bool:
        return self.perm_factor.uses_factor(f)

    def desugar(self, replacements: dict) -> List[Constraint]:
        # Replace perm_factor and possibly Level keys if weights were desugared.
        perm_factor = replacements.get(self.perm_factor, self.perm_factor)
        # Re-map keys if levels got replaced
        new_map: Dict[Level, Tuple[int, ...]] = {}
        for k, v in self.level2perm.items():
            new_k = replacements.get(k, k)
            new_map[new_k] = v
        return [OrderRunsByPermutation(perm_factor, self.inner_block, new_map)]

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        from itertools import product
        from sweetpea._internal.logic import If, And

        # Enumerate valid inner combos respecting excludes/derivations:
        level_lists = [list(f.levels) for f in self.inner_cross]
        all_tuples  = list(product(*level_lists))
        all_dicts   = [{f: lv for f, lv in zip(self.inner_cross, tpl)} for tpl in all_tuples]
        valid       = [d for d in all_dicts if not self.inner_block.is_excluded_or_inconsistent_combination(d)]
        if len(valid) != self.cross_size:
            raise RuntimeError("OrderRunsByPermutation: valid combo count != crossing_size.")

        T = block.trials_per_sample()
        if T % self.run_len != 0:
            raise RuntimeError(f"OrderRunsByPermutation: total trials ({T}) not multiple of run_len ({self.run_len}).")
        W = T // self.run_len

        clauses = []
        for w in range(W):
            start0 = w * self.run_len
            sel_t1 = start0 + 1  # selection read at first trial of window
            for lvl, perm in self.level2perm.items():
                sel = block.get_variable(sel_t1, (self.perm_factor, lvl))
                # pin only post-preamble part
                for t in range(self.cross_size):
                    combo = valid[perm[t]]
                    trial1 = start0 + self.preamble + t + 1
                    need = [block.get_variable(trial1, (f, combo[f])) for f in self.inner_cross]
                    clauses.append(If(sel, And(need)))

        if clauses:
            cnf, backend_request.fresh = block.cnf_fn(And(clauses), backend_request.fresh)
            backend_request.cnfs.append(cnf)

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        from itertools import product

        level_lists = [list(f.levels) for f in self.inner_cross]
        all_tuples  = list(product(*level_lists))
        all_dicts   = [{f: lv for f, lv in zip(self.inner_cross, tpl)} for tpl in all_tuples]
        valid       = [d for d in all_dicts if not self.inner_block.is_excluded_or_inconsistent_combination(d)]
        if len(valid) != self.cross_size:
            return False

        # total trials
        T = len(next(iter(sample.values())))
        if T % self.run_len != 0:
            return False
        W = T // self.run_len

        # permutation sequence for this sample (Levels or strings)
        perm_seq = _series_for(sample, self.perm_factor)

        for w in range(W):
            start0 = w * self.run_len
            chosen = perm_seq[start0]
            # resolve chosen level object (works if chosen is Level or string)
            chosen_lvl = None
            for l in self.perm_factor.levels:
                if _val_name(l) == _val_name(chosen):
                    chosen_lvl = l
                    break
            if chosen_lvl is None:
                return False
            perm = self.level2perm.get(chosen_lvl)
            if perm is None or len(perm) != self.cross_size:
                return False

            # verify inner window matches the selected permutation
            for t in range(self.cross_size):
                idx = start0 + self.preamble + t
                combo = valid[perm[t]]
                for f in self.inner_cross:
                    f_seq = _series_for(sample, f)
                    if _val_name(f_seq[idx]) != _val_name(combo[f]):
                        return False
        return True



class ConstantInWindows(Constraint):
    """
    Enforce that `factor` is constant inside each fixed window of length `run_len`,
    with windows starting at 0, run_len, 2*run_len, ...
    """
    def __init__(self, factor: Factor, run_len: int):
        self.factor = factor
        self.run_len = run_len

    def validate(self, block: Block) -> None:
        validate_factor(block, self.factor)
        if not isinstance(self.run_len, int) or self.run_len <= 0:
            raise ValueError("ConstantInWindows: run_len must be a positive integer.")

    def uses_factor(self, f: Factor) -> bool:
        return self.factor.uses_factor(f)

    def desugar(self, replacements: dict) -> List[Constraint]:
        # honor weight desugaring, etc.
        factor = replacements.get(self.factor, self.factor)
        return [ConstantInWindows(factor, self.run_len)]

    def apply(self, block: Block, backend_request: BackendRequest) -> None:
        from sweetpea._internal.logic import If, And
        T = block.trials_per_sample()
        if T % self.run_len != 0:
            raise RuntimeError(f"ConstantInWindows: total trials ({T}) not multiple of run_len ({self.run_len}).")

        clauses = []
        for start in range(0, T, self.run_len):
            t1 = start + 1  # trials are 1-based internally
            for lvl in self.factor.levels:
                sel = block.get_variable(t1, (self.factor, lvl))
                need = [block.get_variable(t1 + k, (self.factor, lvl)) for k in range(self.run_len)]
                clauses.append(If(sel, And(need)))

        if clauses:
            cnf, backend_request.fresh = block.cnf_fn(And(clauses), backend_request.fresh)
            backend_request.cnfs.append(cnf)

    def potential_sample_conforms(self, sample: dict, block: Block) -> bool:
        # total length from any entry
        T = len(next(iter(sample.values())))
        if T % self.run_len != 0:
            return False

        seq = _series_for(sample, self.factor)  # list of Level or str
        for start in range(0, T, self.run_len):
            window = seq[start:start + self.run_len]
            if not window:  # defensive
                return False
            head = _val_name(window[0])
            if any(_val_name(x) != head for x in window):
                return False
        return True


def _series_for(sample: dict, factor: Factor):
    # Try Factor object key
    if factor in sample:
        return sample[factor]
    # Try the HiddenName / name object itself
    name_obj = getattr(factor, "name", None)
    if name_obj in sample:
        return sample[name_obj]
    # Try string name
    name_str = str(name_obj) if name_obj is not None else None
    if name_str in sample:
        return sample[name_str]
    # Not found
    raise KeyError(f"sample does not contain series for factor {factor}")

def _val_name(x):
    # Works for Level objects or plain strings
    return getattr(x, "name", x)
