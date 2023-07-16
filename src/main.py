from flask import Flask,render_template
app = Flask(__name__,template_folder='templates')

app.debug = True
app.jinja_env.auto_reload = True

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/getRecommendation")
def getRecommendation():
    return render_template("getRecommendation.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run()