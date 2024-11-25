import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 创建示例数据
data = {
    'Time': ['2024-11-10', '2024-11-11', '2024-11-12', '2024-11-13', '2024-11-14', '2024-11-15', '2024-11-16', '2024-11-17', '2024-11-18', '2024-11-19', '2024-11-20', '2024-11-21'],
    'Alice': np.random.rand(12),
    'Bob': np.random.rand(12),
    'Charlie': np.random.rand(12),
    'David': np.random.rand(12),
    'David1': np.random.rand(12),
    'David2': np.random.rand(12),
    'David3': np.random.rand(12),
    'David4': np.random.rand(12),
    'David5': np.random.rand(12),
    'David25': np.random.rand(12),
    'David12': np.random.rand(12),
    'David22': np.random.rand(12),
    'David32': np.random.rand(12),
    'David42': np.random.rand(12),
    'David52': np.random.rand(12),
    'Eve': np.random.rand(12)
}

# 转换为DataFrame格式并设置索引
df = pd.DataFrame(data)
df.set_index('Time', inplace=True)

# 转置DataFrame以便y轴为名字，x轴为时间
df = df.T

# 绘制热力图
plt.figure(figsize=(10, 6))
sns.heatmap(df, annot=True, cmap="YlGnBu", cbar=True)
plt.yticks(rotation=0)
plt.xticks(rotation=45)
# 设置轴标签
# plt.xlabel("Time")
# plt.ylabel("Names")
plt.title("Heatmap of Names over Time")

# 显示图像
plt.show()