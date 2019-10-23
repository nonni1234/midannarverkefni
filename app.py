import os
from flask import Flask, render_template as template, session, url_for, request, redirect, json
import urllib.request
from jinja2 import ext
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(8)

with urllib.request.urlopen("https://apis.is/petrol") as url:
    dicta = json.loads(url.read().decode())

li = dicta["results"]
date = dicta["timestampPriceCheck"]
def inttomon(i):
    dicta = {
        "01": "janúar",
        "02": "febrúar",
        "03": "mars",
        "04": "apríl",
        "05": "maí",
        "06": "júní",
        "07": "júlí",
        "08": "ágúst",
        "09": "september",
        "10": "október",
        "11": "nóvember",
        "12": "desember"
    }
    return dicta[i]

date = dicta["timestampPriceCheck"]
def getdate(values, date=date):
    obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    #print(obj)
    values = values
    return obj.strftime(f"%d {inttomon(obj.strftime('%m'))} %Y %H:%M")

app.jinja_env.filters['getdate'] = getdate

# Til að setja date inní eitthvað notaru {{ 0 | getdate }}
cheapest = {"bensin": 10000, "bensin-nafn": None, "diesel": 10000, "diesel-nafn": None}
def companies():
    companies_list = []
    for x in li:
        if x["bensin95"] < cheapest["bensin"]:
            cheapest["bensin"] = x["bensin95"]
            cheapest["bensin-nafn"] = x["company"]
        if x["diesel"] < cheapest["diesel"]:
            cheapest["diesel"] = x["diesel"]
            cheapest["diesel-nafn"] = x["company"]
        if x["company"] not in companies_list:
            companies_list.append(x["company"])
    return companies_list

def stadir():
    stodvar = {}
    for x in li:
        nafn = x["company"]
        if nafn not in stodvar:
            stodvar[nafn] = [{
                "bensin": x["bensin95"],
                "diesel": x["diesel"],
                "geo": x["geo"],
                "nafn": x["name"],
                "company": x["company"]
                }]
        else:
            stodvar[nafn].append({
                "bensin":x["bensin95"],
                "diesel":x["diesel"],
                "geo":x["geo"],
                "nafn":x["name"],
                "company":x["company"]})
    return stodvar
        

@app.route("/")
def home():
    return template("index.html", li=li, listi = companies(), cheapest= cheapest)

@app.route("/company/<nafn>")
def fyrirtaeki(nafn):
    listi = stadir()
    return template("stadir.html",nafn = nafn, stodvar = listi[nafn])

@app.route("/<company>/<nafn>")
def stod(nafn,company):
    listi = stadir()[company]
    for i in listi:
        if i["nafn"] == nafn:
            dic = i
            break
    return template("stod.html",nafn=dic["nafn"],lat=dic["geo"]["lat"],lon=dic["geo"]["lon"],company = company, bensin=dic["bensin"],diesel=dic["diesel"])
@app.errorhandler(404)
def pagenotfound(error):
    return template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)