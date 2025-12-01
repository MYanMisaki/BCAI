import pandas as pd

# 设定每个类别的均值和标准差
category_mean = {
    'colour': 2.5,  # Colours
    'concept': 2.5,  # Abstract concepts
    'discipline': 2,    # Disciplines
    'place': 3     # Places
}

# 创建字典映射每个Question ID到item名称、category
item_mapping = {
    1: 'Purple', 2: 'Blue', 3: 'Green', 4: 'Red', 5: 'Orange',
    6: 'Risk', 7: 'Hope', 8: 'Safety', 9: 'Vitality', 10: 'Power',
    11: 'Literature', 12: 'Physics', 13: 'Music', 14: 'History',
    15: 'Geography', 16: 'Sea', 17: 'Desert', 18: 'City', 19: 'Mountain',
    20: 'Village'
}

category_mapping = {
    1: 'colour', 2: 'colour', 3: 'colour', 4: 'colour', 5: 'colour',
    6: 'concept', 7: 'concept', 8: 'concept', 9: 'concept', 10: 'concept',
    11: 'discipline', 12: 'discipline', 13: 'discipline', 14: 'discipline', 15: 'discipline',
    16: 'place', 17: 'place', 18: 'place', 19: 'place', 20: 'place'
}

# 读取Excel文件
file_path = 'exptal data 2024.xlsx'
xls = pd.ExcelFile(file_path)
df = pd.read_excel(xls, sheet_name='exptal data final 26')

# 创建一个字典，根据每个玩家（User ID）的前20行填入对应的值
player_data = {}
test_data = {}

# 提取每个玩家前20行数据并保存
for user_id in df['User ID'].unique():
    player_info = []
    user_data = df[df['User ID'] == user_id].head(20)  # 获取每个玩家前20行数据
    for i, row in user_data.iterrows():
        item = item_mapping[row['Question ID']]  # 获取item名称
        category = category_mapping[row['Question ID']]  # 获取category
        score = int(row['Score'])  # 得分转为整数
        player_info.append((item, int(row['id']), category, score))  # 保存数据
    player_data[user_id] = player_info  # 将每个玩家的数据添加到字典中

    test_info = []
    user_data_last_40 = df[df['User ID'] == user_id].iloc[20:60]
    for i, row in user_data_last_40.iterrows():
        if isinstance(row['choose'], str):
            df.at[i, 'choose'] = row['choose'].capitalize()  # 将 'choose' 字段的内容首字母大写
        else:
            df.at[i, 'choose'] = row['choose']  # 如果不是字符串，直接保留原值（可以根据需求进行修改）
        itemname = df.at[i, 'choose']
        # 处理 row['id'] 为 NaN 或无效值的情况
        try:
            category_id = int(row['id'])  # 尝试将 id 转换为整数
        except (ValueError, TypeError):  # 如果转换失败（例如值为 NaN 或无法转换为整数）
            category_id = None  # 设置为 None 或其他默认值

        # 使用 category_mapping 获取类别，若 id 无效则返回默认值 'unknown'
        category = category_mapping.get(category_id, 'unknown')  # 获取类别，若 id 不存在则返回默认值
        score = int(row['Score'])  # 当前得分转为整数
        player_choices = player_data.get(1, [])
        for item, item_id, category, score in player_choices:
            if item == itemname:
                liked_score = score

        if pd.isna(itemname):
        # 如果是 NaN，则将所有字段设为 None
            test_info.append({
                'Question ID': None, 
                'item': None, 
                'score': None, 
                'liked_score': None, 
                'category': None
            })
        else:
         # 如果 itemname 不是 NaN，则正常填充
            test_info.append({
                'Question ID': row['Question ID'] - 20, 
                'item': itemname, 
                'score': score, 
                'liked_score': liked_score, 
                'category': category
        })
    test_data[user_id] = test_info  # 将该玩家的数据添加到字典中

print(test_data[1])
# 每轮得分数据，按照 'colour', 'concept', 'discipline', 'place' 顺序组织
payoffs = [
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [3, 2, 2, 3],
    [3, 2, 2, 3],
    [2, 2, 2, 4],
    [4, 3, 2, 1],
    [2, 2, 2, 4],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [3, 2, 2, 3],
    [1, 3, 2, 4],
    [3, 3, 2, 2],
    [3, 2, 2, 3],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [3, 2, 2, 3],
    [3, 2, 2, 3],
    [2, 2, 2, 4],
    [4, 3, 2, 1],
    [2, 2, 2, 4],
    [1, 3, 2, 4],
    [4, 2, 2, 2],
    [2, 3, 2, 3],
    [3, 2, 2, 3],
    [1, 3, 2, 4],
    [3, 3, 2, 2],
    [3, 2, 2, 3]
]

# 创建 DataFrame
columns = ['colour', 'concept', 'discipline', 'place']
payoff_df = pd.DataFrame(payoffs, columns=columns)

# 获取每轮最大分的类别
def get_max_category_for_round(i):
    return payoff_df.iloc[i].idxmax()

def get_choice_behavior(prev_score, curr_score, prev_category, curr_category, liked_score, max_category, max_liked_score):
    behaviors = []

    # W: winner-chasing
    if prev_category is not None and prev_category == max_category:
        behaviors.append('W')

    # R: regret-based switching
    if prev_score is not None and curr_score is not None and curr_score < prev_score and prev_category != curr_category:
        behaviors.append('R')

    # D: disappointment-driven switching
    if prev_score is not None and curr_score is not None and curr_score < prev_score:
        behaviors.append('D')

    # L: likeability-driven choices
    if liked_score == max_liked_score:
        behaviors.append('L')

    return behaviors



# 主程序：创建字典并计算选择行为
user_behavior = {}
user_id = 1
rounds = test_data.get(user_id, [])
behaviors = []
total_score = 0
# 获取当前用户的所有项的 liked_score (来自 player_data)
player_likescore = {item: score for item, _, _, score in player_data[user_id]}

# 初始状态
prev_score = None
prev_category = None
max_score_category = None

# 遍历该用户的所有选择数据
for i, row in enumerate(rounds):
    print(rounds[i])
    # 获取当前轮次数据
    itemname = row['item']
    score = row['score']
    liked_score = row['liked_score']
    category = row['category']
    
    # 获取payoff_df中当前类别的得分
    max_category = get_max_category_for_round(i)
    
    # 获取当前用户所有 items 的最大 liked_score
    max_liked_score = max(player_likescore.values())

    if i == 0:
        # 初始状态，选择是纯粹的 likeability-driven
        behaviors.append('L')
        prev_score = score
        prev_category = category
        max_score_category = max_category
        print(itemname, prev_score, score, prev_category, category, liked_score, max_score_category, max_liked_score)
    else:
        # 使用规则判断当前选择行为
        print(prev_score, score, prev_category, category, liked_score, max_score_category, max_liked_score)
        new_behaviors = get_choice_behavior(prev_score, score, prev_category, category, liked_score, max_score_category, max_liked_score)
        behaviors.extend(new_behaviors)

        # 更新上一轮的得分、类别信息
        prev_score = score
        prev_category = category
        max_score_category = max_category
    
    # 累计最终得分
    total_score += score

# 记录最终的用户选择行为和得分
user_behavior = {user_id: [behaviors, total_score]}

# 输出用户1的行为
print(user_behavior)

# for user_id, rounds in test_data.items():
#     behaviors = []
#     total_score = 0

#     # 获取当前用户的所有项的 liked_score (来自 player_data)
#     player_likescore = {item: score for item, _, _, score in player_data[user_id]}

#     # 初始状态
#     prev_score = None
#     prev_category = None
#     max_score_category = None

#     # 遍历每个用户的40轮选择数据
#     for i, row in enumerate(rounds):
#         # 获取当前轮次数据
#         itemname = row['item']
#         score = row['score']
#         liked_score = row['liked_score']
#         category = row['category']
        
#         # 获取payoff_df中当前类别的得分
#         max_category = get_max_category_for_round(i)
        
#         # 获取当前用户所有 items 的最大 liked_score
#         max_liked_score = max(player_likescore.values())

#         if i == 0:
#             # 初始状态，选择是纯粹的 likeability-driven
#             behaviors.append('L')
#             prev_score = score
#             prev_category = category
#             max_score_category = max_category
#             continue
        
#         else:
#             # 使用规则判断当前选择行为
#             new_behaviors = get_choice_behavior(prev_score, score, prev_category, category, liked_score, max_score_category, max_liked_score)
#             behaviors.extend(new_behaviors)

#             # 更新上一轮的得分、类别信息
#             prev_score = score
#             prev_category = category
#             max_score_category = max_category
        
#         # 累计最终得分
#         # 在累加分数之前，检查 score 是否为 None
#         if score is not None:
#             total_score += score
#         else:
#             total_score += 0  # 如果 score 是 None，默认为 0


#     # 记录最终的用户选择行为和得分
#     user_behavior[user_id] = [behaviors, total_score]

# # 输出所有用户的行为
# print(user_behavior)