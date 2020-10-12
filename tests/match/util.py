# pylint: disable=missing-docstring

import pathlib
import tempfile
import unittest

from typing import Tuple

def test_data_dir():
    return pathlib.Path(__file__).parent.absolute()

def match_inputs(root_dir) -> Tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    data_dir = test_data_dir().joinpath(root_dir)
    mentee_path = data_dir.joinpath('mentee_rankings.csv')
    mentor_path = data_dir.joinpath('mentor_rankings.csv')
    mentor_capacities_path = data_dir.joinpath('capacities.csv')
    return mentee_path, mentor_path, mentor_capacities_path

class TestWithTempDirectory(unittest.TestCase):
    test_dir: tempfile.TemporaryDirectory

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    def match_output(self) -> pathlib.Path:
        return pathlib.Path(self.test_dir.name).joinpath('matching.csv')
