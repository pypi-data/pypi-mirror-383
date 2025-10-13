> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PhotoMakerEncode/en.md)

The PhotoMakerEncode node processes images and text to generate conditioning data for AI image generation. It takes a reference image and text prompt, then creates embeddings that can be used to guide image generation based on the visual characteristics of the reference image. The node specifically looks for the "photomaker" token in the text to determine where to apply the image-based conditioning.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `photomaker` | PHOTOMAKER | Yes | - | The PhotoMaker model used for processing the image and generating embeddings |
| `image` | IMAGE | Yes | - | The reference image that provides visual characteristics for conditioning |
| `clip` | CLIP | Yes | - | The CLIP model used for text tokenization and encoding |
| `text` | STRING | Yes | - | The text prompt for conditioning generation (default: "photograph of photomaker") |

**Note:** When the text contains the word "photomaker", the node applies image-based conditioning at that position in the prompt. If "photomaker" is not found in the text, the node generates standard text conditioning without image influence.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The conditioning data containing image and text embeddings for guiding image generation |
