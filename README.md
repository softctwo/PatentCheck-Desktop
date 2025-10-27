# PatentCheck-Desktop

**专利自助预审工具（桌面版）V0.9 MVP**

像 Word 拼写检查一样，10分钟发现专利申请中的形式错误。

## 功能特性

- ✅ 说明书结构完整性检查（16个标准章节）
- ✅ 附图形式合规检查（分辨率、色彩、线条）
- ✅ **YOLO模型标号检测**（YOLOv5-nano + OCR混合检测）
- ✅ 图文标号一致性检查
- ✅ 摘要附图验证
- ✅ **文档预览功能**（支持PDF和Word文档，包含图片显示）
- ✅ AI智能审查（集成DeepSeek API）
- ✅ 一键生成PDF检测报告

## 技术栈

- **GUI**: PySide6 (Qt for Python)
- **文档解析**: python-docx, PyMuPDF
- **文档预览**: PyMuPDF (PDF渲染), QTextDocument (Word渲染)
- **图像处理**: OpenCV + Pillow
- **标号检测**: YOLOv5-nano (ultralytics) + OCR (Tesseract)
- **AI集成**: DeepSeek API
- **报告生成**: ReportLab

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

**方式1：命令行运行**
```bash
python src/main.py
```

**方式2：GUI启动器（macOS）**
```bash
./launch_gui.command
```

### 使用流程

1. 点击“📁 选择专利文件夹”，选择包含申请材料的文件夹
2. 点击“🔍 开始检测”，系统将自动扫描和检测文档
3. 检测完成后，点击“📄 预览申请材料”查看文档内容
4. 选择性地使用AI审查功能，获取智能分析建议
5. 点击“📄 导出PDF报告”生成检测报告

### 文档预览功能

- 支持PDF和Word (.docx)文档格式
- 自动识别说明书、权利要求书、摘要
- 多页文档翻页浏览
- 灵活缩放（放大/缩小/适应窗口）
- 完美显示文档中的图片内容
- 异步加载，不阻塞UI界面

## 项目结构

```
PatentCheck-Desktop/
├── src/                    # 源代码
│   ├── core/              # 核心模块（规则引擎）
│   ├── file_parser/       # 文件解析
│   ├── structure_checker/ # 结构检查
│   ├── image_checker/     # 图像检查
│   ├── marker_detector/   # 标号检测
│   ├── alignment_checker/ # 图文对齐
│   ├── abstract_checker/  # 摘要检查
│   ├── report_generator/  # 报告生成
│   └── gui/               # 图形界面
├── resources/             # 资源文件
│   ├── rules/            # 规则配置
│   └── templates/        # 报告模板
├── tests/                 # 测试用例
└── docs/                  # 文档

```

## 开发状态

- [x] 项目结构初始化
- [ ] 规则引擎核心
- [ ] 文件解析模块
- [ ] 各检测模块实现
- [ ] GUI界面开发
- [ ] 集成测试

## 版本规划

- **V0.9 MVP**: 规则引擎优先（当前版本）
- **V1.0**: 集成YOLO模型提升精度
- **V1.1 Pro**: 云端新创性检索

## 许可证

本项目当前处于开发阶段，暂未确定许可证。

## 联系方式

项目开发中，欢迎反馈建议！
