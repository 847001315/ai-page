import os
import json
import subprocess
from typing import List, Dict

import requests
from bs4 import BeautifulSoup
from google import genai

# 仅在本地运行时使用代理；GitHub Actions 在海外无需代理
if os.getenv("GITHUB_ACTIONS") != "true":
  os.environ["http_proxy"] = "http://127.0.0.1:7899"
  os.environ["https_proxy"] = "http://127.0.0.1:7899"

GITHUB_TRENDING_URL = "https://github.com/trending/python?since=daily"
INDEX_HTML_PATH = "index.html"
# 现在改为抓取最多 4 个项目
MAX_PROJECTS = 4  # 最多展示多少个项目


def fetch_trending_repos() -> List[Dict[str, str]]:
  """抓取 GitHub Trending Python 今日热门项目的名称、链接、描述。"""
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
  }
  resp = requests.get(GITHUB_TRENDING_URL, headers=headers, timeout=20)
  resp.raise_for_status()

  soup = BeautifulSoup(resp.text, "html.parser")
  rows = soup.select("article.Box-row")

  projects = []
  for row in rows[:MAX_PROJECTS]:
    a = row.select_one("h2 a")
    if not a:
      continue
    full_name = a.get_text(strip=True).replace(" ", "")
    href = a.get("href", "").strip()
    url = f"https://github.com{href}" if href.startswith("/") else href

    desc_tag = row.select_one("p")
    desc = desc_tag.get_text(strip=True) if desc_tag else ""

    projects.append(
        {
            "name": full_name,
            "url": url,
            "description": desc,
        }
    )

  return projects


def init_gemini_client():
  """初始化 Gemini Client。需要环境变量 GEMINI_API_KEY。"""
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    raise RuntimeError("请先在环境变量中设置 GEMINI_API_KEY。")

  client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
  return client


def extract_json_block(text: str) -> str:
  """从 Gemini 返回的文本中提取第一个 JSON 块。"""
  start = text.find("{")
  end = text.rfind("}")
  if start == -1 or end == -1 or end <= start:
    raise ValueError("未在模型返回中找到合法 JSON。")
  return text[start : end + 1]


def enrich_with_gemini(
    client, projects: List[Dict[str, str]]
) -> List[Dict[str, str]]:
  """调用 Gemini，把项目信息翻译成中文并生成体制内应用点评。"""
  enriched = []

  for idx, p in enumerate(projects, start=1):
    print(f"\n--- 正在处理第 {idx} 个项目 ---")
    print(f"项目名称: {p['name']}")
    print(f"项目地址: {p['url']}")
    print(f"项目简介: {p['description'][:80]}{'...' if len(p['description']) > 80 else ''}")

    prompt = f"""
你是一名熟悉中国体制内业务场景的 AI 咨询顾问。

下面是一个 GitHub 开源项目，请你完成三件事：
1）把项目名称翻译成简体中文，要求自然、简洁。
2）把项目简介翻译成简体中文，50 字以内，保留核心功能信息。
3）写一段 50 字以内的“体制内应用场景点评”，要落在实际场景上，例如：政务服务、政务办公、数据治理、纪检监察、宣传工作等。

请严格按照下面 JSON 格式用中文返回，不要有多余文字、不要换字段名：
{{
  "name_zh": "中文名称",
  "desc_zh": "中文简介（50 字以内）",
  "comment": "体制内应用场景点评（50 字以内）"
}}

项目名称: {p["name"]}
项目地址: {p["url"]}
项目简介: {p["description"]}
"""
    print("调用 Gemini 中，请稍候...")
    response = client.models.generate_content(
        model="gemma-3-27b-it",
        contents=prompt,
    )
    text = (response.text or "").strip()
    print("Gemini 原始返回前 200 字符:")
    print(text[:200].replace("\n", " ") + ("..." if len(text) > 200 else ""))

    try:
      json_str = extract_json_block(text)
      print("提取出的 JSON 片段:")
      print(json_str)
      data = json.loads(json_str)
      print("JSON 解析成功。")
    except Exception as e:
      print(f"JSON 解析失败，错误信息: {e}")
      # 回退策略：如果解析失败，就用原始英文信息简单兜底
      data = {
          "name_zh": p["name"],
          "desc_zh": p["description"] or "开源项目，详情请见 GitHub 页面。",
          "comment": "可结合本单位业务需求评估是否引入或二次开发。",
      }
      print("使用兜底数据。")

    item = {
        "name": p["name"],
        "url": p["url"],
        "description": p["description"],
        "name_zh": data.get("name_zh", p["name"]),
        "desc_zh": data.get("desc_zh", p["description"]),
        "comment": data.get(
            "comment", "可结合本单位业务需求评估是否引入或二次开发。"
        ),
    }

    print("本项目最终生成数据：")
    print(json.dumps(item, ensure_ascii=False, indent=2))

    enriched.append(item)

  return enriched


def build_card_html(item: Dict[str, str]) -> str:
  """根据单个项目数据生成一张 HTML 卡片，复用现有卡片样式。"""
  # 这里统一归到“自动脚本”分类，你也可以按需改成 office / side / productivity
  return f"""
          <article class="card-item group glass-card card-hover rounded-2xl border border-slate-200/80 p-4 flex flex-col justify-between"
                   data-category="script">
            <div class="flex items-start gap-3">
              <div class="h-9 w-9 rounded-2xl bg-violet-500 flex items-center justify-center text-white text-base shadow-sm">
                ⚙️
              </div>
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold tracking-tight text-slate-900 truncate">
                  {item['name_zh']}
                </h3>
                <p class="mt-1 text-xs text-slate-500 line-clamp-2">
                  {item['desc_zh']}
                </p>
              </div>
            </div>
            <div class="mt-4 flex items-center justify-between gap-2">
              <span class="inline-flex items-center rounded-full bg-slate-900 text-slate-100 px-2.5 py-1 text-[11px] font-medium">
                点评：{item['comment']}
              </span>
              <a href="{item['url']}" target="_blank"
                 class="inline-flex items-center rounded-full bg-violet-100 text-violet-700 hover:bg-violet-200 px-3 py-1.5 text-[11px] font-medium">
                查看项目
              </a>
            </div>
          </article>
""".rstrip()


def update_index_html(cards_html: List[str]) -> None:
    with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    grid = soup.select_one("#content-grid") # 使用 CSS 选择器通常更准

    if not grid:
        print("错误：在 index.html 中没找到 id='content-grid' 的容器！")
        return

    if not cards_html:
        print("警告：没有新的卡片内容可以写入。")
        return

    # 清空旧内容
    grid.clear()
    
    # 将所有卡片 HTML 拼接并解析为文档片段
    combined_html = "".join(cards_html)
    cards_soup = BeautifulSoup(combined_html, "html.parser")
    
    # 插入新内容
    grid.append(cards_soup)

    # 写回文件
    with open(INDEX_HTML_PATH, "w", encoding="utf-8") as f:
        # 使用 str(soup) 保持原样输出
        f.write(soup.prettify(formatter="html"))
    print("成功：index.html 已更新。")


def run_git_commands() -> None:
  """在当前仓库执行 git add ., commit, push。"""

  def run(cmd: str) -> None:
    print(f"运行命令: {cmd}")
    subprocess.run(cmd, shell=True, check=True)

  run("git add .")
  # 如果没有变更，commit 会报错，这里捕获后忽略
  try:
    run('git commit -m "Auto Update"')
  except subprocess.CalledProcessError:
    print("git commit 失败（可能没有文件变更），跳过。")
    return
  run("git push")


def main():
  print("开始抓取 GitHub Trending Python 项目...")
  projects = fetch_trending_repos()
  if not projects:
    print("未抓取到任何项目，结束。")
    return

  print(f"已抓取 {len(projects)} 个项目，调用 Gemini 进行中文加工...")
  client = init_gemini_client()
  enriched = enrich_with_gemini(client, projects)
  print(f"Gemini 处理完成，共得到 {len(enriched)} 条结果。")

  print("生成卡片 HTML...")
  cards_html = [build_card_html(p) for p in enriched]
  print(f"准备写入 {len(cards_html)} 张卡片到 index.html ...")

  print("更新 index.html 中的 content-grid 区域...")
  update_index_html(cards_html)

  print("自动执行 git 提交与推送...")
  run_git_commands()

  print("全部完成。")


if __name__ == "__main__":
  main()

