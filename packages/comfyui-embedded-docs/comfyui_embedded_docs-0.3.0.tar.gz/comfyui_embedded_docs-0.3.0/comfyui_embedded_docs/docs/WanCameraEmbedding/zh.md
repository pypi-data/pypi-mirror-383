> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanCameraEmbedding/zh.md)

WanCameraEmbedding 节点基于相机运动参数，使用 Plücker 嵌入生成相机轨迹嵌入。它会创建模拟不同相机运动的相机姿态序列，并将其转换为适用于视频生成流程的嵌入张量。

## 输入参数

| 参数 | 数据类型 | 必填 | 取值范围 | 描述 |
|------|-----------|------|----------|------|
| `camera_pose` | COMBO | 是 | "Static"<br>"Pan Up"<br>"Pan Down"<br>"Pan Left"<br>"Pan Right"<br>"Zoom In"<br>"Zoom Out"<br>"Anti Clockwise (ACW)"<br>"ClockWise (CW)" | 要模拟的相机运动类型（默认："Static"） |
| `width` | INT | 是 | 16 至 MAX_RESOLUTION | 输出的宽度（像素）（默认：832，步长：16） |
| `height` | INT | 是 | 16 至 MAX_RESOLUTION | 输出的高度（像素）（默认：480，步长：16） |
| `length` | INT | 是 | 1 至 MAX_RESOLUTION | 相机轨迹序列的长度（默认：81，步长：4） |
| `speed` | FLOAT | 否 | 0.0 至 10.0 | 相机运动的速度（默认：1.0，步长：0.1） |
| `fx` | FLOAT | 否 | 0.0 至 1.0 | 焦距 x 参数（默认：0.5，步长：0.000000001） |
| `fy` | FLOAT | 否 | 0.0 至 1.0 | 焦距 y 参数（默认：0.5，步长：0.000000001） |
| `cx` | FLOAT | 否 | 0.0 至 1.0 | 主点 x 坐标（默认：0.5，步长：0.01） |
| `cy` | FLOAT | 否 | 0.0 至 1.0 | 主点 y 坐标（默认：0.5，步长：0.01） |

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|----------|-----------|------|
| `camera_embedding` | TENSOR | 生成的包含轨迹序列的相机嵌入张量 |
| `width` | INT | 处理过程中使用的宽度值 |
| `height` | INT | 处理过程中使用的高度值 |
| `length` | INT | 处理过程中使用的长度值 |
