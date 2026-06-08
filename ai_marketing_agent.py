from openai import OpenAI
import requests
import tomllib

# ==========================
# 读取配置
# ==========================

with open(".streamlit/secrets.toml", "rb") as f:
    secrets = tomllib.load(f)

DEEPSEEK_API_KEY = secrets["DEEPSEEK_API_KEY"]

FEISHU_APP_ID = secrets["FEISHU_APP_ID"]
FEISHU_APP_SECRET = secrets["FEISHU_APP_SECRET"]

BASE_ID = secrets["BASE_ID"]
TABLE_ID = secrets["TABLE_ID"]

# ==========================
# DeepSeek
# ==========================

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# ==========================
# 获取飞书Token
# ==========================

auth = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
).json()

if auth.get("code") != 0:
    print("飞书认证失败：")
    print(auth)
    exit()

token = auth["tenant_access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# ==========================
# 输入产品信息
# ==========================

product_name = input("产品名称：")
target_customer = input("目标客户：")
features = input("产品特点：")

# ==========================
# DeepSeek生成文案
# ==========================

prompt = f"""
你是一名资深营销文案专家。

请根据以下信息生成一段营销文案。

产品名称：
{product_name}

目标客户：
{target_customer}

产品特点：
{features}

要求：

1. 突出卖点
2. 80字以内
3. 中文
4. 有购买欲
"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

ai_copy = response.choices[0].message.content

print("\n生成文案：")
print(ai_copy)

# ==========================
# 写入飞书
# ==========================

url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_ID}/tables/{TABLE_ID}/records"

payload = {
    "fields": {
        "产品名称": product_name,
        "目标客户": target_customer,
        "产品特点": features,
        "AI文案": ai_copy
    }
}

resp = requests.post(
    url,
    headers=headers,
    json=payload
)

print("\n飞书返回：")
print(resp.json())