import pandas as pd
import numpy as np
import os
# === 读取两张表 ===
table1 = pd.read_excel("./exptal data 2024.xlsx")
item_payoff = pd.read_csv("./item_payoff.csv")   # 你的新 payoff
item_payoff["Item"] = item_payoff["Item"].str.strip().str.lower()
# ⭐ 关键修改：将 Question ID (21–60) 映射到 trial (1–40)
item_payoff["Trial"] = item_payoff["Question ID"] - 20
# ================================================================
# 0. 工具函数：清洗 choose 字段
# ================================================================
def clean_choice(raw):
    """
    将 Excel 里的混乱 choose 字段清洗成唯一 item 名称或 ID。
    例如:
        'PURPLE</p>,<p>SEA' → 'purple'
        '<p>BLUE</p>' → 'blue'
        '15' → '15'
    """
    if raw is None:
        return None

    s = str(raw).strip()

    # 移除 HTML 标签
    remove_tags = ["<p>", "</p>", "<br>", "</br>", "<p/>"]
    for tag in remove_tags:
        s = s.replace(tag, "")

    # 替换逗号为分隔符
    s = s.replace(",", " ")

    # 拆分成词（可能多个，例如 "PURPLE SEA"）
    parts = s.split()
    if len(parts) == 0:
        return None

    first = parts[0]

    return first.strip()

# ---------------------------------------
# 1. ITEM → CATEGORY 映射（你给的顺序）
# ---------------------------------------

item_to_name = {
    1: 'Purple', 2: 'Blue', 3: 'Green', 4: 'Red', 5: 'Orange',
    6: 'Risk', 7: 'Hope', 8: 'Safety', 9: 'Vitality', 10: 'Power',
    11: 'Literature', 12: 'Physics', 13: 'Music', 14: 'History',
    15: 'Geography', 16: 'Sea', 17: 'Desert', 18: 'City', 19: 'Mountain',
    20: 'Village'
}

# 将 item 名全部转成小写以便匹配
itemname_lower_to_id = {name.lower(): ID for ID, name in item_to_name.items()}

# ================================================================
# 3. Item Name → Category 映射
# ================================================================
category_map = {
    "Color":     ['Purple', 'Blue', 'Green', 'Red', 'Orange'],
    "Abstract":  ['Risk', 'Hope', 'Safety', 'Vitality', 'Power'],
    "Disciplines": ['Literature', 'Physics', 'Music', 'History'],
    "Places":    ['Geography', 'Sea', 'Desert', 'City', 'Mountain', 'Village']
}

item_to_category = {}
for cat, items in category_map.items():
    for item in items:
        item_to_category[item.lower()] = cat   # 小写存储方便匹配

# ================================================================
# 4. 处理 table1：item-level 偏好 + 40 次选择
# ================================================================
users = table1["User ID"].unique()
all_users_data = []

for uid in users:
    user_df = table1[table1["User ID"] == uid].reset_index(drop=True)

    # ---- (1) 前 20 行：偏好 ----
    pref_rows = user_df[user_df["Question ID"] <= 20]
    item_prefs = dict(zip(pref_rows["Question ID"], pref_rows["Score"]))  # itemID → score

    # ---- (2) 后 40 行：选择 ----
    choice_rows = user_df[user_df["Question ID"] > 20]
    choices_raw = choice_rows["choose"].values[:40]

    choices = []
    for ch in choices_raw:

        # Excel 空值（float nan）
        if isinstance(ch, float) and np.isnan(ch):
            choices.append(None)
            continue

        cleaned = clean_choice(ch)

        if cleaned is None:
            choices.append(None)
            continue

        # 情况 1：数字 ID
        if cleaned.isdigit():
            choices.append(int(cleaned))
            continue

        # 情况 2：字符串 item 名（全大写小写都接受）
        cleaned_lower = cleaned.lower()

        if cleaned_lower in itemname_lower_to_id:
            choices.append(itemname_lower_to_id[cleaned_lower])
            continue

        # 其他情况 → 标记 None，不报错
        print(f"[WARNING] 无法映射 choose='{ch}', cleaned='{cleaned_lower}' → 设置为 None")
        choices.append(None)

    # ---- (3) item 名 & 类别 ----
    item_names = [item_to_name[i] if i in item_to_name else None for i in choices]
    categories = [item_to_category[name.lower()] if name else None for name in item_names]

    # ---- (4) 构建 user trial 数据 ----
    user_data = pd.DataFrame({
        "User": uid,
        "Trial": np.arange(1, 41),
        "Choice_itemID": choices,
        "Choice_itemName": item_names,
        "Choice_category": categories
    })

    # ---- (5) 写入 item-level 偏好列 ----
    for item_id, item_name in item_to_name.items():
        col = f"Pref_{item_name}"
        user_data[col] = item_prefs.get(item_id, np.nan)

    all_users_data.append(user_data)


# 合并所有用户
all_users_data = pd.concat(all_users_data, ignore_index=True)

print("\n=== 用户 trial-by-trial 数据预览 ===")
print(all_users_data.head())

# ================================================================
# 6. 合并 long-format payoff（已转 trial）
# ================================================================
merged = all_users_data.copy()

for item_id, item_name in item_to_name.items():

    item_lower = item_name.lower()

    # 找出该 item 在 payoff 表中的记录
    df_item_payoff = item_payoff[item_payoff["Item"] == item_lower]

    if df_item_payoff.empty:
        print(f"[WARNING] payoff 中缺失 item：{item_name}")
        merged[f"Payoff_{item_name}"] = np.nan
        continue

    # 按 trial 合并
    merged = merged.merge(
        df_item_payoff[["Trial", "Payoff"]],
        on="Trial",
        how="left",
        suffixes=("", "")
    )

    merged.rename(columns={"Payoff": f"Payoff_{item_name}"}, inplace=True)

# ================================================================
# 7. 导出 Excel
# ================================================================
output_path = "./all_data.xlsx"
merged.to_excel(output_path, index=False)

print("\n数据已成功导出：", output_path)

