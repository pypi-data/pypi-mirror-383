> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CreateHookKeyframesInterpolated/en.md)

Creates a sequence of hook keyframes with interpolated strength values between a start and end point. The node generates multiple keyframes that smoothly transition the strength parameter across a specified percentage range of the generation process, using various interpolation methods to control the transition curve.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `strength_start` | FLOAT | Yes | 0.0 - 10.0 | The starting strength value for the interpolation sequence (default: 1.0) |
| `strength_end` | FLOAT | Yes | 0.0 - 10.0 | The ending strength value for the interpolation sequence (default: 1.0) |
| `interpolation` | COMBO | Yes | Multiple options available | The interpolation method used to transition between strength values |
| `start_percent` | FLOAT | Yes | 0.0 - 1.0 | The starting percentage position in the generation process (default: 0.0) |
| `end_percent` | FLOAT | Yes | 0.0 - 1.0 | The ending percentage position in the generation process (default: 1.0) |
| `keyframes_count` | INT | Yes | 2 - 100 | The number of keyframes to generate in the interpolation sequence (default: 5) |
| `print_keyframes` | BOOLEAN | Yes | True/False | Whether to print generated keyframe information to the log (default: False) |
| `prev_hook_kf` | HOOK_KEYFRAMES | No | - | Optional previous hook keyframes group to append to |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `HOOK_KF` | HOOK_KEYFRAMES | The generated hook keyframes group containing the interpolated sequence |
