> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookKeyframe/en.md)

The Create Hook Keyframe node allows you to define specific points in a generation process where hook behavior changes. It creates keyframes that modify the strength of hooks at particular percentages of the generation progress, and these keyframes can be chained together to create complex scheduling patterns.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `strength_mult` | FLOAT | Yes | -20.0 to 20.0 | Multiplier for hook strength at this keyframe (default: 1.0) |
| `start_percent` | FLOAT | Yes | 0.0 to 1.0 | The percentage point in the generation process where this keyframe takes effect (default: 0.0) |
| `prev_hook_kf` | HOOK_KEYFRAMES | No | - | Optional previous hook keyframe group to add this keyframe to |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOK_KF` | HOOK_KEYFRAMES | A group of hook keyframes including the newly created keyframe |
