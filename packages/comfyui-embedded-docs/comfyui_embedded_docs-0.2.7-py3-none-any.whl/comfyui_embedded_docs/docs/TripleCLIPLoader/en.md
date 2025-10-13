> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TripleCLIPLoader/en.md)

The TripleCLIPLoader node loads three different text encoder models simultaneously and combines them into a single CLIP model. This is useful for advanced text encoding scenarios where multiple text encoders are needed, such as in SD3 workflows that require clip-l, clip-g, and t5 models working together.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip_name1` | STRING | Yes | Multiple options available | The first text encoder model to load from the available text encoders |
| `clip_name2` | STRING | Yes | Multiple options available | The second text encoder model to load from the available text encoders |
| `clip_name3` | STRING | Yes | Multiple options available | The third text encoder model to load from the available text encoders |

**Note:** All three text encoder parameters must be selected from the available text encoder models in your system. The node will load all three models and combine them into a single CLIP model for processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CLIP` | CLIP | A combined CLIP model containing all three loaded text encoders |
