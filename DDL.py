import mysql.connector
from Config import db_config
from DML import *
database_name = db_config["database"]

def del_n_create_db(database_name):
    conn = mysql.connector.connect(user=db_config["user"], password=db_config["password"], host=db_config["host"])
    cur = conn.cursor()
    cur.execute(f'drop database if exists {database_name};')
    cur.execute(f'create database if not exists {database_name};')
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Database created.")
def create_table_user():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""create table user(
                                    `CID` 		    bigint not null primary key, 
                                    `F_name` 	    varchar(75), 
                                    `L_name` 	    varchar(75), 
                                    `Phone_num` 	bigint unsigned, 
                                    `Address` 	    text, 
                                    `Created` 	    datetime default current_timestamp,
                                    `Last_update`   datetime default current_timestamp on update current_timestamp);""")
    conn.commit()
    cur.close()
    conn.close()
    logging.info("User table created.")
def create_table_product():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""create table product(
                                        `ID` 		    int unsigned not null primary key auto_increment, 
                                        `Name` 		    varchar(255) not null, 
                                        `Inv` 		    smallint unsigned not null, 
                                        `Price` 	    int unsigned not null,
                                        `Descrip` 	    varchar(75), 
                                        `Category` 	    enum("Writing tools", "Clothing", "Electronics", "Tools"),
                                        `File_id`       text,
                                        `Created` 	    datetime default current_timestamp, 
                                        `Last_update` 	datetime default current_timestamp on update current_timestamp);""")
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Product table created.")
def create_table_sale():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""create table sale(
                                    `ID` 		int unsigned not null primary key auto_increment, 
                                    `User_cid` 	bigint not null, 
                                    `Created`	datetime default current_timestamp,
                                    foreign key(User_cid) references user(CID));""")
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Sale table created.")
def create_table_sale_item():
    conn = mysql.connector.connect(**db_config)
    cur = conn.cursor()
    cur.execute("""create table sale_item(
                                        `Sale_id`   int unsigned not null, 
                                        `Prod_id` 	int unsigned not null, 
                                        `Qnt` 		smallint unsigned not null,
                                        `Created` 	datetime default current_timestamp,
                                        foreign key(Sale_id) references sale(ID),
                                        foreign key(Prod_id) references product(ID));""")
    conn.commit()
    cur.close()
    conn.close()
    logging.info("Sale_item table created.")

if __name__ == "__main__":
    del_n_create_db(database_name)
    create_table_user()
    create_table_product()
    create_table_sale()
    create_table_sale_item()
    insert_product("خودکار", 10, 20000, "سیاه", "Writing tools","AgACAgQAAxkBAAIBAWksNYk7yc-vBq4ECtVwpIRhIvTQAAIFDGsb4phgUUhopDGV9BPaAQADAgADdwADNgQ")
    insert_product("خودکار", 50, 20000, "آبی", "Writing tools", "AgACAgQAAxkBAAIF72k5TSbTGq2An5VR_h3ZHqZhTPn3AAIPDGsbgDTJUVtozXRSm3yuAQADAgADeAADNgQ")
    insert_product("مداد", 120, 5000, "مشکی", "Writing tools", "AgACAgQAAxkBAAIGRmk5d1nTV-SSY2kzx6SatZUPKgmCAAJPDGsbgDTJUU83dlfe0x0TAQADAgADeAADNgQ")
    insert_product("پاک کن", 20,  10000, "سفید", "Writing tools", "AgACAgQAAxkBAAIGQmk5dU-rBJVika6NubCVlh5yWreqAAJKDGsbgDTJUREO7h3NsR6RAQADAgADeAADNgQ")
    insert_product("دفتر", 200, 70000, "صد برگ", "Writing tools", "AgACAgQAAxkBAAIGR2k5d_Y1rzpXU-nL9Ib8nrGWCJ8HAAJRDGsbgDTJUSK9sgvEYNagAQADAgADeAADNgQ")
    insert_product("کت", 1, 1650000, "چرمی", "Clothing", "AgACAgQAAxkBAAIGSGk5eQZLEHf230P27EzbgsvEl_d1AAJSDGsbgDTJUe1HWal0jbvxAQADAgADeQADNgQ")
    insert_product("شلوار", 4, 900000, "جین", "Clothing", "AgACAgQAAxkBAAIGSWk5eZQt2laod1ElGZJL8syffJz6AAJVDGsbgDTJUY4SOv-4cOGoAQADAgADeAADNgQ")
    insert_product("رم", 0, 1200000, "8 گیگ DDR5", "Electronics", "AgACAgQAAxkBAAIGSmk5emoZmBeq6BwPnXphGLON-N_fAAJYDGsbgDTJUSZVNVKzpP91AQADAgADeAADNgQ")
    insert_product("موس", 3, 13000000, "هایپر ایکس پولس فایر", "Electronics", "AgACAgQAAxkBAAIGS2k5eysgWGUPNjLE13qiatbpzQwCAAJZDGsbgDTJUR4IfZp5XLw3AQADAgADdwADNgQ")
    insert_product("چکش", 13, 200000, "آهنی", "Tools", "AgACAgQAAxkBAAPCaSbtTaGJ1zmU3qXPMTQjQSwf-RAAAo8Laxvd6zlRPVzGcC556-4BAAMCAAN4AAM2BA")
    insert_product("پیچ گوشتی", 20, 120000, "دو پهلو", "Tools", "AgACAgQAAxkBAAIGTGk5e8Q67kbRobRbZJyzQubi-jJWAAIBC2sbgDTRUQbySW1rmbaTAQADAgADeQADNgQ")