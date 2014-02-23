import yapbib.biblist as biblist

bibfile= 'tesis.bib'
outputfile= 'tesis.html'

htmlstyle={'fields':['author','title','director','school','year'],
           'author': ('<span class="authors">', '</span><BR>'),
           'director':('<BR><span class="director">','</span>. ')}

css_style=""".title a,
.title {font-weight: bold;	color :    #416DFF; }
ol.bibliography li{	nmargin-bottom:0.5em;}
.year:before {content:" (";}
.year:after {content:").";}
.authors {font-weight:bold; display:list;}
.authors:after {content:". ";}
.director:before{content:"Director: ";}
"""

head='''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
<style type="text/css">
{0}</style>
<title>Tesis Doctorales</title>
</head>
<body>
<h2>Tesis Doctorales (PhD Thesis)</h2>
<ol class="bibliography">
'''.format(css_style)

b=biblist.BibList()
b.import_bibtex(bibfile)
b.sort(['year','author','reverse'])
b.export_html(outputfile, head= head, style= htmlstyle, separate_css=False)
