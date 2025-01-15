import pandas as pd
import random


def balanced_grouping_with_teachers(participants_file, num_groups):
    # 读取参与人员表
    participants_df = pd.read_excel(participants_file)
    students = participants_df['Student'].dropna().tolist()  # 学生列
    teachers = participants_df['Teacher'].dropna().tolist()  # 老师列

    # 打乱学生和老师的顺序
    random.shuffle(students)
    random.shuffle(teachers)

    # 初始化分组
    groups = [[] for _ in range(num_groups)]

    # 分配老师
    for i, teacher in enumerate(teachers):
        group_index = i % num_groups  # 确保老师均匀分布
        groups[group_index].append(teacher)

    # 计算每组的目标人数
    total_participants = len(students) + len(teachers)
    target_per_group = total_participants // num_groups
    remainder = total_participants % num_groups

    # 分配学生
    student_index = 0
    for group in groups:
        # 计算当前组还需要多少人
        needed = target_per_group - len(group)
        if remainder > 0:
            needed += 1
            remainder -= 1
        # 添加学生
        group.extend(students[student_index:student_index + needed])
        student_index += needed

    # 输出分组结果
    for i, group in enumerate(groups):
        print(f"Group {i + 1} ({len(group)}人): {', '.join(group)}")

    return groups


# 示例调用
participants_file = 'participants.xlsx'
num_groups = 9
balanced_grouping_with_teachers(participants_file, num_groups)