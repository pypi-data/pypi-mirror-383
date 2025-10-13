> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeControlnet/en.md)

The CLIPTextEncodeControlnet node processes text input using a CLIP model and combines it with existing conditioning data to create enhanced conditioning output for controlnet applications. It tokenizes the input text, encodes it through the CLIP model, and adds the resulting embeddings to the provided conditioning data as cross-attention controlnet parameters.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | Required | - | - | The CLIP model used for text tokenization and encoding |
| `conditioning` | CONDITIONING | Required | - | - | Existing conditioning data to be enhanced with controlnet parameters |
| `text` | STRING | Multiline, Dynamic Prompts | - | - | Text input to be processed by the CLIP model |

**Note:** This node requires both `clip` and `conditioning` inputs to function properly. The `text` input supports dynamic prompts and multiline text for flexible text processing.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | Enhanced conditioning data with added controlnet cross-attention parameters |
