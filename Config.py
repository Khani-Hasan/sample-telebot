import os

db_config = {"user" : os.environ.get("Db_user"), "password" : os.environ.get("Db_pass"), 
             "host" : os.environ.get("Db_host"), "database" : os.environ.get("Db_name")}

API_token = os.environ.get("Store_token")
Support = os.environ.get("Support_cid")
card = os.environ.get("Card_num")

admins = eval(os.environ.get("Admins"))