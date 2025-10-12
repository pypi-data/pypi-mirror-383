# AlphaLens Modify

<div align="right">
  🇨🇳 中文 | <a href="README.md">🇺🇸 English</a>
</div>

**作者：徐啸寅 (XiaoYinXu)**

AlphaLens Modify 是原始 AlphaLens 库的改进版本，针对现代 Python 环境更新了依赖项并修复了兼容性问题，专门用于股票因子分析。

## 📊 **分析结果展示**

*本项目提供全面的因子分析功能。以下是一些示例结果：*

*This project provides comprehensive factor analysis capabilities. Here are some example results:*

### 🔍 **信息系数 (IC) 分析**
![IC值分布](figures/IC_value_distribution.png)

信息系数衡量阿尔法因子的预测能力，显示因子值与未来收益之间的相关性。

### 📈 **累计收益分析**
![累计收益](figures/cumlative_return.png)

累计收益展示了基于因子的投资策略在较长时间段内的表现。

### 📊 **分组平均收益分析**
![分组平均收益](figures/group_mean_return.png)

分组分析显示了不同因子分位数的表现，帮助识别最有效的投资分段。

### 🔄 **因子换手率分析**
![换手率分析](figures/turnover.png)

换手率分析评估基于因子策略的稳定性和交易频率。

## 🚀 **快速开始**

```python
import alphalens_modify as al
import pandas as pd

# 加载因子数据和价格数据
factor_data = pd.read_csv('factor_data.csv')
price_data = pd.read_csv('price_data.csv')

# 获取清洁因子和远期收益
factor_returns = al.utils.get_clean_factor_and_forward_returns(
    factor_data, 
    price_data, 
    periods=[1, 5, 10]
)

# 创建综合分析报告
al.tears.create_summary_tear_sheet(factor_returns)
al.tears.create_returns_tear_sheet(factor_returns)
al.tears.create_information_tear_sheet(factor_returns)
```

## 📦 **安装方法**

### 通过 PyPI 安装
```bash
pip install alphalens-modify
```

### 从源码安装
```bash
git clone https://github.com/GenjiYin/alphalens-modify.git
cd alphalens-modify
pip install -e .
```

## 📋 **系统要求**

- Python >= 3.12
- pandas >= 1.0.0
- numpy >= 1.16.0
- empyrical >= 0.5.0
- scipy >= 1.0.0
- statsmodels >= 0.9.0
- matplotlib >= 3.0.0
- seaborn >= 0.9.0
- IPython >= 7.0.0

## 🎯 **核心功能**

- **因子绩效分析**：分析阿尔法因子的预测能力
- **信息系数计算**：计算和可视化IC指标
- **分位数分析**：按因子分位数进行绩效分析
- **分组分析**：基于行业或自定义分组分析
- **换手率分析**：评估因子稳定性和交易频率
- **事件研究**：分析特定事件周围的因子表现

## 📊 **完整分析流程**

本库提供完整的因子分析工作流程：

1. **数据准备**：清洁和准备因子及价格数据
2. **绩效指标**：计算IC、收益、换手率指标
3. **可视化**：生成综合图表和绘图
4. **报告生成**：创建详细的分析报表

## 💡 **主要特点**

- **现代化依赖**：针对最新Python版本优化
- **修复兼容性**：解决原版库的兼容性问题
- **完整示例**：包含详细的Jupyter notebook示例
- **结果展示**：内置分析结果图表展示
- **易于使用**：简洁的API设计

## 🔧 **使用示例**

参见包含的 Jupyter notebook `market_cap_factor_analys.ipynb`，了解使用市值因子进行完整分析的示例。

**注意：** 要运行 `market_cap_factor_analys.ipynb` 笔记本，您需要从 GitHub 仓库下载 `test_data` 文件夹：
1. 访问 [GitHub 仓库](https://github.com/GenjiYin/alphalens-modify)
2. 导航到 `test_data` 文件夹
3. 下载 `test_data` 文件夹中的所有文件
4. 将它们放在本地项目根目录的 `test_data` 目录中

该笔记本需要这些数据文件来演示因子分析功能。

## 📁 **项目结构**

```
alphalens_modify/
├── alphalens_modify/          # 核心库代码
│   ├── __init__.py
│   ├── performance.py         # 绩效分析模块
│   ├── plotting.py           # 绘图模块
│   ├── tears.py              # 报表生成模块
│   ├── utils.py              # 工具函数
│   └── test_data/            # 测试数据
├── figures/                   # 分析结果图表
├── examples/                  # 示例文件
└── README.md                  # 英文说明文档
```

## 🤝 **技术支持**

如果您遇到任何问题或有疑问，请在 [GitHub](https://github.com/GenjiYin/alphalens-modify/issues) 上提交问题。

## 📄 **开源协议**

本项目采用 Apache License 2.0 协议开源 - 详见 [LICENSE](LICENSE) 文件。

## 👤 **作者信息**

**徐啸寅 (XiaoYinXu)** - 965418170@qq.com

专业的量化金融分析师，专注于美股、港股、A股因子投资和绩效分析领域。

## 🙏 **致谢**

本项目基于 Quantopian 的原始 AlphaLens 库。感谢原始贡献者在因子分析框架方面的工作。特别感谢开源社区的支持和贡献。

## 📈 **应用场景**

本库适用于：
- 量化投资策略研究
- 因子有效性检验
- 投资组合绩效分析
- 学术论文研究支持
- 金融机构投研分析

---

**⭐ 如果您觉得本项目有用，请给个Star支持！**