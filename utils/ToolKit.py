import re


def normalize_role_prefix(text: str, role_name: str, *, keep_other_role=False) -> str:
    """
    解决多轮对话中角色标签重复、格式混乱的问题
    支持识别: [] {} () 【】 <> 《》 等多种括号格式

    参数:
        text:           LLM 或用户发来的原始文本
        role_name:      你期望的角色名，例如 "AI助手"、"小红"
        keep_other_role:
                True  → 发现不是你的角色名也保留原样（适合双人对话存档）
                False → 强制全部改成你的 role_name（推荐给单人连续角色扮演）

    返回: 永远只在最前面有一个干净的 [role_name] 的字符串
    """
    if not text:
        return f"[{role_name}]\n"

    # 定义支持的括号对
    bracket_pairs = [
        (r'\[', r'\]'),  # []
        (r'\{', r'\}'),  # {}
        (r'\(', r'\)'),  # ()
        (r'【', r'】'),  # 【】
        (r'<', r'>'),  # <>
        (r'《', r'》'),  # 《》
    ]

    # 构建匹配所有括号类型的正则表达式
    # 匹配形如: [角色名] {角色名} (角色名) 【角色名】 <角色名> 《角色名》
    bracket_patterns = '|'.join([f'{left}.*?{right}' for left, right in bracket_pairs])

    # 1. 提取开头的所有角色标签（用于 keep_other_role 判断）
    original_prefix_match = re.match(
        rf'^(\s*(?:{bracket_patterns})(?:\s*[:：])?\s*)+',
        text,
        flags=re.MULTILINE
    )
    original_prefix = original_prefix_match.group(0) if original_prefix_match else ""

    # 2. 如果需要保留其他角色的标签，检查是否包含非目标角色
    if keep_other_role and original_prefix:
        # 提取所有括号内的内容
        found_roles = re.findall(
            rf'(?:{"|".join([f"{left}(.*?){right}" for left, right in bracket_pairs])})',
            original_prefix
        )
        # 扁平化结果（因为findall会返回多个捕获组）
        found_roles = [r.strip() for group in found_roles for r in group if r.strip()]

        # 如果找到的角色都不是目标角色，保留原文
        if found_roles and all(role != role_name for role in found_roles):
            return text.rstrip() + "\n"

    # 3. 清理所有开头的角色标签（包括冒号和空白）
    cleaned = re.sub(
        rf'^(\s*(?:{bracket_patterns})(?:\s*[:：])?\s*)+',
        '',
        text,
        flags=re.MULTILINE
    )

    # 4. 去掉开头的空行和空白
    cleaned = cleaned.lstrip('\n\r\t ')

    # 5. 只添加一个标准格式的标签
    prefix = f"[{role_name}]"
    result = prefix + ("\n" + cleaned if cleaned else "")

    # 确保结尾有一个换行
    return result.rstrip("\n\r") + "\n"


if __name__ == "__main__":
    def wrap_llm_output(llm_output: str):
        return normalize_role_prefix(llm_output, role_name="小红", keep_other_role=False)


    # 测试用例 - 覆盖所有括号类型
    texts = [
        "哈哈哈今天好开心",  # 没标签
        "[小红] 嗯呢～",  # 方括号
        "{小红} 嗯呢～",  # 花括号
        "(小红) 嗯呢～",  # 圆括号
        "【小红】嗯呢～",  # 中文方括号
        "<小红> 嗯呢～",  # 尖括号
        "《小红》嗯呢～",  # 书名号
        "[ 小红 ]   嗯呢～",  # 带空格
        "[小红]: 嗯呢～",  # 带冒号
        "【小红】：嗯呢～",  # 带中文冒号
        "[AI助手]\n{小红}我来啦",  # 多个不同括号
        "(用户) 你好啊\n《小红》 我是小红",  # 混合括号
        "   \n\n <错的角色名>   内容内容内容",  # 完全乱的
        "{小美}[小红](AI)内容",  # 三个连续标签
        "《AI》 【用户】 <小红> 哈哈",  # 多种括号混合
    ]

    print("=" * 60)
    print("测试模式: keep_other_role=False (强制统一)")
    print("=" * 60)
    for t in texts:
        result = wrap_llm_output(t)
        print(f"原始    → {repr(t)}")
        print(f"处理后  → {result}")
        print("-" * 60)

    print("\n" + "=" * 60)
    print("测试模式: keep_other_role=True (保留其他角色)")
    print("=" * 60)

    test_cases_keep = [
        "[小红] 我的消息",  # 目标角色 → 规范化
        "{用户} 用户的消息",  # 其他角色 → 保留
        "《AI助手》 AI的回复",  # 其他角色 → 保留
        "[用户] 你好\n[小红] 嗨",  # 其他角色在前 → 保留
    ]

    for t in test_cases_keep:
        result = normalize_role_prefix(t, role_name="小红", keep_other_role=True)
        print(f"原始    → {repr(t)}")
        print(f"处理后  → {result}")
        print("-" * 60)