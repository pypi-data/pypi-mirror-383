import argparse, os, sys
from .render import render_storage_xml
from importlib.metadata import version, PackageNotFoundError
import warnings

def _ver():
    try:
        return version("cuke2confluence")
    except PackageNotFoundError:
        return "0"

def main():
    ap = argparse.ArgumentParser(prog="cuke2conf", description="Render Cucumber JSON to Confluence Storage Format (Jinja2).")
    ap.add_argument("--json", required=True, help="Pfad zur cucumber.json")
    ap.add_argument("--title", required=True, help="Seitentitel in Confluence")
    ap.add_argument("--out", default="page-storage.xml", help="Ausgabedatei (Storage XML)")
    ap.add_argument("--templates", help="Optional: eigenes Template-Verzeichnis verwenden")
    ap.add_argument("--publish", action="store_true", help="Per REST nach Confluence publizieren")
    ap.add_argument("--space", help="Space Key (für Publish)")
    ap.add_argument("--parent", help="Parent Page ID (für Publish)")
    ap.add_argument("--version", action="version", version=f"%(prog)s {_ver()}")
    args = ap.parse_args()

    xml, atts = render_storage_xml(args.title, args.json, args.templates)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[cuke2conf] Storage XML geschrieben: {args.out} (Attachments: {len(atts)})")

    if args.publish:
        try:
            import requests
        except Exception:
            print("[cuke2conf] Für --publish benötigst du das Extra 'publish' (pip install cuke2confluence[publish])", file=sys.stderr)
            sys.exit(2)
        base = os.getenv("CONFLUENCE_BASE_URL")
        token = os.getenv("CONFLUENCE_TOKEN")
        headers={"X-Atlassian-Token": "no-check", "Authorization": f"Bearer {token}"}
        verify_ssl = True
        if os.environ.get("CUKE2CONF_INSECURE", "").lower() in ("1", "true", "yes"):
            verify_ssl = False
        if not all([base, token, args.space]):
            print("[cuke2conf] Fehlende ENV/Parameter: CONFLUENCE_BASE_URL, CONFLUENCE_TOKEN, --space", file=sys.stderr)
            sys.exit(2)

        if not verify_ssl:
            warnings.warn(
                "⚠️ SSL certificate verification disabled via CUKE2CONF_INSECURE. "
                "This should only be used in test environments!",
                UserWarning
            )

        import requests
        # Seite suchen
        r = requests.get(f"{base}/rest/api/content",
                         params={"title": args.title, "spaceKey": args.space, "expand":"version"},
                         headers=headers,
                         verify=verify_ssl)
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            page = results[0]
            page_id = page["id"]
            next_version = page["version"]["number"] + 1
            payload = {
                "id": page_id, "type": "page", "title": args.title,
                "space": {"key": args.space},
                "version": {"number": next_version},
                "body": {"storage": {"value": xml, "representation": "storage"}}
            }
            resp = requests.put(f"{base}/rest/api/content/{page_id}", json=payload, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            print(f"[cuke2conf] Seite aktualisiert: {page_id}")
        else:
            payload = {
                "type": "page", "title": args.title,
                "ancestors": [{"id": str(args.parent)}] if args.parent else [],
                "space": {"key": args.space},
                "body": {"storage": {"value": xml, "representation": "storage"}}
            }
            resp = requests.post(f"{base}/rest/api/content", json=payload, headers=headers, verify=verify_ssl)
            resp.raise_for_status()
            page_id = resp.json()["id"]
            created = True
            print(f"[cuke2conf] Seite erstellt: {page_id}")
        # Attachments:
        uploaded = 0
        for a in atts:
            files_for_upload = {}
            if a["bytes"] is not None:
                files_for_upload = {"file": (a["fname"], a["bytes"], a["mime"])}
            elif a["text"] is not None:
                files_for_upload = {"file": (a["fname"], a["text"].encode("utf-8"), a["mime"])}
            else:
                continue  # nichts zu tun

            # Upload
            up = requests.post(
                f"{base}/rest/api/content/{page_id}/child/attachment",
                headers=headers,
                files=files_for_upload,
                verify=verify_ssl,
            )
            # Falls gleicher Name existiert, 409 -> dann 'update attachment' Endpoint
            if up.status_code == 409:
                # Attachment ID holen
                lst = requests.get(f"{base}/rest/api/content/{page_id}/child/attachment",
                                   params={"filename": a["fname"]},
                                   headers=headers, verify=verify_ssl)
                if lst.ok and lst.json().get("results"):
                    att_id = lst.json()["results"][0]["id"]
                    up = requests.post(
                        f"{base}/rest/api/content/{att_id}/data",
                        headers=headers,
                        files=files_for_upload,
                        verify=verify_ssl
                    )
            up.raise_for_status()
            uploaded += 1

        print(f"[cuke2conf] Attachments hochgeladen: {uploaded}/{len(atts)}")
