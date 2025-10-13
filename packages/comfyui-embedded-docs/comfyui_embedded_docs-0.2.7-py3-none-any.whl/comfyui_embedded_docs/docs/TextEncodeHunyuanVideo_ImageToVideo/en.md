> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TextEncodeHunyuanVideo_ImageToVideo/en.md)

The TextEncodeHunyuanVideo_ImageToVideo node creates conditioning data for video generation by combining text prompts with image embeddings. It uses a CLIP model to process both the text input and visual information from a CLIP vision output, then generates tokens that blend these two sources according to the specified image interleave setting.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model used for tokenization and encoding |
| `clip_vision_output` | CLIP_VISION_OUTPUT | Yes | - | The visual embeddings from a CLIP vision model that provide image context |
| `prompt` | STRING | Yes | - | The text description to guide the video generation, supports multiline input and dynamic prompts |
| `image_interleave` | INT | Yes | 1-512 | How much the image influences things vs the text prompt. Higher number means more influence from the text prompt. (default: 2) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `CONDITIONING` | CONDITIONING | The conditioning data that combines text and image information for video generation |
