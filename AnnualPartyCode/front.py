import streamlit as st
import pandas as pd
import random
import os
import time

# 页面标题
st.set_page_config(page_title="实验室年会工具", page_icon="🎉", layout="wide")
st.title("🎉 实验室年会工具")

# 侧边栏
st.sidebar.header("功能选择")
option = st.sidebar.radio("请选择功能", ["随机分组", "抽奖"])

# 随机分组功能
if option == "随机分组":
    st.header("随机分组")
    st.write("上传参与人员名单文件（Excel），并设置分组数量。")
    # 上传文件
    uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx"])
    if uploaded_file is not None:
        participants_df = pd.read_excel(uploaded_file)
        st.write("参与人员名单：")

        students = participants_df['Student'].dropna().tolist()  # 学生列，去除空值
        teachers = participants_df['Teacher'].dropna().tolist()  # 老师列，去除空值

        excluded_students = {'蓝源泓', '余欣然'}
        students = list(set(students) - excluded_students)
        max_length = max(len(students), len(teachers))
        students += [None] * (max_length - len(students))  # 填充空值
        teachers += [None] * (max_length - len(teachers))  # 填充空值

        participants_df_display = pd.DataFrame({
            '学生': sorted(students),
            '教师': teachers
        })
        styled_df = participants_df_display.style \
            .set_properties(**{
            'background-color': '#f7f7f7',  # 表格背景色
            'color': '#333333',  # 文字颜色
            'border': '1px solid #cccccc',  # 边框
            'text-align': 'center'  # 文字居中
        }) \
            .set_table_styles([{
            'selector': 'th',  # 表头样式
            'props': [('background-color', '#4CAF50'), ('color', 'white')]
        }])

        # 显示表格
        st.dataframe(styled_df, height=400, use_container_width=True)  # 自适应宽度

        # 输入分组数量
        num_groups = st.number_input("分组数量", min_value=1, value=4, step=1)

        if st.button("开始分组"):
            with st.spinner("正在分组，请稍候..."):
                students = participants_df['Student'].dropna().tolist()  # 学生列，去除空值
                teachers = participants_df['Teacher'].dropna().tolist()  # 老师列，去除空值
                time.sleep(2)  # 模拟加载过程
                # 打乱顺序
                random.shuffle(students)
                random.shuffle(teachers)

                # 初始化分组
                groups = [[] for _ in range(num_groups)]

                # 分配老师
                for i, teacher in enumerate(teachers):
                    group_index = i % num_groups
                    groups[group_index].append(teacher)

                # 分配学生
                student_index = 0
                for group in groups:
                    needed = len(students) // num_groups
                    group.extend(students[student_index:student_index + needed])
                    student_index += needed

                # 显示分组结果
                st.success("分组完成！")
                st.balloons()  # 增加气球动画
                for i, group in enumerate(groups):
                    st.write(f"**Group {i + 1}** ({len(group)}人): {', '.join(group)}")

# 抽奖功能
elif option == "抽奖":
    st.header("抽奖")
    st.write("上传参与人员名单文件（Excel），并选择奖品等级。")

    # 上传文件
    uploaded_file = st.file_uploader("上传 Excel 文件", type=["xlsx"])
    if uploaded_file is not None:
        participants_df = pd.read_excel(uploaded_file)
        # 提取老师和学生
        teachers = participants_df['Teacher'].dropna().tolist()  # 老师列，去除空值
        students = participants_df['Student'].dropna().tolist()  # 学生列，去除空值

        # 学生按字典序排序
        students_sorted = sorted(students)

        # 合并老师和学生
        all_participants = teachers + students_sorted

        # 将数据转换为 DataFrame
        participants_df_display = pd.DataFrame({
            '参与人员': all_participants
        })

        st.write("参与人员名单：")

        # 添加样式
        styled_df = participants_df_display.style \
            .set_properties(**{
            'background-color': '#f7f7f7',  # 表格背景色
            'color': '#333333',  # 文字颜色
            'border': '1px solid #cccccc',  # 边框
            'text-align': 'center'  # 文字居中
        }) \
            .set_table_styles([{
            'selector': 'th',  # 表头样式
            'props': [('background-color', '#4CAF50'), ('color', 'white')]
        }])

        # 显示表格
        st.dataframe(styled_df, height=400, use_container_width=True)  # 自适应宽度

        # 选择奖品等级
        prize_level = st.selectbox("选择奖品等级", ["一等奖", "二等奖", "三等奖"])
        prize_class = {"一等奖": ["CHERRY 机械键盘", "智能电动牙刷"], "二等奖": ["四口140W快充", "飞利浦筋膜枪"], "三等奖": ["美的加湿器", "罗技静音鼠标", "思莱宜坐垫"]}
        prize_set = prize_class[prize_level]
        prize_name = st.selectbox("选择奖品", prize_set)
        prize_num = st.number_input("奖品数量", min_value=1, value=1, step=1)

        if st.button("开始抽奖"):
            with st.spinner("正在抽奖，请稍候..."):
                time.sleep(2)  # 模拟加载过程
                students = participants_df['Student'].dropna().tolist()
                teachers = participants_df['Teacher'].dropna().tolist()
                participants = students + teachers

                # 检查中奖记录文件
                winners_file = "winners.xlsx"
                if os.path.exists(winners_file):
                    winners_df = pd.read_excel(winners_file)
                    winners = winners_df['姓名'].tolist()
                    prizes = winners_df['奖品等级'].tolist()
                    prize_names = winners_df['奖品名称'].tolist()
                else:
                    winners = []
                    prizes = []
                    prize_names = []

                # 从未中奖的人员中抽取
                remaining_participants = list(set(participants) - set(winners))
                if not remaining_participants:
                    st.error("没有更多参与者可以抽奖！")
                else:
                    # 根据奖品等级设置抽奖数量
                    if prize_level == "一等奖":
                        remaining_participants = [p for p in remaining_participants if p not in winners or prizes[winners.index(p)]!= "一等奖"]
                    elif prize_level == "二等奖":
                        remaining_participants = [p for p in remaining_participants if p not in winners or prizes[winners.index(p)] != "二等奖"]
                    elif prize_level == "三等奖":
                        remaining_participants = [p for p in remaining_participants if p not in winners or prizes[winners.index(p)] != "三等奖"]
                    # 抽奖
                    num_winners = min(prize_num, len(remaining_participants))
                    new_winners = random.sample(remaining_participants, min(num_winners, len(remaining_participants)))

                    # 模拟抽奖过程
                    st.write("抽奖中...")
                    for i in range(3, 0, -1):  # 倒计时 3、2、1
                        st.write(f"🎉 倒计时: {i} 🎉")
                        time.sleep(1)  # 每秒显示一次

                    # 模拟名单滚动效果
                    placeholder = st.empty()  # 创建一个占位符
                    for _ in range(20):  # 滚动 20 次
                        random_name = random.choice(remaining_participants)
                        placeholder.write(f"**{random_name}**")
                        time.sleep(0.1)  # 控制滚动速度
                    placeholder.empty()  # 清空占位符

                    for i, winner in enumerate(new_winners):
                        placeholder = st.empty()
                        for _ in range(20):  # 滚动 20 次
                            random_name = random.choice(remaining_participants)
                            placeholder.write(f"**{random_name}**")
                            time.sleep(0.1)  # 控制滚动速度
                        placeholder.empty()  # 清空占位符
                        st.write(f"🎉 **{prize_level} 第 {i + 1} 位中奖者**: {winner} 🎉")
                    # 逐个显示中奖者
                    st.success("抽奖完成！")
                    st.balloons()  # 增加气球动画
                    # 保存中奖记录
                    winners.extend(new_winners)
                    prizes.extend([prize_level] * len(new_winners))
                    prize_names.extend([prize_name] * len(new_winners))
                    winners_df = pd.DataFrame({"姓名": winners, "奖品等级": prizes, "奖品名称": prize_names})
                    winners_df.to_excel(winners_file, index=False)

                    st.header("中奖人员名单")
                    if os.path.exists("winners.xlsx"):
                        winners_df = pd.read_excel("winners.xlsx")
                        st.write("中奖记录：")
                        st.dataframe(winners_df.style \
                            .set_properties(**{
                            'background-color': '#f7f7f7',  # 表格背景色
                            'color': '#333333',  # 文字颜色
                            'border': '1px solid #cccccc',  # 边框
                            'text-align': 'center'  # 文字居中
                        }) \
                            .set_table_styles([{
                            'selector': 'th',  # 表头样式
                            'props': [('background-color', '#4CAF50'), ('color', 'white')]
                        }]), height=400, use_container_width=True)
                    # 显示中奖名单