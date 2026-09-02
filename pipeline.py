"""generate -> validate -> publish orchestrator for looksmaxxing.guide.

  python pipeline.py "skincare basics"   # live: needs OPENROUTER_API_KEY
  python pipeline.py --demo               # offline: sample -> validate -> publish
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from steps.publish import render_page  # noqa: E402
from steps.validate import validate    # noqa: E402

PUBLIC = os.path.join(HERE, "public")


def run(topic, use_model=True, max_attempts=2):
    """generate -> validate, with one repair retry on a blocking review.

    Returns (guide, report). Warnings ship; blockers trigger a retry that feeds
    the issues back to the generator. Raises if blockers survive every attempt.
    """
    from steps.generate import generate
    feedback, report = None, None
    for _ in range(max_attempts):
        guide = generate(topic, feedback=feedback)
        report = validate(guide, use_model=use_model)
        if report["passed"] or not any(i["severity"] == "blocker" for i in report["issues"]):
            return guide, report
        feedback = [f'{i["where"]}: {i["message"]}' for i in report["issues"]]
    raise RuntimeError(f"validation gate failed after {max_attempts} attempts: {report}")


def publish(guide, out_dir=PUBLIC):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "index.html")
    with open(path, "w") as fh:
        fh.write(render_page(guide))
    return path


def _demo():
    """Offline check: sample guide -> schema-only validate -> publish. No API key."""
    with open(os.path.join(HERE, "sample_guide.json")) as fh:
        guide = json.load(fh)
    report = validate(guide, use_model=False)
    assert report["passed"], f"sample must pass the schema gate: {report}"
    path = publish(guide)
    assert os.path.getsize(path) > 2000, "rendered HTML looks empty"
    print(f"demo ok -> {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        _demo()
    elif len(sys.argv) > 1:
        guide, report = run(sys.argv[1])
        path = publish(guide)
        print(f"published {sys.argv[1]!r} -> {path}\nreport: {json.dumps(report)}")
    else:
        print('usage: python pipeline.py "topic"  |  python pipeline.py --demo')
