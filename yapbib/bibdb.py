import sqlite3 as sq
import helper


class BibDb(object):
  """Object to manage the connection to a database"""

  def __init__(self, fname):
    super(BibDb, self).__init__()
    self.fname = fname
    con = create_connection(fname)
    if con is not None:
      self.con = con
      self.cur = con.cursor()

      self.fields = get_dbcolnames(self.cur)
      # if fields ==


def opendb(db_file):
  """

  Parameters
  ----------
  db_file :


  Returns
  -------

  """
  con = create_connection(db_file)
  return con


def create_connection(db_file):
  """create a database connection to the SQLite database
      specified by the db_file

  Parameters
  ----------
  db_file :
      database file

  Returns
  -------
  type
      Connection object or None

  """
  conn = None
  try:
    conn = sq.connect(db_file)
  except sq.Error as e:
    print(e)

  return conn


def get_dbtablename(con):
  """Get first table name form connected database

  Parameters
  ----------
  con : sqlite3 connection


  Returns
  -------
  string: table name
  """
  cur = con.cursor()
  cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
  tbns = cur.fetchone()
  if tbns is None:
    return ''
  else:
    return tbns[0]


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
  tabnm = get_tablename(con)  # Get table name

  cur = con.cursor()
  cols = []
  for row in cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{tabnm}');"):
    cols.append(row[0])
  return cols


def create_bibtable(conn, fields, tablename='biblio'):
  """Create a table to store the biblist bibliography

  Parameters
  ----------
  conn : sqlite3 Connection object

  fields : list
      Columns to use
  """

  strcols = f"id integer PRIMARY KEY, \n  "
  strcols += ",\n  ".join([f"{f.replace('-','_')} text" for f in fields])
  try:
    print(f"CREATE TABLE IF NOT EXISTS {tablename} (\n  {strcols}\n);")
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS {tablename} (\n  {strcols}\n);")
  except sq.Error as e:
    print(e)


dbname = '../sqlite/articlesAll0c1del.db'
dbname = '../sqlite/new1.db'

con = create_connection(dbname)
create_bibtable(con, allfields)
con.close()


# # t = "new_pubs2"
# fields = []
# for row in cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('new_pubs2');"):
#   print()
#   fields.append(row[0])
