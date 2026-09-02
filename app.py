"""Local flow UI: watch generate -> validate -> publish run for a topic.

  python app.py   ->  http://localhost:5000

Without OPENROUTER_API_KEY (or with the "use sample" box ticked) it runs the
bundled skincare guide through schema-validate + publish, so the UI works offline.
"""
import json
import os
import sys

from flask import Flask, jsonify, request, send_from_directory

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from pipeline import run  # noqa: E402
from steps.publish import render_page  # noqa: E402
from steps.validate import validate  # noqa: E402

app = Flask(__name__, static_folder=os.path.join(HERE, "static"))


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/run")
def run_flow():
    data = request.get_json(force=True) or {}
    topic = (data.get("topic") or "").strip()
    offline = data.get("demo") or not os.environ.get("OPENROUTER_API_KEY")
    if offline:
        with open(os.path.join(HERE, "sample_guide.json")) as fh:
            guide = json.load(fh)
        report = validate(guide, use_model=False)
        mode = "offline sample"
    else:
        guide, report = run(topic)
        mode = "live"
    return jsonify(mode=mode, topic=guide["topic"], guide=guide,
                   report=report, html=render_page(guide))


if __name__ == "__main__":
    app.run(port=5000, debug=True)
