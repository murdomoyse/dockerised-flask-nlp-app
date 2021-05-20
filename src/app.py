from flask import Flask, request, render_template, Response, url_for
from helpers.common_functions import colouring, format_output_text
from hardrules import HardRules
from json2html import json2html
import logging
import json
import os

log = logging.getLogger(__name__)
app = Flask(__name__, static_folder="./static")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":
        title = str(request.form["title"])
        comment = str(request.form["comment"])
        log.debug("comment and title recieved")

        hr = HardRules(comment=comment, title=title)
        result = hr.apply()
        log.debug("comment and title processed")

        # Formatting json to styled html
        json_result = json.loads(json.dumps(result))
        html_table = json2html.convert(
            json=json_result,
            table_attributes='id="info-table" class="nhsuk-table"',
        )
        html_table = colouring(html_table)
        html_table = format_output_text(html_table)
        log.debug("html outputs rendered")

        return render_template(
            "result.html",
            table=html_table
        )


@app.route("/automoderator", methods=["POST", "GET"])
def automoderator():
    if request.method == "POST":
        title = str(request.form["title"])
        comment = str(request.form["comment"])
        log.debug("comment and title recieved")

        hr = HardRules(comment=comment, title=title)
        result = hr.apply()
        log.debug("comment and title processed")

        return Response(response=json.dumps(result), content_type="application/json")


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)
