"""Synthetic design-system/4 showcase fixture: "Harbor Berth Desk".

SYNTHETIC FIXTURE, NOT AN APPROVED PRODUCT. The HiFi pages below stand in for
an approved ui-hifi/2 package so tests can exercise every gallery path:
variants, rendered and pseudo states, hidden state views, menus, tabs,
container queries, motion triggers and reduced motion.

Regenerate the committed demo after an intentional renderer change:
    python skills/design-system-compiler/scripts/tests/showcase_fixture.py --write
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

DEMO_DIR = Path(__file__).resolve().parent / "fixtures" / "showcase-demo"
CSP = ("default-src 'none'; base-uri 'none'; connect-src 'none'; form-action 'none'; frame-src 'none'; "
       "object-src 'none'; navigate-to 'self'; img-src data:; media-src data:; font-src data:; "
       "style-src 'unsafe-inline'; script-src 'unsafe-inline'")

PRODUCT_CSS = """
:root{--harbor-ink:#16324f;--sea:#2f6f8f;--buoy:#e0a526;--mist:#eef3f5;--alarm:#b3261e;--kelp:#2e6b4f;
--space-1:4px;--space-2:8px;--space-3:12px;--space-4:16px;--space-6:24px;--radius-control:6px;--radius-card:12px;
--shadow-card:0 1px 2px rgba(22,50,79,.18),0 6px 18px rgba(22,50,79,.10);--duration-quick:160ms;--duration-sheet:320ms;
--ease-out:cubic-bezier(.2,0,0,1)}
body{font:16px/1.5 "Segoe UI",system-ui,sans-serif;color:var(--harbor-ink);background:var(--mist)}
[data-hifi-canvas]{container-type:inline-size;margin:0 auto}
[data-hifi-canvas][data-hifi-target="390"]{width:390px}[data-hifi-canvas][data-hifi-target="768"]{width:768px}
[data-hifi-canvas][data-hifi-target="1200"]{width:1200px}
.desk{display:grid;gap:var(--space-4);padding:var(--space-4)}
.desk h1{font-size:28px;line-height:1.15;margin:0}
.btn{font:600 15px/1 inherit;border-radius:var(--radius-control);padding:var(--space-3) var(--space-4);min-height:44px;border:2px solid var(--harbor-ink);cursor:pointer;transition:background-color var(--duration-quick) var(--ease-out)}
.btn[data-tone="primary"]{background:var(--harbor-ink);color:#fff}.btn[data-tone="secondary"]{background:#fff;color:var(--harbor-ink)}
.btn:hover{background:var(--sea);color:#fff}.btn:focus-visible{outline:3px solid var(--buoy);outline-offset:2px}
.btn:active{transform:translateY(1px)}.btn:disabled{opacity:.45;cursor:not-allowed;background:#fff;color:var(--harbor-ink)}
.field{font:inherit;border:2px solid var(--sea);border-radius:var(--radius-control);padding:var(--space-2) var(--space-3);min-height:44px;width:100%;box-sizing:border-box}
.field:focus-visible{outline:3px solid var(--buoy);outline-offset:1px}.field[aria-invalid="true"]{border-color:var(--alarm)}
.field-error{color:var(--alarm);font-size:14px;margin:var(--space-1) 0 0}
.tag{display:inline-block;border-radius:999px;padding:2px var(--space-3);font-size:13px;font-weight:600}
.tag[data-tone="calm"]{background:#d8ece3;color:var(--kelp)}.tag[data-tone="alert"]{background:#f6d9d6;color:var(--alarm)}
.berth-card{background:#fff;border-radius:var(--radius-card);box-shadow:var(--shadow-card);padding:var(--space-4);display:grid;gap:var(--space-2)}
.berth-card[data-card-state="loading"] p{background:linear-gradient(90deg,#e4ebee,#f4f7f8);color:transparent;border-radius:4px}
.berth-card[data-card-state="empty"]{border:2px dashed var(--sea);box-shadow:none}
.board{display:grid;gap:var(--space-4)}
@container (min-width:700px){.board{grid-template-columns:repeat(2,minmax(0,1fr))}}
@container (min-width:1100px){.board{grid-template-columns:repeat(3,minmax(0,1fr))}.desk{padding:var(--space-6)}}
.sheet{background:#fff;border-top:4px solid var(--buoy);padding:var(--space-4);transform:translateY(24px);opacity:.2;transition:transform var(--duration-sheet) var(--ease-out),opacity var(--duration-sheet) var(--ease-out)}
.sheet[data-open="true"]{transform:none;opacity:1}
.tide-dot{display:inline-block;width:12px;height:12px;border-radius:50%;background:var(--sea);animation:tide-pulse 1.6s var(--ease-out) infinite}
@keyframes tide-pulse{0%{transform:scale(.6);opacity:.5}50%{transform:scale(1);opacity:1}100%{transform:scale(.6);opacity:.5}}
.menu{list-style:none;margin:var(--space-2) 0 0;padding:var(--space-2);background:#fff;border-radius:var(--radius-control);box-shadow:var(--shadow-card)}
.menu [role="menuitem"]{display:block;width:100%;text-align:left;border:0;background:none;padding:var(--space-2);font:inherit}
.menu [role="menuitem"]:focus-visible{outline:2px solid var(--buoy)}
.tabs{display:flex;gap:var(--space-2)}.tabs [role="tab"][aria-selected="true"]{border-bottom:3px solid var(--buoy)}
@media (prefers-reduced-motion:reduce){.sheet{transition:none}.tide-dot{animation:none}.btn{transition:none}}
"""

REVIEWER_SEGMENT = ("<!-- hifi-reviewer:css:start --><style>[data-hifi-reviewer-shell]{position:fixed;left:0;top:0;"
                    "width:240px}</style><!-- hifi-reviewer:css:end -->")
PRODUCT_SCRIPT = """document.querySelectorAll("[data-product-menu]").forEach(button => {
  const menu = document.getElementById(button.getAttribute("aria-controls"));
  button.addEventListener("click", () => { const open = button.getAttribute("aria-expanded") !== "true"; button.setAttribute("aria-expanded", String(open)); menu.hidden = !open; if (open) menu.querySelector("[role=menuitem]").focus(); });
  menu.addEventListener("keydown", event => { if (event.key === "Escape") { button.setAttribute("aria-expanded", "false"); menu.hidden = true; button.focus(); } });
});
document.querySelectorAll("[data-product-tab]").forEach(tab => tab.addEventListener("click", () => {
  document.querySelectorAll("[data-product-tab]").forEach(peer => { peer.setAttribute("aria-selected", String(peer === tab)); document.getElementById(peer.getAttribute("aria-controls")).hidden = peer !== tab; });
}));"""


def _card(state: str, title: str, body: str) -> str:
    return (f'<article class="berth-card" data-card-state="{state}" data-specimen-variant="default" '
            f'data-specimen-state="{state}"><h2>{title}</h2><p>{body}</p></article>')


def _page(surface: str, route: str, body: str, *, manifest: str = "") -> str:
    return ('<!doctype html><html lang="en"><head><meta http-equiv="Content-Security-Policy" content="' + CSP + '">'
            f"<title>Harbor Berth Desk {surface}</title><style>{PRODUCT_CSS}</style>{REVIEWER_SEGMENT}</head><body>"
            '<aside data-hifi-reviewer-shell data-hifi-reviewer-version="3">Reviewer shell</aside>'
            '<main data-hifi-reviewer-main><div data-hifi-canvas data-hifi-targets="390 768 1200" data-hifi-target="390">'
            f'<section class="desk" data-ui-surface="{surface}" data-ui-route="{route}">{body}</section></div></main>'
            f"<script>{PRODUCT_SCRIPT}</script>{manifest}</body></html>")


def board_page(manifest: str) -> str:
    views = "".join(
        f'<div data-hifi-state-view="{state}" data-responsive-target="{target}"{" hidden" if state != "ready" or target != "390" else ""}>'
        + ('<div class="board">' + _card(state, "Berth 4", {"ready": "Northbound ferry, 14:20 arrival",
                                                          "loading": "Loading arrivals",
                                                          "empty": "No vessel assigned"}[state]) + "</div>")
        + "</div>" for state in ("ready", "loading", "empty") for target in ("390", "768", "1200"))
    body = ('<header><h1>Berth board</h1><span class="tag" data-tone="calm" data-specimen-variant="calm" data-specimen-state="default">Tide steady</span> '
            '<span class="tag" data-tone="alert" data-specimen-variant="alert" data-specimen-state="default">Swell warning</span> '
            '<span class="tide-dot" data-specimen-variant="default" data-specimen-state="default" aria-hidden="true"></span></header>'
            '<div><button type="button" class="btn" data-tone="primary" data-control-id="assign" data-specimen-variant="primary md" data-specimen-state="default">Assign berth</button> '
            '<button type="button" class="btn" data-tone="secondary" data-control-id="hold" data-specimen-variant="secondary md" data-specimen-state="default">Hold vessel</button> '
            '<button type="button" class="btn" data-tone="primary" disabled data-specimen-variant="primary md" data-specimen-state="disabled">Assign berth</button></div>'
            '<div><button type="button" class="btn" data-tone="secondary" data-product-menu aria-controls="berth-menu" aria-expanded="false" '
            'data-control-id="more" data-specimen-variant="secondary md" data-specimen-state="default">More actions</button>'
            '<ul class="menu" id="berth-menu" role="menu" hidden><li><button type="button" role="menuitem">Swap berth</button></li>'
            '<li><button type="button" role="menuitem">Release berth</button></li></ul></div>'
            '<label>Vessel call sign <input class="field" value="MV Selkie" data-control-id="callsign" data-specimen-variant="default" data-specimen-state="default"></label>'
            '<label>Draft in metres <input class="field" aria-invalid="true" value="41" data-specimen-variant="default" data-specimen-state="error"></label>'
            '<p class="field-error">Draft exceeds the 12 m limit for Berth 4.</p>'
            '<label>Pilot <input class="field" disabled value="Assigned by port control" data-specimen-variant="default" data-specimen-state="disabled"></label>'
            f"{views}"
            '<aside class="sheet" data-open="false" data-specimen-variant="default" data-specimen-state="default"><h2>Arrival brief</h2>'
            '<p>Pilot boards at the outer mark.</p></aside>'
            '<a class="btn" data-tone="secondary" href="log.html" data-navigation-id="log">Open tide log</a>')
    return _page("UI-001", "/berths", body, manifest=manifest)


def log_page() -> str:
    body = ('<header><h1>Tide log</h1></header><div class="tabs" role="tablist">'
            '<button type="button" class="btn" data-tone="secondary" role="tab" data-product-tab aria-controls="tab-today" aria-selected="true" data-control-id="today" data-specimen-variant="secondary md" data-specimen-state="default">Today</button>'
            '<button type="button" class="btn" data-tone="secondary" role="tab" data-product-tab aria-controls="tab-week" aria-selected="false" data-control-id="week">This week</button></div>'
            '<div id="tab-today" role="tabpanel"><p>High water 11:42, 4.1 m.</p></div>'
            '<div id="tab-week" role="tabpanel" hidden><p>Spring tides from Thursday.</p></div>'
            '<div data-hifi-state-view="ready" data-responsive-target="390"></div>'
            '<a class="btn" data-tone="primary" href="index.html" data-navigation-id="board">Back to berths</a>')
    return _page("UI-002", "/tides", body)


def demo_pages() -> dict[str, str]:
    log = log_page()
    manifest = {
        "schema": "ui-hifi/2",
        "pages": [{"path": "log.html", "sha256": hashlib.sha256(log.encode("utf-8")).hexdigest()}],
        "surfaces": [
            {"id": "UI-001", "page": "index.html", "route": "/berths", "states": ["ready", "loading", "empty"],
             "responsive": {"kind": "viewports", "targets": [390, 768, 1200]}, "navigation": ["log"],
             "controls": ["assign", "hold", "more", "callsign"]},
            {"id": "UI-002", "page": "log.html", "route": "/tides", "states": ["ready"],
             "responsive": {"kind": "viewports", "targets": [390, 768, 1200]}, "navigation": ["board"],
             "controls": ["today", "week"]},
        ],
        "interactions": [
            {"id": "OP-open-actions", "source": {"surface": "UI-001", "state": "ready"}, "control": "more",
             "kind": "state", "destination": {"surface": "UI-001", "state": "ready"}},
            {"id": "OP-view-log", "source": {"surface": "UI-001", "state": "ready"}, "control": "log",
             "kind": "navigate", "destination": {"surface": "UI-002", "state": "ready"}},
            {"id": "OP-week", "source": {"surface": "UI-002", "state": "ready"}, "control": "week",
             "kind": "state", "destination": {"surface": "UI-002", "state": "ready"}},
        ],
    }
    script = f'<script id="ui-hifi-manifest" type="application/json">{json.dumps(manifest)}</script>'
    return {"index.html": board_page(script), "log.html": log}


def demo_registry() -> dict:
    na = "not_applicable"
    primitives = {
        "Button": {"dsId": "DS-CTL-001", "layer": "control", "class": "btn", "variants": ["primary", "secondary"],
                   "sizes": ["md"], "defaults": {"variants": "primary", "sizes": "md"}, "minTargetPx": 44},
        "TextField": {"dsId": "DS-CTL-002", "layer": "control", "class": "field", "variants": ["default"]},
        "StatusTag": {"layer": "surface", "class": "tag", "tones": ["calm", "alert"]},
        "TideDot": {"layer": "surface", "class": "tide-dot"},
        "ArrivalSheet": {"layer": "surface", "class": "sheet"},
    }
    specimens = [
        {"id": "button-primary", "subject": {"kind": "primitive", "name": "Button"}, "axes": {"variants": "primary", "sizes": "md"},
         "source": {"page": "index.html", "selector": ".btn", "variant": "primary md", "state": "default"}},
        {"id": "button-secondary", "subject": {"kind": "primitive", "name": "Button"}, "axes": {"variants": "secondary", "sizes": "md"},
         "source": {"page": "index.html", "selector": ".btn", "variant": "secondary md", "state": "default"}},
        {"id": "button-disabled", "subject": {"kind": "primitive", "name": "Button"}, "axes": {"variants": "primary"},
         "source": {"page": "index.html", "selector": ".btn", "variant": "primary md", "state": "disabled"}},
        {"id": "tab-button", "subject": {"kind": "primitive", "name": "Button"}, "axes": {"variants": "secondary"},
         "source": {"page": "log.html", "selector": ".btn", "variant": "secondary md", "state": "default"}},
        {"id": "field-default", "subject": {"kind": "primitive", "name": "TextField"}, "axes": {"variants": "default"},
         "source": {"page": "index.html", "selector": ".field", "variant": "default", "state": "default"}},
        {"id": "field-error", "subject": {"kind": "primitive", "name": "TextField"}, "axes": {"variants": "default"},
         "source": {"page": "index.html", "selector": ".field", "variant": "default", "state": "error"}},
        {"id": "field-disabled", "subject": {"kind": "primitive", "name": "TextField"}, "axes": {"variants": "default"},
         "source": {"page": "index.html", "selector": ".field", "variant": "default", "state": "disabled"}},
        {"id": "tag-calm", "subject": {"kind": "primitive", "name": "StatusTag"}, "axes": {"tones": "calm"},
         "source": {"page": "index.html", "selector": ".tag", "variant": "calm", "state": "default"}},
        {"id": "tag-alert", "subject": {"kind": "primitive", "name": "StatusTag"}, "axes": {"tones": "alert"},
         "source": {"page": "index.html", "selector": ".tag", "variant": "alert", "state": "default"}},
        {"id": "tide-dot", "subject": {"kind": "primitive", "name": "TideDot"}, "axes": {},
         "source": {"page": "index.html", "selector": ".tide-dot", "variant": "default", "state": "default"}},
        {"id": "arrival-sheet", "subject": {"kind": "primitive", "name": "ArrivalSheet"}, "axes": {},
         "source": {"page": "index.html", "selector": ".sheet", "variant": "default", "state": "default"}},
    ] + [
        {"id": f"berth-card-{state}", "subject": {"kind": "component", "name": "BerthCard"}, "axes": {},
         "source": {"page": "index.html", "selector": ".berth-card", "variant": "default", "state": state}}
        for state in ("ready", "loading", "empty")
    ]
    states = [
        {"subject": {"kind": "primitive", "name": "Button"}, "state": "hover", "mode": "pseudo", "specimen": "button-primary"},
        {"subject": {"kind": "primitive", "name": "Button"}, "state": "focus-visible", "mode": "pseudo", "specimen": "button-secondary"},
        {"subject": {"kind": "primitive", "name": "Button"}, "state": "active", "mode": "pseudo", "specimen": "button-primary"},
        {"subject": {"kind": "primitive", "name": "Button"}, "state": "disabled", "mode": "rendered", "specimen": "button-disabled"},
        {"subject": {"kind": "primitive", "name": "TextField"}, "state": "hover", "mode": na,
         "reason": "Fields keep their border on hover; focus carries the affordance."},
        {"subject": {"kind": "primitive", "name": "TextField"}, "state": "focus-visible", "mode": "pseudo", "specimen": "field-default"},
        {"subject": {"kind": "primitive", "name": "TextField"}, "state": "active", "mode": na,
         "reason": "Text entry has no pressed appearance distinct from focus."},
        {"subject": {"kind": "primitive", "name": "TextField"}, "state": "disabled", "mode": "rendered", "specimen": "field-disabled"},
        {"subject": {"kind": "primitive", "name": "TextField"}, "state": "error", "mode": "rendered", "specimen": "field-error"},
    ] + [
        {"subject": {"kind": "component", "name": "BerthCard"}, "state": state, "mode": "rendered", "specimen": f"berth-card-{state}"}
        for state in ("ready", "loading", "empty")
    ] + [
        {"subject": {"kind": "primitive", "name": name}, "state": "default", "mode": "rendered", "specimen": specimen}
        for name, specimen in (("Button", "button-primary"), ("TextField", "field-default"))
    ]
    return {
        "schema": "design-system/4",
        "product": "Harbor Berth Desk (synthetic fixture)",
        "platform": "web",
        "stackSemantics": {"platform": "web", "renderingModel": "SPA", "componentFoundation": "Fixture components",
                           "stylingMechanism": "modern vanilla CSS"},
        "stylingMechanism": "plain CSS",
        "enforcement": "blocking",
        "sourceBindings": {key: {"path": path, "sha256": "0" * 64} for key, path in (
            ("prd", "docs/product/PRD.md"), ("architecture", "docs/product/architecture.md"),
            ("stack", "docs/product/stack-decisions.md"), ("uiDesign", "docs/design/ui-design.md"),
            ("hifi", "docs/design/ui-references/demo/index.html"))},
        "tokenSources": ["src/styles/tokens.css"],
        "primitiveSources": ["src/ui/primitives.css"],
        "viewports": [390, 768, 1200],
        "tokens": {
            "color": {"--harbor-ink": "#16324f", "--sea": "#2f6f8f", "--buoy": "#e0a526", "--mist": "#eef3f5",
                      "--alarm": "#b3261e", "--kelp": "#2e6b4f"},
            "fontSize": {"--text-body": "16px", "--text-heading": "28px"},
            "lineHeight": {"--leading-body": "1.5", "--leading-heading": "1.15"},
            "space": {"--space-1": "4px", "--space-2": "8px", "--space-3": "12px", "--space-4": "16px", "--space-6": "24px"},
            "radius": {"--radius-control": "6px", "--radius-card": "12px"},
            "shadow": {"--shadow-card": "0 1px 2px rgba(22,50,79,.18), 0 6px 18px rgba(22,50,79,.10)"},
            "duration": {"--duration-quick": "160ms", "--duration-sheet": "320ms"},
            "easing": {"--ease-out": "cubic-bezier(.2,0,0,1)"},
        },
        "primitives": primitives,
        "productComponents": {"BerthCard": {"dsId": "DS-COMP-001", "requiredContentOrder": ["berth", "vessel", "arrival"],
                                            "composes": ["StatusTag"], "states": ["ready", "loading", "empty"]}},
        "signatureRules": ["DS-001"],
        "motionVariants": ["sheet-rise", "tide-pulse"],
        "stateMatrix": ["ready", "loading", "empty", "error", "disabled", "reduced-motion", "mobile-reflow"],
        "showcase": {
            "schema": "ds-showcase/1",
            "specimens": specimens,
            "states": states,
            "motion": [
                {"variant": "sheet-rise", "specimen": "arrival-sheet",
                 "trigger": {"kind": "attribute", "name": "data-open", "from": "false", "to": "true"}},
                {"variant": "tide-pulse", "specimen": "tide-dot", "trigger": {"kind": "animation"}},
            ],
        },
    }


def render_demo() -> tuple[str, dict[str, str], dict]:
    import design_system_showcase
    from design_system_gallery import render_gallery

    pages = demo_pages()
    registry = demo_registry()
    manifest = json.loads(design_system_showcase.MANIFEST_RE.search(pages["index.html"]).group("data"))
    resolved, problems = design_system_showcase.resolve(registry, pages)
    if problems:
        raise ValueError("\n".join(problems))
    registry_bytes = (json.dumps(registry, indent=2, sort_keys=True) + "\n").encode("utf-8")
    binding = {"path": "docs/design/ui-references/demo/index.html",
               "sha256": hashlib.sha256(pages["index.html"].encode("utf-8")).hexdigest()}
    html = render_gallery(registry, registry_bytes, b"# Harbor Berth Desk design system (synthetic fixture)\n",
                          pages, manifest, resolved, binding)
    return html, pages, registry


def write_demo() -> None:
    html, pages, registry = render_demo()
    (DEMO_DIR / "hifi").mkdir(parents=True, exist_ok=True)
    for name, text in pages.items():
        (DEMO_DIR / "hifi" / name).write_bytes(text.encode("utf-8"))
    (DEMO_DIR / "design-system.json").write_bytes((json.dumps(registry, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    (DEMO_DIR / "design-system-preview.html").write_bytes(html.encode("utf-8"))


def screenshots() -> list[str]:
    """Capture the committed demo at desktop and phone widths for author review."""
    import shutil
    import subprocess
    import tempfile

    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "ui-design-builder/scripts/tests"))
    from test_reviewer_browser import playwright_module

    node = shutil.which("node")
    module = playwright_module(node) if node else None
    if not module:
        raise SystemExit("Node Playwright is unavailable")
    folder = Path(tempfile.mkdtemp(prefix="pdh-showcase-shots-"))
    script = """const [,, url, module, folder] = process.argv; const {chromium} = require(module);
(async () => { const browser = await chromium.launch();
  for (const [name, width] of [["desktop", 1280], ["phone", 390]]) {
    const page = await browser.newPage({viewport: {width, height: 900}}); await page.goto(url); await page.waitForTimeout(1200);
    for (const [part, y] of [["top", 0], ["components", "#components"], ["surfaces", "#surfaces"], ["motion", "#motion"], ["trace", "#traceability"]]) {
      if (typeof y === "string") await page.$eval(y, item => item.scrollIntoView()); await page.waitForTimeout(300);
      await page.screenshot({path: `${folder}/${name}-${part}.png`}); } }
  await browser.close(); })().catch(error => { console.error(error); process.exit(1); });"""
    subprocess.run([node, "-", (DEMO_DIR / "design-system-preview.html").resolve().as_uri(), module, str(folder)],
                   input=script, text=True, check=True, timeout=120)
    return sorted(str(path) for path in folder.iterdir())


if __name__ == "__main__":
    if sys.argv[1:] == ["--write"]:
        write_demo()
    elif sys.argv[1:] == ["--screenshots"]:
        print("\n".join(screenshots()))
    else:
        raise SystemExit("usage: showcase_fixture.py --write | --screenshots")
