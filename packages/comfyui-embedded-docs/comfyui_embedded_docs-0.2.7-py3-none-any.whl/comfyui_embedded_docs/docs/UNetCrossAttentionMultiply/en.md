> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/UNetCrossAttentionMultiply/en.md)

The UNetCrossAttentionMultiply node applies multiplication factors to the cross-attention mechanism in a UNet model. It allows you to scale the query, key, value, and output components of the cross-attention layers to experiment with different attention behaviors and effects.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The UNet model to modify with attention scaling factors |
| `q` | FLOAT | No | 0.0 - 10.0 | Scaling factor for query components in cross-attention (default: 1.0) |
| `k` | FLOAT | No | 0.0 - 10.0 | Scaling factor for key components in cross-attention (default: 1.0) |
| `v` | FLOAT | No | 0.0 - 10.0 | Scaling factor for value components in cross-attention (default: 1.0) |
| `out` | FLOAT | No | 0.0 - 10.0 | Scaling factor for output components in cross-attention (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified UNet model with scaled cross-attention components |
