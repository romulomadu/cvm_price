#!/usr/bin/env python3
import pandas as pd
import sqlite3
import pymysql

from flask import Flask, jsonify
from registro import cvm, cvm2symbol, get_result
from datetime import datetime
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.types import NVARCHAR, FLOAT, DATETIME, BIGINT
from exception_util import MySendMail

pymysql.install_as_MySQLdb()

# Global variables
lista = []
dia = None

# Database parameters
host='186.242.81.209'
user='root'
password='B@nc0D@d0s'
db='cvm_dfps'

# Connect to the database
conn = create_engine(f'mysql+mysqldb://{user}:{password}@{host}:3306/{db}', echo = False)
print ('Connect successful!!')

# Create flask app
app = Flask(__name__)

# Get register table
reg = cvm()

# Get result table
res = get_result()

try:
    # Get cvm+symbol price table na save to MySQL db
    cs = cvm2symbol(reg.cvm_code, res.set_index('symbol'))
    types = dict(zip(cs.columns, [BIGINT, NVARCHAR(length=6), FLOAT, DATETIME]))
    cs.to_sql('precos', conn, if_exists='replace', index=False, dtype=types)
except Exception as e:
    MySendMail(e)

@app.route("/")
def json_api():
    global lista, dia
    
    # Update once a day
    if dia == datetime.strftime(datetime.today(), '%d'):
        return jsonify(lista)
    else:
        # Get register table
        res = get_result()

        try:
            # Get cvm+symbol price table na save to MySQL db
            cs = cvm2symbol(reg.cvm_code, res.set_index('symbol'))
            cs.to_sql('precos', conn, if_exists='replace', index=False, dtype=types)
        except Exception as e:
            MySendMail(e)

app.run(debug=True)