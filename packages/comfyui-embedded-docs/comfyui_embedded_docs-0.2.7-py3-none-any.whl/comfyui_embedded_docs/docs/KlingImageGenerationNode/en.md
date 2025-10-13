> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingImageGenerationNode/en.md)

Kling Image Generation Node generates images from text prompts with the option to use a reference image for guidance. It creates one or more images based on your text description and reference settings, then returns the generated images as output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt` | STRING | Yes | - | Positive text prompt |
| `negative_prompt` | STRING | Yes | - | Negative text prompt |
| `image_type` | COMBO | Yes | Options from KlingImageGenImageReferenceType<br>(extracted from source code) | Image reference type selection |
| `image_fidelity` | FLOAT | Yes | 0.0 - 1.0 | Reference intensity for user-uploaded images (default: 0.5) |
| `human_fidelity` | FLOAT | Yes | 0.0 - 1.0 | Subject reference similarity (default: 0.45) |
| `model_name` | COMBO | Yes | "kling-v1"<br>(and other options from KlingImageGenModelName) | Model selection for image generation (default: "kling-v1") |
| `aspect_ratio` | COMBO | Yes | "16:9"<br>(and other options from KlingImageGenAspectRatio) | Aspect ratio for generated images (default: "16:9") |
| `n` | INT | Yes | 1 - 9 | Number of generated images (default: 1) |
| `image` | IMAGE | No | - | Optional reference image |

**Parameter Constraints:**

- The `image` parameter is optional, but when provided, the kling-v1 model does not support reference images
- Prompt and negative prompt have maximum length limitations (MAX_PROMPT_LENGTH_IMAGE_GEN)
- When no reference image is provided, the `image_type` parameter is automatically set to None

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | IMAGE | Generated image(s) based on the input parameters |
