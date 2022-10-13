#!/usr/bin/env python3
'''
Script to perform some simple management and get some information form bibtex files.

'''
import yapbib.biblist as biblist
from yapbib.version import VERSION
import argparse

parser = argparse.ArgumentParser(
    description='"Manage bibliography database(s) stored in sqlite"')
# parser.add_argument('files', metavar='File', nargs='+',
#                     help='Name(s) of database files to manage')

parser.add_argument("-f", "--add-file", action="store",
                    help="Name of file to add to database")

args = parser.parse_args()

# files = args.files
dbname = 'biblio.db'
##########################################################################
# Create the List object
b = biblist.BibList()
b.import_bibtex(args.add_file)
b.export_database(dbname)
