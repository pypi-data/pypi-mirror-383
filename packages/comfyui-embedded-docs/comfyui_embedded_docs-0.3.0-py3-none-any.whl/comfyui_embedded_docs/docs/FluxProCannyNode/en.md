> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/FluxProCannyNode/en.md)

Generate image using a control image (canny). This node takes a control image and generates a new image based on the provided prompt while following the edge structure detected in the control image.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `control_image` | IMAGE | Yes | - | The input image used for canny edge detection control |
| `prompt` | STRING | No | - | Prompt for the image generation (default: empty string) |
| `prompt_upsampling` | BOOLEAN | No | - | Whether to perform upsampling on the prompt. If active, automatically modifies the prompt for more creative generation, but results are nondeterministic (same seed will not produce exactly the same result). (default: False) |
| `canny_low_threshold` | FLOAT | No | 0.01 - 0.99 | Low threshold for Canny edge detection; ignored if skip_processing is True (default: 0.1) |
| `canny_high_threshold` | FLOAT | No | 0.01 - 0.99 | High threshold for Canny edge detection; ignored if skip_processing is True (default: 0.4) |
| `skip_preprocessing` | BOOLEAN | No | - | Whether to skip preprocessing; set to True if control_image already is canny-fied, False if it is a raw image. (default: False) |
| `guidance` | FLOAT | No | 1 - 100 | Guidance strength for the image generation process (default: 30) |
| `steps` | INT | No | 15 - 50 | Number of steps for the image generation process (default: 50) |
| `seed` | INT | No | 0 - 18446744073709551615 | The random seed used for creating the noise. (default: 0) |

**Note:** When `skip_preprocessing` is set to True, the `canny_low_threshold` and `canny_high_threshold` parameters are ignored since the control image is assumed to already be processed as a canny edge image.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output_image` | IMAGE | The generated image based on the control image and prompt |
