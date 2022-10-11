import sqlite3 as sq
import helper


class BibDb(object):
  """Object to manage the connection to a database

  """

  def __init__(self, fname):
    super(BibDb, self).__init__()
    self.fname = fname
    con = create_connection(db_file)
    if con is not None:
      self.con = con
      self.cur = con.cursor()

    fields = get_dbcolnames(self.cur)
    if fields ==


def opendb(db_file):
  con = create_connection(db_file)
  return con


def create_connection(db_file):
  """ create a database connection to the SQLite database
      specified by the db_file
  :param db_file: database file
  :return: Connection object or None
  """
  conn = None
  try:
    conn = sq.connect(db_file)
  except sq.Error as e:
    print(e)

  return conn


def get_dbcolnames(cur):
  cols = []
  for row in cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('new_pubs2');"):
    cols.append(row[0])
  return cols


dbname = '../sqlite/articlesAll0c1delB.db'

con = create_connection(dbname)

cur = con.cursor()

# res = cur.execute("SELECT name FROM sqlite_master")
# t = res.fetchall()
# print(t)
t = "new_pubs2"
fields = []
for row in cur.execute(f"SELECT name FROM PRAGMA_TABLE_INFO('new_pubs2');"):
  print()
  fields.append(row[0])
# fields = [c[0] for c in cols]
