> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CLIPTextEncodeSD3/en.md)

The CLIPTextEncodeSD3 node processes text inputs for Stable Diffusion 3 models by encoding multiple text prompts using different CLIP models. It handles three separate text inputs (clip_g, clip_l, and t5xxl) and provides options for managing empty text padding. The node ensures proper token alignment between different text inputs and returns conditioning data suitable for SD3 generation pipelines.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `clip` | CLIP | Required | - | - | The CLIP model used for text encoding |
| `clip_l` | STRING | Multiline, Dynamic Prompts | - | - | Text input for the local CLIP model |
| `clip_g` | STRING | Multiline, Dynamic Prompts | - | - | Text input for the global CLIP model |
| `t5xxl` | STRING | Multiline, Dynamic Prompts | - | - | Text input for the T5-XXL model |
| `empty_padding` | COMBO | Selection | - | ["none", "empty_prompt"] | Controls how empty text inputs are handled |

**Parameter Constraints:**

- When `empty_padding` is set to "none", empty text inputs for `clip_g`, `clip_l`, or `t5xxl` will result in empty token lists instead of padding
- The node automatically balances token lengths between `clip_l` and `clip_g` inputs by padding the shorter one with empty tokens when lengths differ
- All text inputs support dynamic prompts and multiline text entry

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The encoded text conditioning data ready for use in SD3 generation pipelines |
