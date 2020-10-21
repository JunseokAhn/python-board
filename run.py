from flask import Flask, request, render_template, abort, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import time
import math

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myweb"
app.secret_key = 'some secret key'
app.config["PERMANENT_SESSSION_LIFETIME"] = timedelta(minutes=30)
mongo = PyMongo(app)

@app.route("/list")
def lists():
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", 5, type=int)
    search = request.args.get("search", -1, type=int)
    keyword = request.args.get("keyword", type=str)
    
    query = {}
    search_list = []
    if search == 0:
        search_list.append({"title": {"$regex": keyword}})
    elif search == 1:
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 2:
        search_list.append({"title": {"$regex": keyword}})
        search_list.append({"contents": {"$regex": keyword}})
    elif search == 3:
        search_list.append({"name": {"$regex": keyword}})

    if len(search_list) > 0:
        query = {"$or": search_list}
    print(query)

    board = mongo.db.board
    datas = board.find(query).skip((page-1)*limit).limit(limit)
    
    tot_count = board.find({}).count()
    last_page_num = math.ceil(tot_count / limit)
    block_size = 5
    block_num = int((page-1) / block_size)
    block_start = int((block_size * block_num) + 1)
    block_last = math.ceil(block_start + (block_size - 1))

    return render_template(
        "list.html",
        datas=datas,
        limit=limit,
        page=page,
        block_start=block_start,
        block_last=block_last,
        last_page_num=last_page_num,
        search=search,
        keyword=keyword)

@app.template_filter("formatdatetime")
def format_datetime(value):
    if value is None:
        return ""
    
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp) 
    value = datetime.fromtimestamp((int(value) / 1000)) + offset
    return value.strftime('%Y-%m-%d %H:%M:%S')

@app.route("/view/<idx>")
def board_view(idx):
    # idx = request.args.get("idx")
    if idx is not None:
        page = request.args.get("page")
        search = request.args.get("search")
        keyword = request.args.get("keyword")
        board = mongo.db.board
        data = board.find_one(
            {"_id": ObjectId(idx)}
        )

        if data is not None:
            result = {
                "id": data.get("id"),
                "name": data.get("name"),
                "title": data.get("title"),
                "contents": data.get("contents"),
                "pubdate": data.get("pubdate"),
                "view":data.get("view")
            }
        
            return render_template("view.html", result=result, page=page, search=search, keyword=keyword)
    return abort(404)


@app.route("/write", methods=["GET", "POST"])
def board_write():
    if request.method == "POST":
        name = request.form.get("name")
        title = request.form.get("title")
        contents = request.form.get("contents")
        print(name, title, contents)
        
        current_utc_time = round(datetime.utcnow().timestamp()*1000)
        
        board = mongo.db.board
        
        post = {
            "name": name,
            "title": title,
            "contents": contents,
            "pubdate": current_utc_time,
            "view": 0
        }

        x = board.insert_one(post)
        print(x.inserted_id)
        return redirect(url_for("board_view", idx=x.inserted_id))
    else:
        return render_template("write.html")


@app.route("/join", methods=["GET", "POST"])   
def member_join():
    if request.method == "POST":
        name = request.form.get("name", type=str)
        email = request.form.get("email", type=str)
        pass1 = request.form.get("pass1", type=str)
        pass2 = request.form.get("pass2", type=str)

        if name == "" or email == "" or pass1 == "" or pass2 == "":
            flash("입력되지 않은 값이 있습니다.")
            return render_template("join.html")
        
        if pass1 != pass2:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template("join.html") 

        members = mongo.db.members
        cnt = members.find({"email": email}).count()
        if cnt>0:
            flash("중복된 이메일 주소입니다.")
            return render_template("join.html")

        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        post = {
            "name": name,
            "email": email,
            "pass": pass1,
            "joindate": current_utc_time,
            "logintime": "",
            "logincount": 0
        }

        members.insert_one(post)
        return ""
    else:
        return render_template("join.html")

@app.route("/login", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("pass")

        members = mongo.db.members
        data = members.find_one({"email": email})

        if data is None:
            flash("회원 정보가 없습니다.")
            return redirect(url_for("member_login"))

        else:
            if data.get("pass") == password:
                session["email"] = email
                session["name"] = data.get("name")
                session["id"] = str(data.get("_id"))
                session.permanent = True
                return redirect(url_for("lists"))

            else:
                flash("회원 정보가 없습니다2.")
                return redirect(url_for("member_login"))

        return ""
    else:
        return render_template("login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=9000)
