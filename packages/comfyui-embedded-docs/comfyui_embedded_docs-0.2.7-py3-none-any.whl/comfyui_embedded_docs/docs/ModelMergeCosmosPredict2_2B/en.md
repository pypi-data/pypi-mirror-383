> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmosPredict2_2B/en.md)

The ModelMergeCosmosPredict2_2B node merges two diffusion models using a block-based approach with fine-grained control over different model components. It allows you to blend specific parts of two models by adjusting interpolation weights for position embedders, time embedders, transformer blocks, and final layers. This provides precise control over how different architectural components from each model contribute to the final merged result.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge |
| `model2` | MODEL | Yes | - | The second model to merge |
| `pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Position embedder interpolation weight (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Input embedder interpolation weight (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Time embedder interpolation weight (default: 1.0) |
| `t_embedding_norm.` | FLOAT | Yes | 0.0 - 1.0 | Time embedding normalization interpolation weight (default: 1.0) |
| `blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 0 interpolation weight (default: 1.0) |
| `blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 1 interpolation weight (default: 1.0) |
| `blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 2 interpolation weight (default: 1.0) |
| `blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 3 interpolation weight (default: 1.0) |
| `blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 4 interpolation weight (default: 1.0) |
| `blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 5 interpolation weight (default: 1.0) |
| `blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 6 interpolation weight (default: 1.0) |
| `blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 7 interpolation weight (default: 1.0) |
| `blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 8 interpolation weight (default: 1.0) |
| `blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 9 interpolation weight (default: 1.0) |
| `blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 10 interpolation weight (default: 1.0) |
| `blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 11 interpolation weight (default: 1.0) |
| `blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 12 interpolation weight (default: 1.0) |
| `blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 13 interpolation weight (default: 1.0) |
| `blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 14 interpolation weight (default: 1.0) |
| `blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 15 interpolation weight (default: 1.0) |
| `blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 16 interpolation weight (default: 1.0) |
| `blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 17 interpolation weight (default: 1.0) |
| `blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 18 interpolation weight (default: 1.0) |
| `blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 19 interpolation weight (default: 1.0) |
| `blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 20 interpolation weight (default: 1.0) |
| `blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 21 interpolation weight (default: 1.0) |
| `blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 22 interpolation weight (default: 1.0) |
| `blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 23 interpolation weight (default: 1.0) |
| `blocks.24.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 24 interpolation weight (default: 1.0) |
| `blocks.25.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 25 interpolation weight (default: 1.0) |
| `blocks.26.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 26 interpolation weight (default: 1.0) |
| `blocks.27.` | FLOAT | Yes | 0.0 - 1.0 | Transformer block 27 interpolation weight (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Final layer interpolation weight (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models |
