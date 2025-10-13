> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeMochiPreview/en.md)

This node merges two AI models using a block-based approach with fine-grained control over different model components. It allows you to blend models by adjusting interpolation weights for specific sections including positional frequencies, embedding layers, and individual transformer blocks. The merging process combines the architectures and parameters from both input models according to the specified weight values.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge |
| `model2` | MODEL | Yes | - | The second model to merge |
| `pos_frequencies.` | FLOAT | Yes | 0.0 - 1.0 | Weight for positional frequencies interpolation (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for time embedder interpolation (default: 1.0) |
| `t5_y_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Weight for T5-Y embedder interpolation (default: 1.0) |
| `t5_yproj.` | FLOAT | Yes | 0.0 - 1.0 | Weight for T5-Y projection interpolation (default: 1.0) |
| `blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 0 interpolation (default: 1.0) |
| `blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 1 interpolation (default: 1.0) |
| `blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 2 interpolation (default: 1.0) |
| `blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 3 interpolation (default: 1.0) |
| `blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 4 interpolation (default: 1.0) |
| `blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 5 interpolation (default: 1.0) |
| `blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 6 interpolation (default: 1.0) |
| `blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 7 interpolation (default: 1.0) |
| `blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 8 interpolation (default: 1.0) |
| `blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 9 interpolation (default: 1.0) |
| `blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 10 interpolation (default: 1.0) |
| `blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 11 interpolation (default: 1.0) |
| `blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 12 interpolation (default: 1.0) |
| `blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 13 interpolation (default: 1.0) |
| `blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 14 interpolation (default: 1.0) |
| `blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 15 interpolation (default: 1.0) |
| `blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 16 interpolation (default: 1.0) |
| `blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 17 interpolation (default: 1.0) |
| `blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 18 interpolation (default: 1.0) |
| `blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 19 interpolation (default: 1.0) |
| `blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 20 interpolation (default: 1.0) |
| `blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 21 interpolation (default: 1.0) |
| `blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 22 interpolation (default: 1.0) |
| `blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 23 interpolation (default: 1.0) |
| `blocks.24.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 24 interpolation (default: 1.0) |
| `blocks.25.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 25 interpolation (default: 1.0) |
| `blocks.26.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 26 interpolation (default: 1.0) |
| `blocks.27.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 27 interpolation (default: 1.0) |
| `blocks.28.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 28 interpolation (default: 1.0) |
| `blocks.29.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 29 interpolation (default: 1.0) |
| `blocks.30.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 30 interpolation (default: 1.0) |
| `blocks.31.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 31 interpolation (default: 1.0) |
| `blocks.32.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 32 interpolation (default: 1.0) |
| `blocks.33.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 33 interpolation (default: 1.0) |
| `blocks.34.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 34 interpolation (default: 1.0) |
| `blocks.35.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 35 interpolation (default: 1.0) |
| `blocks.36.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 36 interpolation (default: 1.0) |
| `blocks.37.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 37 interpolation (default: 1.0) |
| `blocks.38.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 38 interpolation (default: 1.0) |
| `blocks.39.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 39 interpolation (default: 1.0) |
| `blocks.40.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 40 interpolation (default: 1.0) |
| `blocks.41.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 41 interpolation (default: 1.0) |
| `blocks.42.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 42 interpolation (default: 1.0) |
| `blocks.43.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 43 interpolation (default: 1.0) |
| `blocks.44.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 44 interpolation (default: 1.0) |
| `blocks.45.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 45 interpolation (default: 1.0) |
| `blocks.46.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 46 interpolation (default: 1.0) |
| `blocks.47.` | FLOAT | Yes | 0.0 - 1.0 | Weight for block 47 interpolation (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Weight for final layer interpolation (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models according to the specified weights |
