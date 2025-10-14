# parq-cli

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个强大的 Apache Parquet 文件命令行工具 🚀

## ✨ 特性

- 📊 **元数据查看**: 快速查看 Parquet 文件的元数据信息
- 📋 **Schema 展示**: 美观地展示文件的列结构和数据类型
- 👀 **数据预览**: 支持查看文件的前 N 行或后 N 行
- 🔢 **行数统计**: 快速获取文件的总行数
- 🎨 **美观输出**: 使用 Rich 库提供彩色、格式化的终端输出

## 📦 安装

### 从源码安装

```bash
git clone https://github.com/yourusername/parq-cli.git
cd parq-cli
pip install -e .
```

### 使用 pip 安装（即将支持）

```bash
pip install parq-cli
```

## 🚀 快速开始

### 基本用法

```bash
# 查看文件元数据
parq data.parquet

# 显示 schema 信息
parq data.parquet --schema

# 显示前 10 行
parq data.parquet --head 10

# 显示后 5 行
parq data.parquet --tail 5

# 显示总行数
parq data.parquet --count
```

### 组合使用

```bash
# 同时显示 schema 和行数
parq data.parquet --schema --count

# 显示前 5 行和 schema
parq data.parquet --head 5 --schema
```

## 📖 命令参考

### 主命令

```
parq [OPTIONS] FILE
```

**参数:**
- `FILE`: Parquet 文件路径（必需）

**选项:**
- `--schema, -s`: 显示 schema 信息
- `--head N`: 显示前 N 行
- `--tail N`: 显示后 N 行
- `--count, -c`: 显示总行数
- `--help`: 显示帮助信息

### 版本信息

```bash
parq version
```

## 🎨 输出示例

### 元数据展示

```
╭─────────────────────── 📊 Parquet File Metadata ───────────────────────╮
│ file_path: /path/to/data.parquet                                       │
│ num_rows: 1000                                                         │
│ num_columns: 5                                                         │
│ num_row_groups: 1                                                      │
│ format_version: 2.6                                                    │
│ serialized_size: 2048                                                  │
│ created_by: parquet-cpp-arrow version 18.0.0                          │
╰────────────────────────────────────────────────────────────────────────╯
```

### Schema 展示

```
                    📋 Schema Information
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Column Name ┃ Data Type     ┃ Nullable ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ id          │ int64         │ ✗        │
│ name        │ string        │ ✓        │
│ age         │ int64         │ ✓        │
│ city        │ string        │ ✓        │
│ salary      │ double        │ ✓        │
└─────────────┴───────────────┴──────────┘
```

## 🛠️ 技术栈

- **[PyArrow](https://arrow.apache.org/docs/python/)**: 高性能的 Parquet 读取引擎
- **[Typer](https://typer.tiangolo.com/)**: 现代化的 CLI 框架
- **[Rich](https://rich.readthedocs.io/)**: 美观的终端输出

## 🧪 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 运行测试（带覆盖率）

```bash
pytest --cov=parq --cov-report=html
```

### 代码格式化

```bash
# 使用 Black
black parq tests

# 使用 Ruff 检查
ruff check parq tests
```

## 🗺️ 路线图

- [x] 基础元数据查看
- [x] Schema 展示
- [x] 数据预览（head/tail）
- [x] 行数统计
- [ ] SQL 查询支持
- [ ] 数据统计分析
- [ ] 格式转换（CSV, JSON, Excel）
- [ ] 文件对比
- [ ] 云存储支持（S3, GCS, Azure）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 灵感来源于 [parquet-cli](https://github.com/chhantyal/parquet-cli)
- 感谢 Apache Arrow 团队提供强大的 Parquet 支持
- 感谢 Rich 库为终端输出增添色彩

## 📮 联系方式

- 作者: Jinfeng Sun
- 项目地址: https://github.com/Tendo33/parq-cli

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
