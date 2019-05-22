#!/usr/bin/env python3
'''
Script to perform some simple management and get some information form bibtex files.

'''
import yapbib.biblist as biblist
from yapbib.version import VERSION
import yapbib
import optparse
import os
# import sys
# sys.path.insert(0, '/home/fiol/trabajo/programas/biblio-py')

##########################################################################
# CUSTOMIZE THESE VARIABLES if needed
dumpfile = os.getenv(
    'BIBDB',
    os.path.join(
        os.environ['HOME'],
        'texmf/bibtex/bib/bib.dmp'))
# *******************************************************************************
encoding = 'utf8'


def main():
  # CONFIGURACION ############################################################
  def get_strng_field(k):
    # l= str(k,encoding=encoding).split(':')
    l = k.split(':')
    if len(l) == 1:  # argument was on the form 'search_string. To search in all fields
      ff = []
      ss = l[0]
    elif len(l) == 2:
      if l[0] == '':
        ss = '*'  # Search all strings
      else:
        ss = l[0]
      if l[1] == '':
        ff = []  # Search in all fields
      else:
        ff = l[1].split(':')
    return ss, ff

  ##########################################################################
  # Command line options
  ##########################################################################
  usage = """usage: %prog [options] [datafile1] [datafile2 ...]
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
  parser = optparse.OptionParser(
      usage, version=" %prog with biblio-py-{0}".format(VERSION))

  parser.add_option("", "--list", action="store_true",
                    help="List the database contents")

  parser.add_option("", "--sort", help="Sort the items according to the following fields, for instance to sort them accoding to year and then author we would use --sort=year,author. In the same example, to sort in reverse order we would use: --sort=year,author,reverse. DEFAULT: key.")

  parser.add_option("-s", "--search", action='append', type='string',
                    help='SEARCH is a (COLON separated) pair "string_to_search:fields". If the field is empty defaults to ALL. Fields may be more than one. In that case it can be written as "field1,field2,...". This option may be used more than once')

  parser.add_option("--year", default=None,
                    help="--year=y is a shortcut to '--start-year=y --end-year=y'")

  parser.add_option(
      "-b",
      "--startyear",
      type='int',
      default=0,
      help='Start Year')

  parser.add_option(
      "-e",
      "--endyear",
      type='int',
      default=9999,
      help='End Year')

  parser.add_option(
      "-i",
      "--filter-include",
      action='append',
      type='string',
      help='Include all entries that verify the condition, given in the form string1:field1,field2,...  It may be used more than once and only entries that verify ALL conditions will be retained.')

  parser.add_option(
      "-x",
      "--filter-exclude",
      action='append',
      type='string',
      help='Exclude all entries that verify the condition, given in the form string1:field1,field2,...  It may be used more than once and only entries that do not verify ANY condition will be retained.')

  parser.add_option(
      "",
      "--keep-keys",
      action="store_true",
      default=False,
      help="Keep the original cite key")

  parser.add_option(
      "-I",
      "--case-sensitive",
      action="store_true",
      default=False,
      help="Make the search case sensitive")

  parser.add_option(
      "-o",
      "--output",
      default=None,
      help="Output file. Use '-' for stdout (screen). DEFAULT: No output")

  parser.add_option(
      "-f",
      "--format",
      default=None,
      help="format of output, possible values are: short, full, bibtex, tex, html, xml   DEFAULT= short")

  parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                    default=False, help="Give some informational messages.")

  parser.add_option(
      "-d",
      "--save-dump",
      help="Save (dump) the database IN INTERNAL FORM for faster access")

  (op, args) = parser.parse_args()

  if args == []:
    dbfiles = [dumpfile]
  else:
    dbfiles = args
  modify_keys = not op.keep_keys
  available_formats = {
      's': 'short',
      'f': 'full',
      't': 'latex',
      'b': 'bibtex',
      'h': 'html',
      'x': 'xml'}

  # Try to guess the format from the extension of the file
  if op.format is None:    # Guess a format
    if op.output == '-':
      formato = 'short'
    elif op.output is not None:
      ext = os.path.splitext(op.output)[1][1]
      formato = available_formats.get(ext, 'short')
  else:
    formato = available_formats.get(op.format[0].lower(), 'short')

  ##########################################################################
  # Create the List object
  b = biblist.BibList()
  ##########################################################################
  # Read the database(s)
  if op.verbose:
    print('# Loading database...')
  # b = biblist.BibList()
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
    else:
      failed = True
    if op.verbose:
      print('# %d new items read' % (len(b.ListItems)))

    if failed:
      mensaje = 'Database file %s not found or failed to load. Set the name as an option or set the environment variable BIBDB\n' % (
          fname)
      parser.error(mensaje)

  if op.sort is not None:
    sortorder = op.sort.lower().split(',')
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

  if op.list:
    b.sort(sortorder, reverse)
    print('\n'.join(b.sortedList))
    return

  for k in items:
    year = int(b.get_item(k).get_field('year', str(op.startyear)))
    if year >= op.startyear and year <= op.endyear:
      bout.add_item(b.get_item(k), k)

  if op.search is not None:
    items = []  # overwrite items from sort
    for cond in op.search:
      ss, ff = get_strng_field(cond)
      # search and append the results.
      items.extend(
          bout.search(
              findstr=ss,
              fields=ff,
              caseSens=op.case_sensitive))
    for it in bout.sortedList[:]:  # purge not found items
      if it not in items:
        bout.remove_item(it)

  if op.filter_exclude is not None:
    items = []
    for cond in op.filter_exclude:
      ss, ff = get_strng_field(cond)
      items.extend(b.search(findstr=ss, fields=ff, caseSens=op.case_sensitive))
    for it in bout.sortedList[:]:    # purge found items
      if it in items:
        bout.remove_item(it)

  if op.filter_include is not None:
    items = []
    cond = op.filter_include[0]
    ss, ff = get_strng_field(cond)
    items = b.search(findstr=ss, fields=ff, caseSens=op.case_sensitive)
    for cond in op.filter_include[1:]:
      ss, ff = get_strng_field(cond)
      its = b.search(findstr=ss, fields=ff, caseSens=op.case_sensitive)
      for c in items[:]:
        if c in items and c not in its:
          items.remove(c)
    for it in bout.sortedList[:]:    # purge not found items
      if it not in items:
        bout.remove_item(it)

  # First sort
  if op.sort is not None:
    bout.sort(sortorder, reverse=reverse)

  if op.output is not None:
    bout.output(op.output, formato, op.verbose)
  else:
    print('# %d items processed' % (len(bout.ListItems)))

  if op.save_dump is not None:
    if op.verbose:
      print('# Saving database to %s...' % (op.save_dump))
    bout.dump(op.save_dump)


if __name__ == "__main__":
  main()


# Local Variables:
# tab-width: 2
# END:
