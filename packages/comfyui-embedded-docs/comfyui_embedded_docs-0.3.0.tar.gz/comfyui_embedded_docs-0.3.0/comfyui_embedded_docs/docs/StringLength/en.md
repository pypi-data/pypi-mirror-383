> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringLength/en.md)

The StringLength node calculates the number of characters in a text string. It takes any text input and returns the total count of characters, including spaces and punctuation. This is useful for measuring text length or validating string size requirements.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | N/A | The text string to measure the length of. Supports multiline input. |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `length` | INT | The total number of characters in the input string, including spaces and special characters. |
