"""Step 3 — publish: a Guide -> HTML. Deterministic, no model call.

render_page(guide)      -> full standalone document (Cloudflare Pages, Flask preview).
render_artifact(guide)  -> <title>/<style>/<link> + <article> only, for embedding.
"""
import html
import sys

from models import Guide

EVIDENCE_LABEL = {
    "strong": "Strong evidence",
    "moderate": "Moderate evidence",
    "limited": "Limited evidence",
    "anecdotal": "Anecdotal",
}

FONTS = ("https://fonts.googleapis.com/css2?"
         "family=Spectral:ital,wght@0,500;0,600;0,700;1,500&"
         "family=IBM+Plex+Sans:wght@400;500;600&"
         "family=IBM+Plex+Mono:wght@500&display=swap")

CSS = """
:root{
  color-scheme:light;
  --ground:#F2F5F3; --surface:#FFFFFF; --ink:#16211E; --ink-2:#5A6864;
  --line:#DCE3DF; --accent:#1B6A5D; --accent-ink:#0F4C42; --accent-tint:#E3F0EC;
  --on-accent:#FFFFFF; --caution-ink:#8A5714; --caution-tint:#F7ECD7;
  --caution-line:#E7D3AC; --radius:14px; --measure:44rem;
  --serif:"Spectral",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans",system-ui,-apple-system,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,"SF Mono",Menlo,monospace;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --ground:#0D1311; --surface:#141B19; --ink:#E7ECEA; --ink-2:#96A39F;
    --line:#25302D; --accent:#54C4AF; --accent-ink:#7FD6C6; --accent-tint:#12302B;
    --on-accent:#08201C; --caution-ink:#E2B45E; --caution-tint:#241E10;
    --caution-line:#3D3418;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --ground:#0D1311; --surface:#141B19; --ink:#E7ECEA; --ink-2:#96A39F;
  --line:#25302D; --accent:#54C4AF; --accent-ink:#7FD6C6; --accent-tint:#12302B;
  --on-accent:#08201C; --caution-ink:#E2B45E; --caution-tint:#241E10;
  --caution-line:#3D3418;
}
*{box-sizing:border-box;}
body{margin:0; background:var(--ground); color:var(--ink); font-family:var(--sans);
  font-size:1.0625rem; line-height:1.65; -webkit-font-smoothing:antialiased;}
.guide{max-width:var(--measure); margin:0 auto; padding:clamp(1.5rem,4vw,3.5rem) 1.25rem 5rem;}
.masthead{border-bottom:1px solid var(--line); padding-bottom:1.75rem; margin-bottom:2.25rem;}
.eyebrow{font-family:var(--mono); font-size:.72rem; letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent-ink); margin:0 0 1rem;}
h1{font-family:var(--serif); font-weight:700; font-size:clamp(2rem,5vw,2.9rem);
  line-height:1.08; letter-spacing:-.01em; text-wrap:balance; margin:0 0 1rem;}
.dek{font-family:var(--serif); font-style:italic; font-weight:500; font-size:1.3rem;
  line-height:1.45; color:var(--ink-2); margin:0 0 1.25rem; text-wrap:balance;}
.meta{font-family:var(--mono); font-size:.75rem; letter-spacing:.03em; color:var(--ink-2); margin:0;}
.section{margin:2.75rem 0;}
h2{font-family:var(--serif); font-weight:600; font-size:1.55rem; line-height:1.2;
  letter-spacing:-.01em; text-wrap:balance; margin:0 0 .9rem;}
p{margin:0 0 1rem;}
.bottomline{background:var(--accent-tint);
  border:1px solid color-mix(in srgb,var(--accent) 25%,transparent);
  border-radius:var(--radius); padding:1.5rem 1.6rem; margin:0 0 1rem;}
.bl-title{font-family:var(--mono); font-weight:500; font-size:.8rem; letter-spacing:.12em;
  text-transform:uppercase; color:var(--accent-ink); margin:0 0 1rem;}
.bl-steps{margin:0; padding-left:1.2rem; display:flex; flex-direction:column; gap:.6rem;}
.bl-steps li{padding-left:.3rem;}
.tips{list-style:none; margin:1.25rem 0 0; padding:0; display:flex; flex-direction:column;
  gap:1px; background:var(--line); border:1px solid var(--line); border-radius:var(--radius);
  overflow:hidden;}
.tip{background:var(--surface); padding:1.15rem 1.25rem;}
.tip-claim{font-weight:600; margin:0 0 .35rem;}
.tip-detail{color:var(--ink-2); margin:0 0 .85rem; font-size:.98rem;}
.chips{display:flex; flex-wrap:wrap; gap:.4rem;}
.chip{font-family:var(--mono); font-size:.68rem; letter-spacing:.04em; text-transform:uppercase;
  padding:.28rem .55rem; border-radius:999px; white-space:nowrap; border:1px solid transparent;}
.chip-meta{border-color:var(--line); color:var(--ink-2);}
.ev-strong{background:var(--accent); color:var(--on-accent);}
.ev-moderate{background:var(--accent-tint); color:var(--accent-ink);
  border-color:color-mix(in srgb,var(--accent) 30%,transparent);}
.ev-limited{background:var(--caution-tint); color:var(--caution-ink); border-color:var(--caution-line);}
.ev-anecdotal{color:var(--ink-2); border-color:var(--line);}
.caution{margin:1.25rem 0 0; background:var(--caution-tint); border:1px solid var(--caution-line);
  border-radius:var(--radius); padding:1.1rem 1.25rem;}
.caution-tag{display:inline-block; font-family:var(--mono); font-size:.68rem; letter-spacing:.1em;
  text-transform:uppercase; color:var(--caution-ink); margin-bottom:.4rem;}
.caution p{margin:0;}
.sources{margin-top:3rem; border-top:1px solid var(--line); padding-top:1.75rem;}
.sources h2{font-family:var(--mono); font-weight:500; font-size:1rem; text-transform:uppercase;
  letter-spacing:.1em; color:var(--ink-2);}
.src-list{list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:.9rem;}
.src-list li{display:flex; flex-direction:column; gap:.15rem;}
.src-label{font-weight:600; font-size:.95rem;}
.src-note{color:var(--ink-2); font-size:.9rem;}
.colophon{margin-top:2.5rem; padding-top:1.25rem; border-top:1px solid var(--line);
  font-size:.82rem; color:var(--ink-2);}
.colophon p{margin:0;}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth;}}
"""


def _paras(text):
    blocks = [html.escape(b.strip()) for b in text.split("\n\n") if b.strip()]
    return "".join(f"<p>{b}</p>" for b in blocks)


def _tip(tip):
    return (f'<li class="tip">'
            f'<p class="tip-claim">{html.escape(tip.claim)}</p>'
            f'<p class="tip-detail">{html.escape(tip.detail)}</p>'
            f'<div class="chips">'
            f'<span class="chip ev-{tip.evidence}">{EVIDENCE_LABEL[tip.evidence]}</span>'
            f'<span class="chip chip-meta">Effort &middot; {html.escape(tip.effort)}</span>'
            f'<span class="chip chip-meta">Impact &middot; {html.escape(tip.impact)}</span>'
            f'</div></li>')


def _section(section):
    tips = "".join(_tip(t) for t in section.tips)
    caution = ""
    if section.caution:
        caution = (f'<aside class="caution">'
                   f'<span class="caution-tag">Harm reduction</span>'
                   f'<p>{html.escape(section.caution)}</p></aside>')
    return (f'<section class="section"><h2>{html.escape(section.heading)}</h2>'
            f'{_paras(section.body)}<ul class="tips">{tips}</ul>{caution}</section>')


def _head_bits(guide):
    title = html.escape(guide.title)
    return (f'<title>{title}</title>\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n'
            f'<style>{CSS}</style>')


def _body(guide):
    steps = "".join(f"<li>{html.escape(s)}</li>" for s in guide.bottom_line)
    sections = "".join(_section(s) for s in guide.sections)
    sources = "".join(
        f'<li><span class="src-label">{html.escape(s.label)}</span>'
        f'<span class="src-note">{html.escape(s.note)}</span></li>'
        for s in guide.sources)
    return (
        f'<article class="guide">'
        f'<header class="masthead">'
        f'<p class="eyebrow">looksmaxxing.guide &middot; {html.escape(guide.topic)}</p>'
        f'<h1>{html.escape(guide.title)}</h1>'
        f'<p class="dek">{html.escape(guide.dek)}</p>'
        f'<p class="meta">Updated {html.escape(guide.updated)} &middot; '
        f'{guide.reading_time_min} min read &middot; Evidence-led</p>'
        f'</header>'
        f'<section class="bottomline"><h2 class="bl-title">The bottom line</h2>'
        f'<ol class="bl-steps">{steps}</ol></section>'
        f'{sections}'
        f'<section class="sources"><h2>What this is based on</h2>'
        f'<ul class="src-list">{sources}</ul></section>'
        f'<footer class="colophon"><p>General information, not medical advice. '
        f'See a qualified professional for diagnosis or treatment.</p></footer>'
        f'</article>')


def render_artifact(guide):
    return _head_bits(guide) + "\n" + _body(guide)


def render_page(guide):
    return ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f'{_head_bits(guide)}\n</head>\n<body>\n{_body(guide)}\n</body>\n</html>\n')


if __name__ == "__main__":
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        sys.exit("usage: python publish.py [--artifact] <guide.json> <out.html>")
    with open(args[0]) as fh:
        guide = Guide.model_validate_json(fh.read())
    render = render_artifact if "--artifact" in flags else render_page
    with open(args[1], "w") as fh:
        fh.write(render(guide))
    print(f"wrote {args[1]}")
