> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetHookKeyframes/en.md)

The Set Hook Keyframes node allows you to apply keyframe scheduling to existing hook groups. It takes a hook group and optionally applies keyframe timing information to control when different hooks are executed during the generation process. When keyframes are provided, the node clones the hook group and sets the keyframe timing on all hooks within the group.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `hooks` | HOOKS | Yes | - | The hook group to which keyframe scheduling will be applied |
| `hook_kf` | HOOK_KEYFRAMES | No | - | Optional keyframe group containing timing information for hook execution |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `hooks` | HOOKS | The modified hook group with keyframe scheduling applied (cloned if keyframes were provided) |
