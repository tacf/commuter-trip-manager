#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple CLI to manage your carpooling obligations with your colleagues
"""

__author__ = "Tiago Ferreira"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import yaml

from logzero import logger

def print_balances(balances):
    logger.info("Listing Balances")
    print u"{:<15} {:<0}".format('User', 'Balance')
    for user, amount in balances.iteritems():
        print u"{:<15} {:>3}".format(user, amount)

def update_balance(balances, transactions):
    for user in transactions:
        balances[user] = transactions[user] + (balances[user] if (user in balances) else 0)

def list_balances(db):
    balances = dict()
    for trip in db['trips']:
        drv, n_passengers = trip['driver'], len(trip['passengers'])
        update_balance(balances, {drv: n_passengers})
        update_balance(balances, {passenger: -1 for passenger in trip['passengers']})
    print_balances(balances)


def cmder(cmd, db):
    return {
        'balances': list_balances(db)
    }[cmd.lower()]


def main(args):
    """ Main entry point of the app """
    with open(args.file if 'file' in args else "trips.yaml", 'r') as stream:
        try:
            db = yaml.load(stream)
            cmder(args.operation, db)
        except yaml.YAMLError as exc:
            logger.erro(exc)
        except KeyError:
            logger.error("Invalid Operation: {0}".format(args.operation))


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument("operation", help="Specify operation [balances]")
    PARSER.add_argument("-f", "--file", action="store",
                        dest="file", help="Specify a diferent input file.")

    # Specify output of "--version"
    PARSER.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    ARGS = PARSER.parse_args()
    main(ARGS)
