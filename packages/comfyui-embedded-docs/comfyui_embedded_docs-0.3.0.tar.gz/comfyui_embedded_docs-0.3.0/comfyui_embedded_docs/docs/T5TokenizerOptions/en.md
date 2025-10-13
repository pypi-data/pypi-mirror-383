> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/T5TokenizerOptions/en.md)

The T5TokenizerOptions node allows you to configure tokenizer settings for various T5 model types. It sets minimum padding and minimum length parameters for multiple T5 model variants including t5xxl, pile_t5xl, t5base, mt5xl, and umt5xxl. The node takes a CLIP input and returns a modified CLIP with the specified tokenizer options applied.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model to configure tokenizer options for |
| `min_padding` | INT | No | 0-10000 | Minimum padding value to set for all T5 model types (default: 0) |
| `min_length` | INT | No | 0-10000 | Minimum length value to set for all T5 model types (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | CLIP | The modified CLIP model with updated tokenizer options applied to all T5 variants |
