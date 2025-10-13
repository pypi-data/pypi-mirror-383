> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/UNetTemporalAttentionMultiply/en.md)

The UNetTemporalAttentionMultiply node applies multiplication factors to different types of attention mechanisms in a temporal UNet model. It modifies the model by adjusting the weights of self-attention and cross-attention layers, distinguishing between structural and temporal components. This allows fine-tuning of how much influence each attention type has on the model's output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The input model to modify with attention multipliers |
| `self_structural` | FLOAT | No | 0.0 - 10.0 | Multiplier for self-attention structural components (default: 1.0) |
| `self_temporal` | FLOAT | No | 0.0 - 10.0 | Multiplier for self-attention temporal components (default: 1.0) |
| `cross_structural` | FLOAT | No | 0.0 - 10.0 | Multiplier for cross-attention structural components (default: 1.0) |
| `cross_temporal` | FLOAT | No | 0.0 - 10.0 | Multiplier for cross-attention temporal components (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The modified model with adjusted attention weights |
