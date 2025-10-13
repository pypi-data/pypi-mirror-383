> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmosPredict2_14B/en.md)

The ModelMergeCosmosPredict2_14B node allows you to merge two AI models by adjusting the influence of different model components. It provides fine-grained control over how much each part of the second model contributes to the final merged model, using blending weights for specific model layers and components.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The base model to merge with |
| `model2` | MODEL | Yes | - | The secondary model to merge into the base model |
| `pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Position embedder blending weight (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Input embedder blending weight (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Time embedder blending weight (default: 1.0) |
| `t_embedding_norm.` | FLOAT | Yes | 0.0 - 1.0 | Time embedding normalization blending weight (default: 1.0) |
| `blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Block 0 blending weight (default: 1.0) |
| `blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Block 1 blending weight (default: 1.0) |
| `blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Block 2 blending weight (default: 1.0) |
| `blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Block 3 blending weight (default: 1.0) |
| `blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Block 4 blending weight (default: 1.0) |
| `blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Block 5 blending weight (default: 1.0) |
| `blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Block 6 blending weight (default: 1.0) |
| `blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Block 7 blending weight (default: 1.0) |
| `blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Block 8 blending weight (default: 1.0) |
| `blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Block 9 blending weight (default: 1.0) |
| `blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Block 10 blending weight (default: 1.0) |
| `blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Block 11 blending weight (default: 1.0) |
| `blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Block 12 blending weight (default: 1.0) |
| `blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Block 13 blending weight (default: 1.0) |
| `blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Block 14 blending weight (default: 1.0) |
| `blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Block 15 blending weight (default: 1.0) |
| `blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Block 16 blending weight (default: 1.0) |
| `blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Block 17 blending weight (default: 1.0) |
| `blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Block 18 blending weight (default: 1.0) |
| `blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Block 19 blending weight (default: 1.0) |
| `blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Block 20 blending weight (default: 1.0) |
| `blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Block 21 blending weight (default: 1.0) |
| `blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Block 22 blending weight (default: 1.0) |
| `blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Block 23 blending weight (default: 1.0) |
| `blocks.24.` | FLOAT | Yes | 0.0 - 1.0 | Block 24 blending weight (default: 1.0) |
| `blocks.25.` | FLOAT | Yes | 0.0 - 1.0 | Block 25 blending weight (default: 1.0) |
| `blocks.26.` | FLOAT | Yes | 0.0 - 1.0 | Block 26 blending weight (default: 1.0) |
| `blocks.27.` | FLOAT | Yes | 0.0 - 1.0 | Block 27 blending weight (default: 1.0) |
| `blocks.28.` | FLOAT | Yes | 0.0 - 1.0 | Block 28 blending weight (default: 1.0) |
| `blocks.29.` | FLOAT | Yes | 0.0 - 1.0 | Block 29 blending weight (default: 1.0) |
| `blocks.30.` | FLOAT | Yes | 0.0 - 1.0 | Block 30 blending weight (default: 1.0) |
| `blocks.31.` | FLOAT | Yes | 0.0 - 1.0 | Block 31 blending weight (default: 1.0) |
| `blocks.32.` | FLOAT | Yes | 0.0 - 1.0 | Block 32 blending weight (default: 1.0) |
| `blocks.33.` | FLOAT | Yes | 0.0 - 1.0 | Block 33 blending weight (default: 1.0) |
| `blocks.34.` | FLOAT | Yes | 0.0 - 1.0 | Block 34 blending weight (default: 1.0) |
| `blocks.35.` | FLOAT | Yes | 0.0 - 1.0 | Block 35 blending weight (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Final layer blending weight (default: 1.0) |

**Note:** All blending weight parameters accept values between 0.0 and 1.0, where 0.0 means no contribution from model2 and 1.0 means full contribution from model2 for that specific component.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models |
