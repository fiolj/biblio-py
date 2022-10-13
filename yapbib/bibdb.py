import sqlite3 as sq

DB_TBLNM = 'biblio'


# class BibDb(object):
#   """Object to manage the connection to a database"""

#   def __init__(self, fname):
#     super(BibDb, self).__init__()
#     self.fname = fname
#     con = create_dbconnection(fname)
#     if con is not None:
#       self.con = con
#       self.cur = con.cursor()

#       self.fields = get_dbcolnames(self.cur)
#       # if fields ==

# def opendb(db_file):
#   """
#   Open a connection to a database

#   Parameters
#   ----------
#   db_file : file-like (string or handle or Path)
#     Filename of the database

#   Returns
#   -------
#   Sqlite3 connection to file
#   """
#   con = create_connection(db_file)
#   return con


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

  cur = con.cursor()
  cols = []
  for row in cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('{tabnm}');"):
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

  strcols = "id integer PRIMARY KEY, \n  "
  strcols += ",\n  ".join([f"{f.replace('-','_')} text" for f in fields])
  try:
    # print(f"CREATE TABLE IF NOT EXISTS {tablename} (\n  {strcols}\n);")
    c = conn.cursor()
    c.execute(f"CREATE TABLE IF NOT EXISTS {tablename} (\n  {strcols}\n);")
  except sq.Error as e:
    print(e)


dbname = '../sqlite/articlesAll0c1del.db'
dbname = '../sqlite/new1.db'

con = create_dbconnection(dbname)
create_dbbib(con, ['author', '_code', '_type', 'title'])
con.close()
