> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeAuraflow/en.md)

The ModelMergeAuraflow node allows you to blend two different models together by adjusting specific blending weights for various model components. It provides fine-grained control over how different parts of the models are merged, from initial layers to final outputs. This node is particularly useful for creating custom model combinations with precise control over the merging process.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to be merged |
| `model2` | MODEL | Yes | - | The second model to be merged |
| `init_x_linear.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for the initial linear transformation (default: 1.0) |
| `positional_encoding` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for positional encoding components (default: 1.0) |
| `cond_seq_linear.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for conditional sequence linear layers (default: 1.0) |
| `register_tokens` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for token registration components (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for time embedding components (default: 1.0) |
| `double_layers.0.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for double layer group 0 (default: 1.0) |
| `double_layers.1.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for double layer group 1 (default: 1.0) |
| `double_layers.2.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for double layer group 2 (default: 1.0) |
| `double_layers.3.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for double layer group 3 (default: 1.0) |
| `single_layers.0.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 0 (default: 1.0) |
| `single_layers.1.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 1 (default: 1.0) |
| `single_layers.2.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 2 (default: 1.0) |
| `single_layers.3.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 3 (default: 1.0) |
| `single_layers.4.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 4 (default: 1.0) |
| `single_layers.5.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 5 (default: 1.0) |
| `single_layers.6.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 6 (default: 1.0) |
| `single_layers.7.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 7 (default: 1.0) |
| `single_layers.8.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 8 (default: 1.0) |
| `single_layers.9.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 9 (default: 1.0) |
| `single_layers.10.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 10 (default: 1.0) |
| `single_layers.11.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 11 (default: 1.0) |
| `single_layers.12.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 12 (default: 1.0) |
| `single_layers.13.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 13 (default: 1.0) |
| `single_layers.14.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 14 (default: 1.0) |
| `single_layers.15.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 15 (default: 1.0) |
| `single_layers.16.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 16 (default: 1.0) |
| `single_layers.17.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 17 (default: 1.0) |
| `single_layers.18.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 18 (default: 1.0) |
| `single_layers.19.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 19 (default: 1.0) |
| `single_layers.20.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 20 (default: 1.0) |
| `single_layers.21.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 21 (default: 1.0) |
| `single_layers.22.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 22 (default: 1.0) |
| `single_layers.23.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 23 (default: 1.0) |
| `single_layers.24.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 24 (default: 1.0) |
| `single_layers.25.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 25 (default: 1.0) |
| `single_layers.26.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 26 (default: 1.0) |
| `single_layers.27.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 27 (default: 1.0) |
| `single_layers.28.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 28 (default: 1.0) |
| `single_layers.29.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 29 (default: 1.0) |
| `single_layers.30.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 30 (default: 1.0) |
| `single_layers.31.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for single layer 31 (default: 1.0) |
| `modF.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for modF components (default: 1.0) |
| `final_linear.` | FLOAT | Yes | 0.0 - 1.0 | Blending weight for final linear transformation (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models according to the specified blending weights |
