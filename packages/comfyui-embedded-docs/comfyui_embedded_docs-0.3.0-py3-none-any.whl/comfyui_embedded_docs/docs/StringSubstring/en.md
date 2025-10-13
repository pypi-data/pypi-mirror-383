> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringSubstring/en.md)

The StringSubstring node extracts a portion of text from a larger string. It takes a starting position and ending position to define the section you want to extract, then returns the text between those two positions.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The input text string to extract from |
| `start` | INT | Yes | - | The starting position index for the substring |
| `end` | INT | Yes | - | The ending position index for the substring |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The extracted substring from the input text |
