> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeCosmos14B/en.md)

The ModelMergeCosmos14B node merges two AI models using a block-based approach specifically designed for Cosmos 14B model architecture. It allows you to blend different components of the models by adjusting weight values between 0.0 and 1.0 for each model block and embedding layer.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | First model to merge |
| `model2` | MODEL | Yes | - | Second model to merge |
| `pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Position embedder weight (default: 1.0) |
| `extra_pos_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Extra position embedder weight (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 - 1.0 | X embedder weight (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | T embedder weight (default: 1.0) |
| `affline_norm.` | FLOAT | Yes | 0.0 - 1.0 | Affine normalization weight (default: 1.0) |
| `blocks.block0.` | FLOAT | Yes | 0.0 - 1.0 | Block 0 weight (default: 1.0) |
| `blocks.block1.` | FLOAT | Yes | 0.0 - 1.0 | Block 1 weight (default: 1.0) |
| `blocks.block2.` | FLOAT | Yes | 0.0 - 1.0 | Block 2 weight (default: 1.0) |
| `blocks.block3.` | FLOAT | Yes | 0.0 - 1.0 | Block 3 weight (default: 1.0) |
| `blocks.block4.` | FLOAT | Yes | 0.0 - 1.0 | Block 4 weight (default: 1.0) |
| `blocks.block5.` | FLOAT | Yes | 0.0 - 1.0 | Block 5 weight (default: 1.0) |
| `blocks.block6.` | FLOAT | Yes | 0.0 - 1.0 | Block 6 weight (default: 1.0) |
| `blocks.block7.` | FLOAT | Yes | 0.0 - 1.0 | Block 7 weight (default: 1.0) |
| `blocks.block8.` | FLOAT | Yes | 0.0 - 1.0 | Block 8 weight (default: 1.0) |
| `blocks.block9.` | FLOAT | Yes | 0.0 - 1.0 | Block 9 weight (default: 1.0) |
| `blocks.block10.` | FLOAT | Yes | 0.0 - 1.0 | Block 10 weight (default: 1.0) |
| `blocks.block11.` | FLOAT | Yes | 0.0 - 1.0 | Block 11 weight (default: 1.0) |
| `blocks.block12.` | FLOAT | Yes | 0.0 - 1.0 | Block 12 weight (default: 1.0) |
| `blocks.block13.` | FLOAT | Yes | 0.0 - 1.0 | Block 13 weight (default: 1.0) |
| `blocks.block14.` | FLOAT | Yes | 0.0 - 1.0 | Block 14 weight (default: 1.0) |
| `blocks.block15.` | FLOAT | Yes | 0.0 - 1.0 | Block 15 weight (default: 1.0) |
| `blocks.block16.` | FLOAT | Yes | 0.0 - 1.0 | Block 16 weight (default: 1.0) |
| `blocks.block17.` | FLOAT | Yes | 0.0 - 1.0 | Block 17 weight (default: 1.0) |
| `blocks.block18.` | FLOAT | Yes | 0.0 - 1.0 | Block 18 weight (default: 1.0) |
| `blocks.block19.` | FLOAT | Yes | 0.0 - 1.0 | Block 19 weight (default: 1.0) |
| `blocks.block20.` | FLOAT | Yes | 0.0 - 1.0 | Block 20 weight (default: 1.0) |
| `blocks.block21.` | FLOAT | Yes | 0.0 - 1.0 | Block 21 weight (default: 1.0) |
| `blocks.block22.` | FLOAT | Yes | 0.0 - 1.0 | Block 22 weight (default: 1.0) |
| `blocks.block23.` | FLOAT | Yes | 0.0 - 1.0 | Block 23 weight (default: 1.0) |
| `blocks.block24.` | FLOAT | Yes | 0.0 - 1.0 | Block 24 weight (default: 1.0) |
| `blocks.block25.` | FLOAT | Yes | 0.0 - 1.0 | Block 25 weight (default: 1.0) |
| `blocks.block26.` | FLOAT | Yes | 0.0 - 1.0 | Block 26 weight (default: 1.0) |
| `blocks.block27.` | FLOAT | Yes | 0.0 - 1.0 | Block 27 weight (default: 1.0) |
| `blocks.block28.` | FLOAT | Yes | 0.0 - 1.0 | Block 28 weight (default: 1.0) |
| `blocks.block29.` | FLOAT | Yes | 0.0 - 1.0 | Block 29 weight (default: 1.0) |
| `blocks.block30.` | FLOAT | Yes | 0.0 - 1.0 | Block 30 weight (default: 1.0) |
| `blocks.block31.` | FLOAT | Yes | 0.0 - 1.0 | Block 31 weight (default: 1.0) |
| `blocks.block32.` | FLOAT | Yes | 0.0 - 1.0 | Block 32 weight (default: 1.0) |
| `blocks.block33.` | FLOAT | Yes | 0.0 - 1.0 | Block 33 weight (default: 1.0) |
| `blocks.block34.` | FLOAT | Yes | 0.0 - 1.0 | Block 34 weight (default: 1.0) |
| `blocks.block35.` | FLOAT | Yes | 0.0 - 1.0 | Block 35 weight (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Final layer weight (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models |
