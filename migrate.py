"""create tables in database"""
import time
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from models.base import *
from models.travels import *
from models.users import *


ok = False
engine = None
while not ok:
    try:
        engine = create_engine("postgresql://db/postgres?user=postgres&password=secret", echo=True)
        ok = True
    except OperationalError:
        time.sleep(5)
if engine:
    Base.metadata.create_all(engine)
