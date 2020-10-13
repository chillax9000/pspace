from flask import send_from_directory, request
from flaskr import app
import flaskr.defi as defv


@app.route('/')
def hello_world():
    return send_from_directory("../build", "index.html")


@app.route("/api/<word>", methods=["POST"])
def serve(word):
    data = request.get_json()
    process_func = (defv.process_article_src if data.get("process", False)
                    else defv.process_article_src_dummy)
    html_content, data_src = "No definition found.", None
    if defv.check_input(word):
        word = word.strip()
        html_content, data_src = defv.get_definition_html(word, process_func)
    return {"htmlcontent": html_content, "datasource": data_src}