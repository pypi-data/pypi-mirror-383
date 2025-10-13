> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeHiDream/en.md)

The CLIPTextEncodeHiDream node processes multiple text inputs using different language models and combines them into a single conditioning output. It tokenizes text from four different sources (CLIP-L, CLIP-G, T5-XXL, and LLaMA) and encodes them using a scheduled encoding approach. This allows for more sophisticated text conditioning by leveraging multiple language models simultaneously.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | Required Input | - | - | The CLIP model used for tokenization and encoding |
| `clip_l` | STRING | Multiline Text | - | - | Text input for CLIP-L model processing |
| `clip_g` | STRING | Multiline Text | - | - | Text input for CLIP-G model processing |
| `t5xxl` | STRING | Multiline Text | - | - | Text input for T5-XXL model processing |
| `llama` | STRING | Multiline Text | - | - | Text input for LLaMA model processing |

**Note:** All text inputs support dynamic prompts and multiline text entry. The node requires all four text parameters to be provided for proper functioning, as each contributes to the final conditioning output through the scheduled encoding process.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The combined conditioning output from all processed text inputs |
