> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPAttentionMultiply/en.md)

The CLIPAttentionMultiply node allows you to adjust the attention mechanism in CLIP models by applying multiplication factors to different components of the self-attention layers. It works by modifying the query, key, value, and output projection weights and biases in the CLIP model's attention mechanism. This experimental node creates a modified copy of the input CLIP model with the specified scaling factors applied.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | required | - | - | The CLIP model to modify |
| `q` | FLOAT | required | 1.0 | 0.0 - 10.0 | Multiplication factor for query projection weights and biases |
| `k` | FLOAT | required | 1.0 | 0.0 - 10.0 | Multiplication factor for key projection weights and biases |
| `v` | FLOAT | required | 1.0 | 0.0 - 10.0 | Multiplication factor for value projection weights and biases |
| `out` | FLOAT | required | 1.0 | 0.0 - 10.0 | Multiplication factor for output projection weights and biases |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CLIP` | CLIP | Returns a modified CLIP model with the specified attention scaling factors applied |
