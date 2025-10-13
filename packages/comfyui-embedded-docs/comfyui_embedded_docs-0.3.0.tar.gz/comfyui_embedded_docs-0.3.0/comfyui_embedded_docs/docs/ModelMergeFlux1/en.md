> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeFlux1/en.md)

The ModelMergeFlux1 node merges two diffusion models by blending their components using weighted interpolation. It allows fine-grained control over how different parts of the models are combined, including image processing blocks, time embedding layers, guidance mechanisms, vector inputs, text encoders, and various transformer blocks. This enables creating hybrid models with customized characteristics from two source models.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | First source model to merge |
| `model2` | MODEL | Yes | - | Second source model to merge |
| `img_in.` | FLOAT | Yes | 0.0 to 1.0 | Image input interpolation weight (default: 1.0) |
| `time_in.` | FLOAT | Yes | 0.0 to 1.0 | Time embedding interpolation weight (default: 1.0) |
| `guidance_in` | FLOAT | Yes | 0.0 to 1.0 | Guidance mechanism interpolation weight (default: 1.0) |
| `vector_in.` | FLOAT | Yes | 0.0 to 1.0 | Vector input interpolation weight (default: 1.0) |
| `txt_in.` | FLOAT | Yes | 0.0 to 1.0 | Text encoder interpolation weight (default: 1.0) |
| `double_blocks.0.` | FLOAT | Yes | 0.0 to 1.0 | Double block 0 interpolation weight (default: 1.0) |
| `double_blocks.1.` | FLOAT | Yes | 0.0 to 1.0 | Double block 1 interpolation weight (default: 1.0) |
| `double_blocks.2.` | FLOAT | Yes | 0.0 to 1.0 | Double block 2 interpolation weight (default: 1.0) |
| `double_blocks.3.` | FLOAT | Yes | 0.0 to 1.0 | Double block 3 interpolation weight (default: 1.0) |
| `double_blocks.4.` | FLOAT | Yes | 0.0 to 1.0 | Double block 4 interpolation weight (default: 1.0) |
| `double_blocks.5.` | FLOAT | Yes | 0.0 to 1.0 | Double block 5 interpolation weight (default: 1.0) |
| `double_blocks.6.` | FLOAT | Yes | 0.0 to 1.0 | Double block 6 interpolation weight (default: 1.0) |
| `double_blocks.7.` | FLOAT | Yes | 0.0 to 1.0 | Double block 7 interpolation weight (default: 1.0) |
| `double_blocks.8.` | FLOAT | Yes | 0.0 to 1.0 | Double block 8 interpolation weight (default: 1.0) |
| `double_blocks.9.` | FLOAT | Yes | 0.0 to 1.0 | Double block 9 interpolation weight (default: 1.0) |
| `double_blocks.10.` | FLOAT | Yes | 0.0 to 1.0 | Double block 10 interpolation weight (default: 1.0) |
| `double_blocks.11.` | FLOAT | Yes | 0.0 to 1.0 | Double block 11 interpolation weight (default: 1.0) |
| `double_blocks.12.` | FLOAT | Yes | 0.0 to 1.0 | Double block 12 interpolation weight (default: 1.0) |
| `double_blocks.13.` | FLOAT | Yes | 0.0 to 1.0 | Double block 13 interpolation weight (default: 1.0) |
| `double_blocks.14.` | FLOAT | Yes | 0.0 to 1.0 | Double block 14 interpolation weight (default: 1.0) |
| `double_blocks.15.` | FLOAT | Yes | 0.0 to 1.0 | Double block 15 interpolation weight (default: 1.0) |
| `double_blocks.16.` | FLOAT | Yes | 0.0 to 1.0 | Double block 16 interpolation weight (default: 1.0) |
| `double_blocks.17.` | FLOAT | Yes | 0.0 to 1.0 | Double block 17 interpolation weight (default: 1.0) |
| `double_blocks.18.` | FLOAT | Yes | 0.0 to 1.0 | Double block 18 interpolation weight (default: 1.0) |
| `single_blocks.0.` | FLOAT | Yes | 0.0 to 1.0 | Single block 0 interpolation weight (default: 1.0) |
| `single_blocks.1.` | FLOAT | Yes | 0.0 to 1.0 | Single block 1 interpolation weight (default: 1.0) |
| `single_blocks.2.` | FLOAT | Yes | 0.0 to 1.0 | Single block 2 interpolation weight (default: 1.0) |
| `single_blocks.3.` | FLOAT | Yes | 0.0 to 1.0 | Single block 3 interpolation weight (default: 1.0) |
| `single_blocks.4.` | FLOAT | Yes | 0.0 to 1.0 | Single block 4 interpolation weight (default: 1.0) |
| `single_blocks.5.` | FLOAT | Yes | 0.0 to 1.0 | Single block 5 interpolation weight (default: 1.0) |
| `single_blocks.6.` | FLOAT | Yes | 0.0 to 1.0 | Single block 6 interpolation weight (default: 1.0) |
| `single_blocks.7.` | FLOAT | Yes | 0.0 to 1.0 | Single block 7 interpolation weight (default: 1.0) |
| `single_blocks.8.` | FLOAT | Yes | 0.0 to 1.0 | Single block 8 interpolation weight (default: 1.0) |
| `single_blocks.9.` | FLOAT | Yes | 0.0 to 1.0 | Single block 9 interpolation weight (default: 1.0) |
| `single_blocks.10.` | FLOAT | Yes | 0.0 to 1.0 | Single block 10 interpolation weight (default: 1.0) |
| `single_blocks.11.` | FLOAT | Yes | 0.0 to 1.0 | Single block 11 interpolation weight (default: 1.0) |
| `single_blocks.12.` | FLOAT | Yes | 0.0 to 1.0 | Single block 12 interpolation weight (default: 1.0) |
| `single_blocks.13.` | FLOAT | Yes | 0.0 to 1.0 | Single block 13 interpolation weight (default: 1.0) |
| `single_blocks.14.` | FLOAT | Yes | 0.0 to 1.0 | Single block 14 interpolation weight (default: 1.0) |
| `single_blocks.15.` | FLOAT | Yes | 0.0 to 1.0 | Single block 15 interpolation weight (default: 1.0) |
| `single_blocks.16.` | FLOAT | Yes | 0.0 to 1.0 | Single block 16 interpolation weight (default: 1.0) |
| `single_blocks.17.` | FLOAT | Yes | 0.0 to 1.0 | Single block 17 interpolation weight (default: 1.0) |
| `single_blocks.18.` | FLOAT | Yes | 0.0 to 1.0 | Single block 18 interpolation weight (default: 1.0) |
| `single_blocks.19.` | FLOAT | Yes | 0.0 to 1.0 | Single block 19 interpolation weight (default: 1.0) |
| `single_blocks.20.` | FLOAT | Yes | 0.0 to 1.0 | Single block 20 interpolation weight (default: 1.0) |
| `single_blocks.21.` | FLOAT | Yes | 0.0 to 1.0 | Single block 21 interpolation weight (default: 1.0) |
| `single_blocks.22.` | FLOAT | Yes | 0.0 to 1.0 | Single block 22 interpolation weight (default: 1.0) |
| `single_blocks.23.` | FLOAT | Yes | 0.0 to 1.0 | Single block 23 interpolation weight (default: 1.0) |
| `single_blocks.24.` | FLOAT | Yes | 0.0 to 1.0 | Single block 24 interpolation weight (default: 1.0) |
| `single_blocks.25.` | FLOAT | Yes | 0.0 to 1.0 | Single block 25 interpolation weight (default: 1.0) |
| `single_blocks.26.` | FLOAT | Yes | 0.0 to 1.0 | Single block 26 interpolation weight (default: 1.0) |
| `single_blocks.27.` | FLOAT | Yes | 0.0 to 1.0 | Single block 27 interpolation weight (default: 1.0) |
| `single_blocks.28.` | FLOAT | Yes | 0.0 to 1.0 | Single block 28 interpolation weight (default: 1.0) |
| `single_blocks.29.` | FLOAT | Yes | 0.0 to 1.0 | Single block 29 interpolation weight (default: 1.0) |
| `single_blocks.30.` | FLOAT | Yes | 0.0 to 1.0 | Single block 30 interpolation weight (default: 1.0) |
| `single_blocks.31.` | FLOAT | Yes | 0.0 to 1.0 | Single block 31 interpolation weight (default: 1.0) |
| `single_blocks.32.` | FLOAT | Yes | 0.0 to 1.0 | Single block 32 interpolation weight (default: 1.0) |
| `single_blocks.33.` | FLOAT | Yes | 0.0 to 1.0 | Single block 33 interpolation weight (default: 1.0) |
| `single_blocks.34.` | FLOAT | Yes | 0.0 to 1.0 | Single block 34 interpolation weight (default: 1.0) |
| `single_blocks.35.` | FLOAT | Yes | 0.0 to 1.0 | Single block 35 interpolation weight (default: 1.0) |
| `single_blocks.36.` | FLOAT | Yes | 0.0 to 1.0 | Single block 36 interpolation weight (default: 1.0) |
| `single_blocks.37.` | FLOAT | Yes | 0.0 to 1.0 | Single block 37 interpolation weight (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 to 1.0 | Final layer interpolation weight (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining characteristics from both input models |
