import sqlite3 as sq
from . import helper

DB_TBLNM = 'biblio'


def create_dbconnection(db_file):
  """create a database connection to the SQLite database
      specified by the db_file

  Parameters
  ----------
  db_file : file-like (string or handle or Path)
    Filename of the database

  Returns
  -------
  Sqlite3 connection object or None
  """
  conn = None
  try:
    conn = sq.connect(db_file)
  except sq.Error as e:
    print(e)

  return conn


def parsefile(fname):
  """Parses a bibliography database file

  Parameters
  ----------
  fname : file-like or string
    Filename to parse

  Returns
  -------
  dict: A dictionary of dictionaries with the items
  """
  con = create_dbconnection(fname)
  if con is None:
    print(f"Can't open database {fname}")
    return None

  tbname, cols = get_dbcolnames(con)
  cur = con.cursor()
  if tbname != DB_TBLNM:
    print(f"Warning: Table name in database different from {DB_TBLNM}")

  rows = cur.execute(f"SELECT * FROM {tbname};")  #
  entries = {}
  for row in rows:
    entry = parseentry(row, cols)
    if entry:
      entries[entry['_code']] = entry

  return entries


def parseentry(row, cols):
  """Parse a sqlite database row from a string into a bibliography item

  Parameters
  ----------
  row : tuple

  cols: list-like of strings
    names of the columns in the row

  Returns
  -------
  dict: bibliography entry
  """
  entry = {}
  for c, r in zip(cols, row):
    if r:
      if c in helper.namefields:
        a = [k.split(',') for k in r.split(";")]
        if a:
          entry[c] = a
        pass
      else:
        entry[c] = r

  return entry


def get_dbtablename(con):
  """Get table name from connected database.

  Parameters
  ----------
  con : sqlite3 connection

  Returns
  -------
  table name or empty string if not table present

  Notes
  -----
  If more than a table is present returns only the first
  """
  cur = con.cursor()
  cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
  tbns = cur.fetchone()
  try:
    return tbns[0]
  except TypeError:
    return ''


def get_dbcolnames(con):
  """
  Read column names from first table of connected database

  Parameters
  ----------
  con : sqlite3 connection

  Returns
  -------
  list: names of colunns (fields)

  Notes
  -----
  Assume that only one table is present, or uses the first
  """
  tabnm = get_dbtablename(con)  # Get table name

  c = con.cursor()
  cols = []
  for row in c.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{tabnm}');"):
    cols.append(row[0])
  return tabnm, cols


def create_dbbib(conn, fields, tablename=DB_TBLNM):
  """Create a table with its columns to store the biblist bibliography

  Parameters
  ----------
  conn : sqlite3 Connection object

  fields : list
      Columns to use
  """

  cols = fields[:]
  cols.remove('_code')
  strcols = "_code text NOT NULL PRIMARY KEY, \n  "
  # strcols = ""
  strcols += ",\n  ".join([f"{f.replace('-','_')} text" for f in cols])
  try:
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS {tablename} (\n  {strcols}\n);")
    conn.commit()
  except sq.Error as e:
    print(e)
