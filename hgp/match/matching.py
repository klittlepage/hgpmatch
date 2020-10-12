"""
Methods to facilitate the formulation and solution to a specific flavor of the
Hospital/Resident matching problem used for matching
`Hidden Genius Project (HGP) <https://www.hiddengeniusproject.org/>`_ mentors
to mentees.

The conventional hopsital/resident matching problem requires a secondary
procedure for handling unmatched residents, and rankings must be complete (every
resident ranked by a hospital must rank the hospital and every hospital ranked
by a resident must rank the resident). This module exposes functionality for
normalizing partial "hospital" (mentor) and "resident" (mentee) rankings into a
total ordering that's guaranteed to match every mentee to a mentor, provided
that there's enough aggregate mentor capacity. Furthermore, secondary matching
is done in a way that ensures optimal outcomes when one side hasn't explicitly
ranked the other.
"""

import csv
import random

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import cast, Dict, Iterable, List, Mapping, Set, Tuple, Union

from fuzzywuzzy import process  # type: ignore
from matching.games.hospital_resident import HospitalResident  # type: ignore


class InvalidProblemStatement(Exception):
    """The exception raised when a problem formulation is invalid.
    """

TRawMatrix = List[List[str]]
TRawMatchDict = Mapping[str, Union[Tuple[int, List[str]], List[str]]]
TRawCapacity = List[Tuple[str, Union[str, int]]]
TRankingDict = Dict[str, List[str]]
TCapacity = Dict[str, int]
TMatching = Dict[str, List[str]]


def _throw_with_line(file, idx, msg):
    raise InvalidProblemStatement(f"{msg}. The problem occurred on line "
                                  f"{idx+1} of {file}.")


def _all_players(mentee_rankings: TRankingDict,
                 mentor_rankings: TRankingDict,
                 mentor_capacities: TCapacity):
    all_mentees = set(mentee_rankings.keys())
    all_mentors = set(mentor_rankings.keys())
    all_mentors |= set(mentor_capacities.keys())

    for rankings in mentee_rankings.values():
        all_mentors.update(rankings)

    for rankings in mentor_rankings.values():
        all_mentees.update(rankings)

    return all_mentees, all_mentors


def _ranking_dict(rankings: TRawMatchDict) -> TRankingDict:
    return {k: v[1] if isinstance(v, tuple) else v for k, v in rankings.items()}


def _duplicates(values: Iterable[str]) -> List[str]:
    return [item for item, count in Counter(values).items() if count > 1]


def validate_rankings(mentee_rankings: TRawMatchDict,
                      mentor_rankings: TRawMatchDict,
                      mentor_capacities: TCapacity):
    """
    Verifies that a ranking is structurally correct. The following invariants
    must hold:

    - Every mentor ranked by a mentee must exist in the key set of
      :code:`mentor_capacities`
    - Every mentee ranked by a mentor must exist in the key set of
      :code:`mentee_rankings`
    - Rankings should never contain duplicate entries

    If a mentor or mentee is missing :code:`validate_rankings` will attempt
    to suggest a similar name; if no names are sufficiently similar, the
    suggestion will be **UNKNOWN**

    Parameters
    ----------
    mentee_rankings
        Mentee rankings of mentors
    mentor_rankings
         Mentor rankings of mentees
    mentor_capacities
        The max number of mentees assignable to a mentor

    Raises
    ------
    InvalidProblemStatement
        If the ranking is invalid
    """
    def closest_match(value: str, candidates: Iterable[str]) -> str:
        maybe_match = process.extractOne(value.lower(),
                                         list(x.lower() for x in candidates),
                                         score_cutoff=50)
        if maybe_match:
            for candidate in candidates:
                if candidate.lower() == maybe_match[0]:
                    return candidate
        return 'UNKNOWN'  # pragma: no cover

    def raise_on_duplicates(player, player_type, values):
        duplicates = _duplicates(values)
        if duplicates:
            msg = f"{player_type} {player} has duplicate rankings " \
                  f"[{', '.join(duplicates)}]"
            raise InvalidProblemStatement(msg)

    def validate_mentees(mentee_rankings: TRankingDict,
                         mentors: Set[str]):
        for mentee, rankings in mentee_rankings.items():
            raise_on_duplicates('Mentee', mentee, rankings)
            for mentee_ranking in rankings:
                if not mentee_ranking in mentors:
                    candidate = closest_match(mentee_ranking, mentors)
                    raise InvalidProblemStatement(f"Mentee {mentee} ranked a "
                                                  f"mentor {mentee_ranking} "
                                                  'that does not exist. The '
                                                  'closest candidate is '
                                                  f"{candidate}")

    def validate_mentors(mentor_rankings: TRankingDict,
                         mentor_capacities: TCapacity,
                         mentees: Set[str]):
        for mentor, rankings in mentor_rankings.items():
            raise_on_duplicates('Mentor', mentor, rankings)

            if not mentor in mentor_capacities:
                msg = f"Mentor {mentor} is not listed in the mentor " \
                      "capacities file"
                raise InvalidProblemStatement(msg)

            for mentor_ranking in rankings:
                if not mentor_ranking in mentees:
                    candidate = closest_match(mentor_ranking, mentees)
                    msg = f"Mentor {mentor} ranked a mentee {mentor_ranking} " \
                          'that does not exist. The closest candidate is ' \
                          f"{candidate}"
                    raise InvalidProblemStatement(msg)

    validate_mentees(_ranking_dict(mentee_rankings),
                     set(mentor_capacities.keys()))
    validate_mentors(_ranking_dict(mentor_rankings),
                     mentor_capacities,
                     set(mentee_rankings.keys()))


@dataclass
class MatchStatement:
    """
    A simple data class for representing a mentee/mentor match problem statement

    Attributes
    ----------
    mentee_rankings
        Mentee rankings of mentors
    mentor_rankings
        Mentor rankings of mentees
    mentor_capacities
        The maximum number of mentees assignable to a mentor
    """

    mentee_rankings: TRankingDict
    mentor_rankings: TRankingDict
    mentor_capacities: TCapacity

    def __init__(self,
                 mentee_rankings: TRankingDict,
                 mentor_rankings: TRankingDict,
                 mentor_capacities: TCapacity):
        """
        Initializes the :class:`MatchStatement`

        Raises
        ------
        InvalidProblemStatement
            If the ranking is invalid
        """
        validate_rankings(mentee_rankings, mentor_rankings, mentor_capacities)
        self.mentee_rankings = mentee_rankings
        self.mentor_rankings = mentor_rankings
        self.mentor_capacities = mentor_capacities


def validate_and_transform(mentee_rankings: TRawMatrix,
                           mentor_rankings: TRawMatrix,
                           mentor_capacities: TRawCapacity) -> MatchStatement:
    """
    Validates and converts a matrix representation of the match problem into the
    canonical form that's used elsewhere.

    In mentor and mentee rankings, note that rank is implicit, and specified
    left-to-right. For example:

    :code:`[["S1", "M2", "M1]]` means that :code:`S1` has ranked :code:`M2`
    first and :code:`M1` second.

    The :code:`mentor_capacities` attribute is an :code:`Nx2`
    matrix. The first column of each row is the name of the mentor. The second
    is their mentee capacity.

    Attributes
    ----------
    mentee_rankings
        Mentee rankings of mentors in matrix form
    mentor_rankings
        Mentor rankings of mentees in matrix form
    mentor_capacities
        Mentor capacities in matrix form.

    Returns
    -------
    match_statement
        A :class:`MatchStatement` formulated from the given inputs

    Raises
    ------
    InvalidProblemStatement
        If the ranking is invalid
    """
    def process_capacities(mentor_capacities: TRawCapacity) -> TCapacity:
        mentors: TCapacity = dict()
        for idx, mentor_capacity in enumerate(mentor_capacities):
            if len(mentor_capacity) != 2:
                _throw_with_line('mentor_capacities', idx,
                                 'Every row of the mentor capacity file must '
                                 'have two columns')

            mentor, capacity = mentor_capacity
            if mentor in mentors:
                _throw_with_line('mentor_capacities', idx,
                                 'The same mentor appears twice in the mentor '
                                 'capacity file')
            try:
                if isinstance(capacity, str):
                    numeric_capacity = int(capacity)
                elif isinstance(capacity, int):
                    numeric_capacity = capacity
                else:
                    _throw_with_line('mentor_capacities', idx,
                                     'Capacity must be a string or an int')
                if numeric_capacity < 1:
                    raise Exception()
                mentors[mentor] = numeric_capacity
            except:  # pylint: disable=bare-except
                _throw_with_line('mentor_capacities', idx,
                                 'Invalid mentor capacity. Capacities must be '
                                 'strictly positive (> 0) integer values')

        return mentors

    def process_rankings(rankings: TRawMatrix,
                         ranking_type: str) -> TRawMatchDict:
        rankings_processed = dict()
        for idx, ranking in enumerate(rankings):
            if ranking[0] in rankings_processed:
                _throw_with_line(f"{ranking_type}_ranking",
                                 idx, f"duplicate in {ranking_type} rows")

            if len(ranking[1:]) != len(set(ranking[1:])):
                _throw_with_line(f"{ranking_type}_ranking",
                                 idx, f"duplicate in {ranking_type} columns")

            rankings_processed[ranking[0]] = (idx, ranking[1:])

        return rankings_processed

    mentee_preprocessed = process_rankings(mentee_rankings, 'mentee')
    mentor_preprocessed = process_rankings(mentor_rankings, 'mentor')
    mentor_capacities_processed = process_capacities(mentor_capacities)

    validate_rankings(mentee_preprocessed,
                      mentor_preprocessed,
                      mentor_capacities_processed)

    if sum(mentor_capacities_processed.values()) < len(mentee_preprocessed):
        raise InvalidProblemStatement('Available mentor capacity is less than '
                                      'the number of students; increase '
                                      'mentee capacity for one or more '
                                      'mentors.')

    return MatchStatement(_ranking_dict(mentee_preprocessed),
                          _ranking_dict(mentor_preprocessed),
                          mentor_capacities_processed)


def poset_to_ordered(statement: MatchStatement) -> MatchStatement:
    """
    Expands a partial ordering wherein mentees have not necessarily ranked
    every mentor (and vice versa) into a total order. The expansion is done
    in a way that ensures fairness but results in optimal stable marriage
    outcomes when one party expresses indifference in the face of another
    party's preference.

    Attributes
    ----------
    statement
        A match statement that need not contain a total ordering.

    Returns
    -------
    match_statement
        A :class:`MatchStatement` formulated from the given inputs
    """
    def make_total_ordering(player_rankings: TRankingDict,
                            opponent_rankings: TRankingDict,
                            all_players: Set[str],
                            all_opponents: Set[str]) -> TRankingDict:
        transformed: TRankingDict = dict()
        opponents_ranking_player = defaultdict(set)

        for opponent_name, opponent_ranking in opponent_rankings.items():
            for ranking in opponent_ranking:
                opponents_ranking_player[ranking].add(opponent_name)

        player_rankings = player_rankings.copy()
        for player in all_players:
            if player not in player_rankings:
                player_rankings[player] = list()

        for player, rankings in player_rankings.items():
            opponent_ranked = list(opponents_ranking_player[player])
            unranked = list(all_opponents -
                            (set(rankings) | set(opponent_ranked)))
            random.shuffle(opponent_ranked)
            random.shuffle(unranked)
            total_ordering = list(rankings) + \
                [x for x in opponent_ranked
                 if x not in set(rankings)] + unranked

            transformed[player] = total_ordering

        return transformed

    all_mentees, all_mentors = _all_players(statement.mentee_rankings,
                                            statement.mentor_rankings,
                                            statement.mentor_capacities)

    return MatchStatement(make_total_ordering(statement.mentee_rankings,
                                              statement.mentor_rankings,
                                              all_mentees,
                                              all_mentors),
                          make_total_ordering(statement.mentor_rankings,
                                              statement.mentee_rankings,
                                              all_mentors,
                                              all_mentees),
                          statement.mentor_capacities.copy())


def from_csv_files(mentee_rankings_path: str,
                   mentor_rankings_path: str,
                   mentor_capacities_path: str) -> MatchStatement:
    """
    Formulates a :class:`MatchStatement` from csv inputs.

    Ranking files should have the following format:

    ::

        mentee_rankings.csv
        S1,M2,M1,M3
        S2,M3
        S3,M1,M2

        mentor_rankings.csv
        M1,S1,S2,S3
        M2,S3,S2,S1
        M3,S1,S3

        mentor_capacities.csv
        M1,2
        M2,1
        M3,3

    The names are arbitrary (:code:`S` was chosen to represent students/mentees
    and :code:`M` was chosen to represent mentors) but they must be consistent
    e.g., if :code:`S1` ranks :code:`M1`, :code:`M1` should appear as an entry
    of the first column in mentor_capacities.csv, and if :code:`M1` ranks
    :code:`S3`, :code:`S3` must appear in the first column of
    mentee_rankings.csv.

    Attributes
    ----------
    mentee_rankings_path
        A path to the mentee ranking csv file
    mentor_rankings_path
        A path to the mentor ranking csv file
    mentor_capacities_path
        A path to the mentor capacities csv file

    Returns
    -------
    match_statement
        A :class:`MatchStatement` formulated from the given inputs

    Raises
    ------
    InvalidProblemStatement
        If the ranking is invalid

    See Also
    --------
    validate_and_transform : Which does all of the work after csv files are read
    """
    def read_csv(path: str, file_type: str) -> TRawMatrix:
        try:
            with open(path, 'r') as input_file:
                csv_reader = csv.reader(input_file, lineterminator='\n')
                result = list()
                for row in csv_reader:
                    col = list(x.strip() for x in row)
                    if col:
                        result.append(row)

                return result
        except Exception as e:
            raise InvalidProblemStatement(f"failed to {file_type} file, {e}") \
                from e

    mentee_rankings = read_csv(mentee_rankings_path, 'mentee rankings')
    mentor_rankings = read_csv(mentor_rankings_path, 'mentor rankings')
    mentor_capacities = read_csv(mentor_capacities_path, 'mentor capacities')

    return validate_and_transform(mentee_rankings,
                                  mentor_rankings,
                                  cast(TRawCapacity, mentor_capacities))


def solve_from_poset_problem(poset_problem: MatchStatement,
                             mentee_optimal=True) -> TMatching:
    """
    Finds a stable marriage using the modified Gale–Shapley algorithm, given
    a `class`:MatchStatement that's a total ordering. This ordering can
    be constructed manually, or expanded from a partial ordering via
    :func:`poset_to_ordered`.

    Attributes
    ----------
    poset_problem:
        A totally ordered statement of the matching problem
    mentee_optimal:
        Hospital/resident style stable marrage problems are always optimal
        for one side or the other. By default this function optimizes for
        mentee outcomes.

    Returns
    -------
    matching
        A stable marriage matching. Each key corresponds to a mentor; the list
        of values are their mentees.

    Raises
    ------
    Exception
        If :code:`poset_problem` isn't a valid total ordering
    """
    problem = poset_to_ordered(poset_problem)
    game = HospitalResident.create_from_dictionaries(problem.mentee_rankings,
                                                     problem.mentor_rankings,
                                                     problem.mentor_capacities)

    matching = game.solve(optimal='resident' if mentee_optimal else 'hospital')
    return {key.name: [x.name for x in value] for key, value in
            matching.items()}

def solve(mentee_rankings_path: str,
          mentor_rankings_path: str,
          mentor_capacities_path: str,
          result_path: str,
          mentee_optimal=True):
    """
    Solves the mentor/mentee matching problem, taking csv files as an input
    and outputing the result as another csv file.
    See :func:`from_csv_files` and :func:`solve_from_poset_problem` for
    additional formats on the expected input and output formats.

    The csv file written to :code:`result_path` will contain entries of the
    form:

    ::

        results.csv
        M1,S2,S3
        M2,S1
        M3,S4,S5,S6

    The first column is the name of a mentor; each subsequent column is the name
    of a mentee for that mentor. In the example above, :code:`M1` is mentoring
    :code:`S2` and :code:`S3`.
    """

    poset_problem = from_csv_files(mentee_rankings_path,
                                   mentor_rankings_path,
                                   mentor_capacities_path)
    matching = solve_from_poset_problem(poset_problem,
                                        mentee_optimal=mentee_optimal)
    try:
        with open(result_path, 'w', encoding='utf8') as output_file:
            csv_writer = csv.writer(output_file, lineterminator='\n')
            for mentor in sorted(matching.keys()):
                csv_writer.writerow([mentor] + sorted(matching[mentor]))
    except Exception as e:  # pragma: no cover # pylint: disable=bare-except
        raise Exception('Unable to write output; check output path') from e
