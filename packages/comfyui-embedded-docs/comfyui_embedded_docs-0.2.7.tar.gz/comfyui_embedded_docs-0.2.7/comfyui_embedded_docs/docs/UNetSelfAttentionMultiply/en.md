> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/UNetSelfAttentionMultiply/en.md)

The UNetSelfAttentionMultiply node applies multiplication factors to the query, key, value, and output components of the self-attention mechanism in a UNet model. It allows you to scale different parts of the attention computation to experiment with how attention weights affect the model's behavior.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The UNet model to modify with attention scaling factors |
| `q` | FLOAT | No | 0.0 - 10.0 | Multiplication factor for query component (default: 1.0) |
| `k` | FLOAT | No | 0.0 - 10.0 | Multiplication factor for key component (default: 1.0) |
| `v` | FLOAT | No | 0.0 - 10.0 | Multiplication factor for value component (default: 1.0) |
| `out` | FLOAT | No | 0.0 - 10.0 | Multiplication factor for output component (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `MODEL` | MODEL | The modified UNet model with scaled attention components |
