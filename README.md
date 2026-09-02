# wetheflywheel

A multi-step agentic content pipeline for **looksmaxxing.guide**. A topic goes
in; an evidence-tagged, harm-reduction-reviewed guide page comes out.

```
topic ─▶ generate ─▶ validate ─▶ publish ─▶ guide.html
          (agent)    (agent+gate)  (render)
```

Built on **Pydantic AI**: each step is a typed agent whose output is a Pydantic
model, run against an OpenRouter model.

- **generate** — a `pydantic_ai.Agent` with `output_type=Guide` turns a topic
  into a validated `Guide` (sections, tips, each tip carrying an evidence level
  + effort/impact). Structural validity is guaranteed by Pydantic.
- **validate** — a second agent (`output_type=Report`) reviews for unsafe advice,
  oversold evidence, and missing harm-reduction cautions. Blockers send the draft
  back to `generate` once with the issues attached.
- **publish** — deterministic `Guide` → HTML. Same renderer for the live page,
  the Cloudflare Pages deploy, and the UI preview.

## Run

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-or-...        # https://openrouter.ai/keys

python app.py                              # flow UI at http://localhost:5000
python pipeline.py "jawline"               # CLI: generate → validate → publish
python pipeline.py --demo                  # offline self-check, no API key
```

`--demo` loads the bundled `sample_guide.json` through Pydantic validation and
the renderer and asserts both work — no API key needed, and it only imports
`pydantic` (not the agents), so it's the smallest thing that fails if wiring breaks.

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
models.py            Pydantic models: Guide, Section, Tip, Report, Issue
provider.py          shared OpenRouter model (OpenAIChatModel + OpenAIProvider)
steps/generate.py    step 1 — Agent(output_type=Guide)
steps/validate.py    step 2 — Agent(output_type=Report), the gate
steps/publish.py     step 3 — renderer (render_page / render_artifact)
pipeline.py          orchestrator + CLI
app.py               Flask flow UI
static/index.html    the UI
sample_guide.json    bundled real skincare guide (demo + offline UI)
public/              deploy root (generated)
```
