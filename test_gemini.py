import os

from google import genai

# 与 list_model.py 保持一致的代理设置
os.environ["http_proxy"] = "http://127.0.0.1:7899"
os.environ["https_proxy"] = "http://127.0.0.1:7899"


def main():
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    raise RuntimeError("未找到环境变量 GEMINI_API_KEY，请先在终端或系统环境中配置后再试。")

  print("GEMINI_API_KEY 已读取，开始初始化 Client...")

  try:
    # 使用新版 genai.Client，API 版本与 list_model.py 一致
    client = genai.Client(api_key=api_key, http_options={"api_version": "v1beta"})
  except Exception as e:
    print("初始化 Gemini Client 失败：")
    print(repr(e))
    return

  # 使用你指定的模型名称（与 list_model 打印出来的保持一致）
  model_name = "gemini-2.5-flash"
  print(f"准备使用模型: {model_name}")

  prompt = "用一句中文简短自我介绍一下，你是 Gemini 测试接口。"
  print("开始调用 client.models.generate_content...")

  try:
    res = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
  except Exception as e:
    print("调用 generate_content 失败：")
    print(repr(e))
    return

  try:
    # 新版 SDK 的文本在 res.text 里
    text = (res.text or "").strip()
  except Exception as e:
    print("读取返回文本失败：")
    print(repr(e))
    return

  print("\n=== 调用成功，返回内容如下 ===")
  print(text)
  print("=== 结束 ===")


if __name__ == "__main__":
  main()


