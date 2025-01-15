import pandas as pd
import random
import os

def lottery_draw(participants_file, prize_level, winners_file='winners.xlsx'):
    """
    抽奖函数
    :param participants_file: 参与人员名单文件路径
    :param prize_level: 奖品等级（一等奖、二等奖、三等奖）
    :param winners_file: 中奖记录文件路径
    """
    # 读取参与人员名单
    participants_df = pd.read_excel(participants_file)
    students = participants_df['Student'].dropna().tolist()  # 学生列
    teachers = participants_df['Teacher'].dropna().tolist()  # 老师列

    # 合并学生和老师为一个整体名单
    participants = students + teachers

    # 检查是否有中奖记录文件
    if os.path.exists(winners_file):
        winners_df = pd.read_excel(winners_file)
        winners = winners_df['Name'].tolist()
        prizes = winners_df['Prize'].tolist()
    else:
        winners = []
        prizes = []

    # 从未中奖的人员中抽取
    remaining_participants = list(set(participants) - set(winners))
    if not remaining_participants:
        print("没有更多参与者可以抽奖！")
        return

    # 根据奖品等级设置抽奖数量
    if prize_level == '一等奖':
        num_winners = 1
    elif prize_level == '二等奖':
        num_winners = 3
    elif prize_level == '三等奖':
        num_winners = 5
    else:
        print("无效的奖品等级！")
        return

    # 抽奖
    new_winners = random.sample(remaining_participants, min(num_winners, len(remaining_participants)))
    winners.extend(new_winners)
    prizes.extend([prize_level] * len(new_winners))  # 记录奖项信息

    # 输出抽奖结果
    print(f"{prize_level}中奖者：{', '.join(new_winners)}")

    # 保存中奖记录（包括奖项信息）
    winners_df = pd.DataFrame({'Name': winners, 'Prize': prizes})
    winners_df.to_excel(winners_file, index=False)

# 示例调用
participants_file = 'participants.xlsx'  # 参与人员名单文件
prize_level = '一等奖'  # 抽奖等级（可选：一等奖、二等奖、三等奖）
lottery_draw(participants_file, prize_level)