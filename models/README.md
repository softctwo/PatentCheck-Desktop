# YOLO模型权重文件

本目录用于存放YOLOv5模型权重文件，用于专利附图标号检测。

## 模型文件

### 1. 自定义训练模型（推荐）
- **文件名**: `yolov5n_marker.pt`
- **用途**: 专门训练用于检测专利附图中的圆圈标号和箭头
- **大小**: ~4 MB
- **类别**: 
  - 0: circle_marker (圆圈标号)
  - 1: arrow (指示箭头)
  - 2: number (数字标记)

**获取方式**:
根据PRD文档，需要使用200张公开专利数据训练的自定义模型。

### 2. 预训练模型（Fallback）
如果自定义模型不存在，系统会自动使用ultralytics提供的预训练YOLOv5-nano模型：
- **模型**: `yolov5n.pt`
- **自动下载**: 首次运行时自动从ultralytics下载

## 训练自定义模型

如果需要训练自定义标号检测模型，请按以下步骤：

### 1. 准备数据集

数据集结构：
```
dataset/
├── images/
│   ├── train/
│   │   ├── patent_001.jpg
│   │   ├── patent_002.jpg
│   │   └── ...
│   └── val/
│       ├── patent_101.jpg
│       └── ...
└── labels/
    ├── train/
    │   ├── patent_001.txt
    │   ├── patent_002.txt
    │   └── ...
    └── val/
        ├── patent_101.txt
        └── ...
```

标签格式（YOLO格式）：
```
<class_id> <x_center> <y_center> <width> <height>
```

### 2. 训练模型

使用ultralytics库训练：

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov5n.pt')

# 训练
results = model.train(
    data='patent_marker.yaml',  # 数据集配置文件
    epochs=100,
    imgsz=640,
    batch=16,
    name='patent_marker_yolov5n'
)

# 导出模型
model.export(format='pt')
```

数据集配置文件 `patent_marker.yaml`：
```yaml
path: ./dataset  # 数据集根目录
train: images/train  # 训练集
val: images/val  # 验证集

# 类别
nc: 3  # 类别数量
names: ['circle_marker', 'arrow', 'number']
```

### 3. 验证模型

```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO('runs/detect/patent_marker_yolov5n/weights/best.pt')

# 验证
results = model.val()

# 测试
results = model.predict(source='test_images/', save=True)
```

### 4. 部署模型

将训练好的最佳权重文件复制到此目录：
```bash
cp runs/detect/patent_marker_yolov5n/weights/best.pt models/yolov5n_marker.pt
```

## 使用说明

1. **自动模式**（推荐）：
   - 系统会自动检测 `models/yolov5n_marker.pt` 是否存在
   - 如存在，使用自定义模型
   - 如不存在，fallback到预训练模型

2. **手动指定模型**：
   ```python
   from src.marker_detector.yolo_detector import YOLOMarkerDetector
   
   detector = YOLOMarkerDetector(model_path='models/yolov5n_marker.pt')
   ```

## 模型性能

### 自定义模型（期望性能）
- **精度**: mAP@0.5 > 0.85
- **召回率**: > 0.90
- **推理速度**: ~30ms/image (CPU)
- **模型大小**: ~4 MB

### 预训练模型
- **用途**: 通用目标检测
- **精度**: 可能不如专用模型
- **适用场景**: 初期测试或无自定义模型时

## 注意事项

1. 模型文件较大，不建议提交到git仓库
2. 建议在`.gitignore`中排除`.pt`文件
3. 生产环境部署时需确保模型文件存在
4. CPU推理速度较慢，GPU可显著提升性能

## 许可证

模型权重文件需遵守相应的许可证要求：
- YOLO模型: AGPL-3.0 (商业使用需获得许可)
- 自定义训练模型: 根据训练数据的许可证
