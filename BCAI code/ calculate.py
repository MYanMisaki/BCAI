import pandas as pd
import numpy as np

# ================================================================
# 1. 读取你上传的完整数据
# ================================================================
df = pd.read_excel("./all_data.xlsx")

# 列出全部 item（根据你之前的 mapping）
item_list = [
    'Purple','Blue','Green','Red','Orange',
    'Risk','Hope','Safety','Vitality','Power',
    'Literature','Physics','Music','History',
    'Geography','Sea','Desert','City','Mountain','Village'
]

# ================================================================
# 2. 为输出新增变量创建空间
# ================================================================
for item in item_list:
    df[f"EV_{item}"] = np.nan
    df[f"Var_{item}"] = np.nan
    df[f"RPE_{item}"] = np.nan

df["Regret"] = np.nan
df["Disappointment"] = np.nan
df["Uncertainty"] = np.nan

# ================================================================
# 3. 参数（可修改，可拟合）
# ================================================================
eta = 0.3       # EV 学习率
eta_v = 0.2     # 方差学习率

# ================================================================
# 4. 对每个用户单独计算动态变量
# ================================================================
all_users = df["User"].unique()

for uid in all_users:
    user_df = df[df["User"] == uid].copy()

    # 初始化
    EV = {item: 0 for item in item_list}
    Var = {item: 1 for item in item_list}
    RPE_history = []

    for idx, row in user_df.iterrows():
        trial = row["Trial"]
        
        # 获取当前 trial 的 payoff（每个 item 都有 Payoff_xxx）
        payoff_dict = { item: row[f"Payoff_{item}"] for item in item_list }

        chosen_item = row["Choice_itemName"]

        # ---- (1) 更新 chosen item 的 EV, Var, RPE ----
        if chosen_item in item_list:

            reward = payoff_dict[chosen_item]
            old_EV = EV[chosen_item]

            # RPE
            RPE = reward - old_EV
            RPE_history.append(RPE)

            # EV update
            EV[chosen_item] = old_EV + eta * (reward - old_EV)

            # Var update
            Var[chosen_item] = Var[chosen_item] + eta_v * (reward - old_EV) ** 2

        else:
            RPE = np.nan

        # ---- (2) Regret: max payoff - chosen payoff ----
        all_rewards = list(payoff_dict.values())
        if chosen_item in item_list:
            regret = max(all_rewards) - payoff_dict[chosen_item]
        else:
            regret = np.nan

        # ---- (3) Disappointment: 当前 RPE - 历史平均 RPE ----
        if len(RPE_history) > 1 and not np.isnan(RPE):
            disc = RPE - np.nanmean(RPE_history[:-1])
        else:
            disc = np.nan

        # ---- (4) Uncertainty = 1 / (variance + 1) ----
        if chosen_item in item_list:
            uncertainty = 1 / (Var[chosen_item] + 1)
        else:
            uncertainty = np.nan

        # ---- 写回这一行 ----
        for item in item_list:
            df.loc[idx, f"EV_{item}"] = EV[item]
            df.loc[idx, f"Var_{item}"] = Var[item]
            df.loc[idx, f"RPE_{item}"] = RPE if item == chosen_item else np.nan

        df.loc[idx, "Regret"] = regret
        df.loc[idx, "Disappointment"] = disc
        df.loc[idx, "Uncertainty"] = uncertainty


# ================================================================
# 5. 导出含模型变量的新文件
# ================================================================
output_path = "./model_variables1.xlsx"
df.to_excel(output_path, index=False)

print("模型变量已计算并导出：", output_path)
