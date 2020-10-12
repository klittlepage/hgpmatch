# pylint: disable=missing-docstring

import csv
import sys
import unittest

from unittest.mock import patch

import hgp.match.main as match_main

import tests.match.util as util


class TestVerifyAndTransform(util.TestWithTempDirectory):
    def build_args_for_base_dir(self, base_dir):
        mentee_path, mentor_path, mentor_capacities_path = \
            util.match_inputs(base_dir)
        results_path = self.match_output()

        return ['hgpmatch',
                str(mentee_path.absolute()),
                str(mentor_path.absolute()),
                str(mentor_capacities_path.absolute()),
                str(results_path.absolute())]

    def test_main_bad_command_line_args(self):
        with patch.object(sys, 'argv', ['hgpmatch']):
            with self.assertRaises(SystemExit):
                match_main.main()

    def test_main_bad_data(self):
        args = self.build_args_for_base_dir('data/bad_csv')
        with patch.object(sys, 'argv', args):
            with self.assertRaises(SystemExit):
                match_main.main()

    def test_main(self):
        args = self.build_args_for_base_dir('data/good_csv')
        with patch.object(sys, 'argv', args):
            match_main.main()

            with open(args[-1], 'r') as results_file:
                match = sorted(list(csv.reader(results_file)))
                self.assertEqual(len(match), 2)


if __name__ == '__main__':
    unittest.main()  # pragma: no cover
