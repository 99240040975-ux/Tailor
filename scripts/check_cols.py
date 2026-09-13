import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import sqlalchemy
from config import Config

engine = sqlalchemy.create_engine(Config.SQLALCHEMY_DATABASE_URI)
insp = sqlalchemy.inspect(engine)
for table in insp.get_table_names():
    cols = insp.get_columns(table)
    for c in cols:
        if not c['nullable'] and c['default'] is None and not c.get('autoincrement', False):
            print(f"{table}.{c['name']}: type={c['type']}, nullable={c['nullable']}, default={c['default']}")
