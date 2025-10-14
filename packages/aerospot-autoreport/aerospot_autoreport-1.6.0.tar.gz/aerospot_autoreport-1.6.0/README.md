# AeroSpot AutoReport 项目

AeroSpot AutoReport 是一个用于处理航测数据并生成水质分析报告的工具。项目经过模块化重构，消除了重复定义，提升了可维护性和结构清晰度。各功能模块职责单一，便于扩展和维护。

## 系统要求

- **Python**: >= 3.10 (推荐 3.11)
- **操作系统**: Windows, Linux, macOS
- **内存**: 建议 4GB 以上
- **硬盘**: 建议 1GB 可用空间

### Python版本支持
- ✅ **Python 3.11** (推荐版本)
- ✅ **Python 3.10** (最低版本)
- ✅ **Python 3.12** (最新版本)

## 快速安装

### 用户安装 (推荐)
```bash
# 完整功能安装 (包含水印功能，自动适配平台)
pip install aerospot-autoreport
```

### 开发环境安装
```bash
# 开发环境 (完整功能 + 开发工具)
pip install aerospot-autoreport[dev]
```

### 从源码安装
```bash
git clone https://github.com/1034378361/AutoReportV2.git
cd AutoReportV2
pip install -e .
```

## 安装选项说明

### 两种安装方式
1. **用户安装**: 完整功能 + 智能平台适配
2. **`[dev]`**: 用户功能 + 开发工具(测试、代码质量)

### 智能平台适配
所有安装方式都使用条件依赖，自动根据操作系统安装合适的依赖：

| 平台 | pywin32安装 | Windows目录更新功能 |
|------|-------------|-------------------|
| **Windows** | ✅ 自动安装 | ✅ 完全支持 |
| **Linux** | ❌ 自动跳过 | ❌ 不支持 |
| **macOS** | ❌ 自动跳过 | ❌ 不支持 |

### 功能对比
| 功能 | 用户安装 | [dev] |
|------|----------|-------|
| 报告生成 | ✅ | ✅ |
| 数据处理 | ✅ | ✅ |
| 图表生成 | ✅ | ✅ |
| 水印功能 | ✅ | ✅ |
| Windows目录更新 | 🔄 | 🔄 |
| 开发工具 | ❌ | ✅ |

🔄 = 自动平台适配：Windows支持，Linux/macOS不支持

## 项目结构

项目主要包含以下模块：

```
AeroSpotReportV2/
├── config/               # 配置模块（常量、样式、公司信息等集中管理）
│   ├── __init__.py
│   ├── constants.py      # 常量定义
│   ├── styles.py         # 样式配置
│   ├── company_info.py   # 公司信息配置
│   └── defaults.py       # 默认配置
├── utils/                # 工具模块（通用工具函数，去重整合）
│   ├── __init__.py
│   ├── text.py           # 文本处理工具（如is_chinese、is_numeric等）
│   ├── font.py           # 字体处理工具
│   ├── io.py             # 输入输出工具
│   ├── geo.py            # 地理计算工具
│   └── path.py           # 路径处理工具
├── document/             # 文档生成模块（报告样式、段落、表格、图片、页面等）
│   ├── __init__.py
│   ├── styles.py         # 文档样式
│   ├── paragraphs.py     # 段落生成
│   ├── tables.py         # 表格生成
│   ├── images.py         # 图像处理
│   └── pages.py          # 页面生成
├── processor/            # 数据处理模块
│   ├── data/             # 数据处理子模块
│   │   ├── __init__.py
│   │   ├── processor.py  # 数据处理核心
│   │   ├── standardizer.py # 数据标准化
│   │   ├── analyzer.py   # 数据分析
│   │   ├── matcher.py    # 数据匹配
│   │   └── utils.py      # 数据处理工具
│   ├── config.py         # 配置处理
│   ├── downloader.py     # 数据下载
│   ├── extractor.py      # 数据提取
│   └── maps.py           # 卫星图像与可视化地图生成
├── main.py               # 主程序入口
├── generator.py          # 报告生成器
├── error_handler.py      # 错误处理
├── log_config.py         # 日志配置
└── resource_manager.py   # 资源管理
```

## 主要功能

1. **数据处理**：
   - 从压缩文件中提取航测数据
   - 标准化数据列名和指标名称
   - 计算基本统计信息
   - 数据匹配和分析
   - 卫星图像与指标数据可视化（见processor/maps.py）

2. **报告生成**：
   - 生成专业的Word格式报告
   - 包含统计表格、分布图和分析结果
   - 自定义报告样式和内容

3. **数据可视化**：
   - 生成指标分布图、插值热力图、水质等级分布图
   - 支持卫星底图与自定义地理边界

## 安装使用

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/1034378361/AeroSpotReportV2.git
   cd AeroSpotReportV2
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   创建`.env`文件并设置必要的环境变量。

4. 运行程序：
   ```bash
   python main.py
   ```

## 配置说明

项目支持通过配置文件和环境变量进行配置。主要配置项包括：

- 公司信息配置
- 报告样式配置
- 数据处理参数配置
- 输出路径配置

详细配置说明请参考 `config/` 目录下的相关文件。

## 数据处理与可视化模块

- 数据处理模块(`processor/data/`)是项目的核心，负责处理航测数据和实测数据，主要功能包括：
  - 数据标准化：统一列名和指标名称
  - 数据匹配：将航测数据与实测数据进行匹配
  - 数据分析：计算统计信息，分析数据特征
  - 误差分析：分析原始航测数据和重新反演数据与实测数据的误差
- 地图与可视化模块(`processor/maps.py`)支持基于卫星图像和指标数据生成分布图、插值热力图和水质等级分布图。

## 模块化重构说明

- 本项目已完成配置、工具函数、文档生成等模块的结构化重构，消除了重复定义，提升了可维护性。
- 主程序（如`main.py`、`generator.py`）的导入路径更新与全局适配正在规划中。
- 详细重构计划见 `refactoring_plan.md`。

## 注意事项

- 项目需要Python 3.10或更高版本
- 部分功能需要授权才能使用
- 请确保输入数据格式符合要求 