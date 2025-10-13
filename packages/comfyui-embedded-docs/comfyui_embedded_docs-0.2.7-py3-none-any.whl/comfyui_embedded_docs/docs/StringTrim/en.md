> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringTrim/en.md)

The StringTrim node removes whitespace characters from the beginning, end, or both sides of a text string. You can choose to trim from the left side, right side, or both sides of the string. This is useful for cleaning up text inputs by removing unwanted spaces, tabs, or newline characters.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The text string to process. Supports multiline input. |
| `mode` | COMBO | Yes | "Both"<br>"Left"<br>"Right" | Specifies which side(s) of the string to trim. "Both" removes whitespace from both ends, "Left" removes from the beginning only, "Right" removes from the end only. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The trimmed text string with whitespace removed according to the selected mode. |
