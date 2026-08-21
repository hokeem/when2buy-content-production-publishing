#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "data" / "state.json"
OUTPUT = ROOT / "reports" / "latest.md"

def esc(value):
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")

def render(state):
    snapshots = {}
    for item in state["metricSnapshots"]:
        previous = snapshots.get(item.get("postId"))
        if previous is None or item.get("observedAt", "") > previous.get("observedAt", ""):
            snapshots[item.get("postId")] = item
    posts = sorted(state["posts"], key=lambda post: snapshots.get(post["id"], {}).get("views", 0), reverse=True)
    lines = [
        "# when2buy Agent 运行报告",
        "",
        f"- 状态更新：`{esc(state['updatedAt'])}`",
        f"- X 账号：`@{esc(state['account']['handle'])}`",
        f"- 对标帖子快照：**{len(state['benchmarkPosts'])}**",
        f"- 待选选题：**{len(state['radar'])}**",
        f"- 待发布制作包：**{sum(1 for item in state['packages'] if item.get('status') == 'ready')}**",
        f"- 已验证发布：**{sum(1 for item in state['posts'] if item.get('status') == 'published')}**",
        "",
        "## 对标账号扫描",
        "",
    ]
    if state["benchmarkPosts"]:
        lines += ["| 账号 | 时间 | 内容 | URL |", "|---|---|---|---|"]
        for item in state["benchmarkPosts"][-30:][::-1]:
            lines.append(f"| @{esc(item.get('account'))} | {esc(item.get('postedAt'))} | {esc(item.get('text'))} | [X]({esc(item.get('url'))}) |")
    else:
        lines.append("尚无对标帖子快照；下一次运行必须先扫描 `@WhaleInsider` 和 `@StockMKTNewz`。")
    lines += ["", "## 选题推荐", ""]
    if state["radar"]:
        lines += ["| 排名 | 选题 | 信号源 | 分数 | 为什么是现在 |", "|---:|---|---|---:|---|"]
        for item in sorted(state["radar"], key=lambda value: value.get("rank", 999)):
            lines.append(f"| {esc(item.get('rank'))} | {esc(item.get('title'))} | {esc(item.get('sourceAccount'))} | {esc(item.get('score'))} | {esc(item.get('whyNow'))} |")
    else:
        lines.append("尚无选题；等待下一次 `radar` 运行。")
    lines += ["", "## 制作队列", ""]
    if state["packages"]:
        for item in state["packages"]:
            lines += [f"### {esc(item.get('title'))}", "", f"- 状态：`{esc(item.get('status'))}`", f"- 配图：`{esc(item.get('imagePath'))}`", "", esc(item.get("postText")), ""]
    else:
        lines.append("尚无制作包。")
    lines += ["", "## 已发内容（按最新浏览量排序）", "", "| 选题 | 发布时间 | 浏览 | 喜欢 | 回复 | 转发 | URL |", "|---|---|---:|---:|---:|---:|---|"]
    for post in posts:
        metric = snapshots.get(post["id"], {})
        lines.append(f"| {esc(post.get('title'))} | {esc(post.get('publishedAt'))} | {esc(metric.get('views', '待抓取'))} | {esc(metric.get('likes', '—'))} | {esc(metric.get('replies', '—'))} | {esc(metric.get('reposts', '—'))} | [X]({esc(post.get('url'))}) |")
    lines += ["", "## 最近运行", ""]
    if state["runs"]:
        for run in state["runs"][-20:][::-1]:
            lines.append(f"- `{esc(run.get('startedAt'))}` **{esc(run.get('mode'))} / {esc(run.get('status'))}** — {esc(run.get('summary'))} {esc(run.get('reason'))}".rstrip())
    else:
        lines.append("尚无 Agent 运行记录。")
    return "\n".join(lines) + "\n"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(json.loads(STATE.read_text(encoding="utf-8")))
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != expected:
            raise SystemExit("reports/latest.md is stale; run python3 scripts/render_report.py")
        print("Report is current.")
        return
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    main()
