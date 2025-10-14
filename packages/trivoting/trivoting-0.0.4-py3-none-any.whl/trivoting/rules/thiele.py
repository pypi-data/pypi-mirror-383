from __future__ import annotations

import abc
from abc import abstractmethod
from collections.abc import Iterable
from copy import deepcopy

from trivoting.election import AbstractTrichotomousBallot, Alternative
from trivoting.election.trichotomous_profile import AbstractTrichotomousProfile

from pulp import LpProblem, LpMaximize, LpBinary, LpVariable, lpSum, LpStatusOptimal, value, PULP_CBC_CMD, \
    LpAffineExpression

from trivoting.election.selection import Selection
from trivoting.fractions import Numeric
from trivoting.tiebreaking import TieBreakingRule, lexico_tie_breaking
from trivoting.utils import harmonic_sum


class ThieleScore(abc.ABC):
    def __init__(self, max_size_selection):
        self.max_size_selection = max_size_selection

    @abstractmethod
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        pass

    def score_selection(self, profile: AbstractTrichotomousProfile, selection: Selection, extra_reject: Iterable[Alternative] = None, extra_accept: Iterable[Alternative] = None
                        ) -> Numeric:
        if extra_reject is None:
            extra_reject = []
        if extra_accept is None:
            extra_accept = []
        score = 0
        for ballot in profile:
            num_app_sel = 0
            num_app_rej = 0
            num_disapp_sel = 0
            num_disapp_rej = 0
            for a in ballot.approved:
                if (selection.is_selected(a) and a not in extra_reject) or a in extra_accept:
                    num_app_sel += 1
                elif (selection.is_rejected(a) and a not in extra_accept) or a in extra_reject:
                    num_app_rej += 1
            for a in ballot.disapproved:
                if(selection.is_rejected(a) and a not in extra_accept) or a in extra_reject:
                    num_disapp_rej += 1
                elif (selection.is_selected(a) and a not in extra_reject) or a in extra_accept:
                    num_disapp_sel += 1
            ballot_score = self.score_function(num_app_sel, num_disapp_sel, num_app_rej, num_disapp_rej)
            score += ballot_score * profile.multiplicity(ballot)
        return score

class PAVScoreKraiczy2025(ThieleScore):
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        return harmonic_sum(num_app_sel + num_disapp_rej)

class PAVScoreTalmonPaige2021(ThieleScore):
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        return harmonic_sum(num_app_sel) - harmonic_sum(num_disapp_sel)

class PAVScoreHervouin2025(ThieleScore):
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        return harmonic_sum(num_app_sel) + harmonic_sum(self.max_size_selection - num_disapp_sel)

class ApprovalOnlyScore(ThieleScore):
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        return num_app_sel

class SatisfactionScore(ThieleScore):
    def score_function(self, num_app_sel=0, num_disapp_sel=0, num_app_rej=0, num_disapp_rej=0):
        return num_app_sel - num_disapp_sel

class ThieleILPVoter:
    """
    Helper class holding the necessary information to build the ILP to compute the winner of Thiele a rule.

    Parameters
    ----------
    ballot : AbstractTrichotomousBallot
        The ballot of the voter.
    multiplicity : int
        The number of identical ballots represented by this voter.

    Attributes
    ----------
    ballot : AbstractTrichotomousBallot
        The ballot of the voter.
    multiplicity : int
        The number of identical ballots represented by this voter.
    app_sat_vars : dict[int, LpVariable]
        Decision variables counting the number of approved alternative that have been selected. The higher, the better.
    disapp_sat_vars : dict[int, LpVariable]
        Decision variables counting the number of disapproved alternative that have not been selected. The higher, the better.
    app_dissat_vars : dict[int, LpVariable]
        Decision variables counting the number of approved alternative that have not been selected. The higher, the worst.
    disapp_dissat_vars : dict[int, LpVariable]
        Decision variables counting the number of disapproved alternative that have been selected. The higher, the worst.
    """
    def __init__(self, ballot, multiplicity):
        self.ballot = ballot
        self.multiplicity = multiplicity
        self.app_sat_vars = None
        self.disapp_sat_vars = None
        self.app_dissat_vars = None
        self.disapp_dissat_vars = None
        self.sat_vars = None
        self.dissat_vars = None

class ThieleILPBuilder(abc.ABC):
    """
    Class used to build the ILP to compute the outcome of a Thiele rule.

    Parameters
    ----------
    profile: AbstractTrichotomousProfile
        The profile.
    max_size_selection: int
        Maximum number of alternatives to select.

    Attributes
    ----------
    profile: AbstractTrichotomousProfile
        The profile.
    max_size_selection: int
        Maximum number of alternatives to select.
    model: LpProblem
        ILP model.
    voters: list[ThieleILPVoter]
        List of instances of the :py:class:`ThieleILPVoter` class, each instance representing a voter.
    selection_vars: dict[Alternative, LpVariable]
        Dictionary mapping each alternative to the decision variable indicating whether a given alternative is selected
        or not.
    """
    def __init__(self, profile: AbstractTrichotomousProfile, max_size_selection: int):
        self.profile = profile
        self.max_size_selection = max_size_selection
        self.model = LpProblem("thiele", LpMaximize)
        self.voters = []
        self.selection_vars = {alt: LpVariable(f"y_{alt.name}", cat=LpBinary) for alt in profile.alternatives}

    @abc.abstractmethod
    def init_voters_vars(self) -> None:
        """"""

    @abc.abstractmethod
    def objective(self) -> LpAffineExpression:
        """"""

class PAVILPKraiczy2025(ThieleILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined in Section 3.3 of
    ``Proportionality in Thumbs Up and Down Voting`` (Kraiczy, Papasotiropoulos, Pierczyński and Skowron, 2025).
    The objective is to maximise the PAV score where both approved and selected, and disapproved and not selected
    alternatives contribute positively.
    """
    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = ThieleILPVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.sat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.sat_vars[k] = LpVariable(f"s_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.sat_vars.values()) == lpSum(
                self.selection_vars[alt] for alt in voter.ballot.approved) + lpSum(
                1 - self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.sat_vars.items()) for voter in self.voters)


class PAVILPTalmonPage2021(ThieleILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined in Section 3.3 of
    ``Proportionality in Committee Selection with Negative Feelings`` (Talmon and Page, 2021).
    The objective is to maximise the difference between (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score in which disapproved but selected alternatives are taken into account.
    """

    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = ThieleILPVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.app_sat_vars = dict()
            pav_voter.disapp_dissat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.app_sat_vars[k] = LpVariable(f"as_{i}_{k}", cat=LpBinary)
                pav_voter.disapp_dissat_vars[k] = LpVariable(f"dd_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.app_sat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.approved)
            self.model += lpSum(voter.disapp_dissat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.app_sat_vars.items()) for voter in self.voters) - lpSum(lpSum(v / i for i, v in voter.disapp_dissat_vars.items()) for voter in self.voters)


class PAVILPHervouin2025(ThieleILPBuilder):
    """
    Defines the ILP objective for the PAV ILP solver as defined by Matthieu Hervouin.
    The objective is to maximise the sum of (1) the PAV score in which approved and selected alternatives
    are taken into account, and (2) the PAV score over the maximum size of the selection minus the number of
    disapproved but selected alternatives.
    """

    def init_voters_vars(self) -> None:
        # Init the variables
        for i, ballot in enumerate(self.profile):
            pav_voter = ThieleILPVoter(ballot, multiplicity=self.profile.multiplicity(ballot))
            pav_voter.app_sat_vars = dict()
            pav_voter.disapp_dissat_vars = dict()
            for k in range(1, len(self.profile.alternatives) + 1):
                pav_voter.app_sat_vars[k] = LpVariable(f"as_{i}_{k}", cat=LpBinary)
                pav_voter.disapp_dissat_vars[k] = LpVariable(f"dd_{i}_{k}", cat=LpBinary)
            self.voters.append(pav_voter)

        # Constraint them to ensure proper counting
        for voter in self.voters:
            self.model += lpSum(voter.app_sat_vars.values()) == lpSum(self.selection_vars[alt] for alt in voter.ballot.approved)
            self.model += lpSum(voter.disapp_dissat_vars.values()) == self.max_size_selection - lpSum(self.selection_vars[alt] for alt in voter.ballot.disapproved)

    def objective(self) -> LpAffineExpression:
        return lpSum(lpSum(v / i for i, v in voter.app_sat_vars.items()) for voter in self.voters) + lpSum(lpSum(v / i for i, v in voter.disapp_dissat_vars.items()) for voter in self.voters)

def thiele_method(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    ilp_builder_class: type[ThieleILPBuilder],
    initial_selection: Selection | None = None,
    resoluteness: bool = True,
    verbose: bool = False,
    max_seconds: int = 600
) -> Selection | list[Selection]:
    """
    Compute the selections of a Thiele rule described in the `ild_builder_class` argument. The selections are computed
    by solving integer linear programs (ILP) using the `pulp` package.

    Parameters
    ----------
    profile : AbstractTrichotomousProfile
        The trichotomous profile.
    max_size_selection : int
        Maximum number of alternatives to select.
    ilp_builder_class : type[PAVILPBuilder], optional
        Builder class for the ILP.
    initial_selection : Selection, optional
        An initial partial selection fixing some alternatives as selected or rejected.
        If `implicit_reject` is True in the initial selection, no alternatives are fixed to be rejected.
        Defaults to None.
    resoluteness : bool, optional
        If True, returns a single optimal selection (resolute).
        If False, returns all tied optimal selections (irresolute).
        Defaults to True.
    verbose : bool, optional
        If True, enables ILP solver output.
        Defaults to False.
    max_seconds : int, optional
        Time limit in seconds for the ILP solver.
        Defaults to 600.

    Returns
    -------
    Selection | list[Selection]
        The selection if resolute (:code:`resoluteness == True`), or a list of selections
        if irresolute (:code:`resoluteness == False`).
    """

    if ilp_builder_class is None:
        ilp_builder_class = PAVILPKraiczy2025

    ilp_builder = ilp_builder_class(profile, max_size_selection)

    model = ilp_builder.model
    ilp_builder.init_voters_vars()
    selection_vars = ilp_builder.selection_vars

    # Select no more than allowed
    model += lpSum(selection_vars.values()) <= max_size_selection

    # Handle initial selection
    if initial_selection is not None:
        for alt in initial_selection.selected:
            model += selection_vars[alt] == 1
        if not initial_selection.implicit_reject:
            for alt in initial_selection.rejected:
                model += selection_vars[alt] == 0

    # Objective: max PAV score
    model += ilp_builder.objective()

    status = model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

    all_selections = []

    if status == LpStatusOptimal:
        selection = Selection(implicit_reject=True)
        for alt, v in selection_vars.items():
            if value(v) >= 0.9:
                selection.add_selected(alt)
        all_selections.append(selection)
    else:
        raise ValueError(f"Solver did not find an optimal solution, status is {status}.")

    if resoluteness:
        return all_selections[0]

    # If irresolute, we solve again, banning the previous selections
    model += ilp_builder.objective() == value(model.objective)

    previous_selection = selection
    while True:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        model += (
                             lpSum((1 - selection_vars[a]) for a in previous_selection.selected) +
                             lpSum(selection_vars[a] for a in selection_vars if a not in previous_selection)
                     ) >= 1

        model += (
                             lpSum(selection_vars[a] for a in previous_selection.selected) -
                             lpSum(selection_vars[a] for a in selection_vars if a not in previous_selection)
                     ) <= len(previous_selection) - 1

        status = model.solve(PULP_CBC_CMD(msg=verbose, timeLimit=max_seconds))

        if status != LpStatusOptimal:
            break

        previous_selection = Selection([a for a in selection_vars if value(selection_vars[a]) is not None and value(selection_vars[a]) >= 0.9], implicit_reject=True)
        if previous_selection not in all_selections:
            all_selections.append(previous_selection)

    return all_selections

class SequentialThieleVoter:

    def __init__(self, ballot: AbstractTrichotomousBallot, multiplicity: int):
        self.ballot = ballot
        self.multiplicity = multiplicity
        self.satisfaction = 0

def sequential_thiele(
    profile: AbstractTrichotomousProfile,
    max_size_selection: int,
    thiele_score_class: type[ThieleScore],
    initial_selection: Selection | None = None,
    tie_breaking: TieBreakingRule | None = None,
    resoluteness: bool = True,
) -> Selection | list[Selection]:

    def _sequential_thiele_rec(alternatives: set[Alternative], selection: Selection, skip_remove_phase=False):
        something_changed = False
        branched = False

        # Remove alternatives that have negative marginal contributions
        if not skip_remove_phase:
            min_marginal_contribution = None
            argmin_marginal_contribution = None
            for alternative in selection.selected:
                marginal_contribution = thiele_score.score_selection(profile, selection) - thiele_score.score_selection(profile, selection, extra_reject=[alternative])
                if min_marginal_contribution is None or marginal_contribution < min_marginal_contribution:
                    min_marginal_contribution = marginal_contribution
                    argmin_marginal_contribution = [alternative]
                elif min_marginal_contribution == marginal_contribution:
                    argmin_marginal_contribution.append(alternative)
            if min_marginal_contribution is not None and min_marginal_contribution < 0:
                tied_alternatives = tie_breaking.order(profile, argmin_marginal_contribution)
                # print(f"Removing one of {tied_alternatives} ({min_marginal_contribution})")
                if resoluteness:
                    alt_to_remove = tied_alternatives[0]
                    selection.remove_selected(alt_to_remove)
                    alternatives.add(alt_to_remove)
                    something_changed = True
                else:
                    for alt_to_remove in tied_alternatives:
                        new_selection = deepcopy(selection)
                        new_selection.remove_selected(alt_to_remove)
                        new_alternatives = deepcopy(alternatives)
                        new_alternatives.add(alt_to_remove)
                        _sequential_thiele_rec(new_alternatives, new_selection, skip_remove_phase=True)
                        branched = True
        else:
            something_changed = True

        # Add alternative with maximum marginal contribution
        if len(selection) < max_size_selection:
            max_marginal_contribution = None
            argmax_marginal_contribution = None
            for alternative in alternatives:
                marginal_contribution = thiele_score.score_selection(profile, selection, extra_accept=[alternative]) - thiele_score.score_selection(
                    profile, selection)
                # print(alternative, thiele_score.score_selection(profile, selection, extra_accept=[alternative]), thiele_score.score_selection(profile, selection))
                if max_marginal_contribution is None or marginal_contribution > max_marginal_contribution:
                    max_marginal_contribution = marginal_contribution
                    argmax_marginal_contribution = [alternative]
                elif max_marginal_contribution == marginal_contribution:
                    argmax_marginal_contribution.append(alternative)
            if max_marginal_contribution is not None and max_marginal_contribution > 0:
                tied_alternatives = tie_breaking.order(profile, argmax_marginal_contribution)
                # print(f"Adding one of {tied_alternatives} ({max_marginal_contribution})")
                if resoluteness:
                    alt_to_add = tied_alternatives[0]
                    selection.add_selected(alt_to_add)
                    alternatives.remove(alt_to_add)
                    something_changed = True
                else:
                    for alt_to_add in tied_alternatives:
                        new_selection = deepcopy(selection)
                        new_selection.add_selected(alt_to_add)
                        new_alternatives = deepcopy(alternatives)
                        new_alternatives.remove(alt_to_add)
                        _sequential_thiele_rec(new_alternatives, new_selection)
                        branched = True

        # If nothing has changed, selection is stable and we stop (only if a recursive call has not been launched)
        if not something_changed:
            if not branched:
                if not resoluteness:
                    selection.sort()
                    if selection not in all_selections:
                        all_selections.append(selection)
                else:
                    all_selections.append(selection)
        else:
            _sequential_thiele_rec(alternatives, selection)

    try:
        max_size_selection = int(max_size_selection)
    except ValueError:
        raise ValueError('max_size_selection must be an integer.')

    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking

    if initial_selection is not None:
        max_size_selection -= len(initial_selection)
    else:
        initial_selection = Selection(implicit_reject=True)

    initial_alternatives = {a for a in profile.alternatives if a not in initial_selection}
    all_selections = []
    thiele_score = thiele_score_class(max_size_selection)

    _sequential_thiele_rec(initial_alternatives, initial_selection)

    if resoluteness:
        return all_selections[0]
    return all_selections