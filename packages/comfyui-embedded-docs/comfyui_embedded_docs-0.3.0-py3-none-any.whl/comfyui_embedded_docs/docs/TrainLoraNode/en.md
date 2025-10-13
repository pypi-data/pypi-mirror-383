> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TrainLoraNode/en.md)

The TrainLoraNode creates and trains a LoRA (Low-Rank Adaptation) model on a diffusion model using provided latents and conditioning data. It allows you to fine-tune a model with custom training parameters, optimizers, and loss functions. The node outputs the trained model with LoRA applied, the LoRA weights, training loss metrics, and the total training steps completed.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to train the LoRA on. |
| `latents` | LATENT | Yes | - | The Latents to use for training, serve as dataset/input of the model. |
| `positive` | CONDITIONING | Yes | - | The positive conditioning to use for training. |
| `batch_size` | INT | Yes | 1-10000 | The batch size to use for training (default: 1). |
| `grad_accumulation_steps` | INT | Yes | 1-1024 | The number of gradient accumulation steps to use for training (default: 1). |
| `steps` | INT | Yes | 1-100000 | The number of steps to train the LoRA for (default: 16). |
| `learning_rate` | FLOAT | Yes | 0.0000001-1.0 | The learning rate to use for training (default: 0.0005). |
| `rank` | INT | Yes | 1-128 | The rank of the LoRA layers (default: 8). |
| `optimizer` | COMBO | Yes | "AdamW"<br>"Adam"<br>"SGD"<br>"RMSprop" | The optimizer to use for training (default: "AdamW"). |
| `loss_function` | COMBO | Yes | "MSE"<br>"L1"<br>"Huber"<br>"SmoothL1" | The loss function to use for training (default: "MSE"). |
| `seed` | INT | Yes | 0-18446744073709551615 | The seed to use for training (used in generator for LoRA weight initialization and noise sampling) (default: 0). |
| `training_dtype` | COMBO | Yes | "bf16"<br>"fp32" | The dtype to use for training (default: "bf16"). |
| `lora_dtype` | COMBO | Yes | "bf16"<br>"fp32" | The dtype to use for lora (default: "bf16"). |
| `algorithm` | COMBO | Yes | Multiple options available | The algorithm to use for training. |
| `gradient_checkpointing` | BOOLEAN | Yes | - | Use gradient checkpointing for training (default: True). |
| `existing_lora` | COMBO | Yes | Multiple options available | The existing LoRA to append to. Set to None for new LoRA (default: "[None]"). |

**Note:** The number of positive conditioning inputs must match the number of latent images. If only one positive conditioning is provided with multiple images, it will be automatically repeated for all images.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model_with_lora` | MODEL | The original model with the trained LoRA applied. |
| `lora` | LORA_MODEL | The trained LoRA weights that can be saved or applied to other models. |
| `loss` | LOSS_MAP | A dictionary containing the training loss values over time. |
| `steps` | INT | The total number of training steps completed (including any previous steps from existing LoRA). |
