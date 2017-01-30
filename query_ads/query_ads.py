#! /usr/bin/env python
# Small module to query the Harvard Database at http://adsabs.harvard.edu
# It creates the query and returns the
# import sys,os

import urllib.request
import urllib.error
import urllib.parse
import socket
import re

# Modelo de pedido
# http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PHY&db_key=PRE&qform=PHY&arxiv_sel=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&aut_logic=OR&author=Fiol%2CJ&ned_query=YES&sim_query=YES&start_mon=&start_year=&end_mon=&end_year=&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&article_sel=YES&jou_pick=NO&ref_stems=&data_and=ALL&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=&end_entry_mon=&end_entry_year=&min_score=&sort=SCORE&data_type=BIBTEX&aut_syn=YES&ttl_syn=YES&txt_syn=YES&aut_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1
# http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PHY&db_key=PRE&qform=PHY&arxiv_sel=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&aut_xct=YES&aut_logic=OR&author=Fiol%2CJ&ned_query=YES&sim_query=YES&start_mon=&start_year=2008&end_mon=&end_year=2008&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=&end_entry_mon=&end_entry_year=&min_score=&sort=NDATE&data_type=PORTABLE&aut_syn=YES&ttl_syn=YES&txt_syn=YES&aut_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1
# http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?db_key=AST&db_key=PHY&db_key=PRE&qform=PHY&arxiv_sel=astro-ph&arxiv_sel=cond-mat&arxiv_sel=cs&arxiv_sel=gr-qc&arxiv_sel=hep-ex&arxiv_sel=hep-lat&arxiv_sel=hep-ph&arxiv_sel=hep-th&arxiv_sel=math&arxiv_sel=math-ph&arxiv_sel=nlin&arxiv_sel=nucl-ex&arxiv_sel=nucl-th&arxiv_sel=physics&arxiv_sel=quant-ph&arxiv_sel=q-bio&aut_xct=YES&aut_logic=OR&author=Fiol%2CJ&ned_query=YES&sim_query=YES&start_mon=&start_year=2008&end_mon=&end_year=2008&ttl_logic=OR&title=&txt_logic=OR&text=&nr_to_return=200&start_nr=1&jou_pick=ALL&ref_stems=&data_and=ALL&group_and=ALL&start_entry_day=&start_entry_mon=&start_entry_year=&end_entry_day=&end_entry_mon=&end_entry_year=&min_score=&sort=NDATE&data_type=PORTABLE&aut_syn=YES&ttl_syn=YES&txt_syn=YES&aut_wt=1.0&ttl_wt=0.3&txt_wt=3.0&aut_wgt=YES&obj_wgt=YES&ttl_wgt=YES&txt_wgt=YES&ttl_sco=YES&txt_sco=YES&version=1

# allowed_options=['ned_query', 'ttl_wgt', 'text', 'ttl_syn', 'txt_logic', 'qform', 'start_nr', 'article_sel', 'aut_xct', 'ref_stems', 'start_entry_year', 'end_entry_year', 'group_and', 'txt_wgt', 'min_score', 'txt_wt', 'aut_wgt', 'author', 'ttl_wt', 'end_year', 'txt_sco', 'ttl_sco', 'end_entry_day', 'aut_wt', 'version', 'end_entry_mon', 'aut_syn', 'sort', 'start_year', 'nr_to_return', 'data_type', 'obj_wgt', 'sim_query', 'aut_logic', 'start_entry_mon', 'db_key', 'jou_pick', 'ttl_logic', 'arxiv_sel', 'data_and', 'end_mon', 'start_mon', 'start_entry_day', 'txt_syn', 'title']


all_param = {  # All parameters
    'author': 'list of semicolon separated authornames as last, f',
    'object': 'list of semicolon separated object names',
    'keyword': 'list of semicolon separated keywords',
    'start_mon': 'starting month as integer (Jan == 1, Dec == 12)',
    'start_year': 'starting year as integer (4 digits)',
    'end_mon': 'ending month as integer (Jan == 1, Dec == 12)',
    'end_year': 'ending year as integer (4 digits)',
    'start_entry_day': 'start entry day of month as integer',
    'start_entry_mon': 'start entry month as integer',
    'start_entry_year': 'start entry year as integer',
    'end_entry_day': 'start entry day of month as integer',
    'end_entry_mon': 'start entry month as integer',
    'end_entry_year': 'start entry year as integer',
    'title': 'title words, any non-alpha-numeric character separates',
    'text': 'abstract words, any non-alpha-numeric character separates',
    'fulltext': 'OCRd fulltext, any non-alpha-numeric character separates',
    'affiliation': 'affiliation words, any non-alpha-numeric character separates',
    'bibcode': 'bibcode for partial bibcode search. If a bibcode is specified no other search will be done',
    'nr_to_return': 'how many abstracts to return (default is 50, max 500)',
    'start_nr': 'where to start returning in list of retrieved abstracts default is 1',
    'aut_wt': 'floating point weight for author search, default: 1.0',
    'obj_wt': 'floating point weight for object search, default: 1.0',
    'kwd_wt': 'floating point weight for keyword search, default: 1.0',
    'ttl_wt': 'floating point weight for title search, default: 0.3',
    'txt_wt': 'floating point weight for text search, default: 3.0',
    'full_wt': 'floating point weight for full search, default: 3.0',
    'aff_wt': 'floating point weight for affiliation search, default: 1.0',
    'aut_syn': 'author synonym replacement. aut_syn="YES" turns it on (default is on)',
    'ttl_syn': 'title synonym replacement. ttl_syn="YES" turns it on (default is on)',
    'txt_syn': 'text synonym replacement. txt_syn="YES" turns it on (default is on)',
    'full_syn': 'full text synonym replacement. full_syn="YES" turns it on (default is on)',
    'aff_syn': 'affiliation synonym replacement. aff_syn="YES" turns it on (default is on)',
    'aut_wgt': 'authors used for weighting. aut_wgt="YES" turns it on (default is on)',
    'obj_wgt': 'objects used for weighting. obj_wgt="YES" turns it on (default is on)',
    'kwd_wgt': 'keywords used for weighting. kwd_wgt="YES" turns it on (default is on)',
    'ttl_wgt': 'title used for weighting. ttl_wgt="YES" turns it on (default is on)',
    'txt_wgt': 'text used for weighting. txt_wgt="YES" turns it on (default is on)',
    'full_wgt': 'full text used for weighting. full_wgt="YES" turns it on (default is on)',
    'aff_wgt': 'affiliation used for weighting. aff_wgt="YES" turns it on (default is on)',
    'aut_sco': 'authors weighted scoring. aut_sco="YES" turns it on (default is off)',
    'kwd_sco': 'keywords weighted scoring. kwd_sco="YES" turns it on (default is off)',
    'ttl_sco': 'title weighted scoring. ttl_sco="YES" turns it on (default is on)',
    'txt_sco': 'text weighted scoring. txt_sco="YES" turns it on (default is on)',
    'full_sco': 'text weighted scoring. full_sco="YES" turns it on (default is on)',
    'aff_sco': 'affiliation weighted scoring. aff_sco="YES" turns it on (default is off)',
    'aut_req': 'authors required for results. aut_req="YES" turns it on (default is off)',
    'obj_req': 'objects required for results. obj_req="YES" turns it on (default is off)',
    'kwd_req': 'keywords required for results. kwd_req="YES" turns it on (default is off)',
    'ttl_req': 'title required for results. ttl_req="YES" turns it on (default is off)',
    'txt_req': 'text required for results. txt_req="YES" turns it on (default is off)',
    'full_req': 'text required for results. full_req="YES" turns it on (default is off)',
    'aff_req': 'affiliation required for results. aff_req="YES" turns it on (default is off)',
    'aut_logic': 'obj_logic',
    'kwd_logic': 'ttl_logic',
    'txt_logic': 'full_logic',
    'aff_logic': 'Combination logic: "AND" combine with AND,"OR" combine with OR (default),"SIMPLE" simple logic (use +, -),"BOOL" full boolean logic, "FULLMATCH" do AND query in the selected field and calculate the score according to how many words in the field of the selected reference were matched by the query',
    'return_req': 'requested return: return_req="result" : return results (default), return_req="form" : return new query form, return_req="no_params": return results, set default parameters, dont display params',
    'db_key': 'which database to query: db_key="AST" : Astronomy(default); "PRE": arXiv e-prints; "PHY": Physics, "GEN": General, CFA: CfA Preprints',
    'atcl_only': 'select only OCR pages from articles',
    'jou_pick': 'specify which journals to select: "ALL" : return all journals (default), "NO" : return only refereed journals, "EXCL" : return only non-refereed journals',
    'ref_stems': 'list of comma-separated ADS bibstems to return, e.g. ref_stems="ApJ..,AJ..."',
    'min_score': 'minimum score of returned abstracts (floating point, default 0.0)',
    'data_link': 'return only entries with data., data_link="YES" turns it on, default is off',
    'abstract': 'return only entries with abstracts. "YES" turns it on, default is off',
    'alt_abs': 'return only entries with alternate abstracts. "YES" turns it on, default is off',
    'aut_note': 'return only entries with author notes. "YES" turns it on, default is off',
    'article': 'return only entries with articles. "YES" turns it on, default is off',
    'article_link': 'return only entries with electronic articles."YES" turns it on, default is off',
    'simb_obj': 'return only entries with simbad objects."YES" turns it on, default is off',
    'ned_obj': 'return only entries with ned objects."YES" turns it on, default is off',
    'gpndb_obj': 'return only entries with gpndb objects."YES" turns it on, default is off',
    'lib_link': 'return only entries with library links."YES" turns it on, default is off',
    'data_and': 'return only entries with all selected data available."ALL": no selection, return all refs (default), "NO" : return entries with AT LEAST ONE of the data items selected with the above flags"YES": return only entries that have ALL links selected with the above flags',
    'version': 'version number for the query form',
    'data_type': 'data type to return, "HTML" return regular list (default),"PORTABLE" return portable tagged format, "PLAINTEXT" return plain text,"BIBTEX" return bibtex format,"ENDNOTE" return ENDNOTE format,"DUBLINCORE" return DUBLINCORE format,"XML" return XML format,"SHORT_XML" return short XML format (no abstract),"VOTABLE" return VOTable format,"RSS" return RSS format',
    'mail_link': 'return only entries with mailorder."YES" turns it on, default is off',
    'toc_link': 'return only entries with tocorder."YES" turns it on, default is off',
    'pds_link': 'return only entries with pds data."YES" turns it on, default is off',
    'multimedia_link': 'return only entries with multimedia data."YES" turns it on, default is off',
    'spires_link': 'return only entries with spires data."YES" turns it on, default is off',
    'group_and': 'return only entries from all selected groups."ALL":no selection (default)"NO" :return entries that are in at least one grp, "YES":return only entries from ALL groups selected with group_bits',
    'group_sel': 'which group to select, e.g. group_sel="Chandra,HST"',
    'ref_link': 'return only entries with reference links."YES" turns it on, default is off',
    'citation_link': 'return only entries with citation links."YES" turns it on, default is off',
    'gif_link': 'return only entries with scanned articles links.',
    'open_link': 'return only entries with open access.',
    'aut_xct': 'exact author search. aut_xct="YES" turns it on',
    'lpi_query': 'lpi_query="YES" query for LPI objects, default is off',
    'sim_query': 'sim_query="YES" query for SIMBAD objects, default is on',
    'ned_query': 'ned_query="YES" query for NED objects, default is on',
    'iau_query': 'iau_query="YES" query for IAU objects, default is off',
    'sort': 'sort options:"SCORE": sort by score, "AUTHOR": sort by first author,"NDATE": sort by date (most recent first,"ODATE": sort by date (oldest first),"BIBCODE": sort by bibcode,"ENTRY": sort by entry date in the database,"PAGE": sort by page number,"RPAGE": reverse sort by page number,"CITATIONS": sort by citation count (replaces score with number of citations), "NORMCITATIONS": sort by normalized citation count, (replaces score with number of normalized citations), "AUTHOR_CNT": sort by author count',
    'query_type': 'what to return: query_type=PAPERS returns regular records (default), CITES returns citations to selected records, REFS returns references in selected records, ALSOREADS returns also-reads in selected records',
    'return_fmt': 'return format: return_fmt="LONG": return full abstract, "SHORT": return short listing (default)',
    'type': 'where to return the data (screen, file, printer, etc)',
    'defaultset': 'use default settings (same as ret_req=no_params but displays query parameters on short form)',
    'charset': 'character set for text output',
    'year': 'year field for bibcode matching',
    'bibstem': 'bibstem field for bibcode matching',
    'volume': 'volume field for bibcode matching',
    'page': 'page field for bibcode matching',
    'associated_link': 'return only entries with associated articles. associated_link="YES" turns it on, default is off',
    'ar_link': 'return only entries with AR links. ar_link="YES" turns it on, default is off',
    'tables': 'return results with table formatting (overrides pref.)',
    'email_ret': 'email_ret="YES": return query result via email',
    'exclude': 'exclude=bibcode1[,bibcode2...]: exclude specified bibcodes from results list',
    'include': 'include=bibcode1[,bibcode2...]: include specified bibcodes in results list',
    'selectfrom': 'selectfrom=bibcode1[,bibcode2...]: include only bibcodes from specified bibcode list',
    'RA': 'Right ascension for cone search',
    'DEC': 'Declination for cone search',
    'SR': 'Search radius for cone search (default is 10 arcmin)',
    'method': 'form method of query form: GET or POST',
    'nfeedback': 'number of records to use in feedback queries',
    'doi': 'DOI',
    'preprint_link': 'return only entries with preprint data.',
    'preprint_link': '"YES" turns it on, default is off',
    'refstr': 'reference string to resolve',
    'mimetype': 'mimetype of returned page (default depends on data_type)',
    'blog_link': 'return only entries with blog links',
    'qsearch': 'quick search field, can be author or text',
    'arxiv_sel': 'which arxiv categories to select',
    'article_sel': 'select only articles (not catalogs, abstracts, etc)',
    'adsobj_query': 'search object names in abstract text',
}


param_relevantes = {  # More relevant parameters
    'author': 'list of semicolon separated authornames as last, f',
    'aut_xct': 'exact author search. aut_xct="YES" turns it on',
    'keyword': 'list of semicolon separated keywords',
    'start_mon': 'starting month as integer (Jan == 1, Dec == 12)',
    'start_year': 'starting year as integer (4 digits)',
    'end_mon': 'ending month as integer (Jan == 1, Dec == 12)',
    'end_year': 'ending year as integer (4 digits)',
    'title': 'title words, any non-alpha-numeric character separates',
    'affiliation': 'affiliation words, any non-alpha-numeric character separates',
    'text': 'abstract words, any non-alpha-numeric character separates',
    'fulltext': 'OCRd fulltext, any non-alpha-numeric character separates',
    'charset': 'character set for text output',
    'bibcode': 'bibcode for partial bibcode search. If a bibcode is specified no other search will be done',
    'db_key': 'which database to query: db_key="AST" : Astronomy(default); "PRE": arXiv e-prints; "PHY": Physics, "GEN": General, CFA: CfA Preprints',
    'nr_to_return': 'how many abstracts to return (default is 50, max 500)',
    'start_nr': 'where to start returning in list of retrieved abstracts default is 1',
    'aut_logic': 'Combination logic: "AND" combine with AND,"OR" combine with OR (default),"SIMPLE" simple logic (use +, -),"BOOL" full boolean logic, "FULLMATCH" do AND query in the selected field and calculate the score according to how many words in the field of the selected reference were matched by the query',
    'jou_pick': 'specify which journals to select: "ALL" : return all journals (default), "NO" : return only refereed journals, "EXCL" : return only non-refereed journals',
    'doi': 'DOI',
    'ref_stems': 'list of comma-separated ADS bibstems to return, e.g. ref_stems="ApJ..,AJ..."',
}


def isStringLike(obj):
  try: obj + ''
  except: return False
  else: return True


def isIterable(obj):
  try: iter(obj)
  except: return False
  else: return True


journal_ads_abbrev = [
    (r'\pra', 'Physical Review A'),
    (r'\prb', 'Physical Review B')
]

ads_fields = {'R': 'Bibliographic Code',
              'A': 'Author List',
              'a': 'Book Authors',
              'F': 'Author Affiliation',
              'J': 'Journal Name',
              'V': 'Journal Volume',
              'D': 'Publication Date',
              'P': 'First Page of Article',
              'L': 'Last Page of Article',
              'T': 'Title (required)',
              't': 'Original Language Title',
              'C': 'Abstract Copyright',
              'O': 'Object Name',
              'Q': 'Subject Category',
              'G': 'Origin',
              'S': 'Score from the ADS query (output only)',
              'E': 'Electronic Data Table',
              'I': 'Links to other information (output only)',
              'U': 'for Electronic Document',
              'K': 'Keywords',
              'M': 'Language (if not English)',
              'N': 'Not Documented!!!',
              'X': 'Comment',
              'W': 'Database (if submitting for more than one)',
              'Y': 'DOI',
              'B': 'Abstract Text',
              'Z': 'References'
              }

ads_literal_fields = {
    # Fields that do not need post-procesing. They are just assigned to the dict.
    'R': '_code',
    'V': 'volume',
    'P': 'firstpage',
    'L': 'lastpage',
    'T': 'title',
    'U': 'url',
    'K': 'keywords',
    'B': 'abstract'
}


class AdsQuery(object):
  """Class that creates a query line and allows to perform the query to ads
  """

  url = "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?"
  std_opt = dict(
      db_key=["PHY", "GEN"],
      data_type="PORTABLE",
      charset='utf-8',
      return_fmt="LONG",
  )

  def __init__(self, connection={}, options={}):
    self.opt = self.std_opt
    self.set_options(options)
    self.set_connection_options(connection)

  def set_options(self, options):
    if 'verbose' in options:
      self.verbose = options['verbose']
      del options['verbose']
    else:
      self.verbose = 0
    # We could check that the options are licit. May be we'll do later
    for k, v in options.items():
      self.opt[k] = v

  def set_connection_options(self, connection):
    """
    Set Connection options, they are:
    url:         url of the database to query
    http_proxy:  Proxy to use
    timeout:     time after which we will desist if nothing happens ;)
    """
    timeout = connection.get('timeout', '90')
    # Create a timeout for all sockets (including the connections made by urrlib2)
    socket.setdefaulttimeout(float(timeout))

    if 'url' in connection:
      self.url = connection['url']

    if 'http_proxy' in connection:
      self.proxy = connection['http_proxy']
      if self.verbose > 1:
        print('# Using proxy', self.proxy)
      # Create a proxy handler
      proxy_handler = urllib.request.ProxyHandler({'http': self.proxy})
      # Replace with it the default proxy (from environment)
      opener = urllib.request.build_opener(proxy_handler)
      # ...and install it globally so it can be used with urlopen.
      urllib.request.install_opener(opener)

  def query(self):
    paper_req = self.__create_query__()
    if self.verbose > 0:
      print('# Query Command line:\n# ', paper_req, '\n')
    try:
      response = urllib.request.urlopen(paper_req)
      # str(paper_req, encoding=self.opt['charset']))
      # response = urllib.request.urlopen(paper_req.encode(self.opt['charset']))
    except urllib.error.URLError as e:
      if hasattr(e, 'reason'):
        return -2, 'We failed to reach a server.\nReason: ' + str(e.reason)
      elif hasattr(e, 'code'):
        return -1, 'The server couldn\'t fulfill the request.\n' + 'Error code: ' + str(e.code)
    else:
      the_page = str(response.read(), encoding=self.opt['charset'])
      the_page = ''.join(the_page.splitlines(True)[4:])
      nabstracts = the_page.count('%R')
    return nabstracts, the_page

  def set_charset(encoding):
    self.charset = encoding

  def add_database(db):
    self.db_key.append(db)

  def del_database(db):
    try:
      self.db_key.remove(db)
    except:
      pass

  def __create_query__(self):
    paper_req = self.url
    for k, v in self.opt.items():
      if isStringLike(v):
        op = '%s%s%s%s' % (k, '=', v, '&')
      elif isIterable(v):
        op = '%s%s%s%s' % (k, '=', ';'.join(v), '&')
      else:
        op = ''
        print('# Bad type for option: ', k, '   value:', v)
      paper_req += op
    paper_req = paper_req.replace(' ', '')
    return paper_req[:-1]


def main():
  import re
#   reg_n_abstracts=re.compile('Retrieved ([0-9]+) abstracts')
  my_options = {
      'author': (
          'Fiol,J',
          'Fuhr,J',
          'Fregenal,D'),
      'start_year': '2008',
      'end_year': '2008',
      'verbose': 2}

  Query = AdsQuery(options=my_options)
  status, page = Query.query()

  print(page)
  if status >= 0:
    print('%s\nFound %s entries\n%s' % (80 * '*', status, 80 * '*'))

if __name__ == "__main__":
  main()


# Local Variables:
# tab-width: 2
# END:
