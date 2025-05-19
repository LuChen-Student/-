import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
# 指定包含 Parquet 文件的目录路径
directory = 'C:/Users/12585/Desktop/1G_data/'

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
# Build transactions (list of category lists by order)
order_cats = combined_df.groupby('order_id')['category'].apply(lambda cats: list(set(cats)))
# Compute support counts for single categories
from collections import Counter
support1 = Counter(cat for cats in order_cats for cat in cats)

# Find frequent pairs (support >=0.02 threshold)
min_sup = 0.02 * len(order_cats)
pair_counts = Counter()
for cats in order_cats:
    for a, b in order_cats(sorted(cats), 2):
        pair_counts[(a,b)] += 1

# Filter rules by support and confidence
rules = []
for (a,b), count in pair_counts.items():
    support = count/len(order_cats)
    if support >= 0.02:
        conf_a_to_b = count/support1[a]
        conf_b_to_a = count/support1[b]
        if conf_a_to_b >= 0.5:
            lift = conf_a_to_b / (support1[b]/len(order_cats))
            rules.append((a, "=>", b, support, conf_a_to_b, lift))
        if conf_b_to_a >= 0.5:
            lift = conf_b_to_a / (support1[a]/len(order_cats))
            rules.append((b, "=>", a, support, conf_b_to_a, lift))

high_val_orders = set(combined_df[combined_df['price'] > 5000]['order_id'])
hv_items = combined_df[combined_df['order_id'].isin(high_val_orders)]
# Build baskets of categories + payment method
hv_baskets = []
for oid, grp in hv_items.groupby('order_id'):
    cats = set(grp['category'])
    pm = grp['payment_method'].iloc[0]
    hv_baskets.append(cats.union({pm}))

# Count occurrences and filter for support >=0.01
from collections import Counter
item_count = Counter(it for basket in hv_baskets for it in basket)
pairs = Counter()
for basket in hv_baskets:
    for a, b in order_cats(sorted(basket), 2):
        pairs[(a,b)] += 1

min_sup = 0.01 * len(order_cats)  # 0.01 of all orders
rules_pm = []
for (a,b), count in pairs.items():
    support = count/len(order_cats)
    if support >= min_sup:
        # check only rules mixing payment and category
        if a in order_cats and b not in order_cats:
            conf = count/item_count[a]
            if conf >= 0.6:
                rules_pm.append((a, "=>", b, support, conf))
        if b in order_cats and a not in order_cats:
            conf = count/item_count[b]
            if conf >= 0.6:
                rules_pm.append((b, "=>", a, support, conf))

# Time series aggregation (example: by month and weekday)
combined_df['purchase_date'] = pd.to_datetime(combined_df['purchase_date'])
by_month = combined_df.groupby(combined_df['purchase_date'].dt.month).size()
by_weekday = combined_df.groupby(combined_df['purchase_date'].dt.weekday).size()
print("Monthly sales counts:", by_month.to_dict())
print("Weekday sales counts:", by_weekday.to_dict())

# Sequential pattern example: count A->B across users
user_seq = combined_df.sort_values(['user_id','purchase_date'])
seq_counts = Counter()
for user, grp in user_seq.groupby('user_id'):
    seen = []
    for cat in grp['category']:
        for prev in seen:
            seq_counts[(prev, cat)] += 1
        seen.append(cat)
top_seq = sorted(seq_counts.items(), key=lambda x: -x[1])[:5]
print("Top sequential patterns (count):", top_seq)

# Refund-pattern rule mining (categories among refunded orders)
refund_orders = set(combined_df[combined_df['payment_status'].isin(['已退款','部分退款'])]['order_id'])
refund_baskets = [set(grp['category']) for oid, grp in combined_df[combined_df['order_id'].isin(refund_orders)].groupby('order_id')]
ref_counts = Counter(it for basket in refund_baskets for it in basket)
pair_counts = Counter()
for basket in refund_baskets:
    for a,b in order_cats(sorted(basket), 2):
        pair_counts[(a,b)] += 1
# Find rules with support>=0.005 and confidence>=0.4
rules_ref = []
for (a,b), count in pair_counts.items():
    supp = count/len(refund_baskets)
    conf_ab = count/ref_counts[a]
    conf_ba = count/ref_counts[b]
    if supp >= 0.005:
        if conf_ab >= 0.4:
            lift = conf_ab / (ref_counts[b]/len(refund_baskets))
            rules_ref.append((a, "=>", b, supp, conf_ab, lift))
        if conf_ba >= 0.4:
            lift = conf_ba / (ref_counts[a]/len(refund_baskets))
            rules_ref.append((b, "=>", a, supp, conf_ba, lift))
print("Refund-rules:", rules_ref)
# #收入与信用散点图
# plt.figure(figsize=(10, 6))
# sns.scatterplot(x=df['income'], y=df['credit_score'])
# plt.title('收入与信用评分的关系')
# plt.xlabel('收入')
# plt.ylabel('信用评分')
# plt.show()
#
# #性别比例图
# gender_counts = df['gender'].value_counts()
# plt.figure(figsize=(8, 8))
# plt.pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', startangle=140)
# plt.title('性别比例')
# plt.show()
#
#
# # 按性别和年龄段分析用户数量
# df['age_group'] = pd.cut(df['age'], bins=[18, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])
#
# plt.figure(figsize=(12, 6))
# sns.countplot(x='age_group', hue='gender', data=df)
# plt.title('不同年龄段和性别的用户数量')
# plt.xlabel('年龄段')
# plt.ylabel('用户数量')
# plt.show()
