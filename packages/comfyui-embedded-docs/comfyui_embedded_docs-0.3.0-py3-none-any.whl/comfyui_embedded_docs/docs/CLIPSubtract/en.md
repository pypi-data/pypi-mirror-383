> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPSubtract/en.md)

The CLIPSubtract node performs a subtraction operation between two CLIP models. It takes the first CLIP model as a base and subtracts the key patches from the second CLIP model, with an optional multiplier to control the subtraction strength. This allows for fine-tuned model blending by removing specific characteristics from one model using another.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `clip1` | CLIP | Required | - | - | The base CLIP model that will be modified |
| `clip2` | CLIP | Required | - | - | The CLIP model whose key patches will be subtracted from the base model |
| `multiplier` | FLOAT | Required | 1.0 | -10.0 to 10.0, step 0.01 | Controls the strength of the subtraction operation |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CLIP` | CLIP | The resulting CLIP model after the subtraction operation |
