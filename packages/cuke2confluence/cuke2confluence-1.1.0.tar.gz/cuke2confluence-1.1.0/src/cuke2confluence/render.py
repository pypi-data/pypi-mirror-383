from datetime import datetime, timezone
import json
import xml.sax.saxutils as sax
import base64
import mimetypes
import re
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from importlib.resources import files

def ms(duration_seconds):
    if duration_seconds is None:
        return "-"
    s = float(duration_seconds)
    if s < 1.0:
        return f"{int(s*1000)} ms"
    if s < 60.0:
        return f"{s:.3f} s"
    m, r = divmod(s, 60.0)
    return f"{int(m)} min {r:.1f} s"

def normalize_duration_to_seconds(v):
    if v is None: return 0.0
    try: x = float(v)
    except Exception: return 0.0
    return x / 1e9 if x > 1e6 else x

def status_macro(ok: bool):
    color = "Green" if ok else "Red"
    title = "passed" if ok else "failed"
    return (f'<ac:structured-macro ac:name="status">'
            f'<ac:parameter ac:name="colour">{color}</ac:parameter>'
            f'<ac:parameter ac:name="title">{title}</ac:parameter>'
            f'</ac:structured-macro>')

def code_block(text, language="text"):
    text = "" if text is None else str(text)
    if len(text) > 20000:
        text = text[:20000] + "\n...[truncated]..."
    return (f'<ac:structured-macro ac:name="code">'
            f'<ac:parameter ac:name="language">{language}</ac:parameter>'
            f'<ac:plain-text-body><![CDATA[{text}]]></ac:plain-text-body>'
            f'</ac:structured-macro>')

def expand_macro(title, inner_html):
    return (f'<ac:structured-macro ac:name="expand">'
            f'<ac:parameter ac:name="title">{sax.escape(title)}</ac:parameter>'
            f'<ac:rich-text-body>{inner_html}</ac:rich-text-body>'
            f'</ac:structured-macro>')

def _safe_slug(s: str) -> str:
    s = re.sub(r"\s+", "_", s.strip())
    s = re.sub(r"[^A-Za-z0-9._-]+", "", s)
    return s or "att"

def _ext_for_mime(mime: str) -> str:
    # fallback auf mimetypes, ansonsten konservativ .bin
    if not mime:
        return ".bin"
    guess = mimetypes.guess_extension(mime)
    if guess:
        return guess
    return {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/gif": ".gif",
        "text/plain": ".txt",
        "application/json": ".json",
        "application/pdf": ".pdf",
    }.get(mime, ".bin")

def _collect_attachments(step_json, feat_name, scen_name):
    """
    Unterstützt:
      - 'embeddings': [{data, mime_type, name?}]
      - 'attachments': [{body|data, mediaType|mime_type, fileName|name?}]
    """
    out = []
    # --- FIX: beide Listen zusammenführen ---
    raw_list = []
    emb = step_json.get("embeddings") or []
    att = step_json.get("attachments") or []
    if isinstance(emb, list):
        raw_list.extend(emb)
    if isinstance(att, list):
        raw_list.extend(att)

    idx = 0
    for att in raw_list:
        mime = att.get("mime_type") or att.get("mediaType") or att.get("contentType")
        title = att.get("fileName") or att.get("name") or ""

        body = (
            att.get("data") if att.get("data") is not None
            else att.get("body") if att.get("body") is not None
            else None
        )

        # --- Dateiname bestimmen (keine doppelte Endung) ---
        base_slug = _safe_slug(f"{feat_name}__{scen_name}__{idx}")
        if title:
            # wenn title schon eine Endung hat: direkt verwenden (nur säubern)
            safe_title = _safe_slug(title)
            fname = f"{base_slug}_{safe_title}"
            # falls nach dem Säubern keine Endung blieb, aus MIME ergänzen
            if "." not in safe_title.rsplit("/", 1)[-1]:
                fname += _ext_for_mime(mime)
        else:
            fname = base_slug + _ext_for_mime(mime)

        # --- Daten erkennen: base64 → bytes, sonst Text ---
        bdata = None
        tdata = None
        if isinstance(body, str):
            try:
                bdata = base64.b64decode(body, validate=True)
                if mime and mime.startswith("text/"):
                    # Text lieber als Text
                    tdata = bdata.decode("utf-8", errors="replace")
                    bdata = None
            except Exception:
                # kein Base64 → als Text behandeln
                tdata = body
        elif isinstance(body, (bytes, bytearray)):
            bdata = bytes(body)

        is_image = bool(mime and mime.startswith("image/"))
        out.append({
            "fname": fname,
            "mime": mime or "application/octet-stream",
            "is_image": is_image,
            "bytes": bdata,
            "text": tdata,
            "title": title or fname,
        })
        idx += 1
    return out

def parse_cucumber_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    features = []
    all_attachments = []
    totals = dict(features=0, scenarios=0, passed=0, failed=0, skipped=0, duration=0.0, steps=0)

    for feat in data:
        fname = feat.get("name") or "Unnamed Feature"
        ftags = [t.get("name","") for t in (feat.get("tags") or [])]
        elements = feat.get("elements") or []
        f_stats = dict(passed=0, failed=0, skipped=0, duration=0.0, scenarios=[])

        for el in elements:
            if el.get("type") not in ("scenario", "scenario_outline"):
                continue

            sname = el.get("name") or "Unnamed Scenario"
            stags = [t.get("name","") for t in (el.get("tags") or [])]
            steps = el.get("steps") or []
            s_dur = 0.0
            s_failed = False
            s_skipped = False
            step_models = []

            # Normale Steps
            for st in steps:
                atts = _collect_attachments(st, fname, sname)
                stext = (st.get("keyword","") or "") + (st.get("name") or "")
                res = st.get("result") or {}
                status = (res.get("status") or "unknown").lower()
                dur = normalize_duration_to_seconds(res.get("duration"))
                err = res.get("error_message")
                s_dur += dur
                totals["steps"] += 1
                if status == "failed": s_failed = True
                if status in ("skipped", "pending"): s_skipped = True
                step_models.append({
                    "status": status,
                    "text": stext,
                    "duration": dur,
                    "error": err,
                    "attachments": atts,
                })
                for a in atts:
                    all_attachments.append(a)

            # <<< NEW: Hooks (before/after) als pseudo-step einsammeln
            for hook_key, hook_label in (("before", "Before hook"), ("after", "After hook")):
                for hk in (el.get(hook_key) or []):
                    atts = _collect_attachments(hk, fname, sname)
                    # Optional: Hook-Ausgaben ins Step-Text hängen
                    outputs = hk.get("output") or []
                    text_extra = "\n".join(outputs) if outputs else ""
                    res = hk.get("result") or {}
                    status = (res.get("status") or "passed").lower()
                    dur = normalize_duration_to_seconds(res.get("duration"))
                    s_dur += dur
                    totals["steps"] += 1
                    if status == "failed": s_failed = True
                    if status in ("skipped", "pending"): s_skipped = True
                    step_models.append({
                        "status": status,
                        "text": f"{hook_label}" + (f"\n{text_extra}" if text_extra else ""),
                        "duration": dur,
                        "error": None,
                        "attachments": atts,
                    })
                    for a in atts:
                        all_attachments.append(a)

            # Szenario-Status
            scen_status = "passed" if (not s_failed and not s_skipped) else ("failed" if s_failed else "skipped")
            if scen_status == "passed": f_stats["passed"] += 1
            elif scen_status == "failed": f_stats["failed"] += 1
            else: f_stats["skipped"] += 1
            f_stats["duration"] += s_dur
            f_stats["scenarios"].append({
                "name": sname, "tags": stags, "status": scen_status,
                "duration": s_dur, "steps": step_models
            })

        totals["features"] += 1
        totals["scenarios"] += f_stats["passed"] + f_stats["failed"] + f_stats["skipped"]
        totals["duration"] += f_stats["duration"]
        features.append({"name": fname, "tags": ftags, **f_stats})

    for f in features:
        totals["passed"] += f["passed"]
        totals["failed"] += f["failed"]
        totals["skipped"] += f["skipped"]

    return features, totals, all_attachments

def build_env(templates_dir: str | None = None):
    if templates_dir:
        loader = FileSystemLoader(templates_dir)
    else:
        # Templates aus dem installierten Package laden
        pkg_templates = files("cuke2confluence").joinpath("templates")
        loader = FileSystemLoader(str(pkg_templates))
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(enabled_extensions=('xml',), default=False),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Filter & Globals
    env.filters["ms"] = ms
    env.filters["x"] = lambda s: sax.escape("" if s is None else str(s))
    env.globals["status_macro"] = status_macro
    env.globals["code_block"] = code_block
    env.globals["expand"] = expand_macro
    return env

def render_storage_xml(title: str, json_path: str, templates_dir: str | None = None):
    features, totals, all_attachments = parse_cucumber_json(json_path)
    env = build_env(templates_dir)
    tpl = env.get_template("page.xml.j2")
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    xml = tpl.render(title=title, generated_at=generated_at, features=features, totals=totals)
    return xml, all_attachments
