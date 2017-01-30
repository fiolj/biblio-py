#!/usr/bin/env python
import sys
import os

try:
  from optparse import OptionParser
  import io
  import datetime
except ImportError as e:
  print('file', __file__ ,e)
  sys.exit(1)

try:
  from yapbib.version import VERSION
  from yapbib import biblist
  import query_ads.query_ads as ads
except ImportError as e:
  print('Import Error', __file__ ,e)
  sys.exit(1)

def main():
  '''Retrieve papers list'''
  # Declara algunas variables
  autores="Einstein,A;Schrodinger,E"
  thisyear= datetime.date.today().year

  #########################################################################
  parser = OptionParser(version="%prog with biblio-py-{0}".format(VERSION))

  parser.add_option("-o", "--output-file"
                    , help="write to FILE. Default: standard output", metavar="FILE", default='-')
  parser.add_option("-f", "--format", default=None
                    , help="format of output, possible values are: short, full, bibtex, tex, html, xml   DEFAULT= bib")

  parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False
                    , help="Give some informational messages.")

  parser.add_option("-b", "--start-year", default=str(thisyear),
                    help="Starting year as integer (4 digits)")
  parser.add_option("-e", "--end-year", default=str(thisyear),
                    help="Ending year as integer (4 digits)")

  parser.add_option("-y", "--year", default= None,
                    help="--year=y is a shortcut to '--start-year=y --end-year=y'")

  parser.add_option("--start-month", default='1',
                    help="Starting month as integer (Jan == 1, Dec == 12)")
  parser.add_option("--end-month", default='12',
                    help="Ending month as integer (Jan == 1, Dec == 12)")

  parser.add_option("-a", "--author", default=autores,
                    help="list of semicolon separated author names as last,f")

  parser.add_option("--author-logic", default='AND',
                    help="Logic to use to search for authors. Default: 'AND'. Use 'OR' to get ALL authors articles")

  parser.add_option("--proxy", default=None,
                    help="Proxy used to connect")

  parser.add_option("--advanced-options", default=None,
                    help="""Additional options supported by Harvard. They should be written as option1:value1;option2:value2,...  
                          To get a list of options use: '--help-advanced-options'""")

  parser.add_option("--help-advanced-options", action="store_true", default=False,
                    help="Show information on additional options supported by Harvard ADS site")

  parser.add_option("-d","--save-dump"
                    , help="Save (dump) the database IN INTERNAL FORM")

  parser.add_option("", "--sort", default='key'
                    , help="Sort the items according to the following fields, for instance to sort them accoding to year and then author we would use --sort=year,author. In the same example, to sort in reverse order we would use: --sort=year,author,reverse. DEFAULT: key.")

  (op, args) = parser.parse_args()
  
  if op.help_advanced_options != False:
    if op.verbose:
      print('Complete list of possible options supported by Harvard:')
      for k,v in ads.all_param.items():
        print('  %18s : %s'%(k,v))
    else:
      print('The more important parameters are:')
      for k,v in ads.param_relevantes.items():
        print('  %18s : %s'%(k,v))
      print('** To get a complete list use also --verbose **')
    return 1
  
  if op.proxy != None: conexion={'http_proxy': op.proxy}
  else: conexion= {}

  available_formats= {'s':'short','f':'full','t':'latex','b':'bibtex','h':'html','x':'xml'}

  output_file= op.output_file

  if op.format == None:    # Guess a format
    if output_file != '-':
      ext= os.path.splitext(output_file)[1][1]
      if ext in 'tbhx': formato=available_formats.get(ext)
      else: formato='bibtex'
    else: formato='bibtex'
  else:
    formato=available_formats.get(op.format[0].lower())

  #########################################################################################
  opciones={}
  opciones['start_year']=op.start_year
  opciones['end_year']= op.end_year
  if op.year != None:  opciones['start_year']=opciones['end_year']= op.year
    
  opciones['start_mon']=op.start_month
  opciones['end_mon']= op.end_month
  opciones['author']= op.author
  opciones['aut_logic']= op.author_logic
  if op.advanced_options != None:
    for o in op.advanced_options.split(';'):
      k,v= o.split(':')
      opciones[k]= v
  #########################################################################################
  # Create the List object
  b= biblist.BibList()
  #########################################################################################
  Query= ads.AdsQuery(connection=conexion,options=opciones)
  nabst, page= Query.query()
  if nabst < 0:
    print('Error (%d), %s' %(nabst,page))
    sys.exit()
  else:
    if op.verbose:  print('%d items downloaded' %(nabst))
    
  # Load the results into the biblist object
  fi= io.StringIO(page)
  n= b.import_ads(fi)
  if op.verbose:  print('# %d items downloaded, total number of items %d' %(n, len(b.ListItems)))

  sortorder= op.sort.lower().split(',')
  if 'reverse' in sortorder:      reverse=True
  else: reverse= False
  if reverse: sortorder.remove('reverse')
  b.sort(sortorder,reverse=reverse)

  if op.save_dump != None:
    if op.verbose:
      print('# Saving database to %s...' %(op.save_dump))
    b.dump(op.save_dump)

  b.output(output_file, formato, op.verbose)

  


if __name__ == "__main__":
  main()


### Local Variables: 
### tab-width: 2
### END:
