> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/Pikaffects/en.md)

The Pikaffects node generates videos with various visual effects applied to an input image. It uses Pika's video generation API to transform static images into animated videos with specific effects like melting, exploding, or levitating. The node requires an API key and authentication token to access the Pika service.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `image` | IMAGE | Yes | - | The reference image to apply the Pikaffect to. |
| `pikaffect` | COMBO | Yes | "Cake-ify"<br>"Crumble"<br>"Crush"<br>"Decapitate"<br>"Deflate"<br>"Dissolve"<br>"Explode"<br>"Eye-pop"<br>"Inflate"<br>"Levitate"<br>"Melt"<br>"Peel"<br>"Poke"<br>"Squish"<br>"Ta-da"<br>"Tear" | The specific visual effect to apply to the image (default: "Cake-ify"). |
| `prompt_text` | STRING | Yes | - | Text description guiding the video generation. |
| `negative_prompt` | STRING | Yes | - | Text description of what to avoid in the generated video. |
| `seed` | INT | Yes | 0 to 4294967295 | Random seed value for reproducible results. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | VIDEO | The generated video with the applied Pikaffect. |
