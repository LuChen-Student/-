import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
# 指定包含 Parquet 文件的目录路径
directory = 'D:/30G_data/'

# 初始化一个空的 DataFrame 用于存储合并的数据
df_list = []

# 遍历目录中的所有文件
for filename in os.listdir(directory):
    if filename.endswith('.parquet'):
        file_path = os.path.join(directory, filename)
        df = pd.read_parquet(file_path)
        df_list.append(df)

# 合并所有 DataFrame
combined_df = pd.concat(df_list, ignore_index=True)
# print(combined_df)

# print(combined_df.columns)

#缺失值检测
# missing_values = combined_df.isnull().sum()
# print("缺失值统计：\n", missing_values)
# 重复值检测
# duplicate_rows = combined_df.duplicated().sum()
# print(f"重复行数：{duplicate_rows}")
# 数据一致性检查
# unique_values = combined_df['your_categorical_column'].unique()
# print("类别变量的唯一值：", unique_values)
# 处理缺失值
# combined_df_cleaned = combined_df.dropna()
# #删除重复行
# combined_df_no_duplicates = combined_df.drop_duplicates()
#年纪分布直方图
plt.figure(figsize=(10, 6))
sns.histplot(df['age'], bins=100, kde=True)
plt.title('年龄分布直方图')
plt.xlabel('年龄')
plt.ylabel('频数')
plt.show()

#收入与信用散点图
plt.figure(figsize=(10, 6))
sns.scatterplot(x=df['income'], y=df['credit_score'])
plt.title('收入与信用评分的关系')
plt.xlabel('收入')
plt.ylabel('信用评分')
plt.show()

#性别比例图
gender_counts = df['gender'].value_counts()
plt.figure(figsize=(8, 8))
plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140)
plt.title('性别比例')
plt.show()


# 按性别和年龄段分析用户数量
df['age_group'] = pd.cut(df['age'], bins=[18, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])

plt.figure(figsize=(12, 6))
sns.countplot(x='age_group', hue='gender', data=df)
plt.title('不同年龄段和性别的用户数量')
plt.xlabel('年龄段')
plt.ylabel('用户数量')
plt.show()
