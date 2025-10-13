> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetModelHooksOnCond/en.md)

This node attaches custom hooks to conditioning data, allowing you to intercept and modify the conditioning process during model execution. It takes a set of hooks and applies them to the provided conditioning data, enabling advanced customization of the text-to-image generation workflow. The modified conditioning with attached hooks is then returned for use in subsequent processing steps.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `conditioning` | CONDITIONING | Yes | - | The conditioning data to which hooks will be attached |
| `hooks` | HOOKS | Yes | - | The hook definitions that will be applied to the conditioning data |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The modified conditioning data with hooks attached |
