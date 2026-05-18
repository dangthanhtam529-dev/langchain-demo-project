import os
import json
import urllib.request
import urllib.error

IMAGE_DIR = "image"
IMAGE_NAME = "bar_scene.png"
IMAGE_PATH = os.path.join(IMAGE_DIR, IMAGE_NAME)

PROMPT = """在一个有趣的酒吧里，吧台上有两个人在喝着酒聊着天，然后还有一个酒保为他们服务，附近的座位上坐着形形色色的客人，画面整体风格是日漫形式的风格，色彩轻柔符合亚洲人审美，酒吧的装饰要现代化精美，客人服饰随机，不要出现和服和日文等强日式元素，只是借鉴日漫的那种轻松的氛围感。"""

API_KEY = "sk-F2h3IFLd5coFnLDREfKw3hFmsr7imbkldEvw6XfIc2Vk1MTf"
BASE_URL = "https://api.zhongzhuan.win/v1"

def generate_image():
    print("正在生成图片...")

    url = f"{BASE_URL}/images/generations"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "model": "gpt-image-2",
        "prompt": PROMPT,
        "n": 1,
        "size": "1024x1024"
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))

        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0]["url"]
            print(f"图片生成成功!")
            print(f"URL: {image_url}")

            print("\n正在下载图片...")
            os.makedirs(IMAGE_DIR, exist_ok=True)
            urllib.request.urlretrieve(image_url, IMAGE_PATH)

            print(f"图片已保存到: {IMAGE_PATH}")
        else:
            print(f"生成失败: {result}")

    except urllib.error.HTTPError as e:
        print(f"HTTP 错误: {e.code}")
        print(e.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"请求错误: {e.reason}")

if __name__ == "__main__":
    generate_image()
