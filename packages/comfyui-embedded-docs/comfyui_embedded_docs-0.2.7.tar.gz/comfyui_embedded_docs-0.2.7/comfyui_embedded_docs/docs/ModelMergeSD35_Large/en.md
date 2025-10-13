> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeSD35_Large/en.md)

The ModelMergeSD35_Large node allows you to blend two Stable Diffusion 3.5 Large models together by adjusting the influence of different model components. It provides precise control over how much each part of the second model contributes to the final merged model, from embedding layers to joint blocks and final layers.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The base model that serves as the foundation for merging |
| `model2` | MODEL | Yes | - | The secondary model whose components will be blended into the base model |
| `pos_embed.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the position embedding from model2 is blended into the merged model (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the x embedder from model2 is blended into the merged model (default: 1.0) |
| `context_embedder.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the context embedder from model2 is blended into the merged model (default: 1.0) |
| `y_embedder.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the y embedder from model2 is blended into the merged model (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the t embedder from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.0.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 0 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.1.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 1 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.2.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 2 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.3.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 3 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.4.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 4 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.5.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 5 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.6.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 6 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.7.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 7 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.8.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 8 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.9.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 9 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.10.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 10 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.11.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 11 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.12.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 12 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.13.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 13 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.14.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 14 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.15.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 15 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.16.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 16 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.17.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 17 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.18.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 18 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.19.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 19 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.20.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 20 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.21.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 21 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.22.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 22 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.23.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 23 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.24.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 24 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.25.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 25 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.26.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 26 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.27.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 27 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.28.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 28 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.29.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 29 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.30.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 30 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.31.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 31 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.32.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 32 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.33.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 33 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.34.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 34 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.35.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 35 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.36.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 36 from model2 is blended into the merged model (default: 1.0) |
| `joint_blocks.37.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of joint block 37 from model2 is blended into the merged model (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 to 1.0 | Controls how much of the final layer from model2 is blended into the merged model (default: 1.0) |

**Note:** All blend parameters accept values from 0.0 to 1.0, where 0.0 means no contribution from model2 and 1.0 means full contribution from model2 for that specific component.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The resulting merged model combining features from both input models according to the specified blend parameters |
