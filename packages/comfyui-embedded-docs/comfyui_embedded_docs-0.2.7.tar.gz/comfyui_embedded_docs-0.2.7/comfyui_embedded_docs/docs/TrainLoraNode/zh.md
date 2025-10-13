> 本文档由 AI 生成。如果您发现任何错误或有改进建议，欢迎贡献！ [在 GitHub 上编辑](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrainLoraNode/zh.md)

TrainLoraNode 使用提供的潜空间数据和条件数据，在扩散模型上创建并训练 LoRA（低秩适应）模型。该节点允许您使用自定义训练参数、优化器和损失函数来微调模型。节点输出应用了 LoRA 的训练后模型、LoRA 权重、训练损失指标以及完成的总训练步数。

## 输入参数

| 参数名 | 数据类型 | 必填 | 取值范围 | 描述 |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | 是 | - | 要训练 LoRA 的基础模型。 |
| `latents` | LATENT | 是 | - | 用于训练的潜空间数据，作为模型的数据集/输入。 |
| `positive` | CONDITIONING | 是 | - | 用于训练的正向条件数据。 |
| `batch_size` | INT | 是 | 1-10000 | 训练时使用的批大小（默认值：1）。 |
| `grad_accumulation_steps` | INT | 是 | 1-1024 | 训练时使用的梯度累积步数（默认值：1）。 |
| `steps` | INT | 是 | 1-100000 | 训练 LoRA 的步数（默认值：16）。 |
| `learning_rate` | FLOAT | 是 | 0.0000001-1.0 | 训练时使用的学习率（默认值：0.0005）。 |
| `rank` | INT | 是 | 1-128 | LoRA 层的秩（默认值：8）。 |
| `optimizer` | COMBO | 是 | "AdamW"<br>"Adam"<br>"SGD"<br>"RMSprop" | 训练时使用的优化器（默认值："AdamW"）。 |
| `loss_function` | COMBO | 是 | "MSE"<br>"L1"<br>"Huber"<br>"SmoothL1" | 训练时使用的损失函数（默认值："MSE"）。 |
| `seed` | INT | 是 | 0-18446744073709551615 | 训练时使用的随机种子（用于 LoRA 权重初始化和噪声采样的生成器）（默认值：0）。 |
| `training_dtype` | COMBO | 是 | "bf16"<br>"fp32" | 训练时使用的数据类型（默认值："bf16"）。 |
| `lora_dtype` | COMBO | 是 | "bf16"<br>"fp32" | LoRA 使用的数据类型（默认值："bf16"）。 |
| `algorithm` | COMBO | 是 | 多种可选算法 | 训练时使用的算法。 |
| `gradient_checkpointing` | BOOLEAN | 是 | - | 训练时是否使用梯度检查点（默认值：True）。 |
| `existing_lora` | COMBO | 是 | 多种可选选项 | 要附加到的现有 LoRA。设置为 None 表示创建新的 LoRA（默认值："[None]"）。 |

**注意：** 正向条件数据的数量必须与潜空间图像的数量匹配。如果只提供了一个正向条件数据但有多个图像，该条件数据将自动为所有图像重复使用。

## 输出结果

| 输出名称 | 数据类型 | 描述 |
|-------------|-----------|-------------|
| `model_with_lora` | MODEL | 应用了训练后 LoRA 的原始模型。 |
| `lora` | LORA_MODEL | 训练后的 LoRA 权重，可以保存或应用于其他模型。 |
| `loss` | LOSS_MAP | 包含随时间变化的训练损失值的字典。 |
| `steps` | INT | 完成的总训练步数（包括现有 LoRA 的任何先前步数）。 |
