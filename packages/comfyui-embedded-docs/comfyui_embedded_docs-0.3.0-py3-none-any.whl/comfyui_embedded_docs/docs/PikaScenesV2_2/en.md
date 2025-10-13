> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/PikaScenesV2_2/en.md)

The PikaScenes v2.2 node combines multiple images to create a video that incorporates objects from all the input images. You can upload up to five different images as ingredients and generate a high-quality video that blends them together seamlessly.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `prompt_text` | STRING | Yes | - | Text description of what to generate |
| `negative_prompt` | STRING | Yes | - | Text description of what to avoid in the generation |
| `seed` | INT | Yes | - | Random seed value for generation |
| `resolution` | STRING | Yes | - | Output resolution for the video |
| `duration` | INT | Yes | - | Duration of the generated video |
| `ingredients_mode` | COMBO | No | "creative"<br>"precise" | Mode for combining ingredients (default: "creative") |
| `aspect_ratio` | FLOAT | No | 0.4 - 2.5 | Aspect ratio (width / height) (default: 1.778) |
| `image_ingredient_1` | IMAGE | No | - | Image that will be used as ingredient to create a video |
| `image_ingredient_2` | IMAGE | No | - | Image that will be used as ingredient to create a video |
| `image_ingredient_3` | IMAGE | No | - | Image that will be used as ingredient to create a video |
| `image_ingredient_4` | IMAGE | No | - | Image that will be used as ingredient to create a video |
| `image_ingredient_5` | IMAGE | No | - | Image that will be used as ingredient to create a video |

**Note:** You can provide up to 5 image ingredients, but at least one image is required to generate a video. The node will use all provided images to create the final video composition.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video combining all input images |
