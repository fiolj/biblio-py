from .latex_equivalents import latex_equivalents
"""latex.py

Character translation utilities for LaTeX-formatted text.

Usage:
 - unicode(string,'latex')
 - ustring.decode('latex')
are both available just by letting "import latex" find this file.
 - unicode(string,'latex+latin1')
 - ustring.decode('latex+latin1')
where latin1 can be replaced by any other known encoding, also
become available by calling latex.register().

We also make public a dictionary latex_equivalents,
mapping ord(unicode char) to LaTeX code.

D. Eppstein, October 2003.
"""


import codecs
import re
try:
  set([1, 2, 2, 1])
except BaseException:
  from sets import Set as set


def register():
  """Enable encodings of the form 'latex+x' where x describes another encoding.
  Unicode characters are translated to or from x when possible, otherwise
  expanded to latex.
  """
  codecs.register(_registry)


def getregentry():
  """Encodings module API."""
  return _registry('latex')


def _registry(encoding):
  if encoding == 'latex':
    encoding = None
  elif encoding.startswith('latex+'):
    encoding = encoding[6:]
  else:
    return None

  class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
      """Convert unicode string to latex."""
      output = []
      for c in input:
        if encoding:
          try:
            output.append(c.encode(encoding).decode('utf-8'))
            continue
          except BaseException:
            pass
        if ord(c) in latex_equivalents:
          # lt = latex_equivalents[ord(c)]
          # if lt[0] in ['_','^']:
          #     output.append('${0}$'.format(lt))
          # else:
          output.append(latex_equivalents[ord(c)])
        else:
          output += ['{\\char', str(ord(c)), '}']
      return ''.join(s for s in output).encode('utf-8'), len(input)

    def decode(self, input, errors='strict'):
      """Convert latex source string to unicode."""
      if encoding:
        if isinstance(input, str):
          pass
        elif isinstance(input, str) or hasattr(s, '__unicode__'):
          input = str(input, encoding, errors)
        else:
          input = str(str(input), encoding, errors)

      # Note: we may get buffer objects here.
      # It is not permussable to call join on buffer objects
      # but we can make them joinable by calling unicode.
      # This should always be safe since we are supposed
      # to be producing unicode output anyway.
      x = list(map(str, _unlatex(input)))
      return ''.join(x), len(input)

  class StreamWriter(Codec, codecs.StreamWriter):
    pass

  class StreamReader(Codec, codecs.StreamReader):
    pass

  return (Codec().encode, Codec().decode, StreamReader, StreamWriter)


def _tokenize(tex):
  """Convert latex source into sequence of single-token substrings."""
  start = 0
  try:
    # skip quickly across boring stuff
    pos = next(_stoppers.finditer(tex)).span()[0]
  except StopIteration:
    yield tex
    return

  while True:
    if pos > start:
      yield tex[start:pos]
      if tex[start] == '\\' and not (
              tex[pos - 1].isdigit() and tex[start + 1].isalpha()):
        while pos < len(tex) and tex[pos].isspace():
          # skip blanks after csname
          pos += 1

    while pos < len(tex) and tex[pos] in _ignore:
      pos += 1    # flush control characters
    if pos >= len(tex):
      return
    start = pos
    # protect ~ in urls
    if tex[pos:pos + 2] in {'$$': None, '/~': None}:
      pos += 2
    elif tex[pos].isdigit():
      while pos < len(tex) and tex[pos].isdigit():
        pos += 1
    elif tex[pos] == '-':
      while pos < len(tex) and tex[pos] == '-':
        pos += 1
    elif tex[pos] != '\\' or pos == len(tex) - 1:
      pos += 1
    elif not tex[pos + 1].isalpha():
      pos += 2
    else:
      pos += 1
      while pos < len(tex) and tex[pos].isalpha():
        pos += 1
      if tex[start:pos] == '\\char' or tex[start:pos] == '\\accent':
        while pos < len(tex) and tex[pos].isdigit():
          pos += 1


class _unlatex:
  """Convert tokenized tex into sequence of unicode strings.  Helper for decode()."""

  def __iter__(self):
    """Turn self into an iterator.  It already is one, nothing to do."""
    return self

  def __init__(self, tex):
    """Create a new token converter from a string."""
    self.tex = tuple(_tokenize(tex))  # turn tokens into indexable list
    self.pos = 0                    # index of first unprocessed token
    self.lastoutput = 'x'           # lastoutput must always be nonempty string

  def __getitem__(self, n):
    """Return token at offset n from current pos."""
    p = self.pos + n
    t = self.tex
    return p < len(t) and t[p] or None

  def __next__(self):
    """Find and return another piece of converted output."""
    if self.pos >= len(self.tex):
      raise StopIteration
    nextoutput = self.chunk()
    if nextoutput is None:
      return ''
    if self.lastoutput[0] == '\\' and self.lastoutput[-1].isalpha() and nextoutput[0].isalpha():
      nextoutput = ' ' + nextoutput   # add extra space to terminate csname
    self.lastoutput = nextoutput
    return nextoutput

  def chunk(self):
    """Grab another set of input tokens and convert them to an output string."""
    for delta, c in self.candidates(0):
      if c in _l2u:
        self.pos += delta
        return chr(_l2u[c])
      elif len(c) == 2 and c[1] == 'i' and (c[0], '\\i') in _l2u:
        self.pos += delta       # correct failure to undot i
        return chr(_l2u[(c[0], '\\i')])
      elif len(c) == 1 and c[0].startswith('\\char') and c[0][5:].isdigit():
        self.pos += delta
        return chr(int(c[0][5:]))

    # nothing matches, just pass through token as-is
    self.pos += 1
    if self[-1] == '$':
      return None
    return self[-1]

  def candidates(self, offset):
    """Generate pairs delta,c where c is a token or tuple of tokens from tex
    (after deleting extraneous brackets starting at pos) and delta
    is the length of the tokens prior to bracket deletion.
    """
    t = self[offset]
    if t in _blacklist:
      return
    elif t == '{':
      for delta, c in self.candidates(offset + 1):
        if self[offset + delta + 1] == '}':
          yield delta + 2, c
    elif t == '\\mbox':
      for delta, c in self.candidates(offset + 1):
        yield delta + 1, c
    elif t == '$' and self[offset + 2] == '$':
      yield 3, (t, self[offset + 1], t)
    else:
      q = self[offset + 1]
      if q == '{' and self[offset + 3] == '}':
        yield 4, (t, self[offset + 2])
      elif q:
        yield 2, (t, q)
      yield 1, t


# Characters that should be ignored and not output in tokenization
_ignore = set([chr(i) for i in list(range(32)) + [127]]) - set('\t\n\r')

# Regexp of chars not in blacklist, for quick start of tokenize
_stoppers = re.compile('[\x00-\x1f!$\\-?\\{~\\\\`\']')

_blacklist = set(' \n\r')
_blacklist.add(None)    # shortcut candidate generation at end of data

# Construction of inverse translation table
_l2u = {
    r'\ ': ord(' ')   # unexpanding space makes no sense in non-TeX contexts
}


for _i in range(0x0020):
  if _i not in latex_equivalents:
    latex_equivalents[_i] = ''
for _i in range(0x0020, 0x007f):
  if _i not in latex_equivalents:
    latex_equivalents[_i] = chr(_i)

for _tex in latex_equivalents:
  if _tex <= 0x0020 or (_tex <= 0x007f and len(latex_equivalents[_tex]) <= 1):
    continue    # boring entry
  _toks = tuple(_tokenize(latex_equivalents[_tex]))
  if _toks[0] == '{' and _toks[-1] == '}':
    _toks = _toks[1:-1]
  if _toks[0].isalpha():
    continue    # don't turn ligatures into single chars
  if len(_toks) == 1 and (_toks[0] == "'" or _toks[0] == "`"):
    continue    # don't turn ascii quotes into curly quotes
  if _toks[0] == '\\mbox' and _toks[1] == '{' and _toks[-1] == '}':
    _toks = _toks[2:-1]
  if len(_toks) == 4 and _toks[1] == '{' and _toks[3] == '}':
    _toks = (_toks[0], _toks[2])
  if len(_toks) == 1:
    _toks = _toks[0]
  _l2u[_toks] = _tex

# Shortcut candidate generation for certain useless candidates:
# a character is in _blacklist if it can not be at the start
# of any translation in _l2u.  We use this to quickly skip through
# such characters before getting to more difficult-translate parts.
# _blacklist is defined several lines up from here because it must
# be defined in order to call _tokenize, however it is safe to
# delay filling it out until now.

for i in range(0x0020, 0x007f):
  _blacklist.add(chr(i))
_blacklist.remove('{')
_blacklist.remove('$')
for candidate in _l2u:
  if isinstance(candidate, tuple):
    if not candidate or not candidate[0]:
      continue
    firstchar = candidate[0][0]
  else:
    firstchar = candidate[0]
  _blacklist.discard(firstchar)
