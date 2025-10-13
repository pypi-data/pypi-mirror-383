> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrimAudioDuration/zh.md)

TrimAudioDuration 节点允许您从音频文件中截取特定时间段。您可以指定开始裁剪的时间点以及生成音频片段的时长。该节点通过将时间值转换为音频帧位置并提取相应的音频波形部分来实现此功能。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `audio` | AUDIO | 是 | - | 需要裁剪的音频输入 |
| `start_index` | FLOAT | 是 | -0xffffffffffffffff 到 0xffffffffffffffff | 开始时间（秒），可为负值表示从末尾倒计时（支持亚秒级精度）。默认值：0.0 |
| `duration` | FLOAT | 是 | 0.0 到 0xffffffffffffffff | 持续时间（秒）。默认值：60.0 |

**注意：** 开始时间必须小于结束时间且在音频长度范围内。负的开始时间值表示从音频末尾向前倒计时。

## 输出参数

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `audio` | AUDIO | 具有指定开始时间和持续时间的裁剪后音频片段 |
