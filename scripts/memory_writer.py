#!/usr/bin/env python3
"""
Deterministic Memory-Writer for Google Ads Agent.

Parses the Memory-Update-JSON from a weekly report and updates the 4 memory files:
- 01_session_log.md (append session entry)
- 02_findings_log.md (new + resolved findings)
- 03_negatives.md (new hard negatives, deduplicated)
- 04_top_performers.md (new top performer candidates)

Usage:
    python scripts/memory_writer.py memory/reports/2026-W16-report.md
"""
import json
import pathlib
import re
import sys
from datetime import datetime


def extract_memory_json(report_path: pathlib.Path) -> dict:
    """Extract the first ```json ... ``` block from the report."""
    content = report_path.read_text(encoding="utf-8")
    match = re.search(r"```json\s*\n(.*?)\n```", content, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON block found in {report_path}")
    return json.loads(match.group(1))


def append_session_log(memory_dir: pathlib.Path, entry: dict) -> None:
    path = memory_dir / "01_session_log.md"
    text = path.read_text(encoding="utf-8")

    week = entry.get("iso_week", "?")
    year = entry.get("year", "?")
    block = [
        f"\n### Session: {year}-W{week:02d}",
        f"**Trigger:** {entry.get('trigger', '?')}",
        f"**Status:** {entry.get('status_color', '?')}",
        f"**Report:** `{entry.get('report_path', '?')}`",
        f"**Resolved Open Items:** {entry.get('resolved_oi_count', 0)}",
        f"**New Open Items:** {entry.get('new_oi_count', 0)}",
        "",
        "**Headlines:**",
    ]
    for h in entry.get("headlines", []):
        block.append(f"- {h}")
    block.append("")

    # Insert before the "Archiv"-section marker if present, else append
    new_section = "\n".join(block)
    if "## Archiv" in text:
        text = text.replace("## Archiv", new_section + "\n---\n\n## Archiv")
    else:
        text = text.rstrip() + "\n" + new_section + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"  session_log.md: appended entry for {year}-W{week:02d}")


def append_findings(memory_dir: pathlib.Path, new_findings: list, resolved: list) -> None:
    path = memory_dir / "02_findings_log.md"
    text = path.read_text(encoding="utf-8")

    today = datetime.now().strftime("%Y-%m-%d")
    blocks = []

    for f in new_findings:
        fid = f.get("id", "F-???")
        blocks.append(f"\n### {fid} — {f.get('hypothesis', f.get('type', 'Unnamed'))}")
        blocks.append(f"**Status:** {f.get('status', 'open')}")
        blocks.append(f"**Erstellt:** {today}")
        blocks.append(f"**Letzte Pruefung:** {today}")
        blocks.append(f"**Quelle:** {f.get('source', 'memory_writer_auto')}")
        blocks.append("")
        blocks.append("**Hypothese:**")
        blocks.append(f.get("hypothesis", "—"))
        blocks.append("")
        if "context" in f:
            blocks.append(f"**Kontext:** {f['context']}")
            blocks.append("")
        if "note" in f:
            blocks.append(f"**Notiz:** {f['note']}")
            blocks.append("")
        if "p_h1" in f:
            blocks.append(f"**P(H1):** {f['p_h1']}")
        if "n_required" in f:
            blocks.append(f"**Benoetigte Sample-Size:** {f['n_required']}")
        if "revisit" in f:
            blocks.append(f"**Revisit:** {f['revisit']}")
        if "action_required" in f:
            blocks.append(f"**Action Required:** {f['action_required']}")
        if "action" in f:
            blocks.append(f"**Action:** {f['action']}")
        blocks.append("")

    for r in resolved:
        rid = r.get("id", "OI-???")
        desc = r.get("description", r.get("old_status", "Resolved"))
        new_status = r.get("new_status", "resolved")
        blocks.append(f"\n### {rid} — UPDATE ({today})")
        blocks.append(f"**Neuer Status:** {new_status}")
        if "test" in r:
            blocks.append(f"**Test:** {r['test']}")
        if "p_h1" in r:
            blocks.append(f"**P(H1):** {r['p_h1']}")
        if "effect_size" in r:
            blocks.append(f"**Effect Size:** {r['effect_size']}")
        if "ci_95" in r:
            blocks.append(f"**95% KI:** {r['ci_95']}")
        if "action_recommended" in r:
            blocks.append(f"**Empfohlene Action:** {r['action_recommended']}")
        if "data" in r:
            blocks.append(f"**Daten:** `{json.dumps(r['data'])}`")
        blocks.append("")

    if not blocks:
        return

    new_section = "\n".join(blocks)
    if "## Abgeschlossen" in text:
        text = text.replace("## Abgeschlossen", new_section + "\n---\n\n## Abgeschlossen")
    else:
        text = text.rstrip() + "\n" + new_section + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"  findings_log.md: appended {len(new_findings)} new + {len(resolved)} resolved")


def append_negatives(memory_dir: pathlib.Path, new_negatives: list) -> None:
    path = memory_dir / "03_negatives.md"
    text = path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m")

    category_order = {
        "b2c": "B2C / Privatkunden",
        "jobs": "Jobs / Karriere",
        "informational": "DIY / Gratis / Informational",
        "diy_download": "DIY / Gratis / Informational",
        "diy": "DIY / Gratis / Informational",
        "competitor_brand": "Wettbewerber-Brand",
        "competitor": "Wettbewerber-Brand",
        "irrelevant": "Sonstige / Irrelevant",
        "irrelevant_trading": "Sonstige / Irrelevant",
        "irrelevant_settlement": "Sonstige / Irrelevant",
        "irrelevant_consulting": "Sonstige / Irrelevant",
        "irrelevant_foreign_program": "Sonstige / Irrelevant",
        "irrelevant_subsidy": "Sonstige / Irrelevant",
        "strategy_nogo_onsite": "Sonstige / Irrelevant (Onsite-PPA No-Go)",
    }

    added = 0
    skipped_dedup = 0
    appendix_rows = []
    for n in new_negatives:
        term = n.get("term", "").strip()
        if not term:
            continue
        # dedup check: is term already in file (case-insensitive)
        if re.search(r"\|\s*" + re.escape(term) + r"\s*\|", text, re.IGNORECASE):
            skipped_dedup += 1
            continue
        category_label = category_order.get(n.get("category", "").lower(), "Sonstige / Irrelevant")
        appendix_rows.append(f"| {term} | Phrase | {category_label} — {n.get('priority', 'high')} priority (auto-added {today}) |")
        added += 1

    if appendix_rows:
        section_header = f"\n---\n\n## Auto-Appended (Memory-Writer Session {today})\n\n| Term | Typ | Kategorie / Begruendung |\n|---|---|---|\n"
        text = text.rstrip() + section_header + "\n".join(appendix_rows) + "\n"
        path.write_text(text, encoding="utf-8")
    print(f"  negatives.md: added {added} new, skipped {skipped_dedup} duplicates")


def append_top_performers(memory_dir: pathlib.Path, new_performers: list) -> None:
    path = memory_dir / "04_top_performers.md"
    text = path.read_text(encoding="utf-8")
    today = datetime.now().strftime("%Y-%m-%d")

    if not new_performers:
        return

    blocks = ["\n---\n\n## Auto-Appended Candidates (Memory-Writer)"]
    for p in new_performers:
        status = p.get("status", "candidate")
        blocks.append(f"\n### {p.get('keyword', '?')} ({p.get('match_type', '?')}) — {status}")
        if "campaign" in p:
            blocks.append(f"- **Kampagne:** {p['campaign']}")
        if "cpa" in p:
            blocks.append(f"- **CPA:** {p['cpa']} EUR")
        if "conversions" in p:
            blocks.append(f"- **Conversions:** {p['conversions']}")
        if "note" in p:
            blocks.append(f"- **Notiz:** {p['note']}")
        blocks.append(f"- **First seen:** {p.get('date_first_seen', today)}")

    text = text.rstrip() + "\n" + "\n".join(blocks) + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"  top_performers.md: added {len(new_performers)} candidates")


def main():
    if len(sys.argv) < 2:
        print("Usage: memory_writer.py <path-to-report.md>", file=sys.stderr)
        sys.exit(1)

    report_path = pathlib.Path(sys.argv[1])
    if not report_path.exists():
        print(f"Report not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    memory_dir = report_path.parent.parent  # memory/reports/foo.md -> memory/
    print(f"Report: {report_path}")
    print(f"Memory dir: {memory_dir}")

    data = extract_memory_json(report_path)
    print(f"Extracted session entry: {data['session_entry'].get('iso_week', '?')}/W")

    append_session_log(memory_dir, data.get("session_entry", {}))
    append_findings(memory_dir, data.get("new_findings", []), data.get("resolved_findings", []))
    append_negatives(memory_dir, data.get("new_negatives", []))
    append_top_performers(memory_dir, data.get("new_top_performers", []))

    print("\nDone. Review changes with `git diff memory/`.")


if __name__ == "__main__":
    main()
