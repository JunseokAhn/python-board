import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(host="localhost", port=27017)
db = client.myweb
col = db.board

header = {"user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Mobile Safari/537.36"}
for i in range(5):
    url = "https://www.google.com/search?q={}&start={}".format("파이썬", i*10)
    r = requests.get(url, headers=header)
    bs = BeautifulSoup(r.text, "lxml")
    lists = bs.select("div.g")

    for l in lists:
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)

        try:
            title = l.select_one("div.V7Sr0.p5AXld.PpBGzd.YcUVQe").text
            contents = l.select_one("div.MUxGbd.yDYNvb.lEBKkf").text
            col.insert_one({
                "name": "테스트",
                "title": title,
                "contents": contents,
                "view": 0,
                "pubdate": current_utc_time
            })
        except:
            pass
        