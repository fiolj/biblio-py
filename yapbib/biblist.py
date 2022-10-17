#!/usr/bin/env python
'''
Class storing a bibliography

A Class that store a list of references (list of papers, books, manuals, ...)
It is based in dictionaries, with a unique self-generated key

Example of use:

import yapbib.biblist as biblist
b=biblist.BibList()
b.import_bibtex("mybib.bib")
items= b.List() # Shows the keys of all entries
it= b.get_item(items[0]) # Get first item
# (Alternatively, to get the first item you can use
it= b.get_items()[0]
it.get_fields() # Show all fields for item
it.preview()    # Show a preview (brief info)
bib= it.to_bibtex() # get item in BibTeX form
tex= it.to_latex() # get item in LaTeX form
html= it.to_html() # get item in html form
print(it)  # print full information on the item
print(unicode(it)) # Use this if it has non-ascii characters

'''
import sys
import os
from pathlib import Path
import pickle as pickle

# import bibitem
# import helper
# import latex
from . import bibitem
from . import helper
from . import latex
from . import bibdb
latex.register()


# Index used internally for each part of a name
# (A_VON, A_LAST, A_FIRST, A_JR)= range(4)

class BibList(dict):
  """Class storing a bibliography(list of papers, books, manuals, ...)"""

  def __init__(self):
    self.ListItems = []
    self.abbrevDict = dict(helper.standard_abbrev)
    self.sortorder = ['_type', 'key']  # Fields used to sort the list
    self.sortedList = []   # Sorted version of ListItems
    self.issorted = False  # Keeps tracks whether the List is sorted
    self.reverse = False
    self.keepAbbrevs = True
    self.encoding = 'utf-8'
    self.bib = {}

  def __len__(self):
    return len(self.ListItems)

  def update(self, blist):
    """
    Update the bibiography list with a new bibliography list

    Parameters
    ----------
    blist : BibList or dict Object
    """
    try:
      self.bib.update(blist.bib)  # blist es un objeto del tipo BibList
      self.set_properties_from(blist)
    except BaseException:
      try:
        self.bib.update(blist)  # blist es solo un diccionario
      except BaseException:
        raise TypeError('Argument incorrect type, must be BibList object')

  def set_properties_from(self, blist):
    """Copy properties from other biblist object

    Does not fail if properties are not found

    Parameters
    ----------
    blist : BibList object
    """
    # JF: TODO: If blist is a dictionary we could make the list from the keys()
    try:
      self.ListItems += blist.ListItems
    except BaseException:
      pass
    else:
      self.ListItems = list(set(self.ListItems))

    try:
      self.abbrevDict.update(blist.abbrevDict)
    except BaseException:
      pass

    if self.issorted:
      self.sort()
    else:
      self.sortedList = self.ListItems[:]

  def __str__(self):
    s = ''
    if not self.issorted:
      self.sortedList = self.sort()
    for l0 in self.sortedList:
      s += '%s\n' % (self.get_item(l0).__str__())
    # return s.encode(self.encoding, 'ignore')
    return s

  def __repr__(self):
    s = f"bib= {str(self.bib)}\n"
    s += f'abbrevDict= {self.abbrevDict}\n'
    s += f'ListItems= {self.ListItems}\n'
    s += f'sortedList= {self.sortedList}\n'
    s += f'issorted= {self.issorted}\n'
    s += f'encoding= {self.encoding}\n'
    return s

  def preview(self, n=None):
    """Show a preview of the publications (sorted).

    Optionally, only show the first n of them. If n is None, show all publications.

    Parameters
    ----------
    n : int
      If not None, only the first n values are shown (Default value = None)

    Returns
    -------

    """
    s = ''
    nn = len(self.ListItems)
    if n is not None:
      nn = min(n, nn)
    if not self.issorted:
      self.sort()
    for li in self.sortedList[:nn]:
      s += '{}\n'.format(self.get_item(li).preview())

    # s = str(s, self.encoding, 'ignore')
    return s

  def add_item(self, bib, key=None):
    """Add a new bibliography entry into the list

    Parameters
    ----------
    bib : BibItem object or dict

    key : string
      key  (Default value = None)

    Returns
    -------
    string:
      Internal key of added item or None on failing
    """
    be = bibitem.BibItem(bib, key)
    key = be.get_key()
    if key is None:
      sys.stderr.write('%s\nENTRY FAILED TO IMPORT: %s\n%s%s\n' %
                       (80 * '*', be.get_field('_code', ''), bib, 80 * '*'))
      return False

    if key in self.ListItems:
      if key == self.get_item(key).get_field('_code'):
        sys.stderr.write(f"W: ENTRY ALREADY PRESENT: {key} {bib['_code']}\n")
        return None

    self.bib[key] = be
    self.ListItems.append(key)
    self.sortedList.append(key)
    self.issorted = False
    return key

  def remove_item(self, key):
    """Remove an entry from the List

    Parameters
    ----------
    key : string
      The item to remove
    """
    if key in self.ListItems[:]:
      self.ListItems.remove(key)
      self.sortedList.remove(key)
      del (self.bib[key])
      return True
    else:
      return False

  def get_items(self):
    """List all items"""
    return list(self.bib.values())

  def get_item(self, key):
    """Retrieve one entry

    Parameters
    ----------
    key : string
      key of the entry to retrieve

    Returns
    -------
    BibItem object:
      Bibliography entry
    """
    return self.bib.get(key)

  def set_item(self, key, value):
    """Sets one bibliography entry that already is in the list

    If key is not in the list, does not add it.

    Parameters
    ----------
    key : string
      key to use

    value : BibItem or dict
      Value to update
    """
    "Set the value of a given item (that already exists)"
    if key in self.ListItems:
      self.bib[key].update(value)
      return True
    else:
      return False

  def insertAbbrev(self, abbrev, value):
    """
    Add an item to the list of abbreviations
    Parameters
    ----------
    abbrev : string
      name of the string

    value : string
      definition of the string

    Returns
    -------
    True or False indicating if abbrev was added
    """
    if abbrev in self.abbrevDict:
      return False
    self.abbrevDict[abbrev] = value
    return True

  # resolve all abbreviations found in the value fields of all entries
  def resolve_abbrevs(self):
    self.keepAbbrevs = False
    for k in self.ListItems:
      self.get_item(k).resolve_abbrevs(self.abbrevDict)

  def List(self):
    """List all items in bibliography """
    return self.ListItems

  def sort(self, order=[], reverse=False):
    """Sort the entries according to the specified order

    Parameters
    ----------
    order : list
      Each value is a string indicating a field (Default value = [])
    reverse : bool
      If sorting must be in reverse order  (Default value = False)
    """
    if not order:
      order = self.sortorder
    else:
      self.sortorder = order
    if reverse:
      self.reverse = reverse
    else:
      reverse = self.reverse

    numericfields = ['year', 'volume', 'number', 'firstpage', 'lastpage']
    sortorder = order
    sortorder.append('key')
    s = []
    for k in self.ListItems:
      oo = []
      for o in sortorder:
        if o in numericfields:  # For Numerical values we complete to the left with zeros
          oo.append(self.get_item(k).get(o, '').zfill(10))
        elif o == 'author':
          oo.append(self.get_item(k).get_authors_last())
        elif o == 'date':  # Shorthand for ['year','month']
          oo.append(self.get_item(k).get_field('year', '').zfill(10))
          oo.append(self.get_item(k).get_field('month', ''))
        else:
          # At the end if they have not field o
          oo.append(self.get_item(k).get_field(o, 'ZZZZ'))
      s.append(oo)

    s.sort(reverse=reverse)
    self.issorted = True
    self.sortedList = [x[-1] for x in s]
    return self.sortedList

  def search(self, findstr, fields=[], ignore_case=True, types='all'):
    """Search on the bibliography
    The result is a list with the keys of the items that match the search
    keys are the keys that we look
    types are on what kind of publication do we search (article, book,...)

    Parameters
    ----------
    findstr : string
      Expression to search for

    fields : list-like
      fields to search  (Default value = [])
    ignore_case : bool
      flag indicating if search is case sensitive   (Default value = True)
    types : string
      Type of bibliography entry to search  (Default value = 'all')

    Returns
    -------
    list:
      keys of entries where the expression is found
    """
    result = []
    for f in self.sortedList:
      if types == 'all' or self.get_item(f).get('_type') in types:
        if findstr == '*':
          found = True
        else:
          found = self.get_item(f).search(findstr, fields, ignore_case)
        if found:
          result.append(f)
    return result

#   def recreate_keys(self):
#     for b in self.sortedList[:]:
#       b1= self.get_item(b)
#       if b1 != None:
#         self.ListItems.remove(b)
#         key= b1.recreate_key()
#     self.sortedList= self.ListItems[:]
#     self.sort()

  def normalize(self):
    """Make bibtex key tha same that internal key"""
    for b in self.sortedList:
      self.get_item(b).normalize()

      # 3
      # import methods
      # 3
  def load(self, fname):
    """Load a biblist from file "fname" using the standard cPickle module.
    It can be used uncompressed or compressed with gzip or bzip

    Parameters
    ----------
    fname : string or file-like
      File where the bibliography is "dumped"

    Returns
    -------
    Biblist object:
      List of items found in file
    """
    try:
      fi = helper.openfile(fname, 'rb')
      c = pickle.load(fi)
      helper.closefile(fi)
    except BaseException:
      raise ValueError('Error loading data')
    try:
      self.update(c)
    except BaseException:
      raise ValueError('Error updating data')

  def dump(self, fname, protocol=pickle.HIGHEST_PROTOCOL):
    """Store the biblist in file "fname" using the standard cPickle module.
    It can be used uncompressed or compressed with gzip or bzip

    Parameters
    ----------
    fname : string or file-like

    protocol :
      Pickle protocol to use  (Default value = pickle.HIGHEST_PROTOCOL)
    """
    # if not '.dmp' in fname: fname='%s.dmp' %(fname)
    try:
      fo = helper.openfile(fname, 'wb')
      pickle.dump(self, fo, protocol=pickle.HIGHEST_PROTOCOL)
      helper.closefile(fo)
    except BaseException:
      raise ValueError('Error loading data')

  def import_bibtex(self, fname=None, normalize=True, ReplaceAbbrevs=True):
    """Import a bibliography (set of items) from a file
    If normalize the code (citekey) is overwritten with a standard key

    Parameters
    ----------
    fname : string or file-like
      Bibtex filename  (Default value = None)
    normalize : bool
      flag indicating if the key must be created (Default value = True)
    ReplaceAbbrevs : bool
      Replace all abbreviations in the items (Default value = True)
    """
    ncount = 0
    st, db = bibitem.bibparse.parsefile(fname)
    if st != []:
      for k, v in list(st.items()):
        self.insertAbbrev(k, v)

    self.keepAbbrevs = not ReplaceAbbrevs
    if db is not None:
      for k, v in list(db.items()):  # type(v) = dict
        if self.keepAbbrevs:
          v = bibitem.bibparse.replace_abbrevs(self.abbrevDict, v)
        key = self.add_item(v)
        if key:
          ncount += 1
          if normalize:
            self.get_item(key).normalize()  # _code is put equal to key
    self.sort()
    return ncount

  def import_database(self, fname, normalize=True):
    """Import a bibliography from a sqlite database

    Parameters
    ----------
    fname : Database filename

    normalize : bool
      flag indicating that key must be created (Default value = True)
    """
    ncount = 0
    db = bibitem.bibdb.parsefile(fname)

    for k, v in db.items():
      b1 = bibitem.BibItem(v, normalize=normalize)
      # key = b1.get_key()               # The key generated
      key = self.add_item(b1)
      if key:
        ncount += 1
        if normalize:
          self.get_item(key).normalize()  # _code is put equal to key

    self.sort()
    return ncount

  def import_ads(self, fname, normalize=True):
    """Import a bibliography (set of items) from a file
    If normalize the code (citekey) is overwritten with a standard key following our criteria

    Parameters
    ----------
    fname : Database filename

    normalize : bool
      flag indicating that key must be created (Default value = True)
    """
    ncount = 0
    db = bibitem.adsparse.parsefile(fname)
    if db is not None:
      for k, v in list(db.items()):
        key = self.add_item(v)
        if key:
          ncount += 1
          if normalize:
            self.get_item(key).normalize()

    self.sort()
    return ncount

##########################################################################
    # export methods
##########################################################################
  def set_default_styles(self):
    """Reset sytles to default values """
    for item in self.get_items():
      item.set_default_styles()

  def to_bibtex(self, indent=2, width=80, fields=None, encoding='latex'):
    """Convert all entries to bibtex format. All strings are resolved.

    Parameters
    ----------
    indent : int
      Indent to use in bibtex file  (Default value = 2)
    width : int
      Width of paragraphs   (Default value = 80)
    fields : list
      List of fields to include in exported file (Default value = None)
    encoding : string
      Encoding to use for output file   (Default value = 'latex')

    Returns
    -------
    string:
      Contents of bibliography in bibtex form
    """
    if not self.issorted:
      self.sort()

    s = ''
    if self.keepAbbrevs:
      # Abbreviations with no standard abbreviations
      abbrevs = {}
      std_abb = [x[0] for x in helper.standard_abbrev]
      for k in list(self.abbrevDict.keys())[:]:
        if k not in std_abb:
          abbrevs[k] = self.abbrevDict[k]

      for k in sorted(abbrevs):
        s += '@STRING{%s = "%s"}\n' % (k, self.abbrevDict[k])
      s += '\n\n'

    for l0 in self.sortedList:
      s += '%s\n' % (self.get_item(l0).to_bibtex(indent=indent,
                                                 width=width, fields=fields, encoding=encoding))

    if not self.keepAbbrevs:
      return s
    else:
      return helper.reg_defstrng.sub(r'\1\2', s)

  def export_bibtex(self, fname=None, indent=2, width=80,
                    fields=None, encoding='latex'):
    """Export a bibliography (set of items) to a file in bibtex format:

    Parameters
    ----------
    fname : string or file-like
         (Default value = None)
    indent : int
      Indent to use in bibtex file  (Default value = 2)
    width : int
      Width of paragraphs   (Default value = 80)
    fields : list
      List of fields to include in exported file (Default value = None)
    encoding : string
      Encoding to use for output file   (Default value = 'latex')
    """
    fi = helper.openfile(fname, 'w')
    s = self.to_bibtex(indent, width, fields, encoding=encoding)
    # fi.write(s.encode("utf8"))
    fi.write(s)
    helper.closefile(fi)

  ##############################

  def export_database(self, fname="biblio.db", fields=helper.allfields):
    """Export a bibliography (set of items) to a file in bibtex format:

    Parameters
    ----------
    fname : string or file-like
         (Default value = "biblio.db")
    indent : int
      Indent to use in bibtex file  (Default value = 2)
    width : int
      Width of paragraphs   (Default value = 80)
    fields : list
      List of fields to include in exported file (Default value = helper.allfields)
    """
    fi = Path(fname)
    con = bibdb.create_dbconnection(fi)
    if con is None:
      return None

    tblnm, cols = bibdb.get_dbcolnames(con)
    if tblnm == '':             # Empty database -> Create the table
      tblnm = bibdb.DB_TBLNM
      cols = fields
      bibdb.create_dbbib(con, fields=cols, tablename=tblnm)
    else:
      try:
        assert (tblnm == bibdb.DB_TBLNM and fields ==
                helper.allfields), "Database table name and columns  must coincide exactly with default at this moment"
      except AssertionError as e:
        print(e)

    # Agregamos los items
    cur = con.cursor()
    form = f"{','.join(len(cols)*'?')}"  # Formato
    for it in self.get_items():
      key = it.get_field('_code')
      r = cur.execute(
          f"SELECT EXISTS(SELECT 1 FROM {tblnm} WHERE _code='{key}' LIMIT 1);")
      if r.fetchone()[0]:
        print(f"Entry {key} already present. Not adding.")
      else:
        v = it.to_dbformat(fields=cols)
        cur.execute(f"INSERT INTO {tblnm} VALUES({form});", tuple(v))

    con.commit()
    con.close()

  ##############################

  def to_latex(self, style={}, label=r'\item'):
    """Convert to latex form

    Parameters
    ----------
    style : dict
      Definition of style used for each field (Default value = {})
    label : string
      prefix to use before each entry (Default value = r'\\item')

    Returns
    -------
    string:
      Latex-formated list of items
    """
    if not self.issorted:
      self.sort()

    s = ''
    for l0 in self.sortedList:
      if self.keepAbbrevs:
        # copy the item to resolve_abbrevs
        bib = bibitem.BibItem(self.get_item(l0))
        bib.resolve_abbrevs(self.abbrevDict)
        ss = bib.to_latex(style)
      else:
        ss = self.get_item(l0).to_latex(style)
      s += f'{label} {ss}\n'
    return s

  def export_latex(self, fname=None, style={},
                   label=r'\item', head=None, tail=None):
    """Export a bibliography (set of items) to a file in latex format:

    Parameters
    ----------
    fname : string or file-like
      Output filename (Default value = None)
    style : dict
      Definition of style used for each field (Default value = {})
    label : string
      prefix to use before each entry (Default value = r'\\item')
    head : string
      Text to include before list (Default value = None)
    tail : string
      Text to include after list (Default value = None)
    """
    if head is None:
      head = r'''\documentclass[12pt]{article}
\newcommand{\authors}[1]{#1}
\usepackage{hyperref}
\begin{document}
\begin{enumerate}
'''
    if tail is None:
      tail = r'\end{enumerate} \end{document}'
    # s = '%s\n%s\n%s\n' % (head, self.to_latex(style=style,
    #                                           label=label).encode('latex').decode('utf-8'),
    #                       tail)
    # fi = helper.openfile(fname, 'w'); fi.write(s); helper.closefile(fi)
    # s = '%s\n%s\n%s\n' % (head, self.to_latex(style=style, label=label),
    # tail)
    s = '{}\n{}\n{}\n'.format(
        head, self.to_latex(
            style=style, label=label), tail)
    # print('***S***', s)
    fi = helper.openfile(fname, 'w', encoding='latex')
    fi.write(s)
    helper.closefile(fi)

  ##############################
  def to_html(self, style={}):
    """Convert to html form

    Parameters
    ----------
    style : dict
      Definition of style used for each field (Default value = {})

    Returns
    -------
    string:
      Contents in html form
    """
    if not self.issorted:
      self.sort()

    s = ''
    for li in self.sortedList:
      tipo = self.get_item(li).get_field('_type', 'article')

      if self.keepAbbrevs:
        # copy the item to resolve_abbrevs
        bib = bibitem.BibItem(self.get_item(li))
        bib.resolve_abbrevs(self.abbrevDict)
        ss = bib.to_html(style)
      else:
        ss = self.get_item(li).to_html(style)
      s += '<li class="%s"> %s </li>\n' % (tipo, ss)
    return s

  def export_html(self, fname=None, style={}, head='', tail='',
                  separate_css='biblio.css', css_style=None, encoding='utf-8'):
    """Export a bibliography (set of items) to a file in html format: style is a dictionary
    (like in bibitem objects) where the values is a pair (open,close) to insert around the
    data.
    head and tail
    separate_css may have the

    Parameters
    ----------
    fname : string or file-like
      Output filename (Default value = None)
    style : dict
      Definition of style used for each field (Default value = {})
    head : string
      html code to insert before the list of publications  (Default value = '')
    tail : string
      html code to insert after the list of publications  (Default value = '')
    separate_css : string
      Name of a css style sheet file (Default value = 'biblio.css')
    css_style : string
      css style (Default value = None)
    encoding : string
      HTML encoding  (Default value = 'utf-8')
    """
    # default style
    def_css_style = """
.title a,
.title {font-weight: bold;	color :    #416DFF; }
ol.bibliography li{	margin-bottom:0.5em;}
.journal {  font-style: italic;}
.book .series {  font-style: italic;}
.journal:after {content:" ";}
.series:after {content:" ";}
li.article .publisher {display:none;}
.publisher:before {content:" (";}
.publisher:after {content:") ";}
.year:before {content:" (";}
.year:after {content:").";}
.authors {font-weight:bold; display:list;}
.authors:after {content:". ";}
.volume { font-weight: bold;}
.book .volume: before { content: "Vol. ";}
.number:before {content:":";}
.button {display:inline; border: 3px ridge;line-height:2.2em;margin: 0pt 10pt 0pt 0pt;padding:1pt;}
.masterthesis:before{font-weight: bold;content:"Master Thesis"}
.phdthesis:before{font-weight: bold;content:"Phd Thesis"}
div.abstracts {display: inline; font-weight: bold; text-decoration : none;  border: 3px ridge;}
div.abstract {display: none;padding: 0em 1% 0em 1%; border: 3px double rgb(130,100,110); text-align: justify;}
    """
    if css_style is None:
      css_style = def_css_style

    if helper.is_string_like(separate_css):
      the_path, fname_css = os.path.split(separate_css)
      fpath = os.path.dirname(fname)
      the_path = os.path.normpath(os.path.join(fpath, the_path))
      fname_css = os.path.join(the_path, fname_css)
      css = '  <link title="new" rel="stylesheet" href="' + \
          separate_css + '" type="text/css">'
      fi = helper.openfile(fname_css, 'w')
      fi.write(css_style)
      helper.closefile(fi)
    else:
      css = '<style type="text/css">' + css_style + '</style>'

    if head == '':
      head = '''
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=''' + encoding.upper() + '''">
    ''' + css + '''
    <title>Publicaciones</title>
    <script language="JavaScript" type="text/javascript">
    //<![CDATA[
    function toggle(thisid) {
    var thislayer=document.getElementById(thisid);
    if (thislayer.style.display == 'block') {
    thislayer.style.display='none';
    } else {
    thislayer.style.display='block';}
    }
    //]]>
    </script>
    </head>
    <body>
    <h2>Publicaciones</h2>
    <ol class="bibliography">
    '''
    if tail == '':
      tail = """
      </ol>
      </body>
      </html>
      """

    s = head + self.to_html(style=style) + tail
    fi = helper.openfile(fname, 'w')
    # fi.write(s.encode(encoding, 'xmlcharrefreplace'))
    fi.write(s)
    helper.closefile(fi)

  ##############################
  def to_xml(self, prefix='', indent=2):
    """Convert to xml form

    Parameters
    ----------
    prefix : string
      Text to include before output  (Default value = '')
    indent : int
      Indent to use (Default value = 2)

    Returns
    -------
    string:
      Contents in xml format
    """
    if not self.issorted:
      self.sort()

    s = ""
    for li in self.sortedList:
      # copy the item to resolve_abbrevs
      bib = bibitem.BibItem(self.get_item(li))
      if self.keepAbbrevs:
        bib.resolve_abbrevs(self.abbrevDict)
      s += f"{bib.to_xml(p=prefix, indent=indent)}"
    return s

  def export_xml(self, fname=None, prefix='', head='', tail='', indent=2):
    """Export a bibliography (set of items) to a file in xml format:
     But if added both head and tail
    should take it into account to make it a valid xml document

    Parameters
    ----------
    fname : string or file-like
      Output filename (Default value = None)
    prefix : string
      A prefix may be added to account for a namespace.  (Default value = '')
    head : string
      xml code to insert before the list of publications  (Default value = '')
    tail : string
      xml code to insert after the list of publications  (Default value = '')
    indent : int
         (Default value = 2)
    """
    if head == '':
      head = '''<?xml version="1.0" encoding="utf-8"?>
  <''' + prefix + '''bibliography>
'''
    if tail == '':
      tail = "\n</" + prefix + "bibliography>"

    s = head + self.to_xml(prefix=prefix) + tail
    fi = helper.openfile(fname, 'w')
    # fi.write(s.encode('utf-8', 'xmlcharrefreplace'))
    fi.write(s)
    helper.closefile(fi)

  def output(self, fout=None, formato=None, verbose=True):
    """Export all entries to a fout file with default options. All strings are resolved.
    following formats are defined:
          short (default)
          full
          bibtex
          latex
          html
          xml
          database

    Parameters
    ----------
    fout : string or file-like
         (Default value = None)
    formato : string
      One of the possible formats (Default value = None)
    verbose : bool
      Print informational text (Default value = True)

    """
    def write_full(fout):
      """Writer in full format

      Parameters
      ----------
      fout : string or file-like
      """
      fi = helper.openfile(fout, 'w')
      fi.write(str(self))
      helper.closefile(fi)

    def write_short(fout):
      """Output in Short format

      Parameters
      ----------
      fout : string or file-like
      """
      # fi = helper.openfile(fout, 'w');
      # fi.write(self.preview().encode(self.encoding))
      fi = helper.openfile(fout, 'w')
      fi.write(self.preview())
      helper.closefile(fi)

    # Available export methods
    exp_meth = {'b': self.export_bibtex, 'd': self.export_database,
                'l': self.export_latex, 't': self.export_latex,
                'h': self.export_html, 'x': self.export_xml,
                's': write_short, 'f': write_full
                }
    if verbose:
      print(('# %d items to output' % (len(self.ListItems))))

    if formato is not None:
      fform = formato[0].lower()
    else:
      if (fout is not None) and (fout != '-'):
        fform = os.path.splitext(fout)[1][1].lower()
      else:
        fform = 's'
    exp_meth[fform](fout)


##########################################################################
##########################################################################

def test():
  if sys.argv[1:]:
    filepath = sys.argv[1]
  else:
    print("No input file")
    print(("USAGE:  " +
           sys.argv[0] +
           " FILE.bib\n\n  It will output the XML file: FILE.xml"))
    sys.exit(2)

  biblio = BibList()
  if filepath.find('.bib') != -1:
    nitems = biblio.import_bibtex(filepath, False, False)
    print(('%s\nFrom BibTeX file: %s' % (80 * "*", filepath)))
  elif filepath.find('.ads') != -1:
    nitems = biblio.import_ads(filepath, True)
    print(('%s\nFrom ADS file: %s' % (70 * "*", filepath)))
  print(('%d items ingresados\n' % (nitems)))
  print(('Rodrig en los siguientes items:', biblio.search('Rodrig')))
  print((20 * '='))
  print(('Items Ordenados por cite: %s' % (biblio.sort(['key']))))
  print((20 * '*'))
  print(('Items Ordenados por Apellido de Autores: %s' %
         (biblio.sort(['author']))))
  print((20 * '*'))
  print(('Items Ordenados por Fecha: %s' % (biblio.sort(['date']))))
  print((20 * '*'))
  nn = 5
  print(('Preview (At most %d items):' % (nn)))
  print((20 * '*'))
  print((biblio.preview(nn)))
  print(('Preview with LaTeX symbols (At most First %d items):' % (nn)))
  print((20 * '*'))
  print((biblio.preview(nn).encode('latex')))
  biblio.export_bibtex('tempo.bib', 4)
  biblio.export_html('tempo.html')
  biblio.export_xml('tempo.xml', prefix='')


def main():
  test()


if __name__ == "__main__":
  main()
