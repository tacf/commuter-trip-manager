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
from tabulate import tabulate

def print_balances(balances):
    '''Print Balances to stdout'''
    logger.info("Listing Balances")
    balances_list = []
    for user, amount in balances.iteritems():
        balances_list.append([user, amount])
    print tabulate(balances_list, headers=['User', 'Balance'], numalign='center')

def update_balance(balances, transactions):
    '''Update Users balances'''
    for user in transactions:
        balances[user] = transactions[user] + (balances[user] if (user in balances) else 0)

def list_balances(_, database):
    '''List Users Balances'''
    balances = dict()
    # Process trips
    for trip in database['trips']:
        drv, n_passengers = trip['driver'], len(trip['passengers'])
        update_balance(balances, {drv: n_passengers})
        update_balance(balances, {passenger: -1 for passenger in trip['passengers']})
    #Process adjustments
    for adjst in database['adjustments']:
        update_balance(balances, {adjst['source']: -adjst['amount']})
        update_balance(balances, {adjst['destination']: adjst['amount']})
    print_balances(balances)

def list_transactions(args, database):
    '''List a User transactions'''
    logger.info("Listing Transactions for user: %s", args.user)
    for trip in database['trips']:
        drv, n_passengers = trip['driver'], len(trip['passengers'])
        balance = 0
        if drv == args.user:
            balance = str(n_passengers)
        if args.user in trip['passengers']:
            balance = '-1'
        if balance != 0:
            print u'{:^0}: {:^5}'.format(str(trip['date']), balance)
            print u'{:>15} {:^0}'.format('Driver:', drv)
            print u'{:>15} {:^0}'.format('Passengers:', trip['passengers'])


def get_cmd(operation):
    '''CLI verbs function bindings'''
    return {
        'balances': list_balances,
        'transactions': list_transactions
    }[operation.lower()]


def main(args):
    """ Main entry point of the app """
    with open(args.file if args.file != None else 'trips.yaml', 'r') as stream:
        try:
            database = yaml.load(stream)
            cmd = get_cmd(args.operation)
            cmd(args, database)
        except yaml.YAMLError as exc:
            logger.erro(exc)
        except KeyError:
            logger.error('Invalid Operation: %s', args.operation)


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    SUBPARSER = PARSER.add_subparsers(dest="operation",
                                      help="Specify operation [balances, transactions]")
    PARSER.add_argument("-f", "--file", action="store",
                        dest="file", help="Specify a diferent input file.")
    BALANCES_PARSER = SUBPARSER.add_parser('balances')
    TRANSACTIONS_PARSER = SUBPARSER.add_parser('transactions')
    TRANSACTIONS_PARSER.add_argument('user', help='User to list transactions')

    # Specify output of "--version"
    PARSER.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))
    ARGS = PARSER.parse_args()

    main(ARGS)
