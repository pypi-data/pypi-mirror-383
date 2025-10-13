> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeSDXL/en.md)

The ModelMergeSDXL node allows you to blend two SDXL models together by adjusting the influence of each model on different parts of the architecture. You can control how much each model contributes to time embeddings, label embeddings, and various blocks within the model structure. This creates a hybrid model that combines characteristics from both input models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first SDXL model to merge |
| `model2` | MODEL | Yes | - | The second SDXL model to merge |
| `time_embed.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for time embedding layers (default: 1.0) |
| `label_emb.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for label embedding layers (default: 1.0) |
| `input_blocks.0` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 0 (default: 1.0) |
| `input_blocks.1` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 1 (default: 1.0) |
| `input_blocks.2` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 2 (default: 1.0) |
| `input_blocks.3` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 3 (default: 1.0) |
| `input_blocks.4` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 4 (default: 1.0) |
| `input_blocks.5` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 5 (default: 1.0) |
| `input_blocks.6` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 6 (default: 1.0) |
| `input_blocks.7` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 7 (default: 1.0) |
| `input_blocks.8` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for input block 8 (default: 1.0) |
| `middle_block.0` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for middle block 0 (default: 1.0) |
| `middle_block.1` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for middle block 1 (default: 1.0) |
| `middle_block.2` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for middle block 2 (default: 1.0) |
| `output_blocks.0` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 0 (default: 1.0) |
| `output_blocks.1` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 1 (default: 1.0) |
| `output_blocks.2` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 2 (default: 1.0) |
| `output_blocks.3` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 3 (default: 1.0) |
| `output_blocks.4` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 4 (default: 1.0) |
| `output_blocks.5` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 5 (default: 1.0) |
| `output_blocks.6` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 6 (default: 1.0) |
| `output_blocks.7` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 7 (default: 1.0) |
| `output_blocks.8` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output block 8 (default: 1.0) |
| `out.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for output layers (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged SDXL model combining characteristics from both input models |
