#!/usr/bin/env python3
"""
iCost 智能记账助手 - 提供支出、收入、转账记录管理，支持多账户、多币种、分类识别等完整记账功能的MCP服务
"""

import json
import logging
import subprocess
import urllib.parse
from typing import Any, Dict, Optional

from fastmcp import FastMCP

# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('icost_mcp_server.log')
    ]
)
logger = logging.getLogger(__name__)

# 创建FastMCP服务器实例，并设置MCP的描述信息
# mcp = FastMCP(name = "iCost MCP Server", description="iCost 智能记账助手 - 提供支出、收入、转账记录管理，支持多账户、多币种、分类识别等完整记账功能的MCP服务")
mcp = FastMCP("iCost App MCP Server")

def open_icost_url(url: str) -> Dict[str, Any]:
    """
    打开iCost URL协议
    
    Args:
        url: iCost URL协议字符串
        
    Returns:
        操作结果
    """
    try:
        # 在macOS上使用open命令打开URL
        result = subprocess.run(
            ["open", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "message": f"成功打开iCost: {url}",
                "url": url
            }
        else:
            return {
                "success": False,
                "message": f"打开失败: {result.stderr}",
                "url": url
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "message": "操作超时",
            "url": url
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"执行错误: {str(e)}",
            "url": url
        }

def build_expense_url(
    amount: float,
    category: str,
    currency: str = "CNY",
    account: Optional[str] = None,
    book: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    claim: bool = False,
    remark: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None,
    discount: Optional[float] = None
) -> str:
    """
    构建支出记录URL
    
    Args:
        amount: 金额（必填）
        category: 分类名称（必填）
        currency: 货币类型，默认CNY
        account: 账户名称
        book: 账本名称
        date: 记账日期，格式：2019.10.10
        time: 记账时间，格式：12:00
        claim: 是否可报销
        remark: 备注
        no_budget: 不计入预算
        no_count: 不计入收支
        location: 位置信息
        tag: 标签
        discount: 优惠金额
        
    Returns:
        iCost URL字符串
    """
    params = {
        "amount": str(amount),
        "category": category,
        "currency": currency
    }
    
    # 添加可选参数
    if account:
        params["account"] = account
    if book:
        params["book"] = book
    if date:
        params["date"] = date
    if time:
        params["time"] = time
    if claim:
        params["claim"] = "1"
    if remark:
        params["remark"] = remark
    if no_budget:
        params["noBudget"] = "1"
    if no_count:
        params["noCount"] = "1"
    if location:
        params["location"] = location
    if tag:
        params["tag"] = tag
    if discount:
        params["discount"] = str(discount)
    
    # 构建URL
    query_string = urllib.parse.urlencode(params)
    return f"iCost://expense?{query_string}"

def build_income_url(
    amount: float,
    category: str,
    currency: str = "CNY",
    account: Optional[str] = None,
    book: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = "12:00",
    remark: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """
    构建收入记录URL
    """
    params = {
        "amount": str(amount),
        "category": category,
        "currency": currency
    }
    
    # 添加可选参数
    if account:
        params["account"] = account
    if book:
        params["book"] = book
    if date:
        params["date"] = date
    if time:
        params["time"] = time
    if remark:
        params["remark"] = remark
    if no_budget:
        params["noBudget"] = "1"
    if no_count:
        params["noCount"] = "1"
    if location:
        params["location"] = location
    if tag:
        params["tag"] = tag
    
    query_string = urllib.parse.urlencode(params)
    return f"iCost://income?{query_string}"

def build_transfer_url(
    amount: float,
    from_account: str,
    to_account: str,
    currency: str = "CNY",
    book: Optional[str] = None,
    remark: Optional[str] = None,
    fee: Optional[float] = None,
    discount: Optional[float] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """
    构建转账记录URL
    """
    params = {
        "amount": str(amount),
        "from_account": from_account,
        "to_account": to_account,
        "currency": currency
    }
    
    # 添加可选参数
    if book:
        params["book"] = book
    if remark:
        params["remark"] = remark
    if fee:
        params["fee"] = str(fee)
    if discount:
        params["discount"] = str(discount)
    if date:
        params["date"] = date
    if time:
        params["time"] = time
    if no_budget:
        params["noBudget"] = "1"
    if no_count:
        params["noCount"] = "1"
    if location:
        params["location"] = location
    if tag:
        params["tag"] = tag
    
    query_string = urllib.parse.urlencode(params)
    return f"iCost://transfer?{query_string}"

@mcp.tool()
def icost_open_app(page: str) -> str:
    """
    打开iCost应用的不同页面
    
    Args:
        page: 要打开的页面 (asset_main: 资产首页, chart_main: 统计首页, quick_record: 记账页面)
    
    Returns:
        操作结果的JSON字符串
    """
    logger.info(f"调用 icost_open_app - 页面: {page}")
    
    if page not in ["asset_main", "chart_main", "quick_record"]:
        error_msg = f"无效的页面类型: {page}，支持的类型: asset_main, chart_main, quick_record"
        logger.error(error_msg)
        return json.dumps({
            "success": False,
            "message": error_msg
        }, ensure_ascii=False)
    
    url = f"iCost://{page}"
    logger.info(f"生成URL: {url}")
    result = open_icost_url(url)
    logger.info(f"操作结果: {result}")
    return json.dumps(result, ensure_ascii=False, indent=2)

@mcp.tool()
def icost_add_expense(
    amount: float,
    category: str,
    currency: str = "CNY",
    account: Optional[str] = None,
    book: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    claim: bool = False,
    remark: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None,
    discount: Optional[float] = None
) -> str:
    """
    添加支出记录到iCost
    
    Args:
        amount: 金额（必填）
        category: 分类名称（必填），从icost_categories()返回的支出分类中选择
        currency: 货币类型，默认CNY
        account: 账户名称，如：支付宝、微信钱包等
        book: 账本名称，默认为【默认账本】
        date: 记账日期（必填），格式：2019.10.10, 为空时默认当天日期
        time: 记账时间（必填），格式：12:00（24小时制），为空时默认当前时间
        claim: 是否可以进行报销
        remark: 备注信息
        no_budget: 不计入预算
        no_count: 不计入收支
        location: 位置信息，格式：位置#longitude#latitude
        tag: 标签，格式：标签1#标签2
        discount: 优惠金额
    
    Returns:
        操作结果的JSON字符串
    """
    logger.info(f"调用 icost_add_expense - 金额: {amount}, 分类: {category}, 备注: {remark}")
    
    url = build_expense_url(
        amount=amount,
        category=category,
        currency=currency,
        account=account,
        book=book,
        date=date,
        time=time,
        claim=claim,
        remark=remark,
        no_budget=no_budget,
        no_count=no_count,
        location=location,
        tag=tag,
        discount=discount
    )
    logger.info(f"生成支出URL: {url}")
    result = open_icost_url(url)
    logger.info(f"支出记录操作结果: {result}")
    return json.dumps({
        **result,
        "type": "expense",
        "data": {
            "amount": amount,
            "category": category,
            "currency": currency,
            "account": account,
            "book": book,
            "date": date,
            "time": time,
            "claim": claim,
            "remark": remark,
            "no_budget": no_budget,
            "no_count": no_count,
            "location": location,
            "tag": tag,
            "discount": discount
        }
    }, ensure_ascii=False, indent=2)

@mcp.tool()
def icost_add_income(
    amount: float,
    category: str,
    currency: str = "CNY",
    account: Optional[str] = None,
    book: Optional[str] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    remark: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """
    添加收入记录到iCost
    
    Args:
        amount: 金额（必填）
        category: 分类名称（必填），从icost_categories()返回的收入分类中选择
        currency: 货币类型，默认CNY
        account: 账户名称，如：支付宝、微信钱包等
        book: 账本名称，默认为【默认账本】
        date: 记账日期（必填），格式：2019.10.10, 为空时默认当天日期
        time: 记账时间（必填），格式：12:00（24小时制），为空时默认当前时间
        remark: 备注信息
        no_budget: 不计入预算
        no_count: 不计入收支
        location: 位置信息，格式：位置#longitude#latitude
        tag: 标签，格式：标签1#标签2
    
    Returns:
        操作结果的JSON字符串
    """
    logger.info(f"调用 icost_add_income - 金额: {amount}, 分类: {category}, 备注: {remark}")
    
    url = build_income_url(
        amount=amount,
        category=category,
        currency=currency,
        account=account,
        book=book,
        date=date,
        time=time,
        remark=remark,
        no_budget=no_budget,
        no_count=no_count,
        location=location,
        tag=tag
    )
    logger.info(f"生成收入URL: {url}")
    result = open_icost_url(url)
    logger.info(f"收入记录操作结果: {result}")
    return json.dumps({
        **result,
        "type": "income",
        "data": {
            "amount": amount,
            "category": category,
            "currency": currency,
            "account": account,
            "book": book,
            "date": date,
            "time": time,
            "remark": remark,
            "no_budget": no_budget,
            "no_count": no_count,
            "location": location,
            "tag": tag
        }
    }, ensure_ascii=False, indent=2)

@mcp.tool()
def icost_add_transfer(
    amount: float,
    from_account: str,
    to_account: str,
    currency: str = "CNY",
    book: Optional[str] = None,
    remark: Optional[str] = None,
    fee: Optional[float] = None,
    discount: Optional[float] = None,
    date: Optional[str] = None,
    time: Optional[str] = None,
    no_budget: bool = False,
    no_count: bool = False,
    location: Optional[str] = None,
    tag: Optional[str] = None
) -> str:
    """
    添加转账记录到iCost
    
    Args:
        amount: 转账金额（必填）
        from_account: 转出账户名称（必填），如：支付宝、微信钱包等
        to_account: 转入账户名称（必填），如：支付宝、微信钱包等
        currency: 货币类型，默认CNY
        book: 账本名称，默认为【默认账本】
        remark: 备注信息
        fee: 手续费
        discount: 折扣费用
        date: 记账日期，格式：2019.10.10
        time: 记账时间，格式：12:00（24小时制）
        no_budget: 不计入预算
        no_count: 不计入收支
        location: 位置信息，格式：位置#longitude#latitude
        tag: 标签，格式：标签1#标签2
    
    Returns:
        操作结果的JSON字符串
    """
    logger.info(f"调用 icost_add_transfer - 金额: {amount}, 从账户: {from_account}, 到账户: {to_account}, 备注: {remark}")
    
    url = build_transfer_url(
        amount=amount,
        from_account=from_account,
        to_account=to_account,
        currency=currency,
        book=book,
        remark=remark,
        fee=fee,
        discount=discount,
        date=date,
        time=time,
        no_budget=no_budget,
        no_count=no_count,
        location=location,
        tag=tag
    )
    logger.info(f"生成转账URL: {url}")
    result = open_icost_url(url)
    logger.info(f"转账记录操作结果: {result}")
    return json.dumps({
        **result,
        "type": "transfer",
        "data": {
            "amount": amount,
            "from_account": from_account,
            "to_account": to_account,
            "currency": currency,
            "book": book,
            "remark": remark,
            "fee": fee,
            "discount": discount,
            "date": date,
            "time": time,
            "no_budget": no_budget,
            "no_count": no_count,
            "location": location,
            "tag": tag
        }
    }, ensure_ascii=False, indent=2)

# iCost 支出的分类
@mcp.tool()
def icost_categories() -> dict:
    """iCost支持的收入、支出分类
    
    重要提示：AI大模型在处理记账请求时，必须优先从此函数返回的分类列表中选择合适的类型。
    - 对于支出记录，category参数必须从返回结果的"支出"列表中选择最匹配的分类
    - 对于收入记录，category参数必须从返回结果的"收入"列表中选择最匹配的分类
    - 如果用户描述的内容无法精确匹配现有分类，应选择最相近的分类或使用"其他"
    - 禁止使用此列表之外的自定义分类名称
    
    Returns:
        dict: 包含"支出"和"收入"两个键的字典，每个键对应一个分类列表
    """
    logger.info("调用 icost_categories - 获取支持的分类列表")
    
    categories = {
        "支出": [
            "餐饮", "购物", "交通", "日用",
            "通讯", "住房", "医疗", "医疗健康", "服饰", "数码电器",
            "汽车", "学习", "办公", "运动", "社交", "人情", "育儿", 
            "母婴亲子", "旅行", "烟酒", "扫二维码付款", "充值缴费", 
            "生活服务", "文化休闲", "理财", "水果", "其他"
        ], 
        "收入": ["工资", "奖金", "福利", "退款", "红包", "副业", "退税", "投资", "其他"]
    }
    
    logger.info(f"返回分类列表 - 支出类型数量: {len(categories['支出'])}, 收入类型数量: {len(categories['收入'])}")
    return categories

##### 时间相关 Tools ###

@mcp.tool
def current_time() -> str:
    """获取当前时间(年-月-日 小时:分钟:秒)，可判断今天、昨天、前天、上周一等等时间语意"""
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool
def am() -> str:
    """上午，默认为09:00"""
    return "09:00"

@mcp.tool
def pm() -> str:
    """下午，默认为18:00"""
    return "18:00"

@mcp.tool
def default_time() -> str:
    """默认具体时间：时分秒"""
    return "12:00:00"

if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=9000)
