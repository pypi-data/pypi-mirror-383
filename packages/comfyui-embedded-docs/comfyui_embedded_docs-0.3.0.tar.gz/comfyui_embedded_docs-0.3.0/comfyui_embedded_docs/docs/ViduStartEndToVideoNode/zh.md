> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ViduStartEndToVideoNode/zh.md)

Vidu Start End To Video Generation 节点通过在起始帧和结束帧之间生成帧来创建视频。它使用文本提示来指导视频生成过程，并支持具有不同分辨率和运动设置的各种视频模型。该节点在处理前会验证起始帧和结束帧是否具有兼容的宽高比。

## 输入参数

| 参数名称 | 数据类型 | 是否必需 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | COMBO | 是 | `"vidu_q1"`<br>[VideoModelName 枚举中的其他模型值] | 模型名称（默认值："vidu_q1"） |
| `first_frame` | IMAGE | 是 | - | 起始帧 |
| `end_frame` | IMAGE | 是 | - | 结束帧 |
| `prompt` | STRING | 否 | - | 用于视频生成的文本描述 |
| `duration` | INT | 否 | 5-5 | 输出视频的时长（单位：秒）（默认值：5，固定为5秒） |
| `seed` | INT | 否 | 0-2147483647 | 视频生成的随机种子（0表示随机）（默认值：0） |
| `resolution` | COMBO | 否 | `"1080p"`<br>[Resolution 枚举中的其他分辨率值] | 支持的值可能因模型和时长而异（默认值："1080p"） |
| `movement_amplitude` | COMBO | 否 | `"auto"`<br>[MovementAmplitude 枚举中的其他运动幅度值] | 画面中物体的运动幅度（默认值："auto"） |

**注意：** 起始帧和结束帧必须具有兼容的宽高比（使用 min_rel=0.8, max_rel=1.25 的比率容差进行验证）。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `output` | VIDEO | 生成的视频文件 |
