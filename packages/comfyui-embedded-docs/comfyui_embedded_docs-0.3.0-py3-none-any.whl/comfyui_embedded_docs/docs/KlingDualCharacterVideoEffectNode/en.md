> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/KlingDualCharacterVideoEffectNode/en.md)

The Kling Dual Character Video Effect Node creates videos with special effects based on the selected scene. It takes two images and positions the first image on the left side and the second image on the right side of the composite video. Different visual effects are applied depending on the chosen effect scene.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image_left` | IMAGE | Yes | - | Left side image |
| `image_right` | IMAGE | Yes | - | Right side image |
| `effect_scene` | COMBO | Yes | Multiple options available | The type of special effect scene to apply to the video generation |
| `model_name` | COMBO | No | Multiple options available | The model to use for character effects (default: "kling-v1") |
| `mode` | COMBO | No | Multiple options available | The video generation mode (default: "std") |
| `duration` | COMBO | Yes | Multiple options available | The duration of the generated video |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video with dual character effects |
| `duration` | STRING | The duration information of the generated video |
