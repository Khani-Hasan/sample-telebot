import telebot
from telebot.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton
from DML import *
from DQL import *
from Config import API_token, Support, card, admins

steps = {}
carts = {}

bot = telebot.TeleBot(API_token)
hideboard = ReplyKeyboardRemove()
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add("مشاهده محصولات", "سبد خرید و نهایی سازی")
keyboard.add("اطلاعات مشتری", "مرجوعی")

def listener(messages):
    for m in messages:
        if m.content_type != "text":
            logging.info(f"{str(m.chat.id)} sent {m.content_type}.")
        #print(m)
    
bot.set_update_listener(listener)

def check_user(cid):
    cids = get_CIDs()
    if (cid,) not in cids:
        user_info = bot.get_chat(cid)
        insert_user(cid, user_info.first_name, user_info.last_name)

def gen_prod_markup(products, qty=1):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("-", callback_data=f"change,{products["ID"]},{qty-1}"),InlineKeyboardButton(str(qty), callback_data="Deco"),InlineKeyboardButton("+", callback_data=f"change,{products["ID"]},{qty+1}"))
    markup.add(InlineKeyboardButton("اضافه کردن به سبد خرید", callback_data=f"add,{products["ID"]},{qty}"))
    markup.add(InlineKeyboardButton("لغو خرید", callback_data="nobuy"))
    return markup

def gen_cartprod_markup(prod, qty):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("-", callback_data=f"change,cart,{prod["ID"]},{qty-1}"),InlineKeyboardButton(str(qty), callback_data="Deco"),InlineKeyboardButton("+", callback_data=f"change,cart,{prod["ID"]},{qty+1}"))
    markup.add(InlineKeyboardButton("ثبت مقدار جدید", callback_data=f"qty,{prod["ID"]},{qty}"))
    markup.add(InlineKeyboardButton("لغو تغییرات", callback_data="nobuy"))
    return markup

def gen_prod_caption(products, qty=1):
    text = f'''
نام کالا: {products["Name"]}
توضیحات: {products["Descrip"]}
قیمت: {products["Price"]*qty} تومان 
'''
    return text

@bot.message_handler(commands=["start"])
def start(message):
    cid = message.chat.id
    check_user(cid)
    bot.send_message(cid, "به فروشگاه خوش آمدید.", reply_markup=keyboard)
    if cid in admins:
        text = f"""
اضافه کردن یک کالای جدید : /add_product
تغییر قیمت یا تعداد موجود یک کالا : /change_product
حذف کردن یک کالا : /remove_product"""
        bot.send_message(cid, text)

@bot.message_handler(commands=["add_product"])
def add_prod(message):
    cid = message.chat.id
    if cid in admins:
        bot.send_message(cid, "لطفا یک عکس به همراه نام کالا، تعداد، قیمت و توضیحات کالا (هر کدام در خط مجزا) را ارسال کنید.")
        steps[cid] = "AP"

@bot.message_handler(commands=["change_product"])
def change_prod(message):
    cid = message.chat.id
    if cid in admins:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("نوشت افزار", callback_data="adm_products_Writing tools"))
        markup.add(InlineKeyboardButton("پوشاک", callback_data="adm_products_Clothing"))
        markup.add(InlineKeyboardButton("دیجیتال", callback_data="adm_products_Electronics"))
        markup.add(InlineKeyboardButton("ابزار آلات", callback_data="adm_products_Tools"))
        markup.add(InlineKeyboardButton("غیره", callback_data="adm_products_Other"))
        bot.send_message(cid, "لطفا دسته ی مورد نظر را انتخاب کنید.", reply_markup=markup)

@bot.message_handler(commands=["remove_product"])
def remove_product(message):
    cid = message.chat.id
    if cid in admins:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("نوشت افزار", callback_data="adm_remove_products_Writing tools"))
        markup.add(InlineKeyboardButton("پوشاک", callback_data="adm_remove_products_Clothing"))
        markup.add(InlineKeyboardButton("دیجیتال", callback_data="adm_remove_products_Electronics"))
        markup.add(InlineKeyboardButton("ابزار آلات", callback_data="adm_remove_products_Tools"))
        markup.add(InlineKeyboardButton("غیره", callback_data="adm_remove_products_Other"))
        bot.send_message(cid, "لطفا دسته ی مورد نظر را انتخاب کنید.", reply_markup=markup)

@bot.callback_query_handler(func= lambda call : True)
def call_handler(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    call_id = call.id
    if data.startswith("products"):
        cat = data.split("_")[-1]
        data = get_prod_list(cat)
        if len(data) == 0:
            bot.answer_callback_query(call_id,"Oops.")
            bot.send_message(cid, "فعلا محصولی برای نمایش در این دسته بندی نداریم.")
        else:
            text = ""
            for i in range(len(data)):
                text += f'{data[i]["ID"]}: '
                text += f'{data[i]["Name"]} '
                text += data[i]["Descrip"]
                text += "\n"
            markup = InlineKeyboardMarkup()
            for i in range(len(data)):
                markup.add(InlineKeyboardButton(f'{data[i]["ID"]}', callback_data=f"product_{data[i]["ID"]}"))
            bot.answer_callback_query(call_id, f"دسته بندی {cat}.")
            bot.send_message(cid, text, reply_markup=markup)
    elif data.startswith("product_"):
        pid = data.split("_")[-1]
        prod_data = get_prod_data(pid)
        caption = gen_prod_caption(prod_data)
        markup = gen_prod_markup(prod_data)
        photo = prod_data["File_id"]
        bot.answer_callback_query(call_id, "لطفا تعداد مورد نظر را انتخاب کنید.")
        bot.send_photo(cid, photo, caption, reply_markup=markup)
    elif data.startswith("change,"):
        new_data = data.split(",")
        prod = new_data[-2]
        qty = new_data[-1]
        prod_data = get_prod_data(prod)
        if not data.startswith("change,cart") and qty == "0":
            bot.answer_callback_query(call_id, "تعداد نمی تواند صفر باشد.")
        elif qty < "0":
            bot.answer_callback_query(call_id, "مقدار نمی تواند کمتر از صفر باشد.")
        elif qty > "5":
            bot.answer_callback_query(call_id, "تعداد نمی تواند بیشتر از پنج باشد.")
        else:
            if data.startswith("change,cart"):
                markup = gen_cartprod_markup(prod_data, int(qty))
            else:
                markup = gen_prod_markup(prod_data, int(qty))
            caption = gen_prod_caption(prod_data, int(qty))
            bot.edit_message_caption(caption, cid, mid, reply_markup=markup)
    elif data.startswith("add"):
        data = data.split(",")
        prod = data[1]
        qty = data[2]
        carts.setdefault(cid, {})
        if len(carts.get(cid)) >= 5:
            bot.send_message(cid,"سبد خرید شما پر است.")
        else:
            carts[cid].setdefault(int(prod), 0)
            carts[cid][int(prod)] += int(qty)
            if carts[cid][int(prod)] > 5:
                carts[cid][int(prod)] = 5
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("به سبد خرید اضافه شد.", callback_data="Deco"))
            bot.edit_message_reply_markup(cid, mid, reply_markup=markup)
    elif data == "nobuy":
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
    elif data == "change_cart":
        markup = InlineKeyboardMarkup()
        for i in carts.get(cid):
            markup = markup.add(InlineKeyboardButton(f'{i}', callback_data=f"changeprod_{i}_{carts[cid][i]}"))
        markup.add(InlineKeyboardButton("لغو", callback_data="nobuy"))
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        bot.send_message(cid, "لطفا کالای مورد نظر را انتخاب کنید.", reply_markup=markup)
    elif data.startswith("changeprod"):
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        prod = data.split("_")[-2]
        qty = data.split("_")[-1]
        prod_data = get_prod_data(prod)
        caption = gen_prod_caption(prod_data, int(qty))
        markup = gen_cartprod_markup(prod_data, int(qty))
        photo = prod_data["File_id"]
        bot.send_photo(cid, photo, caption, reply_markup=markup)
    elif data.startswith("qty"):
        data = data.split(",")
        prod = int(data[-2])
        qty = int(data[-1])
        if qty == 0:
            carts[cid].pop(prod)
        else:
            carts[cid][prod] = qty
        bot.edit_message_caption("تغییرات اعمال شد.", cid, mid, reply_markup=None)
    elif data.startswith("mod"):
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        if data.split("_")[-1] == "Fname":
            bot.send_message(cid, "لطفا نام خود را وارد کنید.", reply_markup=hideboard)
            steps[cid] = "F"
        elif data.split("_")[-1] == "Lname":
            bot.send_message(cid, "لطفا نام خانوادگی خود را وارد کنید.", reply_markup=hideboard)
            steps[cid] = "L"
        elif data.split("_")[-1] == "addr":
            bot.send_message(cid, "لطفا آدرس خود را وارد کنید.", reply_markup=hideboard)
            steps[cid] = "A"
        elif data.split("_")[-1] == "phone":
            markup = ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(KeyboardButton("ثبت شماره", request_contact=True))
            bot.send_message(cid,"لطفا با استفاده از دکمه ی تلگرام شماره ی خود را ارسال کنید.", reply_markup=markup)
            steps[cid] = "P"
    elif data == "finalize":
        check_user(cid)
        if get_user_data(cid)["Phone_num"] == None or get_user_data(cid)["Address"] == None:
            bot.send_message(cid, "لطفا اطلاعات خود را در پنل اطلاعات مشتری وارد کنید.")
        else:
            bot.edit_message_reply_markup(cid, mid, reply_markup=None)
            for i in carts.get(cid):
                if carts[cid][i] <= get_prod_data(i)["Inv"]:
                    continue
                else:
                    bot.send_message(cid,f'کالای {i} به اندازه ی درخواست شما موجود نیست.')
                    break
            else:   
                markup = InlineKeyboardMarkup()
                markup.add(InlineKeyboardButton("نهایی کردن خرید", callback_data="end"))
                markup.add(InlineKeyboardButton("لغو خرید", callback_data="cancel"))
                bot.send_message(cid, f"برای ثبت خرید لطفا مبلغ رسید را به شماره ی {card} واریز کرده و عکس فیش پرداختی را به همراه فاکتور برای [ادمین](tg:\\user?id={Support}) ارسال کنید\\. ",reply_markup=markup, parse_mode="MarkdownV2")
    elif data == "end":
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        insert_sale(cid, carts[cid])
        inv_deduct_from_sale(carts[cid])
        carts.pop(cid)
        bot.send_message(cid, "خرید شما ثبت شد.")
    elif data == "cancel":
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        carts.pop(cid)
    elif data == "Deco":
        bot.answer_callback_query(call_id, ". . .")
    elif data.startswith("setcat"):
        bot.edit_message_reply_markup(cid, mid, reply_markup=None)
        if data == "setcat_null":
            bot.send_message(cid, "کالا در دسته بندی غیره قرار گرفت.")
        else:
            p_id = data.split("_")[-2]
            cat = data.split("_")[-1]
            change_cat(int(p_id), cat)
            bot.send_message(cid, f"کالا در دسته بندی {cat} قرار داده شد.")
    elif data.startswith("adm_"):
        bot.answer_callback_query(call_id, "قبل از اعمال هر تغییر به ادمین های دیگر گزارش دهید.")
        if data.startswith("adm_product"):
            cat = data.split("_")[-1]
            data = get_prod_list(cat)
            if len(data) == 0:
                bot.send_message(cid, "فعلا محصولی برای نمایش در این دسته بندی نداریم.")
            else:
                text = ""
                for i in range(len(data)):
                    text += f'{data[i]["ID"]}: '
                    text += f'{data[i]["Name"]} '
                    text += data[i]["Descrip"]
                    text += "\n"
                bot.send_message(cid, text)
                bot.send_message(cid, "لطفا کد، تعداد جدید و قیمت جدید را ارسال کنید.")
                steps[cid] = "CH"
        elif data.startswith("adm_remove"):
            cat = data.split("_")[-1]
            data = get_prod_list(cat)
            if len(data) == 0:
                bot.send_message(cid, "فعلا محصولی برای نمایش در این دسته بندی نداریم.")
            else:
                text = ""
                for i in range(len(data)):
                    text += f'{data[i]["ID"]}: '
                    text += f'{data[i]["Name"]} '
                    text += data[i]["Descrip"]
                    text += "\n"
                markup = InlineKeyboardMarkup()
                for i in range(len(data)):
                    markup.add(InlineKeyboardButton(f'{data[i]["ID"]}', callback_data=f"remove_product_{data[i]["ID"]}"))
                markup.add(InlineKeyboardButton("لغو", callback_data="nobuy"))
                bot.send_message(cid, text, reply_markup=markup)
    elif data.startswith("remove"):
        bot.answer_callback_query(call_id, "حذف کالا ثبت شد.")
        p_id = data.split("_")[-1]
        del_prod(p_id)
        bot.send_message(cid, f"کالای {p_id} حذف شد.")


@bot.message_handler(func = lambda message : True)
def message_handler(message):
    cid = message.chat.id
    if message.text == "مشاهده محصولات":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("نوشت افزار", callback_data="products_Writing tools"))
        markup.add(InlineKeyboardButton("پوشاک", callback_data="products_Clothing"))
        markup.add(InlineKeyboardButton("دیجیتال", callback_data="products_Electronics"))
        markup.add(InlineKeyboardButton("ابزار آلات", callback_data="products_Tools"))
        markup.add(InlineKeyboardButton("غیره", callback_data="products_Other"))
        bot.send_message(cid, "لطفا دسته ی مورد نظر را انتخاب کنید.", reply_markup=markup)
    elif message.text == "سبد خرید و نهایی سازی":
        check_user(cid)
        if not carts.get(cid):
            bot.send_message(cid, "محصولی در سبد خرید نیست.")
        else:
            text = ""
            total = 0
            for i in carts[cid]:
                data = get_prod_data(i)
                price = data["Price"]*carts[cid][i]
                total += price
                line = f"کد: {data["ID"]} - {data["Name"]} {data["Descrip"]} - تعداد:  {carts[cid][i]} - قیمت: {price} تومان\n"
                text += line
            line = f"قیمت کل: {total} تومان\n"
            text += line
            data = get_user_data(cid)
            line = f"""
کد مشتری: {cid}
نام مشتری: {data["F_name"]} {data["L_name"]}
شماره ی مشتری: {data["Phone_num"]}
آدرس مشتری: {data["Address"]}"""
            text += line
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("اضافه یا کم کردن یک کالا", callback_data="change_cart"))
            markup.add(InlineKeyboardButton("نهایی کردن خرید", callback_data="finalize"))
            bot.send_message(cid, text, reply_markup=markup)
    elif message.text == "اطلاعات مشتری":
        check_user(cid)
        data = get_user_data(cid)
        text = f"""
نام: {data["F_name"]}
نام خانوادگی: {data["L_name"]}
آدرس: {data["Address"]}
شماره همراه: {data["Phone_num"]}"""
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("اصلاح نام", callback_data="mod_Fname"), InlineKeyboardButton("اصلاح نام خانوادگی", callback_data="mod_Lname"))
        markup.add(InlineKeyboardButton("اصلاح آدرس", callback_data="mod_addr"))
        if get_user_data(cid)["Phone_num"] == None:
            markup.add(InlineKeyboardButton("ثبت شماره همراه", callback_data="mod_phone"))
        bot.send_message(cid, text, reply_markup=markup)
    elif message.text == "مرجوعی":
        bot.send_message(cid, f'لطفا برای مرجوعی با [پشتیبانی](tg://user?id={Support}) تماس بگیرید\\.', parse_mode="MarkdownV2")
    elif steps.get(cid) == "F":
        Fname = message.text
        mod_Fname(Fname, cid)
        steps.pop(cid)
        bot.send_message(cid, "نام شما اصلاح شد.", reply_markup=keyboard)
    elif steps.get(cid) == "L":
        Lname = message.text
        mod_Lname(Lname, cid)
        steps.pop(cid)
        bot.send_message(cid, "نام خانوادگی شما اصلاح شد.", reply_markup=keyboard)
    elif steps.get(cid) == "A":
        Addr = message.text
        mod_addr(Addr, cid)
        steps.pop(cid)
        bot.send_message(cid, "آدرس شما اصلاح شد.", reply_markup=keyboard)
    elif steps.get(cid) == "P":
        steps.pop(cid)
        bot.send_message(cid, "شماره همراه ثبت نشد.", reply_markup=keyboard)
    elif steps.get(cid) == "AP":
        steps.pop(cid)
        bot.send_message(cid, "اضافه کردن کالا لغو شد.")
    elif steps.get(cid) == "CH":
        p_id = message.text.split(" ")[0]
        qty = message.text.split(" ")[1]
        price = message.text.split(" ")[2]
        change_inv_price(p_id, qty, price)
        steps.pop(cid)
        bot.send_message(cid, f'تعداد و قیمت کالای {p_id} به {qty} و {price} تغییر یافت.')

@bot.message_handler(content_types=["contact"])
def contact_handler(message):
    cid = message.chat.id
    contact = message.contact
    if steps.get(cid) == "P":
        user_id = contact.user_id
        if user_id == cid:
            phone = contact.phone_number
            mod_phone(phone, cid)
            bot.send_message(cid, "شماره ی شما ثبت شد.", reply_markup=keyboard)
            steps.pop(cid)
        else:
            bot.send_message(cid, "لطفا شماره ی خود را ارسال کنید.",reply_markup=keyboard)
            steps.pop(cid)

@bot.message_handler(content_types=["photo"])
def photo_handler(message):
    cid = message.chat.id
    if steps.get(cid) == "AP":
        caption = message.caption
        data = caption.split("\n")
        prod_name = data[0].strip()
        prod_qty = int(data[1].strip())
        prod_price = int(data[2].strip())
        prod_desc = data[3].strip()
        File_id = message.photo[-1].file_id
        p_id = insert_product(prod_name, prod_qty, prod_price, prod_desc, File_id=File_id)
        steps.pop(cid)
        markup = InlineKeyboardMarkup()
        for cat in ("Writing tools", "Clothing", "Electronics", "Tools"):
            markup.add(InlineKeyboardButton(cat, callback_data=f'setcat_{p_id}_{cat}'))
        markup.add(InlineKeyboardButton("غیره", callback_data="setcat_null"))
        bot.send_message(cid, "لطفا یک دسته بندی برای کالا انتخاب کنید.", reply_markup=markup, reply_to_message_id=message.message_id)


        

bot.infinity_polling()