#!/usr/bin/env python3
"""
Fetch MIT TR China articles and generate two markdown books.
"""

import json
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

BASE_LIST = "https://apii.web.mittrchina.com/information/index"
BASE_DETAIL = "https://apii.web.mittrchina.com/information/details"

MAY1_2026 = 1777593600


def fetch_list(page, limit=100):
    url = f"{BASE_LIST}?page={page}&limit={limit}&author=&type=&label=&is_ad=true"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", {}).get("items", [])
    except Exception as e:
        print(f"  List page {page} error: {e}")
        return []


def fetch_detail(article_id):
    url = f"{BASE_DETAIL}?id={article_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("data", {})
    except Exception as e:
        print(f"  Detail id={article_id} error: {e}")
        return {}


def ts_to_str(ts):
    if not ts:
        return ""
    try:
        dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def clean_html(text):
    """Basic HTML tag removal for readable markdown."""
    if not text:
        return ""
    import re
    # Remove script/style
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
    # Convert common tags
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<p[^>]*>", "", text, flags=re.I)
    text = re.sub(r"</div>", "\n", text, flags=re.I)
    text = re.sub(r"<div[^>]*>", "", text, flags=re.I)
    text = re.sub(r"<li[^>]*>", "- ", text, flags=re.I)
    text = re.sub(r"</li>", "\n", text, flags=re.I)
    text = re.sub(r"<h[1-6][^>]*>", "\n## ", text, flags=re.I)
    text = re.sub(r"</h[1-6]>", "\n", text, flags=re.I)
    text = re.sub(r"<strong[^>]*>", "**", text, flags=re.I)
    text = re.sub(r"</strong>", "**", text, flags=re.I)
    text = re.sub(r"<b[^>]*>", "**", text, flags=re.I)
    text = re.sub(r"</b>", "**", text, flags=re.I)
    text = re.sub(r"<em[^>]*>", "*", text, flags=re.I)
    text = re.sub(r"</em>", "*", text, flags=re.I)
    text = re.sub(r"<i[^>]*>", "*", text, flags=re.I)
    text = re.sub(r"</i>", "*", text, flags=re.I)
    text = re.sub(r"<a[^>]*href=\"([^\"]*)\"[^>]*>(.*?)</a>", r"[\2](\1)", text, flags=re.S | re.I)
    text = re.sub(r"<img[^>]*src=\"([^\"]*)\"[^>]*>", r"\n![image](\1)\n", text, flags=re.I)
    # Remove remaining tags
    text = re.sub(r"<[^>]+>", "", text)
    # Clean up whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def main():
    print("=== Step 1: Fetching all article list pages ===")
    all_articles = []
    for page in range(1, 125):
        items = fetch_list(page)
        if not items:
            print(f"  Page {page}: no items, stopping")
            break
        all_articles.extend(items)
        print(f"  Page {page}: fetched {len(items)} items, total={len(all_articles)}")
        time.sleep(0.15)

    print(f"\nTotal articles fetched: {len(all_articles)}")

    # Sort by pv descending
    all_articles.sort(key=lambda x: x.get("pv", 0) or 0, reverse=True)
    top100 = all_articles[:100]

    # Filter for author "加洋" after May 1, 2026
    jy_articles = []
    for a in all_articles:
        authors = a.get("authors", [])
        author_names = [auth.get("username", "") for auth in authors]
        start_time = a.get("start_time", 0) or 0
        if "加洋" in author_names and int(start_time) >= MAY1_2026:
            jy_articles.append(a)

    print(f"Top 100 by pv: {len(top100)} articles")
    print(f"Author '加洋' after 2026-05-01: {len(jy_articles)} articles")

    # Fetch details for top 100
    print("\n=== Step 2: Fetching details for top 100 ===")
    top100_details = []
    for i, article in enumerate(top100):
        detail = fetch_detail(article["id"])
        if detail:
            top100_details.append(detail)
            print(f"  [{i+1}/100] id={article['id']} ok")
        else:
            print(f"  [{i+1}/100] id={article['id']} FAILED")
        time.sleep(0.15)

    # Fetch details for 加洋 articles
    print("\n=== Step 3: Fetching details for 加洋 articles ===")
    jy_details = []
    for i, article in enumerate(jy_articles):
        detail = fetch_detail(article["id"])
        if detail:
            jy_details.append(detail)
            print(f"  [{i+1}/{len(jy_articles)}] id={article['id']} ok")
        else:
            print(f"  [{i+1}/{len(jy_articles)}] id={article['id']} FAILED")
        time.sleep(0.15)

    # Generate document 1: Top 100
    print("\n=== Step 4: Generating MIT TR top100.md ===")
    with open("MIT_TR_top100.md", "w", encoding="utf-8") as f:
        f.write("# 《MIT Technology Review 中国》阅读量 TOP100 文章合集\n\n")
        f.write("> 数据来源：apii.web.mittrchina.com  \n")
        f.write("> 整理时间：{}  \n".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))
        f.write("> 排序依据：阅读量（pv）降序  \n\n")
        f.write("---\n\n")

        # Table of contents
        f.write("## 目录\n\n")
        f.write("| 排名 | 标题 | 作者 | 发布时间 | 阅读量 |\n")
        f.write("|------|------|------|----------|--------|\n")
        for i, d in enumerate(top100_details):
            authors = ", ".join([a.get("username", "") for a in d.get("authors", [])])
            ts = ts_to_str(d.get("start_time"))
            pv = d.get("look_num", d.get("pv", "N/A"))
            title = d.get("name", "无标题")
            f.write(f"| {i+1} | [{title}](#article-{d['id']}) | {authors} | {ts} | {pv} |\n")
        f.write("\n---\n\n")

        # Full articles
        for i, d in enumerate(top100_details):
            authors = ", ".join([a.get("username", "") for a in d.get("authors", [])])
            ts = ts_to_str(d.get("start_time"))
            pv = d.get("look_num", d.get("pv", "N/A"))
            title = d.get("name", "无标题")

            f.write(f"## <a id=\"article-{d['id']}\"></a>第 {i+1} 篇：{title}\n\n")
            f.write(f"**作者**：{authors}  \n")
            f.write(f"**发布时间**：{ts}  \n")
            f.write(f"**阅读量**：{pv}  \n")
            f.write(f"**原文链接**：{d.get('article_url', '')}  \n\n")

            content = d.get("content_str", "") or ""
            if content:
                f.write(content)
            else:
                html_content = d.get("content", "") or ""
                f.write(clean_html(html_content))
            f.write("\n\n---\n\n")

    # Generate document 2: 加洋 articles
    print("=== Step 5: Generating MIT TR jy.md ===")
    with open("MIT_TR_jy.md", "w", encoding="utf-8") as f:
        f.write("# 《MIT Technology Review 中国》加洋 文章合集（2026年5月1日后）\n\n")
        f.write("> 数据来源：apii.web.mittrchina.com  \n")
        f.write("> 整理时间：{}  \n".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")))
        f.write("> 筛选条件：作者=加洋，发布时间>=2026-05-01  \n\n")
        f.write("---\n\n")

        f.write("## 目录\n\n")
        f.write("| 序号 | 标题 | 发布时间 | 阅读量 |\n")
        f.write("|------|------|----------|--------|\n")
        for i, d in enumerate(jy_details):
            ts = ts_to_str(d.get("start_time"))
            pv = d.get("look_num", d.get("pv", "N/A"))
            title = d.get("name", "无标题")
            f.write(f"| {i+1} | [{title}](#article-{d['id']}) | {ts} | {pv} |\n")
        f.write("\n---\n\n")

        for i, d in enumerate(jy_details):
            authors = ", ".join([a.get("username", "") for a in d.get("authors", [])])
            ts = ts_to_str(d.get("start_time"))
            pv = d.get("look_num", d.get("pv", "N/A"))
            title = d.get("name", "无标题")

            f.write(f"## <a id=\"article-{d['id']}\"></a>第 {i+1} 篇：{title}\n\n")
            f.write(f"**作者**：{authors}  \n")
            f.write(f"**发布时间**：{ts}  \n")
            f.write(f"**阅读量**：{pv}  \n")
            f.write(f"**原文链接**：{d.get('article_url', '')}  \n\n")

            content = d.get("content_str", "") or ""
            if content:
                f.write(content)
            else:
                html_content = d.get("content", "") or ""
                f.write(clean_html(html_content))
            f.write("\n\n---\n\n")

    print("\n=== Done ===")
    print(f"MIT_TR_top100.md: {len(top100_details)} articles")
    print(f"MIT_TR_jy.md: {len(jy_details)} articles")


if __name__ == "__main__":
    main()
