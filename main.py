# project: p4
# submitter: jjung83
# partner: none
# hours: 20

# zip ../p4.zip main.py main.csv *.html

import pandas as pd
from flask import Flask, request, jsonify, Response
import time
import re
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
df = pd.read_csv("main.csv")
count_pageA = 0
count_pageB = 0
count = 0
b_dict = {}

@app.route('/')
def home():
    global count
    global count_pageA
    global count_pageB
    count += 1
    with open("index.html") as f:
        html = f.read()
    if(count % 2 == 0 and count <= 10) or (count > 10 and count_pageA > count_pageB):
        html = html.replace('donate.html', 'donate.html?from=A" style = "color : skyblue')
    if(count % 2 == 1 and count <= 10) or (count > 10 and count_pageA <= count_pageB):
        html = html.replace('donate.html', 'donate.html?from=B" style = "color : pink')

    return html

@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[A-Za-z0-9]+@{1}[A-Za-z0-9]+(\b.com\b)$", email)) > 0: # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2     
        with open("emails.txt", 'r') as ff:    
            num_subscribed = len(ff.readlines())
        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    return jsonify(f"Please check your email and write it again.") # 3

@app.route("/donate.html")
def donate():
    global count_pageA
    global count_pageB
    link_type = request.args.get("from")
    if link_type == "A":
        count_pageA += 1
    with open("donate.html") as f:
        html = f.read()
        #     return html
    if link_type == "B":
        count_pageB += 1
        with open("donate1.html") as f:
            html = f.read()
            # return html
    # html = "<body>{}<body>".format("<h1>Donate<h1>")
    return html

@app.route("/browse.html")
def browse():
    with open("browse.html") as f:
        html = f.read() + pd.read_csv("main.csv").to_html()
        return html

@app.route("/browse.json")
def b_json():
    global b_dict
    if request.remote_addr not in b_dict:
        b_dict[request.remote_addr] = 0
    if time.time() - b_dict[request.remote_addr] > 60:
        b_dict[request.remote_addr] = time.time()
        res = pd.read_csv("main.csv").to_dict()
        return jsonify(res)
    else:
        return Response("<b>TOO MANY REQUESTS</b>",status = 429, headers = {"Retry-After": "60"})
    
@app.route("/visitors.json")
def v_json():
    return b_dict

@app.route("/dashboard_1.svg")
def dash1():
    global df
    fig, ax = plt.subplots()
    bin_num = request.args.get("bins")
    ax.set_xlabel("Uploads")
    ax.set_ylabel("Number of people")
    ax.set_title("Number of Uploads by top 100 YouTuber")
    if bin_num is None:      
        df["Uploads"] = df["Uploads"].astype(str).astype(int)
        ax = df["Uploads"].plot.hist(bins = int(10))
        "dashboard_1.svg" + '?bins=' + str(10)
        ax.get_figure().savefig("dashboard_1.svg")
        plt.close(fig)
        with open("dashboard_1.svg") as f:
            return Response(f.read(), headers = {"Content-Type": "image/svg+xml"})
    else:
        df["Uploads"] = df["Uploads"].astype(str).astype(int)
        ax = df["Uploads"].plot.hist(bins = int(bin_num))
        "dashboard_1.svg" + '?bins=' + str(bin_num)
        ax.get_figure().savefig("dashboard_1.svg")
        plt.close(fig)
        with open("dashboard_1.svg") as f:
            return Response(f.read(), headers = {"Content-Type": "image/svg+xml"})
        
@app.route("/dashboard_2.svg")
def dash2():
    global df
    fig, ax = plt.subplots()
    
    for c_num in df["Subscribers"]:
        df["Uploads"] = df["Uploads"].astype(str).astype(int)
        df["Subscribers"] = df["Subscribers"].astype(str)
        df["Subscribers"] = df["Subscribers"].str.replace("M", "")
        # df["Subscribers"] = Double.parseDouble(df["Subscribers"])
        df["Subscribers"] = df["Subscribers"].astype(float)
    # ax = df["Subscribers", "Uploads"].plot.scatter()
    plt.scatter(df["Subscribers"], df["Uploads"])
    ax.set_xlabel("Subscribers")
    ax.set_ylabel("Uploads")
    ax.set_title("Number of Uploads by YouTube Subscribers")
    ax.get_figure().savefig("dashboard_2.svg")
    plt.close(fig)
    with open("dashboard_2.svg") as f:
        return Response(f.read(), headers = {"Content-Type": "image/svg+xml"})
           
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
