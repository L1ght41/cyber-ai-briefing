# Daily publishing runbook

Signal & Shield publishes one briefing per day at https://l1ght41.github.io/cyber-ai-briefing/ via GitHub Pages (branch `main`, folder `/docs`).

## Steps

1. Get the repo: `git clone https://github.com/L1ght41/cyber-ai-briefing.git` (or `git pull` if it already exists).
2. Research the last 24-36 hours of news:
   - Cybersecurity, 4-6 items: actively exploited vulnerabilities (check CISA KEV alerts), major breaches, ransomware, threat-actor activity, cloud/DevSecOps/supply-chain security, and significant policy.
   - AI & Tech, 4-6 items: model releases, AI security and AI governance, agents, regulation and policy, and major industry moves.
   - Prefer primary and reputable sources: CISA, vendor advisories, BleepingComputer, The Hacker News, SecurityWeek, The Record, Reuters, AP, Ars Technica, The Verge, TechCrunch, official company blogs. Every fact must come from a source you actually read.
   - Skip anything already covered in the last 3 posts unless there is material new information.
3. Write `posts/YYYY-MM-DD.json` (today's date in America/Chicago) using the schema below. Copy the structure of an existing post.
4. Run `python3 build.py`. It must print `Built N post(s)`. Fix any `BUILD ERROR` and rebuild.
5. Commit and push:
   `git add -A && git commit -m "Briefing YYYY-MM-DD" -m "Co-authored-by: Perplexity <noreply@perplexity.ai>" && git push`
6. Confirm the live post at `https://l1ght41.github.io/cyber-ai-briefing/posts/YYYY-MM-DD.html` returns HTTP 200 (Pages can take 1-3 minutes).

## Post schema

```json
{
  "date": "YYYY-MM-DD",            // must match the filename
  "title": "Headline-style title naming the 2-3 biggest stories",
  "summary": "2-3 sentence overview of the day",
  "sections": [
    {"key": "cyber", "items": [ITEM, ...]},   // 2-7 items
    {"key": "ai",    "items": [ITEM, ...]}    // 2-7 items
  ],
  "takeaway": "2-3 sentences: the practical lesson for defenders and builders"
}
```

ITEM:

```json
{
  "headline": "Specific, factual headline",
  "body": "2-4 sentences: what happened, with key specifics (CVE, CVSS, versions, who, when)",
  "why": "1-2 sentences: why it matters and what to do",
  "sources": [{"name": "Publication", "url": "https://..."}]
}
```

## Style

- Plain, precise, practitioner tone. No hype, no exclamation points, no emojis.
- Attribute claims ("Mandiant says", "according to Reuters"). Don't speculate past the sources.
- Write the text yourself; never copy article paragraphs.
- Plain text only in fields (no HTML or Markdown). The build escapes everything.
