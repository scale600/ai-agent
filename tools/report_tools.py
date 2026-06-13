"""
Report generation tools — formats raw audit results into Markdown for display in Streamlit.
"""

from datetime import datetime, timezone


_SEVERITY_EMOJI = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}


def generate_audit_report(analysis_result: dict) -> str:
    """
    Convert analyze_permissions() output into a formatted Markdown report.

    Args:
        analysis_result: dict returned by analyze_permissions().

    Returns:
        Markdown string ready for st.markdown() rendering.
    """
    project_id = analysis_result.get("project_id", "unknown")
    violations = analysis_result.get("violations", [])
    summary = analysis_result.get("summary", "")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        f"# IAM Audit Report",
        f"**Project:** `{project_id}`  ",
        f"**Generated:** {timestamp}",
        "",
        "---",
        "",
        f"## Summary",
        f"> {summary}",
        "",
    ]

    if not violations:
        lines += ["## Violations", "", "No violations found. IAM policy looks clean."]
        return "\n".join(lines)

    # Group by severity
    for severity in ("CRITICAL", "HIGH", "MEDIUM"):
        group = [v for v in violations if v["severity"] == severity]
        if not group:
            continue

        emoji = _SEVERITY_EMOJI[severity]
        lines += [f"## {emoji} {severity} ({len(group)})", ""]
        lines += ["| Role | Member | Reason |", "|------|--------|--------|"]
        for v in group:
            lines.append(f"| `{v['role']}` | `{v['member']}` | {v['reason']} |")
        lines.append("")

    lines += [
        "---",
        "",
        "## Recommendations",
        "",
        "1. Replace `roles/owner` and `roles/editor` with granular predefined roles.",
        "2. Remove `allUsers` / `allAuthenticatedUsers` bindings immediately.",
        "3. Use Workload Identity for service accounts instead of primitive roles.",
        "4. Schedule regular IAM audits (recommend: weekly).",
    ]

    return "\n".join(lines)
