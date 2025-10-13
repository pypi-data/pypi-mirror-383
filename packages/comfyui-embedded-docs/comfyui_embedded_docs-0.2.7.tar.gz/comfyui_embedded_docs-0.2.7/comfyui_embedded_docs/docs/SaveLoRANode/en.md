> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SaveLoRANode/en.md)

The SaveLoRA node saves LoRA (Low-Rank Adaptation) models to your output directory. It takes a LoRA model as input and creates a safetensors file with an automatically generated filename. You can customize the filename prefix and optionally include the training step count in the filename for better organization.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `lora` | LORA_MODEL | Yes | - | The LoRA model to save. Do not use the model with LoRA layers. |
| `prefix` | STRING | Yes | - | The prefix to use for the saved LoRA file (default: "loras/ComfyUI_trained_lora"). |
| `steps` | INT | No | - | Optional: The number of steps the LoRA has been trained for, used to name the saved file. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| *None* | - | This node does not return any outputs but saves the LoRA model to the output directory. |
