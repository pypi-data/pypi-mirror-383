> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPMergeSubtract/en.md)

The CLIPMergeSubtract node performs model merging by subtracting the weights of one CLIP model from another. It creates a new CLIP model by cloning the first model and then subtracting the key patches from the second model, with an adjustable multiplier to control the subtraction strength. This allows for fine-tuned model blending by removing specific characteristics from the base model.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip1` | CLIP | Yes | - | The base CLIP model that will be cloned and modified |
| `clip2` | CLIP | Yes | - | The CLIP model whose key patches will be subtracted from the base model |
| `multiplier` | FLOAT | Yes | -10.0 to 10.0 | Controls the strength of the subtraction operation (default: 1.0) |

**Note:** The node excludes `.position_ids` and `.logit_scale` parameters from the subtraction operation, regardless of the multiplier value.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `clip` | CLIP | The resulting CLIP model after subtracting the second model's weights from the first |
