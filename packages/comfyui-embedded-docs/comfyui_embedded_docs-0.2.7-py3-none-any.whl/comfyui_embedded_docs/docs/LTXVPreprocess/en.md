> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LTXVPreprocess/en.md)

The LTXVPreprocess node applies compression preprocessing to images. It takes input images and processes them with a specified compression level, outputting the processed images with the applied compression settings.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The input image to be processed |
| `img_compression` | INT | No | 0-100 | Amount of compression to apply on image (default: 35) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output_image` | IMAGE | The processed output image with applied compression |
