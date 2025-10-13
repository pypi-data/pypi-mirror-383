> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmos7B/en.md)

The ModelMergeCosmos7B node merges two AI models together using weighted blending of specific components. It allows fine-grained control over how different parts of the models are combined by adjusting individual weights for position embeddings, transformer blocks, and final layers.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | First model to merge |
| `model2` | MODEL | Yes | - | Second model to merge |
| `pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for position embedder component (default: 1.0) |
| `extra_pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for extra position embedder component (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for x embedder component (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for t embedder component (default: 1.0) |
| `affline_norm.` | FLOAT | Yes | 0.0 - 1.0 | Weight for affine normalization component (default: 1.0) |
| `blocks.block0.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 0 (default: 1.0) |
| `blocks.block1.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 1 (default: 1.0) |
| `blocks.block2.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 2 (default: 1.0) |
| `blocks.block3.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 3 (default: 1.0) |
| `blocks.block4.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 4 (default: 1.0) |
| `blocks.block5.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 5 (default: 1.0) |
| `blocks.block6.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 6 (default: 1.0) |
| `blocks.block7.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 7 (default: 1.0) |
| `blocks.block8.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 8 (default: 1.0) |
| `blocks.block9.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 9 (default: 1.0) |
| `blocks.block10.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 10 (default: 1.0) |
| `blocks.block11.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 11 (default: 1.0) |
| `blocks.block12.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 12 (default: 1.0) |
| `blocks.block13.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 13 (default: 1.0) |
| `blocks.block14.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 14 (default: 1.0) |
| `blocks.block15.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 15 (default: 1.0) |
| `blocks.block16.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 16 (default: 1.0) |
| `blocks.block17.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 17 (default: 1.0) |
| `blocks.block18.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 18 (default: 1.0) |
| `blocks.block19.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 19 (default: 1.0) |
| `blocks.block20.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 20 (default: 1.0) |
| `blocks.block21.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 21 (default: 1.0) |
| `blocks.block22.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 22 (default: 1.0) |
| `blocks.block23.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 23 (default: 1.0) |
| `blocks.block24.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 24 (default: 1.0) |
| `blocks.block25.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 25 (default: 1.0) |
| `blocks.block26.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 26 (default: 1.0) |
| `blocks.block27.` | FLOAT | Yes | 0.0 - 1.0 | Weight for transformer block 27 (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Weight for final layer component (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models |
