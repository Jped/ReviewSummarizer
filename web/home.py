from flask import Flask, render_template, request
import re
from scraper import scrapeAmazonReviews
app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def home():
    if request.method =="GET":
        return render_template("home.html")
    elif request.method=="POST":
        product_selection = request.form.to_dict()
        reviews = {"reviews": False}
        if "product" in product_selection:
            correct = re.match(r"(https?:\/\/)?(www\.)?(?i)amazon\.[a-z]{2,4}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)",product_selection["product"])
            if correct:
                print("scraping reviews")
                scraped_reviews = scrapeAmazonReviews(product_selection["product"])
                reviews = {"reviews":scraped_reviews}
        #make sure we have an amazon link, if we do then run it through the system.
        return render_template("reviews.html", reviews=reviews)
