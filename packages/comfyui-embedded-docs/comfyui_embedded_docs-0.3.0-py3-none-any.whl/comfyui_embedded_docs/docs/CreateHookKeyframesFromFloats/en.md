> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookKeyframesFromFloats/en.md)

This node creates hook keyframes from a list of floating-point strength values, distributing them evenly between specified start and end percentages. It generates a sequence of keyframes where each strength value is assigned to a specific percentage position in the animation timeline. The node can either create a new keyframe group or add to an existing one, with an option to print the generated keyframes for debugging purposes.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `floats_strength` | FLOATS | Yes | -1 to ∞ | A single float value or list of float values representing strength values for the keyframes (default: -1) |
| `start_percent` | FLOAT | Yes | 0.0 to 1.0 | The starting percentage position for the first keyframe in the timeline (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 to 1.0 | The ending percentage position for the last keyframe in the timeline (default: 1.0) |
| `print_keyframes` | BOOLEAN | Yes | True/False | When enabled, prints the generated keyframe information to the console (default: False) |
| `prev_hook_kf` | HOOK_KEYFRAMES | No | - | An existing hook keyframe group to add the new keyframes to, or creates a new group if not provided |

**Note:** The `floats_strength` parameter accepts either a single float value or an iterable list of floats. The keyframes are distributed linearly between `start_percent` and `end_percent` based on the number of strength values provided.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOK_KF` | HOOK_KEYFRAMES | A hook keyframe group containing the newly created keyframes, either as a new group or appended to the input keyframe group |
