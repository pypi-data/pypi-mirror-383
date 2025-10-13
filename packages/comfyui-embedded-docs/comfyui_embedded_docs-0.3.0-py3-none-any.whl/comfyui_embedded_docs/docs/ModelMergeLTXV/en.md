> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeLTXV/en.md)

The ModelMergeLTXV node performs advanced model merging operations specifically designed for LTXV model architectures. It allows you to blend two different models together by adjusting interpolation weights for various model components including transformer blocks, projection layers, and other specialized modules.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge |
| `model2` | MODEL | Yes | - | The second model to merge |
| `patchify_proj.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for patchify projection layers (default: 1.0) |
| `adaln_single.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for adaptive layer normalization single layers (default: 1.0) |
| `caption_projection.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for caption projection layers (default: 1.0) |
| `transformer_blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 0 (default: 1.0) |
| `transformer_blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 1 (default: 1.0) |
| `transformer_blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 2 (default: 1.0) |
| `transformer_blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 3 (default: 1.0) |
| `transformer_blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 4 (default: 1.0) |
| `transformer_blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 5 (default: 1.0) |
| `transformer_blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 6 (default: 1.0) |
| `transformer_blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 7 (default: 1.0) |
| `transformer_blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 8 (default: 1.0) |
| `transformer_blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 9 (default: 1.0) |
| `transformer_blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 10 (default: 1.0) |
| `transformer_blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 11 (default: 1.0) |
| `transformer_blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 12 (default: 1.0) |
| `transformer_blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 13 (default: 1.0) |
| `transformer_blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 14 (default: 1.0) |
| `transformer_blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 15 (default: 1.0) |
| `transformer_blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 16 (default: 1.0) |
| `transformer_blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 17 (default: 1.0) |
| `transformer_blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 18 (default: 1.0) |
| `transformer_blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 19 (default: 1.0) |
| `transformer_blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 20 (default: 1.0) |
| `transformer_blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 21 (default: 1.0) |
| `transformer_blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 22 (default: 1.0) |
| `transformer_blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 23 (default: 1.0) |
| `transformer_blocks.24.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 24 (default: 1.0) |
| `transformer_blocks.25.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 25 (default: 1.0) |
| `transformer_blocks.26.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 26 (default: 1.0) |
| `transformer_blocks.27.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for transformer block 27 (default: 1.0) |
| `scale_shift_table` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for scale shift table (default: 1.0) |
| `proj_out.` | FLOAT | Yes | 0.0 - 1.0 | Interpolation weight for projection output layers (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models according to the specified interpolation weights |
