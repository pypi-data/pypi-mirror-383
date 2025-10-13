> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SetUnionControlNetType/en.md)

The SetUnionControlNetType node allows you to specify the type of control network to use for conditioning. It takes an existing control network and sets its control type based on your selection, creating a modified copy of the control network with the specified type configuration.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `control_net` | CONTROL_NET | Yes | - | The control network to modify with a new type setting |
| `type` | STRING | Yes | `"auto"`<br>All available UNION_CONTROLNET_TYPES keys | The control network type to apply. Use "auto" for automatic type detection or select a specific control network type from the available options |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `control_net` | CONTROL_NET | The modified control network with the specified type setting applied |
