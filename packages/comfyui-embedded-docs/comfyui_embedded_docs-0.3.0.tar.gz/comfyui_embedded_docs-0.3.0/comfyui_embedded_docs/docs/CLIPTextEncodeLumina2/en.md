> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeLumina2/en.md)

The CLIP Text Encode for Lumina2 node encodes a system prompt and a user prompt using a CLIP model into an embedding that can guide the diffusion model to generate specific images. It combines a pre-defined system prompt with your custom text prompt and processes them through the CLIP model to create conditioning data for image generation.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `system_prompt` | STRING | COMBO | - | "superior", "alignment" | Lumina2 provide two types of system prompts: Superior: You are an assistant designed to generate superior images with the superior degree of image-text alignment based on textual prompts or user prompts. Alignment: You are an assistant designed to generate high-quality images with the highest degree of image-text alignment based on textual prompts. |
| `user_prompt` | STRING | STRING | - | - | The text to be encoded. |
| `clip` | CLIP | CLIP | - | - | The CLIP model used for encoding the text. |

**Note:** The `clip` input is required and cannot be None. If the clip input is invalid, the node will raise an error indicating that the checkpoint may not contain a valid CLIP or text encoder model.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | A conditioning containing the embedded text used to guide the diffusion model. |
