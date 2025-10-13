> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LoraSave/en.md)

The LoraSave node extracts and saves LoRA (Low-Rank Adaptation) files from model differences. It can process diffusion model differences, text encoder differences, or both, converting them into LoRA format with specified rank and type. The resulting LoRA file is saved to the output directory for later use.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `filename_prefix` | STRING | Yes | - | The prefix for the output filename (default: "loras/ComfyUI_extracted_lora") |
| `rank` | INT | Yes | 1-4096 | The rank value for the LoRA, controlling the size and complexity (default: 8) |
| `lora_type` | COMBO | Yes | Multiple options available | The type of LoRA to create, with various available options |
| `bias_diff` | BOOLEAN | Yes | - | Whether to include bias differences in the LoRA calculation (default: True) |
| `model_diff` | MODEL | No | - | The ModelSubtract output to be converted to a lora |
| `text_encoder_diff` | CLIP | No | - | The CLIPSubtract output to be converted to a lora |

**Note:** At least one of `model_diff` or `text_encoder_diff` must be provided for the node to function. If both are omitted, the node will produce no output.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| - | - | This node saves a LoRA file to the output directory but does not return any data through the workflow |
