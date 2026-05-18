"""
test14_agent.py - 使用 Pydantic 定义复杂参数的工具
演示如何让模型理解并填充复杂的结构化参数
"""

from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()


# ============================================
# 1. 使用 Pydantic 定义复杂参数结构
# ============================================

class Address(BaseModel):
    """地址信息"""
    province: str = Field(description="省份")
    city: str = Field(description="城市")
    district: str = Field(description="区县")
    street: str = Field(description="街道")
    detail: str = Field(description="详细地址")


class ProductItem(BaseModel):
    """商品条目"""
    name: str = Field(description="商品名称")
    quantity: int = Field(description="数量", ge=1)
    unit_price: float = Field(description="单价", ge=0)
    specification: str = Field(description="规格，如 '500ml', 'L码'", default="")


class OrderRequest(BaseModel):
    """创建订单的请求参数"""
    customer_name: str = Field(description="客户姓名")
    phone: str = Field(description="联系电话")
    shipping_address: Address = Field(description="收货地址")
    products: list[ProductItem] = Field(description="商品列表，至少包含一个商品")
    payment_method: str = Field(description="支付方式，如 '支付宝', '微信支付', '银行卡'")
    remark: str = Field(description="订单备注，如 '加急', '请电话联系'", default="")
    coupon_code: str = Field(description="优惠券代码，没有则留空", default="")


# ============================================
# 2. 定义工具函数
# ============================================
@tool(args_schema=OrderRequest)
def create_order(
    customer_name: str,
    phone: str,
    shipping_address: Address,
    products: list[ProductItem],
    payment_method: str,
    remark: str = "",
    coupon_code: str = "",
) -> str:
    """
    创建新订单。
    接收一个包含客户信息、地址、商品列表等的结构化订单请求。
    """
    total_amount = sum(p.quantity * p.unit_price for p in products)

    product_details = "\n".join(
        f"  - {p.name} x{p.quantity} ({p.specification}) = ¥{p.quantity * p.unit_price:.2f}"
        for p in products
    )

    address_str = f"{shipping_address.province}{shipping_address.city}{shipping_address.district}{shipping_address.street}{shipping_address.detail}"

    result = f"""
✅ 订单创建成功！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 订单信息
  客户: {customer_name}
  电话: {phone}
  地址: {address_str}

📦 商品清单:
{product_details}

💰 订单金额: ¥{total_amount:.2f}
💳 支付方式: {payment_method}
📝 备注: {remark if remark else '无'}
🎫 优惠券: {coupon_code if coupon_code else '未使用'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    return result


# ============================================
# 3. 创建结构化工具
# ============================================




# ============================================
# 4. 初始化模型和 Agent
# ============================================

model = init_chat_model(
    "glm-4.7",
    model_provider="openai",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
)

from langchain.agents import create_agent

agent = create_agent(
    model=model,
    tools=[create_order],
    system_prompt="""你是一个电商客服助手，帮助用户创建订单。

当用户表达购买意向时，你需要：
1. 理解用户的购买需求
2. 从对话中提取或询问必要信息
3. 使用 create_order 工具创建订单

必要信息包括：
- 客户姓名、电话
- 完整的收货地址
- 购买的商品（名称、数量、单价、规格）
- 支付方式

如果信息不完整，请友好地向用户询问缺失的信息。
"""
)


# ============================================
# 5. 测试
# ============================================

if __name__ == "__main__":
    test_inputs = [
        "我叫张三，电话13800138000，想买2瓶可乐（500ml，3元一瓶）和1袋薯片（原味，5元），送到北京市朝阳区建国路88号SOHO现代城A座1201，用支付宝支付",
        "帮我下单，李四，15912345678，上海市浦东新区陆家嘴环路1000号，买3盒牛奶（250ml，4元一盒），微信支付",
    ]

    print("=" * 70)
    print("Pydantic 复杂参数工具演示")
    print("=" * 70)

    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'=' * 70}")
        print(f"测试 {i}: {user_input[:50]}...")
        print(f"{'=' * 70}")

        try:
            result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
            print(result["messages"][-1].content)
        except Exception as e:
            print(f"❌ 错误: {e}")

    print("\n" + "=" * 70)
    print("演示完成！")
    print("=" * 70)
