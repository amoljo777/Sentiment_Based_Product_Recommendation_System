from flask import Flask, render_template, request
from model import recommend_5

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    username = ""
    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not username:
            error = "Please enter a username."
        else:
            recommendations = recommend_5(username)
            if not recommendations:
                error = "Username not found (or user has no ratings). Try an existing username from the dataset."

    return render_template("index.html", recommendations=recommendations, username=username, error=error)

if __name__ == "__main__":
    app.run(debug=True)
