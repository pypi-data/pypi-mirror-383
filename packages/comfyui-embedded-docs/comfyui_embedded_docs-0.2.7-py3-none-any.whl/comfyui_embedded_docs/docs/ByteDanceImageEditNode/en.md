> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ByteDanceImageEditNode/en.md)

The ByteDance Image Edit node allows you to modify images using ByteDance's AI models through an API. You provide an input image and a text prompt describing the desired changes, and the node processes the image according to your instructions. The node handles the API communication automatically and returns the edited image.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | COMBO | seededit_3 | Image2ImageModelName options | Model name |
| `image` | IMAGE | IMAGE | - | - | The base image to edit |
| `prompt` | STRING | STRING | "" | - | Instruction to edit image |
| `seed` | INT | INT | 0 | 0-2147483647 | Seed to use for generation |
| `guidance_scale` | FLOAT | FLOAT | 5.5 | 1.0-10.0 | Higher value makes the image follow the prompt more closely |
| `watermark` | BOOLEAN | BOOLEAN | True | - | Whether to add an "AI generated" watermark to the image |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `IMAGE` | IMAGE | The edited image returned from the ByteDance API |
