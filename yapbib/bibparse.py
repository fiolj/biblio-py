#!/usr/bin/env python
from . import helper
"""
Set of routines to parse bibtex data and return each entry as a dictionary
It is mainly intended as a helper file to the Class BibItem (see bibitem.py)
but can be used as a standalone script

USAGE:
  strings,db = parsefile(bibtexfile)

"""


import sys
import re
import string
import codecs
from . import latex
# from pylatexenc.latex2text import LatexNodes2Text
latex.register()

reg_pages = re.compile(r'\W+')


def process_pages(pages):
  """Process a range of pages and return initial and final pages

  Parameters
  ----------
  pages : string
    a string of the form: xxx or mmm-nnn (where m and n are numbers)

  Returns
  -------
  tuple of strings:
    2-tuple (firstpage,lastpage)
  """
  pp = reg_pages.split(pages)
  firstpage = pp[0]
  if len(pp) == 2:
    lastpage = pp[1]
  else:
    lastpage = ''
  return firstpage, lastpage


def bibtexauthor(data):
  """Process a list of author in bibtex form and Returns a list of authors
  where each author is a list of the form:

                    [von, Last, First, Jr]

  Parameters
  ----------
  data : string
    Author list given in standard bibtex form


  Returns
  -------
  list:
    Each element is an author, described by a list
  """
  return list(map(helper.process_name, data.split(' and ')))


def get_fields(strng, strict=False):
  """Process a string from a bibtex entry and identify fields and values

  Parameters
  ----------
  strng : string

  strict : bool
    If True, only fields recognized by program bibtex are included  (Default value = False)

  Returns
  -------
  list:
    Each element is a pair (field, value)
  """

  comma_rex = re.compile(r'\s*[,]')
  ss = strng.strip()

  if not ss.endswith(','):  # Add the last commma if missing
    ss += ','

  fields = []

  while True:
    name, sep, ss = ss.partition('=')
    name = name.strip().lower()  # This should be enough if there is no error in the entry
    if len(name.split()) > 1:   # Help recover from errors. name should be only one word anyway
      name = name.split()[-1]
    ss = ss.strip()
    if sep == '':
      break  # We reached the end of the string

    if ss[0] == '{':    # The value is surrounded by '{}'
      s, e = helper.match_pair(ss)
      data = ss[s + 1:e - 1].strip()
    elif ss[0] == '"':  # The value is surrounded by '"'
      s = ss.find(r'"')
      e = ss.find(r'"', s + 1)
      data = ss[s + 1:e].strip()
    else:  # It should be a number or something involving a string
      e = ss.find(',')
      data = ss[0:e].strip()
      if not data.isdigit():  # Then should be some string
        dd = data.split('#')  # Test for joined strings
        if len(dd) > 1:
          for n in range(len(dd)):
            dd[n] = dd[n].strip()
            dd[n] = dd[n].replace('{', '"').replace('}', '"')
            if dd[n][0] != '"':
              dd[n] = 'definitionofstring(%s) ' % (dd[n])
          data = '#'.join(dd)
        else:
          data = 'definitionofstring(%s) ' % (data.strip())
    s = ss[e].find(',')
    ss = ss[s + e + 1:]
# JF: Temporario, descomentar si hay problemas
#     if name=='title':
#       data=helper.capitalizestring(data)
#     else:
#       data=helper.removebraces(data)
    if not strict or name in helper.bibtexfields:
      fields.append((name, data))
  return fields


# Creates a (hopefully) unique key code
def create_entrycode(b={}):
  """Creates a 'hopefully unique' entry key from a bibliography item

  Parameters
  ----------
  b : dict
    describes the bibliografy entry  (Default value = {})

  Returns
  -------
  string:
    An unique key code.
  """
  len_aut = 7  # Length of the author surname used
  try:
    aut = helper.capitalizestring(f"{b['author'][0][0]}{b['author'][0][1]}")
  except BaseException:
    print("Error in bibparse.create_entrycode: ",
          (b['author']), (b['_code']), sep="\n")

  aut = helper.oversimplify(aut).strip()
  if len(aut) > len_aut:
    bibid = aut[:len_aut]
  else:
    bibid = aut

  bibid += b.get('year', '')
  bibid += b.get('journal_abbrev', '')

  if b['_type'] == 'mastersthesis':
    bibid += 'MT'
  elif b['_type'] == 'phdthesis':
    bibid += 'PHD'
  elif b['_type'] in ['book', 'incollection', 'proceedings', 'conference', 'misc', 'techreport']:
    if 'booktitle' in b:
      bibid += helper.create_initials(b['booktitle'])
    elif 'series' in b:
      bibid += helper.create_initials(b['series'])

    if 'title' in b:
      bibid += '_' + helper.create_initials(b.get('title', '').upper())[:3]

  if 'thesis' not in b['_type']:
    if 'firstpage' in b:
      bibid += 'p' + b['firstpage'].strip()
    elif 'volume' in b:
      bibid += 'v' + b['volume'].strip()
  return helper.oversimplify(bibid)


def replace_abbrevs(strs, bitem):
  """Resolve all abbreviations found in the value fields of one entry

  Parameters
  ----------
  strs : string
    STRING defined in bibtex file

  bitem : dict-like
    bibliography item

  Returns
  -------
  dict-like:
    modified bibliography item
  """
  b = bitem
  for f, v in list(b.items()):
    if helper.is_string_like(v):
      b[f] = helper.replace_abbrevs(strs, v)
  return b


def parsefile(fname=None):
  """
  Read and parses a bibtex file (*.bib)

  Parameters
  ----------
  fname : string or file-like
    Filename or file-handler   (Default value = None)

  Returns
  -------
  dict:
    Each element is a dict whose value describes a bibliography entry.
    Its key is generated automatically from the data
  """
  fi = helper.openfile(fname)
  s = fi.read()
  db = parsedata(s)
  return db


def parsedata(data):
  """Parses a string with a bibtex database

  Parameters
  ----------
  data : string
    Contents of a bibtex file

  Returns
  -------
  tuple: (strings, entries)
    - strings is a dict with all defined strings
    - entries is a dict with all the bibtex entries
  """
  # Regular expressions to use
  # A '@' followed by any word and an opening
  pub_rex = re.compile(r'\s?@(\w*)\s*[{\(]')
  # brace or parenthesis
  ##########################################################################
  #################### Reformat the string ####################
  ss = re.sub(r'\s+', ' ', data).strip()

  # Find entries
  strings = {}
  preamble = []
  comment = []
  tmpentries = []
  entries = {}

  while True:
    entry = {}
    m = pub_rex.search(ss)
    if m is None:
      break

    if m.group(0)[-1] == '(':
      d = helper.match_pair(ss, pair=('[(]', '[)]'), start=m.end() - 1)
    else:
      d = helper.match_pair(ss, start=m.end() - 1)

    if d is not None:
      current = ss[m.start():d[1] - 1]  # Currently analyzed entry
      st, entry = parseentry(current)
      if st is not None:
        strings.update(st)
      if entry is not None and entry != {}:
        entries[entry['_code']] = entry
      ss = ss[d[1] + 1:].strip()
    else:
      # Algo falló en el archivo bibtex. Esto debería mejorarse
      print('El archivo bibtex tiene un error en la zona:' +
            ss[m.end():m.end() + 20])
      break
  return strings, entries


def parseentry(source):
  """Reads an item in bibtex form from a string

  Parameters
  ----------
  source : string

  Returns
  -------
  tuple: (None, entry) or (string, None)
  depending if the source has a bibtex STRING definition or an entry
  """
  try:
    source + ' '
  except BaseException:
    raise TypeError
  # Strip newlines and multiple spaces
  source.replace('\n', ' ')
  source = re.sub(r'\s+', ' ', source)

  entry = {}
  # st = None
  s = source.partition('{')

  if s[1] == '':
    return None, None

  arttype = s[0].strip()[1:].lower()

  if arttype == 'string':
    # Split string name and definition, removing outer "comillas" and put them
    # in a list
    name, defin = s[2].strip().split("=")
    defin = defin.replace('"', '').strip()
    if defin.startswith('{'):
      defin = defin[1:-1]
    return {name.strip(): defin.strip()}, None

  elif arttype in helper.alltypes:
    # Then it is a publication that we want to keep
    p = re.match('([^,]+),', s[2])  # Look for the key followed by a comma
    entry['_type'] = arttype
    entry['_code'] = p.group()[:-1]
    ff = get_fields(s[2][p.end():])
    for n, d in ff:
      if n in helper.namefields:
        entry[n] = bibtexauthor(d)
      elif n in ['title', 'abstract']:
        # May be is better to do not change capitalization
        # t = helper.capitalizestring(d)
        # t = LatexNodes2Text().latex_to_text(d)
        t = d
        #
        # JF: Algo no está bien. Porque no estoy convertiendo latex a strings
        # entry[n] = codecs.decode(t, 'latex+utf8', 'ignore')
        #
        entry[n] = t
      elif n == 'pages':
        entry['firstpage'], entry['lastpage'] = process_pages(d)
      elif n == 'year':
        entry[n] = d.strip('.')
      else:
        entry[n] = d
    return None, entry

  elif arttype == 'comment' or arttype == 'preamble':
    # Do nothing (for now)
    return None, None
  else:
    return None, None


def test():
  """Test """
  if sys.argv[1:]:
    filepath = sys.argv[1]
  else:
    print("No input file")
    print(("USAGE:  " +
           sys.argv[0] +
           " FILE.bib\n\n  It will output the XML file: FILE.xml"))
    sys.exit(2)

  strings, db = parsefile(filepath)
  print(db)


def main():
  test()


if __name__ == "__main__":
  main()
