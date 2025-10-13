> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningCombine/en.md)

The PairConditioningCombine node combines two pairs of conditioning data (positive and negative) into a single pair. It takes two separate conditioning pairs as input and merges them using ComfyUI's internal conditioning combination logic. This node is experimental and primarily used for advanced conditioning manipulation workflows.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive_A` | CONDITIONING | Yes | - | First positive conditioning input |
| `negative_A` | CONDITIONING | Yes | - | First negative conditioning input |
| `positive_B` | CONDITIONING | Yes | - | Second positive conditioning input |
| `negative_B` | CONDITIONING | Yes | - | Second negative conditioning input |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | Combined positive conditioning output |
| `negative` | CONDITIONING | Combined negative conditioning output |
