# PatentCheck-Desktop 用户指南

## 🎉 V0.9 完整版已就绪！

PatentCheck-Desktop 现已实现核心检测功能，可以对真实的专利文件进行自动检查。

---

## ✅ 已实现功能

### 1. ✅ **文件解析**
- 自动识别Word文档（说明书、权利要求书、摘要）
- 支持多种图片格式（JPG、PNG、TIF、BMP）
- 递归扫描文件夹

### 2. ✅ **Word文档结构检查**
- 检查5个必需章节：
  - 技术领域
  - 背景技术
  - 发明内容
  - 附图说明
  - 具体实施方式

### 3. ✅ **图片格式检查**
- 分辨率检测（要求≥200dpi）
- 彩色像素检测（应为黑白图）
- 自动计算彩色像素比例

### 4. ✅ **PDF报告生成**
- 专业的PDF格式报告
- 包含统计摘要和详细问题列表
- 带有法规参考和修改建议

### 5. ✅ **JSON报告导出**
- 结构化数据输出
- 便于二次处理和分析

---

## 🚀 快速开始

### 安装依赖

```bash
cd /Users/zhangyanlong/workspaces/PatentCheck-Desktop
pip install -r requirements.txt
```

### 基本用法

```bash
# 检测文件夹
python3 src/main_full.py test_data

# 指定输出路径
python3 src/main_full.py test_data --output my_report.pdf

# 仅生成JSON报告（不生成PDF）
python3 src/main_full.py test_data --no-pdf

# 查看帮助
python3 src/main_full.py --help
```

---

## 📋 使用示例

### 示例1：检测测试数据

项目自带测试数据，可以直接运行：

```bash
python3 src/main_full.py test_data
```

**输出示例：**
```
============================================================
PatentCheck-Desktop V0.9 完整版
专利自助预审工具
============================================================

📁 正在扫描文件...
   ✓ 找到说明书: test_data/说明书.docx
   ✓ 找到附图: 2张

🔍 正在执行检查...
   ✓ 完成检查，共4项结果

📊 检测报告摘要
------------------------------------------------------------
  总检查项: 4
  🛑 严重错误: 1
  ⚠️  警告: 2
  ✅ 通过: 1

⚠️  发现的主要问题：
  ⚠️ 附图1分辨率过低
     位置: test_data/图1.png
  🛑 附图2包含彩色像素
     位置: test_data/图2.jpg

📄 正在生成报告...
   ✓ JSON报告: patent_check_report.json
   ✓ PDF报告: patent_check_report.pdf

✨ 检测完成！
```

### 示例2：检测你自己的专利文件

准备文件夹结构如下：

```
my_patent/
├── 说明书.docx    # 必需
├── 图1.jpg
├── 图2.png
└── 图3.jpg
```

运行检测：

```bash
python3 src/main_full.py /path/to/my_patent
```

---

## 📄 文件命名规范

### Word文档识别

文件名包含以下关键词会被自动识别：

- **说明书**: `说明书`、`specification`、`spec`、`发明`
- **权利要求**: `权利要求`、`claims`、`claim`
- **摘要**: `摘要`、`abstract`

### 图片文件

支持的格式：`.jpg`、`.jpeg`、`.png`、`.tif`、`.tiff`、`.bmp`

---

## 📊 检测结果说明

### 错误等级

| 图标 | 级别 | 说明 | 影响 |
|------|------|------|------|
| 🛑 | ERROR（严重错误） | 必须修改的问题 | 可能被补正或驳回 |
| ⚠️ | WARNING（警告） | 建议修改的问题 | 可能影响审查 |
| ℹ️ | INFO（提示） | 改进建议 | 不影响申请 |
| ✅ | PASS（通过） | 符合要求 | - |

### 检测项说明

#### 说明书结构检查
- **检测内容**: 5个必需章节是否齐全
- **参考依据**: 专利法实施细则第18条

#### 附图分辨率检查
- **检测标准**: ≥200dpi
- **参考依据**: 专利审查指南第一部分第一章5.2节

#### 附图彩色检查
- **检测标准**: 彩色像素比例≤5%
- **参考依据**: 专利法实施细则第17条

---

## 📂 输出文件

检测完成后会生成两个文件：

### 1. JSON报告（`patent_check_report.json`）

```json
{
  "timestamp": "2025-10-27T11:44:02.455575",
  "summary": {
    "total": 4,
    "errors": 1,
    "warnings": 2,
    "passes": 1
  },
  "results": [
    {
      "rule_id": "S002",
      "category": "structure",
      "severity": "pass",
      "title": "说明书结构完整",
      "location": "test_data/说明书.docx",
      ...
    }
  ]
}
```

### 2. PDF报告（`patent_check_report.pdf`）

包含：
- 生成时间和文件信息
- 统计摘要表格
- 详细问题列表（位置、描述、建议、参考）
- 免责声明

---

## 🔧 命令行选项

```
usage: main_full.py [-h] [-o OUTPUT] [-j JSON] [--no-pdf] path

PatentCheck-Desktop - 专利申请自检工具

positional arguments:
  path                  专利文件或文件夹路径

optional arguments:
  -h, --help            显示帮助信息
  -o OUTPUT, --output OUTPUT
                        输出PDF报告路径 (默认: patent_check_report.pdf)
  -j JSON, --json JSON  输出JSON报告路径 (默认: patent_check_report.json)
  --no-pdf              不生成PDF报告
```

---

## 🎯 典型使用场景

### 场景1：申请前自检

```bash
# 在提交专利申请前检查文件
python3 src/main_full.py ~/Documents/我的专利申请
```

### 场景2：批量检查

```bash
# 检查多个专利（逐个运行）
for dir in patent1 patent2 patent3; do
  python3 src/main_full.py $dir -o ${dir}_report.pdf
done
```

### 场景3：仅要JSON数据

```bash
# 用于自动化处理
python3 src/main_full.py my_patent --no-pdf -j output.json
```

---

## ⚠️ 注意事项

### 1. 文件格式要求
- Word文档必须是 `.docx` 格式（不支持 `.doc`）
- 图片需要是常见格式（JPG/PNG/TIF/BMP）

### 2. 检测限制
- 当前版本为规则引擎，精度约70%
- 标号检测功能尚未实现（需OCR）
- 图文对齐检查尚未实现

### 3. 运行环境
- Python 3.9+
- macOS / Linux / Windows
- 需要安装所有依赖库

---

## 🐛 常见问题

### Q1: 提示"未找到说明书文件"

**解决方法**:
- 确保文件名包含"说明书"关键词
- 或重命名为：`发明说明书.docx`

### Q2: PDF生成失败

**解决方法**:
- 使用 `--no-pdf` 选项仅生成JSON
- JSON报告包含完整数据，可手动转换

### Q3: 图片分辨率检测不准确

**原因**: 部分图片文件不包含DPI信息，默认为72dpi

**解决方法**: 使用图像编辑软件显式设置DPI后保存

---

## 📞 获取帮助

如遇到问题，请：

1. 查看错误提示信息
2. 检查文件格式和命名
3. 查看生成的JSON报告了解详情

---

## 🎓 技术实现

本工具基于以下技术：

- **python-docx**: Word文档解析
- **Pillow**: 图像处理
- **NumPy**: 数值计算
- **ReportLab**: PDF生成

检测准确率：**70-75%**（规则引擎版本）

---

## 📈 版本信息

- **当前版本**: V0.9 MVP
- **发布日期**: 2025-10-27
- **下一版本**: V1.0（计划增加YOLO模型提升精度）

---

**免责声明**：  
本工具生成的报告仅供参考，不构成法律意见。最终审查以国家知识产权局的正式审查为准。

---

**PatentCheck-Desktop** - 让专利申请更简单 ✨
