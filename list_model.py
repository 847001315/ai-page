

import os
from google import genai

# 代理配置（确保端口正确）
os.environ['http_proxy'] = 'http://127.0.0.1:7899'
os.environ['https_proxy'] = 'http://127.0.0.1:7899'

def list_my_models():
    api_key = os.getenv("GEMINI_API_KEY") or "你的_API_KEY"
    
    # 初始化新版 Client
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1beta'})

    print("--- 正在拉取可用模型列表 ---")
    try:
        # 使用新 SDK 的模型列表获取方法
        for model in client.models.list():
            print(f"模型名称: {model.name}")
            print(f"支持功能: {model.supported_actions}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ 还是获取失败: {e}")

if __name__ == "__main__":
    list_my_models()