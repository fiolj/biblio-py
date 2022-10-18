#!/usr/bin/env python3
'''
Script to perform some simple management and get some information form bibtex files.

'''
import yapbib.biblist as biblist
from yapbib.version import VERSION
from pathlib import Path
from os import getenv
import argparse

##########################################################################
# CUSTOMIZE THESE VARIABLES if needed
dumpfile = getenv('BIBDB', Path().home() / 'texmf/bibtex/bib/bib.dmp')

# *******************************************************************************
encoding = 'utf8'


def main():
  # CONFIGURACION ############################################################
  def get_strng_field(k):
    # l= str(k,encoding=encoding).split(':')
    strf = k.split(':')
    if len(strf) == 1:  # argument was on the form 'search_string. To search in all fields
      ff = []
      ss = strf[0]
    elif len(strf) == 2:
      if strf[0] == '':
        ss = '*'  # Search all strings
      else:
        ss = strf[0]
      if strf[1] == '':
        ff = []  # Search in all fields
      else:
        ff = strf[1].split(':')
    return ss, ff

  ##########################################################################
  # Command line options
  ##########################################################################
  ejemplos = """
  Ejemplo de uso:

  $> %prog --search=LastName1:author --search=LastName2:author --search=LastName3:author --startyear=2000 --endyear=2008 --filter-exclude=2006:year --filter-exclude=LastName4:author --sort=year,month,author --format=tex --output=salida.tex biblio1.bib biblio2.bib.bz2 biblio1.dmp biblio2.dmp.gz

Will get data from two bibtex files (biblio1.bib and biblio2.bib.bz2) and two dump files (biblio1.dmp and biblio2.dmp.gz) and retain all entries between 2000 and 2008 (except those of 2006) by authors LastName1,LastName2 and LastName3 but where LastName4 is not an author. The search is case insensitive. The output is written in latex form, ordered by key in ascending order, to the file salida.tex

  $> %prog - -o biblio.html
Will get the data from standard input in BibTeX format and output it in html form to the file biblio.html

                           ******** Working with pipes ********
  $> %prog -s LastName1:author biblio1.bib -f bib -o - | %prog -s LastName2:author biblio2.dmp - -o biblio.html

Will get the items with LastName1 as author from biblio1.bib and the results are taken as input to merge with items by LastName2 from database biblio2.dmp. The output is in html format to the file biblio.html

Note that two of the input files are compressed
  """

  parser = argparse.ArgumentParser(
      description="Manage bibliography lists",
      formatter_class=argparse.RawDescriptionHelpFormatter,
      epilog=ejemplos)

  parser.add_argument("--version", action='version',
                      version=f"%(prog)s with biblio-py-{VERSION}",
                      )
  parser.add_argument("--list", action="store_true", default=False,
                      help="List the database unique keys and exit")
  parser.add_argument('files', metavar='File', nargs='+',
                      help='Files to process (data accumulates)')
  parser.add_argument("-o", "--output", default=None, metavar="Output",
                      help="Output file. Use '-' for stdout (screen)")

  parser.add_argument('--repeated', choices=['ignore', 'replace', "merge-old", "merge-new"], default='ignore',
                      help="Action to take when importing repeated entries")
  parser.add_argument("--sort",
                      help="Sort the items according to the following fields, for instance to sort them accoding to year and then author we would use --sort=year,author. In the same example, to sort in reverse order we would use: --sort=year,author,reverse. (default: key).")

  parser.add_argument("-s", "--search", action='append',
                      help='SEARCH is a (COLON separated) pair "string_to_search:fields". If the field is empty defaults to ALL. Fields may be more than one. In that case it can be written as "field1,field2,...". This option may be used more than once')

  parser.add_argument("--year", default=None,
                      help="--year=y is a shortcut to '--start-year=y --end-year=y'")

  parser.add_argument("-b", "--startyear", type=int, default=0,
                      help='Start Year')

  parser.add_argument("-e", "--endyear", type=int, default=9999,
                      help='End Year')

  parser.add_argument("-i", "--filter-include", action='append',
                      help='Include all entries that verify the condition, given in the form string1:field1,field2,...  It may be used more than once and only entries that verify ALL conditions will be retained.')

  parser.add_argument("-x", "--filter-exclude", action='append',
                      help='Exclude all entries that verify the condition, given in the form string1:field1,field2,...  It may be used more than once and only entries that do not verify ANY condition will be retained.')

  parser.add_argument("--keep-keys", action="store_true", default=False,
                      help="Keep the original cite key")

  parser.add_argument("-I", "--case-sensitive", action="store_true", default=False,
                      help="Make the search case sensitive")

  parser.add_argument("-f", "--format", default=None,
                      help="format of output, possible values are: short, full, bibtex, tex, html, xml   DEFAULT= short")

  parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Give some informational messages.")

  parser.add_argument("-d", "--save-dump",
                      help="Save (dump) the database IN INTERNAL FORM for faster access")

  # (op, args) = parser.parse_args()

  args = parser.parse_args()

  if args.files == []:
    dbfiles = [dumpfile]
  else:
    dbfiles = args.files

  ignore_case = not args.case_sensitive
  modify_keys = not args.keep_keys
  available_formats = {
      's': 'short',
      'f': 'full',
      't': 'latex',
      'b': 'bibtex',
      'h': 'html',
      'x': 'xml',
      'd': 'database'}

  # Try to guess the format from the extension of the file
  if args.format is None:    # Guess a format
    if args.output == '-':
      formato = 'short'
    elif args.output is not None:
      ext = Path(args.output).suffix[1]
      formato = available_formats.get(ext, 'short')
  else:
    formato = available_formats.get(args.format[0].lower(), 'short')

  ##########################################################################
  # Create the List object
  b = biblist.BibList()
  ##########################################################################
  # Read the database(s)
  if args.verbose:
    print('# Loading database...')

  for fname in dbfiles:
    failed = False
    if '.dmp' in fname:
      try:
        b.load(fname)
      except BaseException:
        failed = True
    elif '.bib' in fname or fname == '-':
      try:
        b.import_bibtex(fname, normalize=modify_keys)
      except BaseException:
        failed = True
    elif '.db' in fname:
      try:
        b.import_database(fname, normalize=modify_keys)
      except BaseException:
        failed = True
    else:
      failed = True
    if args.verbose:
      print(f'# {len(b.ListItems)} new items read')

    if failed:
      mensaje = f"Database {fname} not found or failed to load.\n"
      mensaje += "Set the name as an option or set the environment variable BIBDB\n"
      parser.error(mensaje)

  if args.sort is not None:
    sortorder = args.sort.lower().split(',')
    if 'reverse' in sortorder:
      reverse = True
    else:
      reverse = False
    if reverse:
      sortorder.remove('reverse')
  else:
    sortorder = []
    reverse = False

  ##########################################################################
  # Do the required action(s)
  bout = biblist.BibList()
  items = b.sortedList[:]  # All items
  bout.abbrevDict.update(b.abbrevDict)

  if args.list:
    b.sort(sortorder, reverse)
    print('\n'.join(b.sortedList))
    return

  for k in items:
    year = int(b.get_item(k).get_field('year', str(args.startyear)))
    if year >= args.startyear and year <= args.endyear:
      # bout.add_item(b.get_item(k), k)
      bout.add_item(b.get_item(k))

  if args.search:
    items = []  # overwrite items from sort
    for cond in args.search:
      ss, ff = get_strng_field(cond)
      # search and append the results.
      items.extend(bout.search(findstr=ss, fields=ff,
                               ignore_case=ignore_case))
    for it in bout.sortedList[:]:  # purge not found items
      if it not in items:
        bout.remove_item(it)

  if args.filter_exclude is not None:
    items = []
    for cond in args.filter_exclude:
      ss, ff = get_strng_field(cond)
      items.extend(b.search(findstr=ss, fields=ff,
                            ignore_case=ignore_case))
    for it in bout.sortedList[:]:    # purge found items
      if it in items:
        bout.remove_item(it)

  if args.filter_include is not None:
    items = []
    cond = args.filter_include[0]
    ss, ff = get_strng_field(cond)
    items = b.search(findstr=ss, fields=ff, ignore_case=ignore_case)
    for cond in args.filter_include[1:]:
      ss, ff = get_strng_field(cond)
      its = b.search(findstr=ss, fields=ff, ignore_case=ignore_case)
      for c in items[:]:
        if c in items and c not in its:
          items.remove(c)
    for it in bout.sortedList[:]:    # purge not found items
      if it not in items:
        bout.remove_item(it)

  # First sort
  if args.sort:
    bout.sort(sortorder, reverse=reverse)

  if args.output:
    bout.output(args.output, formato, args.verbose)
    if args.verbose:
      print(f"# Saving database to {args.output}")
  else:
    print(f"# {len(bout.ListItems)} items processed")

  if args.save_dump:
    if args.verbose:
      print(f"# Saving database to {args.save_dump}...")
    bout.dump(args.save_dump)


if __name__ == "__main__":
  main()


# Local Variables:
# tab-width: 2
# END:
