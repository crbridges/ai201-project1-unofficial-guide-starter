"""
clean_documents.py — preprocess raw Reddit copy-paste into clean, chunkable text.

For each documents/postN.txt (raw Reddit thread pasted as-is) this script:
  1. Backs up the raw file to documents/raw/postN.txt (once).
  2. Strips Reddit scaffolding noise (Upvote/Downvote/Award/Share, vote counts,
     usernames, avatars, "Xy ago" timestamps, promoted ads, video-player junk).
  3. Splits the thread into the original post + each reply.
  4. Writes a cleaned file with the thread URL on line 1 and each post
     separated by a "===" delimiter, ready for load_documents().

Re-run any time you add or update a raw post. URLs map 1:1 with the
Documents table in planning.md (post1 -> source 1, etc.).
"""

import re
import shutil
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"
RAW_DIR = DOCS_DIR / "raw"
DELIM = "==="

# post file -> source thread URL (matches the Documents table in planning.md)
URLS = {
    "post1.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/1tbdq3m/what_electives_do_you_reccomend/",
    "post2.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/135yej9/best_electives/",
    "post3.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/scythe/easy_electives_to_finish_off_the_program/",
    "post4.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/1362sm5/need_one_more_elective_to_take_in_the_summer_term/",
    "post5.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/1hi5c5x/what_are_some_interesting_and_fun_electives_you/",
    "post6.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/muc6r7/feedback_on_electives/",
    "post7.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/1hxg5h8/elective_recommendations/",
    "post8.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/jro3a1/what_are_the_bestmost_fullfilling_electives_that/",
    "post9.txt":  "https://www.reddit.com/r/OSUOnlineCS/comments/1n5u40a/recommended_electives/",
    "post10.txt": "https://www.reddit.com/r/OSUOnlineCS/comments/18nu07r/what_electives_were_most_useful_in_your_job_search/",
}

# A line that is purely a timestamp / edited marker (text always follows this).
TIME_RE = re.compile(
    r"^\s*(edited\s+)?(\d+\s*\w+\.?\s+ago|just now|yesterday)\s*$",
    re.IGNORECASE,
)

# Lines that are always noise, dropped wherever they appear.
NOISE_EXACT = {
    "upvote", "downvote", "award", "share", "reply", "report", "save",
    "follow", "go to comments", "sort by:", "best", "top", "new",
    "controversial", "old", "q&a", "search comments", "expand comment search",
    "comments section", "promoted", "collapse video player", "shop now",
    "learn more", "more replies", "read more", "read less", "•",
}
NOISE_RE = [
    re.compile(r"^\d+$"),                          # bare vote counts
    re.compile(r"^u/.*\bavatar$", re.IGNORECASE),  # "u/name avatar"
    re.compile(r"^\d+\s*:\s*\d+\s*/\s*\d+\s*:\s*\d+$"),  # 0:00 / 0:00
    re.compile(r"^\d+\s+more repl(y|ies)$", re.IGNORECASE),
    re.compile(r"^clickable image", re.IGNORECASE),
    re.compile(r"^continue this thread", re.IGNORECASE),
    re.compile(r"^view all \d+ replies", re.IGNORECASE),
    re.compile(r"^[a-z0-9.-]+\.(com|org|net|ai|io|edu)$", re.IGNORECASE),  # bare ad domains
]


def is_noise(line):
    s = line.strip()
    if not s:
        return True
    if s.lower() in NOISE_EXACT:
        return True
    return any(rx.match(s) for rx in NOISE_RE)


def extract_op(lines):
    """Original post = title + body, up to the first scaffolding marker."""
    body = []
    for ln in lines:
        s = ln.strip()
        if (s == "Archived post. New comments cannot be posted and votes cannot be cast."
                or s.lower() in ("upvote", "sort by:", "comments section")):
            break
        body.append(ln)
    return clean_block(body)


def clean_block(lines):
    """Collapse a list of raw text lines into a tidy paragraph block."""
    kept = [ln.rstrip() for ln in lines if not is_noise(ln)]
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()  # collapse blank runs
    return text


def comment_text(buffer):
    """Given a comment's [metadata + text] lines, return just the text.

    Text always begins after the last timestamp/edited marker. If a buffer has
    no timestamp it isn't a real comment (e.g. a promoted ad block) -> skip.
    """
    last_marker = -1
    for i, ln in enumerate(buffer):
        if TIME_RE.match(ln):
            last_marker = i
    if last_marker == -1:
        return None  # not a comment (ad / junk)
    return clean_block(buffer[last_marker + 1:])


def extract_comments(lines):
    """Parse the comments region into individual reply texts."""
    # Comments start after the "Comments Section" marker (fall back gracefully).
    start = 0
    for i, ln in enumerate(lines):
        if ln.strip().lower() == "comments section":
            start = i + 1
            break
    else:
        for i, ln in enumerate(lines):
            if ln.strip().lower() == "best":
                start = i + 1
                break

    comments = []
    buffer = []
    for ln in lines[start:]:
        if ln.strip().lower() == "upvote":   # footer -> end of a comment
            txt = comment_text(buffer)
            if txt:
                comments.append(txt)
            buffer = []
        else:
            buffer.append(ln)
    # trailing buffer (last comment may have no Upvote footer paste)
    txt = comment_text(buffer)
    if txt:
        comments.append(txt)
    return comments


def process(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()

    op = extract_op(lines)
    comments = extract_comments(lines)

    blocks = ([op] if op else []) + comments
    url = URLS.get(path.name, "UNKNOWN")
    out = f"URL: {url}\n" + f"\n{DELIM}\n".join(blocks) + "\n"
    return out, len(blocks)


def main():
    RAW_DIR.mkdir(exist_ok=True)
    total = 0
    for name in sorted(URLS, key=lambda n: int(re.search(r"\d+", n).group())):
        path = DOCS_DIR / name
        if not path.exists():
            print(f"  skip {name} (missing)")
            continue
        backup = RAW_DIR / name
        if not backup.exists():
            shutil.copy2(path, backup)  # preserve raw once
        cleaned, n = process(backup)    # always clean from the raw backup
        path.write_text(cleaned, encoding="utf-8")
        total += n
        print(f"  {name}: {n} posts")
    print(f"\nDone. {total} posts across {len(URLS)} threads. Raw preserved in documents/raw/")


if __name__ == "__main__":
    main()
