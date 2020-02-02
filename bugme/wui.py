from flask import Flask, render_template, request, redirect, url_for

import app

WEB_APP_NAME = "bugme"
instance = app.get_app_instance()
if instance is None:
    raise RuntimeError("No valid instance found")
web_app = Flask(WEB_APP_NAME)


IN_PROGRESS = '''
<html>
<H2> Page under construction </H2>
<p> The page or functionality you have requested in under construction </p>
</html>'''


def in_progress():
    return IN_PROGRESS

@web_app.route("/")
@web_app.route("/dashboard")
def dashboard():
    bugs = app.get_all_bugs(instance)

    required_columns = ['defect_id', 'description', 'created_date', 'status']
    bug_list = []
    for bug in bugs:
        item = {key:value for key, value in bug.items() if key in required_columns}
        bug_list.append(item)
    bugs = bug_list
    header = bugs[0].keys()
    header = [item.replace('_',' ').title() for item in header]
    header[0] = 'ID'

    values = [list(bug.values()) for bug in bugs]
    context = {"header": header, "bugs":values}
    text = render_template("dashboard.html", **context)
    return text

@web_app.route("/new_defect", methods=["GET", "POST"])
def new_defect():
    if request.method == "POST":
        print(request.form)
        description = request.form["description"]
        expected = request.form["expected"]
        observed = request.form["observed"]
        def_id = app.create_new_defect(description, expected, observed, instance)
        return redirect(url_for("get_defect", defect_id=def_id))
    resp = render_template("new.html")
    return resp

@web_app.route("/view/<int:defect_id>")
def get_defect(defect_id):
    bug = app.get_bug(defect_id, instance)
    resp = render_template("defect.html", bug=bug)
    return resp

web_app.run()
