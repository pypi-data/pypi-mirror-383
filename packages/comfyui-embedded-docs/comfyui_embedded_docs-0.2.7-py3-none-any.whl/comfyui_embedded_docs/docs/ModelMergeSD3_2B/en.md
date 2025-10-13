> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeSD3_2B/en.md)

The ModelMergeSD3_2B node allows you to merge two Stable Diffusion 3 2B models by blending their components with adjustable weights. It provides individual control over embedding layers and transformer blocks, enabling fine-tuned model combinations for specialized generation tasks.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge |
| `model2` | MODEL | Yes | - | The second model to merge |
| `pos_embed.` | FLOAT | Yes | 0.0 - 1.0 | Position embedding interpolation weight (default: 1.0) |
| `x_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Input embedding interpolation weight (default: 1.0) |
| `context_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Context embedding interpolation weight (default: 1.0) |
| `y_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Y embedding interpolation weight (default: 1.0) |
| `t_embedder.` | FLOAT | Yes | 0.0 - 1.0 | Time embedding interpolation weight (default: 1.0) |
| `joint_blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 0 interpolation weight (default: 1.0) |
| `joint_blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 1 interpolation weight (default: 1.0) |
| `joint_blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 2 interpolation weight (default: 1.0) |
| `joint_blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 3 interpolation weight (default: 1.0) |
| `joint_blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 4 interpolation weight (default: 1.0) |
| `joint_blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 5 interpolation weight (default: 1.0) |
| `joint_blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 6 interpolation weight (default: 1.0) |
| `joint_blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 7 interpolation weight (default: 1.0) |
| `joint_blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 8 interpolation weight (default: 1.0) |
| `joint_blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 9 interpolation weight (default: 1.0) |
| `joint_blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 10 interpolation weight (default: 1.0) |
| `joint_blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 11 interpolation weight (default: 1.0) |
| `joint_blocks.12.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 12 interpolation weight (default: 1.0) |
| `joint_blocks.13.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 13 interpolation weight (default: 1.0) |
| `joint_blocks.14.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 14 interpolation weight (default: 1.0) |
| `joint_blocks.15.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 15 interpolation weight (default: 1.0) |
| `joint_blocks.16.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 16 interpolation weight (default: 1.0) |
| `joint_blocks.17.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 17 interpolation weight (default: 1.0) |
| `joint_blocks.18.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 18 interpolation weight (default: 1.0) |
| `joint_blocks.19.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 19 interpolation weight (default: 1.0) |
| `joint_blocks.20.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 20 interpolation weight (default: 1.0) |
| `joint_blocks.21.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 21 interpolation weight (default: 1.0) |
| `joint_blocks.22.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 22 interpolation weight (default: 1.0) |
| `joint_blocks.23.` | FLOAT | Yes | 0.0 - 1.0 | Joint block 23 interpolation weight (default: 1.0) |
| `final_layer.` | FLOAT | Yes | 0.0 - 1.0 | Final layer interpolation weight (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining features from both input models |
