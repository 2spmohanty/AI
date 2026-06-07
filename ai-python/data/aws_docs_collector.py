import httpx
import xml.etree.ElementTree as ET
import json

def fetch_aws_blogs(limit=30) -> list[dict]:
    url = "https://aws.amazon.com/blogs/aws/feed/"
    resp = httpx.get(url, timeout=15, follow_redirects=True)
    root = ET.fromstring(resp.text)
    posts = []
    for item in root.findall(".//item")[:limit]:
        title   = item.findtext("title", "").strip()
        desc    = item.findtext("description", "").strip()
        link    = item.findtext("link", "").strip()
        # strip HTML tags from description
        import re
        desc = re.sub(r"<[^>]+>", "", desc)[:500]
        posts.append({"title": title, "content": f"{title}. {desc}", "url": link})
    return posts

posts = fetch_aws_blogs(30)

with open("aws/aws_blogs.json", "w") as f:
    json.dump(posts, f, indent=2)

print(f"Saved {len(posts)} posts to data/aws/aws_blogs.json")

