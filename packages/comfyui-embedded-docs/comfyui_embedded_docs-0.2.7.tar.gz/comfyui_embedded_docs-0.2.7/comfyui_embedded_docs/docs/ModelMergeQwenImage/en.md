> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ModelMergeQwenImage/en.md)

The ModelMergeQwenImage node merges two AI models by combining their components with adjustable weights. It allows you to blend specific parts of Qwen image models, including transformer blocks, positional embeddings, and text processing components. You can control how much influence each model has on different sections of the merged result.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model1` | MODEL | Yes | - | The first model to merge (default: none) |
| `model2` | MODEL | Yes | - | The second model to merge (default: none) |
| `pos_embeds.` | FLOAT | Yes | 0.0 to 1.0 | Weight for positional embeddings blending (default: 1.0) |
| `img_in.` | FLOAT | Yes | 0.0 to 1.0 | Weight for image input processing blending (default: 1.0) |
| `txt_norm.` | FLOAT | Yes | 0.0 to 1.0 | Weight for text normalization blending (default: 1.0) |
| `txt_in.` | FLOAT | Yes | 0.0 to 1.0 | Weight for text input processing blending (default: 1.0) |
| `time_text_embed.` | FLOAT | Yes | 0.0 to 1.0 | Weight for time and text embedding blending (default: 1.0) |
| `transformer_blocks.0.` to `transformer_blocks.59.` | FLOAT | Yes | 0.0 to 1.0 | Weight for each transformer block blending (default: 1.0) |
| `proj_out.` | FLOAT | Yes | 0.0 to 1.0 | Weight for output projection blending (default: 1.0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `model` | MODEL | The merged model combining components from both input models with the specified weights |
