> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PairConditioningSetDefaultAndCombine/en.md)

The PairConditioningSetDefaultAndCombine node sets default conditioning values and combines them with input conditioning data. It takes positive and negative conditioning inputs along with their default counterparts, then processes them through ComfyUI's hook system to produce final conditioning outputs that incorporate the default values.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `positive` | CONDITIONING | Yes | - | The primary positive conditioning input to be processed |
| `negative` | CONDITIONING | Yes | - | The primary negative conditioning input to be processed |
| `positive_DEFAULT` | CONDITIONING | Yes | - | The default positive conditioning values to be used as fallback |
| `negative_DEFAULT` | CONDITIONING | Yes | - | The default negative conditioning values to be used as fallback |
| `hooks` | HOOKS | No | - | Optional hook group for custom processing logic |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `positive` | CONDITIONING | The processed positive conditioning with default values incorporated |
| `negative` | CONDITIONING | The processed negative conditioning with default values incorporated |
