> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/WanImageToImageApi/en.md)

The Wan Image to Image node generates an image from one or two input images and a text prompt. It transforms your input images based on the description you provide, creating a new image that maintains the aspect ratio of your original input. The output image is fixed at 1.6 megapixels regardless of the input size.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | COMBO | Yes | "wan2.5-i2i-preview" | Model to use (default: "wan2.5-i2i-preview"). |
| `image` | IMAGE | Yes | - | Single-image editing or multi-image fusion, maximum 2 images. |
| `prompt` | STRING | Yes | - | Prompt used to describe the elements and visual features, supports English/Chinese (default: empty). |
| `negative_prompt` | STRING | No | - | Negative text prompt to guide what to avoid (default: empty). |
| `seed` | INT | No | 0 to 2147483647 | Seed to use for generation (default: 0). |
| `watermark` | BOOLEAN | No | - | Whether to add an "AI generated" watermark to the result (default: true). |

**Note:** This node accepts exactly 1 or 2 input images. If you provide more than 2 images or no images at all, the node will return an error.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `image` | IMAGE | The generated image based on the input images and text prompts. |
