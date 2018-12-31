from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def home():
    if request.method =="GET":
        return render_template("home.html")
    elif request.method=="POST":
        product_selection = request.form
        return render_template("reviews.html")
