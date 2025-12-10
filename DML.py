import mysql.connector
import logging
from DQL import get_prod_data
from Config import db_config

logging.basicConfig(level=20, filename="Logs/project.log", filemode="a", format="%(levelname)s - %(message)s - %(asctime)s")


def insert_user(CID, First_name, Last_name, Phone_num=None, Address=None):
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""insert into user
                    (CID, F_name, L_name, Phone_num, Address) values (%s, %s, %s, %s, %s);""",
                    (CID, First_name, Last_name, Phone_num, Address))
        conn.commit()
        cur.close()
        conn.close()
        logging.info(f'{CID} added.')

def insert_product(Name, Inv, Price, Descrip=None, Category=None, File_id=None):
        conn = mysql.connector.connect(**db_config)
        cur = conn.cursor()
        cur.execute("""insert into product 
                    (Name, Inv, Price, Descrip, Category, File_id) values (%s, %s, %s, %s, %s, %s);""",
                    (Name, Inv, Price, Descrip, Category, File_id))
        conn.commit()
        p_id = cur.lastrowid
        cur.close()
        conn.close()
        logging.info(f'{Name} product added.')
        return p_id

def insert_sale(CID, prods):
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""insert into sale
                (User_cid) values (%s);""", (CID,))
    sale_id = cur.lastrowid
    for prod_id, qty in prods.items():
          prod_data = get_prod_data(prod_id)
          if prod_data["Inv"] >= qty:
                cur.execute("""insert into sale_item
                            (Sale_id, Prod_id, Qnt) values (%s, %s, %s);""",
                            (sale_id, prod_id, qty))
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f'sale for {CID} added.')

def mod_Fname(Fname, cid):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute("update user set F_name = %s where CID = %s;",(Fname, cid))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'{cid}, F_name updated.')

def mod_Lname(Lname, cid):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute("update user set L_name = %s where CID = %s;",(Lname, cid))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'{cid}, L_name updated.')

def mod_addr(addr, cid):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute("update user set Address = %s where CID = %s;",(addr, cid))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'{cid}, Address updated.')

def mod_phone(phone, cid):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute('update user set Phone_num = %s where CID = %s;',(phone, cid))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'{cid}, phone verfied.')

def inv_deduct_from_sale(prods):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      for p_id, qty in prods.items():
            cur.execute('update product set Inv = Inv - %s where ID = %s;', (qty, p_id))
            logging.info(f'Product {p_id} inv reduced by {qty}.')
      conn.commit()
      cur.close()
      conn.close()

def change_cat(p_id, cat):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute('update product set Category = %s where ID = %s;',(cat, p_id))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'Product {p_id} category set to {cat}.')

def change_inv_price(p_id, inv, price):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute('update product set Inv = %s, Price = %s where ID = %s;',(inv, price, p_id))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'Product {p_id} inv changed to {inv}, price changed to {price}.')

def del_prod(p_id):
      conn = mysql.connector.connect(**db_config)
      cur = conn.cursor()
      cur.execute('delete from product where ID = %s;',(p_id,))
      conn.commit()
      cur.close()
      conn.close()
      logging.info(f'Product {p_id} removed.')