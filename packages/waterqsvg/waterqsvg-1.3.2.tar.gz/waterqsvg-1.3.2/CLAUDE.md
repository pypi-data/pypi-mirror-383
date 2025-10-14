# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

WaterQSVG 是一个专用于从水质监测数据生成SVG热力图的独立Python库。支持从OSS ZIP文件下载、解析INDEXS.CSV+POS.TXT格式数据、使用Kriging插值算法生成平滑热力图，并输出精确的地理边界信息用于地图叠加。

**核心特性**：
- OSS直连下载 + ZIP自动解压
- 多种插值算法：Universal Kriging（默认）、Ordinary Kriging、Alpha Shape边界检测
- KML边界支持：可使用KML文件定义插值区域
- SVG矢量输出：透明背景，适合地图叠加
- 批量处理：自动识别并处理所有可用指标

## 常用开发命令

### 安装依赖
```bash
# 使用uv安装依赖（推荐）
uv sync

# 或使用pip
pip install -e .
```

### 运行测试
```bash
# 运行所有测试
uv run python -m pytest tests/ -v

# 运行特定测试
uv run python tests/test_kriging_migration.py
uv run python tests/test_kml_integration.py
```

### 命令行使用
```bash
# 基本用法（通过pip安装后可用waterqsvg命令）
waterqsvg --zip-url "https://example.com/data.zip"

# 开发模式（使用interface.py）
uv run python interface.py --zip-url "https://example.com/data.zip"

# 使用JSON配置文件（支持file_url + kml_boundary_url）
uv run python interface.py --zip-url "/path/to/config.json"

# 指定插值方法和边界检测
uv run python interface.py --zip-url "..." \
  --interpolation-method universal_kriging \
  --boundary-method alpha_shape

# 使用KML边界文件
uv run python interface.py --zip-url "..." \
  --boundary-method kml \
  --kml-boundary "/path/to/boundary.kml"

# Windows用户处理URL中的&符号
echo "https://example.com/data.zip" | uv run python interface.py
```

### JSON配置文件格式
```json
{
  "file_url": "https://example.com/water_quality_data.zip",
  "kml_boundary_url": "https://example.com/boundary.kml",
  "visualization_mode": "quantitative",
  "description": "数据描述（可选）"
}
```

**可选字段说明**：
- `visualization_mode`: Colorbar显示模式
  - `quantitative`（默认）: 显示具体数值刻度
  - `qualitative`: 显示"低"和"高"标签

## 核心架构

### 数据处理流程
整个处理流程由 `WaterQualityProcessor` 类（`src/waterqsvg/unified_interface.py`）协调：

1. **下载** (`core/downloader.py`): 从HTTP/OSS下载ZIP文件
2. **解压** (`core/extractor.py`): 安全解压ZIP文件
3. **解析** (`data/parser.py`): 解析INDEXS.CSV + POS.TXT格式
4. **标准化** (`data/standardizer.py`): 统一坐标和指标名称
5. **验证** (`data/validator.py`): 数据质量检查
6. **插值** (`interpolation/`): 使用Kriging算法生成网格数据
7. **生成SVG** (`visualization/svg_generator.py`): 输出矢量图

### 插值算法模块 (`waterqsvg/interpolation/`)

**Kriging插值** (`kriging_interpolation.py`):
- 从AutoReportV3完整迁移的Universal Kriging和Ordinary Kriging算法
- 支持3种变差函数模型：Gaussian（默认）、Spherical、Exponential
- 自动处理负数/零值：对数变换（log）或截断（clip）
- 配置系统：`KRIGING_CONFIG` 字典定义所有参数

**边界检测算法**:
- `alpha_shape.py`: 高精度Alpha Shape边界检测（使用scipy.spatial.Delaunay）
- `convex_hull.py`: 快速凸包边界计算
- `density_boundary.py`: 基于点密度的边界检测
- `kml_boundary.py`: KML文件解析和区域提取（支持Polygon/LineString）

**增强插值** (`enhanced_interpolation.py`):
- 集成边界检测 + 插值的统一接口
- 自动选择和切换插值方法
- 支持KML边界约束

### 主要入口点

**WaterQualityProcessor类** (`waterqsvg/unified_interface.py`):
```python
# 核心方法
process_from_oss_zip(
    zip_url: str,
    colormap: str = "jet",
    boundary_method: str = "alpha_shape",  # alpha_shape | convex_hull | density_based | kml
    interpolation_method: str = "ordinary_kriging_spherical",  # universal_kriging | ordinary_kriging_*
    kml_boundary_path: Optional[str] = None,
) -> Dict[str, Any]
```

**关键参数说明**:
- `interpolation_method`: 插值算法选择
  - `universal_kriging`: 泛克里金（高斯模型，支持趋势建模）
  - `ordinary_kriging_spherical`: 普通克里金-球形模型（类似ArcGIS）
  - `ordinary_kriging_exponential`: 普通克里金-指数模型（快速衰减）
- `boundary_method`: 边界检测方法
  - `alpha_shape`: Alpha Shape（高精度）
  - `convex_hull`: 凸包（快速）
  - `density_based`: 密度边界
  - `kml`: KML文件边界
- `grid_resolution`: 网格分辨率（默认300，与AutoReportV3一致）
- `colormap`: 颜色映射（jet | water_quality | viridis | RdYlBu_r）

### 数据格式要求

**输入ZIP结构**:
```
data.zip
├── INDEXS.csv  # 水质指标数据（列：number, CHLa, Turbidity, COD, ...）
└── POS.txt     # GPS坐标（格式：/path/file.csv latitude: XX longitude: YY）
```

**输出文件**:
- `{indicator}_heatmap.svg`: SVG热力图（透明背景）
- `{indicator}_colorbar.png`: 独立Colorbar图片（定量/定性模式）
- `{indicator}_bounds.json`: 地理边界信息（经纬度坐标）

**边界信息JSON格式**:
```json
{
  "geographic_bounds": {
    "min_longitude": 120.264922,
    "max_longitude": 120.267936,
    "min_latitude": 31.515932,
    "max_latitude": 31.520750,
    "center_longitude": 120.266429,
    "center_latitude": 31.518341
  },
  "grid_info": {
    "grid_resolution": 300,
    "valid_pixels": 83583
  }
}
```

## 支持的水质指标

项目支持15+种水质指标，通过 `waterqsvg/config/indicators.py` 配置。主要指标包括：

| 指标代码 | 中文名称 | 英文名称 | 单位 |
|---------|---------|----------|------|
| cod | 化学需氧量 | Chemical Oxygen Demand | mg/L |
| nh3n | 氨氮 | Ammonia Nitrogen | mg/L |
| tp | 总磷 | Total Phosphorus | mg/L |
| tn | 总氮 | Total Nitrogen | mg/L |
| chla | 叶绿素a | Chlorophyll-a | μg/L |
| do | 溶解氧 | Dissolved Oxygen | mg/L |

系统会自动识别未知指标并使用通用配置处理。

## 环境变量配置

可通过 `.env` 文件或环境变量配置：

```bash
# 阿里云OSS配置（可选）
OSS_ACCESS_KEY_ID=your_key_id
OSS_ACCESS_KEY_SECRET=your_secret
OSS_ENDPOINT=oss-cn-shanghai.aliyuncs.com

# 插值配置（可选）
INTERPOLATION_RESOLUTION=300
DEFAULT_COLORMAP=jet
```

## 开发注意事项

1. **使用uv运行Python命令是推荐方式** - 确保依赖隔离
2. **项目使用中文注释** - 保持与原AutoReportV3项目一致的风格
3. **所有核心算法都有详细的数学原理注释** - 特别是Kriging插值模块
4. **错误处理机制完善** - 提供详细的错误信息和日志
5. **Kriging插值配置** - 修改 `kriging_interpolation.py` 中的 `GLOBAL_KRIGING_METHOD` 可切换默认插值方法
6. **KML边界检测** - 当JSON配置中提供 `kml_boundary_url` 时，系统会自动下载并启用KML边界

## 代码风格

- 遵循PEP 8规范
- 使用类型注解（Python 3.11+）
- 使用Google风格的docstring
- 推荐使用black格式化代码
