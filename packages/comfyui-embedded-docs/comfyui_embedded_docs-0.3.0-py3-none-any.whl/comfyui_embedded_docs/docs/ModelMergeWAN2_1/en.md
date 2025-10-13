> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeWAN2_1/en.md)

The ModelMergeWAN2_1 node merges two models by blending their components using weighted averages. It supports different model sizes including 1.3B models with 30 blocks and 14B models with 40 blocks, with special handling for image to video models that include an extra image embedding component. Each component of the models can be individually weighted to control the blending ratio between the two input models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | First model to merge |
| `model2` | MODEL | Yes | - | Second model to merge |
| `patch_embedding.` | FLOAT | Yes | 0.0 - 1.0 | Weight for patch embedding component (default: 1.0) |
| `time_embedding.` | FLOAT | Yes | 0.0 - 1.0 | Weight for time embedding component (default: 1.0) |
| `time_projection.` | FLOAT | Yes | 0.0 - 1.0 | Weight for time projection component (default: 1.0) |
| `text_embedding.` | FLOAT | Yes | 0.0 - 1.0 | Weight for text embedding component (default: 1.0) |
| `img_emb.` | FLOAT | Yes | 0.0 - 1.0 | Weight for image embedding component, used in image to video models (default: 1.0) |
| `blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 0 (default: 1.0) |
| `blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 1 (default: 1.0) |
| `blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 2 (default: 1.0) |
| `blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 3 (default: 1.0) |
| `blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 4 (default: 1.0) |
| `blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 5 (default: 1.0) |
| `blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 6 (default: 1.0) |
| `blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 7 (default: 1.0) |
| `blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 8 (default: 1.0) |
| `blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 9 (default: 1.0) |
| `blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 10 (default: 1.0) |
| `blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 11 (default: 1.0) |
| `blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 12 (default: 1.0) |
| `blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 13 (default: 1.0) |
| `blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 14 (default: 1.0) |
| `blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 15 (default: 1.0) |
| `blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 16 (default: 1.0) |
| `blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 17 (default: 1.0) |
| `blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 18 (default: 1.0) |
| `blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 19 (default: 1.0) |
| `blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 20 (default: 1.0) |
| `blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 21 (default: 1.0) |
| `blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 22 (default: 1.0) |
| `blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 23 (default: 1.0) |
| `blocks.24.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 24 (default: 1.0) |
| `blocks.25.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 25 (default: 1.0) |
| `blocks.26.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 26 (default: 1.0) |
| `blocks.27.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 27 (default: 1.0) |
| `blocks.28.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 28 (default: 1.0) |
| `blocks.29.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 29 (default: 1.0) |
| `blocks.30.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 30 (default: 1.0) |
| `blocks.31.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 31 (default: 1.0) |
| `blocks.32.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 32 (default: 1.0) |
| `blocks.33.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 33 (default: 1.0) |
| `blocks.34.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 34 (default: 1.0) |
| `blocks.35.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 35 (default: 1.0) |
| `blocks.36.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 36 (default: 1.0) |
| `blocks.37.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 37 (default: 1.0) |
| `blocks.38.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 38 (default: 1.0) |
| `blocks.39.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 39 (default: 1.0) |
| `head.` | FLOAT | Yes | 0.0 - 1.0 | Weight for head component (default: 1.0) |

**Note:** All weight parameters use a range from 0.0 to 1.0 with 0.01 step increments. The node supports up to 40 blocks to accommodate different model sizes, where 1.3B models use 30 blocks and 14B models use 40 blocks. The `img_emb.` parameter is specifically for image to video models.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining components from both input models according to the specified weights |
