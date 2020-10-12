"""Main method for the hgpmatch CLI"""

import argparse
import sys

import hgp.match.matching as matching


def main():
    """Main method for the hgpmatch CLI"""
    parser = \
        argparse.ArgumentParser(
            description='Solve the mentor/mentee matching problem')
    parser.prog = 'hgpmatch'

    parser.add_argument('mentee_rankings', help='path to mentee rankings csv')
    parser.add_argument('mentor_rankings', help='path to mentor rankings csv')
    parser.add_argument('mentor_capacities',
                        help='path to mentor capacities csv')
    parser.add_argument('results', help='path to results')
    parser.add_argument('--mentor-optimal', action='store_false',
                        help='optimize matching in favor of mentors (mentee '
                             'optimal matching is the default')

    args = parser.parse_args()
    try:
        matching.solve(args.mentee_rankings,
                       args.mentor_rankings,
                       args.mentor_capacities,
                       args.results,
                       mentee_optimal=not args.mentor_optimal)
    except Exception as e:  # pylint: disable=broad-except
        print(str(e))
        sys.exit(1)
