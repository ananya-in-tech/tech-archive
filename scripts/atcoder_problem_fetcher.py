"""Build the AtCoder briefing card for a new AtCoder Arena discussion.

AtCoder has no official API, so this reads two sources:
  - atcoder.jp (official): task title, contest, time and memory limits, score and
    the English problem statement with samples, from the problem's own page.
  - AtCoder Problems (kenkoooo.com, community-run): the estimated difficulty.
    AtCoder itself does not publish one.

The discussion body may hold either:
  - a task URL, such as https://atcoder.jp/contests/abc300/tasks/abc300_a
  - Contest ID and Problem Index headings, the same way as the Codeforces Arena:
        # Contest ID
        abc300

        # Problem Index
        A

Reads the body from DISCUSSION_BODY and writes the card to comment_body.txt.
Prints a reason and writes nothing when the body cannot be matched to a problem.
"""
import math
import os
import re
import sys

import requests
from bs4 import BeautifulSoup, NavigableString

BASE = "https://atcoder.jp"
MODELS_URL = "https://kenkoooo.com/atcoder/resources/problem-models.json"
HEADERS = {
    "User-Agent": "tech-archive-discussion-bot (+https://github.com/ananya-in-tech/tech-archive)",
    "Accept-Language": "en",
}
TIMEOUT = 20
# GitHub rejects comments over 65,536 characters
MAX_STATEMENT = 55_000

CONTEST_PATTERN = re.compile(
    r"(?:### 🔢 Contest ID|# Contest ID|#contest id|# contest|#contest)\s*([A-Za-z0-9_-]+)", re.IGNORECASE)
INDEX_PATTERN = re.compile(
    r"(?:### 🔤 Problem Index|# Problem Index|#problem index|# problem|#problem)\s*([A-Za-z0-9]+)", re.IGNORECASE)
URL_PATTERN = re.compile(r"atcoder\.jp/contests/([A-Za-z0-9_-]+)/tasks/([A-Za-z0-9_-]+)", re.IGNORECASE)

# AtCoder's rating colours, used for the difficulty badge
COLOURS = [(400, "⚪", "Gray"), (800, "🟤", "Brown"), (1200, "🟢", "Green"), (1600, "🩵", "Cyan"),
           (2000, "🔵", "Blue"), (2400, "🟡", "Yellow"), (2800, "🟠", "Orange"), (math.inf, "🔴", "Red")]

# TeX that shows up inside sample formats, where math rendering does not apply
PLAIN_TEX = {r"\ldots": "...", r"\dots": "...", r"\cdots": "⋯", r"\vdots": "⋮", r"\ddots": "⋱",
             r"\times": "×", r"\le": "≤", r"\ge": "≥", r"\ne": "≠", r"\ ": " ", r"\quad": "  "}


def parse_body(body):
    """Return (contest_id, task_id or None, problem_index or None), or None if nothing matched."""
    url = URL_PATTERN.search(body)
    if url:
        return url.group(1), url.group(2), None
    contest, index = CONTEST_PATTERN.search(body), INDEX_PATTERN.search(body)
    if contest and index:
        return contest.group(1), None, index.group(1)
    return None


def get(session, url):
    response = session.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def find_task_id(session, contest_id, index):
    """Look the problem up on the contest's official task list."""
    soup = BeautifulSoup(get(session, f"{BASE}/contests/{contest_id}/tasks").text, "html.parser")
    for row in soup.select("table tbody tr"):
        link = row.find("a", href=re.compile(r"/tasks/"))
        if link and link.get_text(strip=True).lower() == index.lower():
            return link["href"].rsplit("/", 1)[-1]
    return None


def difficulty_badge(session, task_id):
    """Estimated difficulty from AtCoder Problems, clipped the same way that site shows it."""
    try:
        model = get(session, MODELS_URL).json().get(task_id) or {}
    except (requests.RequestException, ValueError):
        return "`Not available right now`"
    raw = model.get("difficulty")
    if raw is None:
        return "`Not rated yet`"
    shown = raw if raw >= 400 else round(400 / math.exp((400 - raw) / 400))
    emoji, name = next((e, n) for limit, e, n in COLOURS if shown < limit)
    note = ", experimental" if model.get("is_experimental") else ""
    return f"{emoji} **{shown}** ({name}{note})"


# ---------- statement: AtCoder HTML to GitHub Markdown ----------

def inline(node):
    """Inline HTML to Markdown, with <var> as GitHub math."""
    if isinstance(node, NavigableString):
        return re.sub(r"\s+", " ", str(node))
    tag = node.name
    if tag == "var":
        return f"${node.get_text().strip()}$"
    if tag == "br":
        return "<br>"
    inner = "".join(inline(child) for child in node.children)
    if tag in ("strong", "b"):
        return f"**{inner.strip()}**"
    if tag in ("em", "i"):
        return f"*{inner.strip()}*"
    if tag == "code":
        return f"`{node.get_text()}`"
    if tag == "a" and node.get("href"):
        href = node["href"]
        return f"[{inner.strip()}]({BASE + href if href.startswith('/') else href})"
    if tag == "img":
        return ""
    return inner


def plain_tex(text):
    for macro in sorted(PLAIN_TEX, key=len, reverse=True):
        text = re.sub(re.escape(macro) + r"(?![A-Za-z])", PLAIN_TEX[macro], text)
    return text


INLINE_TAGS = {"var", "strong", "b", "em", "i", "code", "a", "br", "span", "sup", "sub", "img", "small", "u", "s"}


def is_inline(node):
    return isinstance(node, NavigableString) or node.name in INLINE_TAGS


def block(node, out):
    """Block HTML to Markdown lines."""
    if isinstance(node, NavigableString):
        text = str(node).strip()
        if text:
            out.append(text)
        return
    tag = node.name
    if tag == "h3":
        out.append(f"#### {node.get_text(strip=True)}")
    elif tag == "p":
        text = "".join(inline(child) for child in node.children).strip()
        if text:
            out.append(text)
    elif tag in ("ul", "ol"):
        marker = "1." if tag == "ol" else "-"
        out.append("\n".join(f"{marker} {''.join(inline(c) for c in li.children).strip()}"
                             for li in node.find_all("li", recursive=False)))
    elif tag == "pre":
        out.append("```text\n" + plain_tex(node.get_text()).rstrip("\n") + "\n```")
    elif tag == "hr":
        return
    else:
        # text and math sitting straight inside a container form one paragraph
        run = []

        def flush():
            text = "".join(inline(n) for n in run).strip()
            if text:
                out.append(text)
            run.clear()

        for child in node.children:
            if is_inline(child) and not (getattr(child, "name", None) == "span" and child.find(["p", "div", "section", "pre", "ul", "ol", "h3"])):
                run.append(child)
            else:
                flush()
                block(child, out)
        flush()


def statement_markdown(statement):
    """Prefer the English statement; older problems only have Japanese."""
    english = statement.select_one("span.lang-en")
    root = english or statement.select_one("span.lang-ja") or statement
    out = []
    if not english:
        out.append("> This problem's statement is only available in Japanese on AtCoder.")
    block(root, out)
    return "\n\n".join(part for part in out if part.strip())


# ---------- card ----------

def build_card(session, contest_id, task_id):
    url = f"{BASE}/contests/{contest_id}/tasks/{task_id}"
    soup = BeautifulSoup(get(session, url).text, "html.parser")

    title_tag = soup.select_one("span.h2")
    title = title_tag.find(string=True, recursive=False).strip() if title_tag else task_id
    contest_tag = soup.select_one("a.contest-title")
    contest_name = contest_tag.get_text(strip=True) if contest_tag else contest_id
    limits = re.search(r"Time Limit:\s*([^/]+?)\s*/\s*Memory Limit:\s*([^\n<]+)", soup.get_text())
    limit_text = f"{limits.group(1).strip()} · {limits.group(2).strip()}" if limits else "`Not listed`"

    statement_tag = soup.select_one("#task-statement")
    statement = statement_markdown(statement_tag) if statement_tag else "Statement not found on the page."
    score = re.search(r"^Score\s*:\s*(.+)$", statement, re.MULTILINE)
    if score:
        statement = statement.replace(score.group(0), "", 1).strip()
    if len(statement) > MAX_STATEMENT:
        statement = statement[:MAX_STATEMENT].rsplit("\n\n", 1)[0] + f"\n\n*The statement is too long to show in full. [Read the rest on AtCoder]({url}).*"

    lines = [
        "## 🤖 AtCoder Automated Briefing",
        "",
        f"🎯 **Problem:** [{title}]({url})",
        f"🏆 **Contest:** [{contest_name}]({BASE}/contests/{contest_id})",
        f"📊 **Estimated Difficulty:** {difficulty_badge(session, task_id)}",
        f"⏱️ **Limits:** {limit_text}",
    ]
    if score:
        lines.append(f"💯 **Score:** {re.sub(r'[$]', '', score.group(1)).strip()}")
    lines += [
        "",
        "### 📄 Problem Statement",
        "<details>",
        "<summary><b>📖 Click to expand Full Description & Examples</b></summary>",
        "",
        statement,
        "",
        "</details>",
        "",
        "<sub>Difficulty is an estimate from [AtCoder Problems](https://kenkoooo.com/atcoder/), since AtCoder does not publish one.</sub>",
        "",
        "---",
        "*Use the discussion space below to share your approaches, talk about complexities, more optimized solutions, or link your solution files and much more together with the community!*",
        "*Happy Coding!*",
    ]
    return "\n".join(lines)


def main():
    parsed = parse_body(os.getenv("DISCUSSION_BODY", ""))
    if not parsed:
        print("ERROR: Could not find an AtCoder problem URL or Contest ID and Problem Index headings in the post.")
        return 0
    contest_id, task_id, index = parsed
    session = requests.Session()
    try:
        if not task_id:
            task_id = find_task_id(session, contest_id, index)
            if not task_id:
                print(f"ERROR: Contest {contest_id} has no problem with index {index}.")
                return 0
        print(f"Targeting AtCoder -> Contest: {contest_id}, Task: {task_id}")
        card = build_card(session, contest_id, task_id)
    except requests.HTTPError as error:
        print(f"ERROR: AtCoder returned {error.response.status_code} for {error.request.url}")
        return 0
    except requests.RequestException as error:
        print(f"ERROR: Could not reach AtCoder: {error}")
        return 0
    with open("comment_body.txt", "w", encoding="utf-8") as f:
        f.write(card)
    print("SUCCESS: AtCoder context card compiled successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
