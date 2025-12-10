import mysql.connector
from Config import db_config
categories = ["Writing tools", "Clothing", "Electronics", "Tools"]

def get_prod_data(prod_id):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute("Select * from product where ID=%s;",(prod_id,))
    data = cur.fetchall()[0]
    cur.close()
    conn.close()
    return data

def get_prod_list(category):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    if category in categories:
        cur.execute('select * from product where category=%s;',(category,))
    else:
        cur.execute("select * from product where category is NULL;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_CIDs():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("select CID from user;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_user_data(cid):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor(dictionary=True)
    cur.execute('select * from user where CID = %s;',(cid,))
    data = cur.fetchall()[0]
    cur.close()
    conn.close()
    return data