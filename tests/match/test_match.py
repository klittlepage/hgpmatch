# pylint: disable=missing-docstring

import csv
import random
import unittest

import hgp.match.matching as matching

import tests.match.util as util

from hgp.match.matching import MatchStatement

# pylint: disable=no-self-use, too-many-public-methods


class TestVerify(unittest.TestCase):
    def test_no_duplicate_mentees(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_rankings({'S1': ['M1', 'M1']},
                                       {'M1': ['S1']},
                                       {'M1': 1})

    def test_no_duplicate_mentors(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_rankings({'S1': ['M1']},
                                       {'M1': ['S1', 'S1']},
                                       {'M1': 1})


class TestVerifyAndTransform(unittest.TestCase):
    def test_no_capacity_for_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a']])

    def test_non_numeric_capacity_for_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', 'b']])

    def test_negative_capacity_for_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', -1]])

    def test_zero_capacity_for_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', 0]])

    def test_too_many_capacity_columns(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', 1, 2]])

    def test_duplicate_capacity_columns(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', 1], ['a', 1]])

    def test_bad_type_for_capacity_columns(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], [], [['a', []]])

    def test_string_capacity_columns(self):
        res = matching.validate_and_transform([], [], [['a', '1']])
        self.assertDictEqual(res.mentor_capacities, {'a': 1})

    def test_int_capacity_columns(self):
        res = matching.validate_and_transform([], [], [['a', 1]])
        self.assertDictEqual(res.mentor_capacities, {'a': 1})

    def test_duplicate_mentee(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1'], ['S1', 'M1']]
            mentor = [['M1', 'S1']]
            capacity = [['M1', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

    def test_duplicate_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1']]
            mentor = [['M1', 'S1'], ['M1', 'S1']]
            capacity = [['M1', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

    def test_duplicate_ranking(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1', 'M1']]
            mentor = [['M1', 'S1']]
            capacity = [['M1', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1']]
            mentor = [['M1', 'S1', 'S1']]
            capacity = [['M1', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

    def test_unknown_mentor(self):
        mentee = [['S1', 'M2']]
        capacity = [['M1', '1']]

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform(mentee, [['M1', 'S1']], capacity)

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform(mentee, [], capacity)

    def test_unknown_mentee(self):
        mentor = [['M1', 'S2']]
        capacity = [['M1', '1']]

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([['S1', 'M1']], mentor, capacity)

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.validate_and_transform([], mentor, capacity)

    def test_missing_capacity_for_mentor(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1']]
            mentor = [['M1', 'S1']]
            capacity = [['M2', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1']]
            mentor = [['M1', 'S1'], ['M2', 'S1']]
            capacity = [['M1', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

    def test_insufficient_mentor_capacity(self):
        with self.assertRaises(matching.InvalidProblemStatement):
            mentee = [['S1', 'M1', 'M2'], ['S2', 'M1'], ['S3', 'M1']]
            mentor = [['M1', 'S1'], ['M2', 'S1', 'S2']]
            capacity = [['M1', '1'], ['M2', '1']]
            matching.validate_and_transform(mentee, mentor, capacity)

    def test_valid_ranking(self):
        mentee = [['S1', 'M1', 'M2'], ['S2', 'M1']]
        mentor = [['M1', 'S1'], ['M2', 'S1', 'S2']]
        capacity = [['M1', '1'], ['M2', '2']]

        res = matching.validate_and_transform(mentee, mentor, capacity)
        self.assertDictEqual(res.mentee_rankings, {'S1': ['M1', 'M2'],
                                                   'S2': ['M1']})
        self.assertDictEqual(res.mentor_rankings, {'M1': ['S1'],
                                                   'M2': ['S1', 'S2']})
        self.assertDictEqual(res.mentor_capacities, {'M1': 1, 'M2': 2})

    def test_complex_partial_rankings(self):
        mentee_rankings = {
            'S0': [],
            'S1': [],
            'S2': ['M1', 'M2'],
            'S3': ['M2', 'M0'],
            'S4': []
        }
        mentor_rankings = {'M0': ['S3', 'S0', 'S2', 'S1', 'S4']}
        mentor_capacities = {'M1': 2, 'M2': 3, 'M0': 1}
        problem = matching.MatchStatement(mentee_rankings,
                                          mentor_rankings,
                                          mentor_capacities)
        matching.solve_from_poset_problem(problem)

    def test_all_match_when_mentor_unranked(self):
        mentee_rankings = {
            'S1': ['M1', 'M2'],
            'S2': ['M2', 'M1'],
            'S3': ['M1'],
            'S4': ['M1']
        }
        mentor_rankings = {'M1': ['S2', 'S3'], 'M2': ['S1', 'S2', 'S4']}
        mentor_capacities = {'M1': 1, 'M2': 2, 'M3': 1}
        problem = matching.MatchStatement(mentee_rankings,
                                          mentor_rankings,
                                          mentor_capacities)
        res = matching.solve_from_poset_problem(problem)
        self.assertEqual(len(res.keys()), 3)
        self.assertEqual(sum(len(x) for x in res.values()), 4)

    def test_all_match_when_student_unranked(self):
        mentee_rankings = {
            'S1': ['M1', 'M2'],
            'S2': ['M2', 'M1'],
            'S3': ['M3'],
        }
        mentor_rankings = {'M1': ['S2'], 'M2': ['S1', 'S2']}
        mentor_capacities = {'M1': 1, 'M2': 2, 'M3': 1}
        problem = matching.MatchStatement(mentee_rankings,
                                          mentor_rankings,
                                          mentor_capacities)
        res = matching.solve_from_poset_problem(problem)
        self.assertEqual(len(res.keys()), 3)
        self.assertEqual(sum(len(x) for x in res.values()), 3)

    def test_random_instances(self):
        def ranking_dict(row_name, max_rows, col_name, max_cols):
            ranking_dict = dict()
            rows = list(range(max_rows))
            cols = list(range(max_cols))
            random.shuffle(rows)

            for row_player in rows[:random.randint(1, max_rows)]:
                random.shuffle(cols)
                rankings = [f"{col_name}{col}" for col in
                            cols[:random.randint(1, max_cols)]]
                ranking_dict[f"{row_name}{row_player}"] = rankings

            return ranking_dict

        def generate_problem(max_mentees, max_mentors):
            mentee_ranks = ranking_dict('S', max_mentees, 'M', max_mentors)
            mentor_ranks = ranking_dict('M', max_mentors, 'S', max_mentees)
            mentor_ranks = {k: [x for x in v if x in set(mentee_ranks.keys())]
                            for k, v in mentor_ranks.items()}
            all_mentors = set(mentor_ranks.keys())
            for ranks in mentee_ranks.values():
                all_mentors.update(ranks)

            mentor_capacity = dict(zip(all_mentors,
                                       (random.randint(1, 5) for _ in
                                        range(len(all_mentors)))))

            while sum(mentor_capacity.values()) < len(mentee_ranks):
                for key in mentor_capacity.keys():
                    mentor_capacity[key] += 1

            return matching.MatchStatement(mentee_ranks,
                                           mentor_ranks,
                                           mentor_capacity)

        for _ in range(2**10):
            problem = generate_problem(30, 20)
            matching.solve_from_poset_problem(problem)


class TestFromCSV(unittest.TestCase):
    def test_bad_mentee_path(self):
        data_dir = util.test_data_dir().joinpath('data/good_csv')
        mentee_path = data_dir.joinpath('menteez_rankings.csv')
        mentor_path = data_dir.joinpath('mentor_rankings.csv')
        mentor_capacities_path = data_dir.joinpath('capacities.csv')

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.from_csv_files(mentee_path,
                                    mentor_path,
                                    mentor_capacities_path)

    def test_bad_mentor_path(self):
        data_dir = util.test_data_dir().joinpath('data/good_csv')
        mentee_path = data_dir.joinpath('mentee_rankings.csv')
        mentor_path = data_dir.joinpath('mentorz_rankings.csv')
        mentor_capacities_path = data_dir.joinpath('capacities.csv')

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.from_csv_files(mentee_path,
                                    mentor_path,
                                    mentor_capacities_path)

    def test_bad_capacity_path(self):
        data_dir = util.test_data_dir().joinpath('data/good_csv')
        mentee_path = data_dir.joinpath('mentee_rankings.csv')
        mentor_path = data_dir.joinpath('mentor_rankings.csv')
        mentor_capacities_path = data_dir.joinpath('capacitiesz.csv')

        with self.assertRaises(matching.InvalidProblemStatement):
            matching.from_csv_files(mentee_path,
                                    mentor_path,
                                    mentor_capacities_path)

    def test_valid_ranking(self):
        data_dir = util.test_data_dir().joinpath('data/good_csv')
        mentee_path = data_dir.joinpath('mentee_rankings.csv')
        mentor_path = data_dir.joinpath('mentor_rankings.csv')
        mentor_capacities_path = data_dir.joinpath('capacities.csv')

        res = matching.from_csv_files(mentee_path,
                                      mentor_path,
                                      mentor_capacities_path)
        self.assertDictEqual(res.mentee_rankings, {'S1': ['M1', 'M2'],
                                                   'S2': ['M1']})
        self.assertDictEqual(res.mentor_rankings, {'M1': ['S1'], 'M2':
                                                   ['S1', 'S2']})
        self.assertDictEqual(res.mentor_capacities, {'M1': 1,
                                                     'M2': 2})


class TestPosetToOrdered(unittest.TestCase):
    def test_total_ordering_unchanged(self):
        mentee = {
            'S1': ['M1', 'M2'],
            'S2': ['M2', 'M1']
        }
        mentor = {
            'M1': ['S2', 'S1'],
            'M2': ['S2', 'S1']
        }
        capacities = {'M1': 1, 'M2': 1}

        res = matching.poset_to_ordered(
            MatchStatement(mentee, mentor, capacities))

        self.assertDictEqual(mentee, res.mentee_rankings)
        self.assertDictEqual(mentor, res.mentor_rankings)
        self.assertDictEqual(capacities, res.mentor_capacities)

    def test_partial_ordering_expanded(self):
        mentee = {
            'S1': [],
            'S2': ['M2', 'M1'],
            'S3': ['M1', 'M3', 'M2']
        }
        mentor = {
            'M1': ['S1', 'S2', 'S3'],
            'M2': ['S3'],
            'M3': ['S2', 'S1']
        }
        capacities = {'M1': 1, 'M2': 1, 'M3': 1}

        for _ in range(2**10):
            res = matching.poset_to_ordered(
                MatchStatement(mentee, mentor, capacities))

            self.assertDictEqual(res.mentor_capacities, capacities)
            self.assertEqual(res.mentee_rankings.keys(), mentee.keys())
            self.assertEqual(res.mentor_rankings.keys(), mentor.keys())

            for rankings in res.mentee_rankings.values():
                self.assertEqual(len(set(rankings)), 3)

            s_1 = res.mentee_rankings['S1']
            self.assertEqual(set(s_1[:2]), set(['M1', 'M3']))
            self.assertEqual(s_1[2], 'M2')
            self.assertEqual(res.mentee_rankings['S2'], ['M2', 'M1', 'M3'])
            self.assertEqual(res.mentee_rankings['S3'], ['M1', 'M3', 'M2'])

            for rankings in res.mentor_rankings.values():
                self.assertEqual(len(set(rankings)), 3)

            self.assertEqual(res.mentor_rankings['M1'], ['S1', 'S2', 'S3'])
            self.assertEqual(res.mentor_rankings['M2'], ['S3', 'S2', 'S1'])
            self.assertEqual(res.mentor_rankings['M3'], ['S2', 'S1', 'S3'])


class TestSolve(util.TestWithTempDirectory):
    def test_solve(self):
        mentee_path, mentor_path, mentor_capacities_path = \
            util.match_inputs('data/good_csv')
        results_path = self.match_output()

        matching.solve(mentee_path,
                       mentor_path,
                       mentor_capacities_path,
                       results_path)

        with open(results_path, 'r') as results_file:
            match = sorted(list(csv.reader(results_file)))
            self.assertEqual(len(match), 2)

            self.assertEqual(len(match[0]), 2)
            self.assertEqual(match[0][0], 'M1', 'S1')

            self.assertEqual(len(match[1]), 2)
            self.assertEqual(match[1][0], 'M2', 'S2')

if __name__ == '__main__':
    unittest.main()  # pragma: no cover
