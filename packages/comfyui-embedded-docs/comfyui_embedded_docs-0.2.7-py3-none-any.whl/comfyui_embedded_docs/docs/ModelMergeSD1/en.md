> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeSD1/en.md)

The ModelMergeSD1 node allows you to blend two Stable Diffusion 1.x models together by adjusting the influence of different model components. It provides individual control over time embedding, label embedding, and all input, middle, and output blocks, enabling fine-tuned model merging for specific use cases.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge |
| `model2` | MODEL | Yes | - | The second model to merge |
| `time_embed.` | FLOAT | Yes | 0.0 - 1.0 | Time embedding layer blending weight (default: 1.0) |
| `label_emb.` | FLOAT | Yes | 0.0 - 1.0 | Label embedding layer blending weight (default: 1.0) |
| `input_blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Input block 0 blending weight (default: 1.0) |
| `input_blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Input block 1 blending weight (default: 1.0) |
| `input_blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Input block 2 blending weight (default: 1.0) |
| `input_blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Input block 3 blending weight (default: 1.0) |
| `input_blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Input block 4 blending weight (default: 1.0) |
| `input_blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Input block 5 blending weight (default: 1.0) |
| `input_blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Input block 6 blending weight (default: 1.0) |
| `input_blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Input block 7 blending weight (default: 1.0) |
| `input_blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Input block 8 blending weight (default: 1.0) |
| `input_blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Input block 9 blending weight (default: 1.0) |
| `input_blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Input block 10 blending weight (default: 1.0) |
| `input_blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Input block 11 blending weight (default: 1.0) |
| `middle_block.0.` | FLOAT | Yes | 0.0 - 1.0 | Middle block 0 blending weight (default: 1.0) |
| `middle_block.1.` | FLOAT | Yes | 0.0 - 1.0 | Middle block 1 blending weight (default: 1.0) |
| `middle_block.2.` | FLOAT | Yes | 0.0 - 1.0 | Middle block 2 blending weight (default: 1.0) |
| `output_blocks.0.` | FLOAT | Yes | 0.0 - 1.0 | Output block 0 blending weight (default: 1.0) |
| `output_blocks.1.` | FLOAT | Yes | 0.0 - 1.0 | Output block 1 blending weight (default: 1.0) |
| `output_blocks.2.` | FLOAT | Yes | 0.0 - 1.0 | Output block 2 blending weight (default: 1.0) |
| `output_blocks.3.` | FLOAT | Yes | 0.0 - 1.0 | Output block 3 blending weight (default: 1.0) |
| `output_blocks.4.` | FLOAT | Yes | 0.0 - 1.0 | Output block 4 blending weight (default: 1.0) |
| `output_blocks.5.` | FLOAT | Yes | 0.0 - 1.0 | Output block 5 blending weight (default: 1.0) |
| `output_blocks.6.` | FLOAT | Yes | 0.0 - 1.0 | Output block 6 blending weight (default: 1.0) |
| `output_blocks.7.` | FLOAT | Yes | 0.0 - 1.0 | Output block 7 blending weight (default: 1.0) |
| `output_blocks.8.` | FLOAT | Yes | 0.0 - 1.0 | Output block 8 blending weight (default: 1.0) |
| `output_blocks.9.` | FLOAT | Yes | 0.0 - 1.0 | Output block 9 blending weight (default: 1.0) |
| `output_blocks.10.` | FLOAT | Yes | 0.0 - 1.0 | Output block 10 blending weight (default: 1.0) |
| `output_blocks.11.` | FLOAT | Yes | 0.0 - 1.0 | Output block 11 blending weight (default: 1.0) |
| `out.` | FLOAT | Yes | 0.0 - 1.0 | Output layer blending weight (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `MODEL` | MODEL | The merged model combining features from both input models |
