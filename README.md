# wetheflywheel

A multi-step agentic content pipeline for **looksmaxxing.guide**. A topic goes
in; an evidence-tagged, harm-reduction-reviewed guide page comes out.

```
topic ─▶ generate ─▶ validate ─▶ publish ─▶ guide.html
          (agent)    (agent+gate)  (render)
```

- **generate** — an OpenRouter model turns a topic into structured guide JSON
  (sections, tips, each tip carrying an evidence level + effort/impact).
- **validate** — a code-side schema check **and** a cheaper model reviewing for
  unsafe advice, oversold evidence, and missing harm-reduction cautions. Blockers
  send the draft back to `generate` once with the issues attached.
- **publish** — deterministic JSON → HTML. Same renderer for the live page, the
  Cloudflare Pages deploy, and the UI preview.

## Run

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-or-...        # https://openrouter.ai/keys

python app.py                              # flow UI at http://localhost:5000
python pipeline.py "jawline"               # CLI: generate → validate → publish
python pipeline.py --demo                  # offline self-check, no API key
```

`--demo` runs the bundled `sample_guide.json` through the schema gate and the
renderer and asserts both work — the smallest thing that fails if wiring breaks.

## Config

| env | default | notes |
|-----|---------|-------|
| `OPENROUTER_API_KEY` | — | required for live runs |
| `GENERATE_MODEL` | `openai/gpt-5` | any slug from openrouter.ai/models |
| `VALIDATE_MODEL` | `openai/gpt-5-mini` | cheaper model for the review pass |

## Deploy (Cloudflare Pages)

`publish` writes to `public/`, which is the Pages deploy root:

```bash
python pipeline.py --demo                  # or a live run; both write public/index.html
npx wrangler pages deploy public --project-name looksmaxxing-guide
```

`wrangler` uses `CLOUDFLARE_API_TOKEN` (+ `CLOUDFLARE_ACCOUNT_ID`) if set,
otherwise `npx wrangler login` first.

## Layout

```
schema.py            guide + report JSON schemas (shared)
client.py            OpenRouter client + structured() helper
steps/generate.py    step 1
steps/validate.py    step 2 (the gate)
steps/publish.py     step 3 (renderer; render_page / render_artifact)
pipeline.py          orchestrator + CLI
app.py               Flask flow UI
static/index.html    the UI
sample_guide.json    bundled real skincare guide (demo + offline UI)
public/              deploy root (generated)
```
