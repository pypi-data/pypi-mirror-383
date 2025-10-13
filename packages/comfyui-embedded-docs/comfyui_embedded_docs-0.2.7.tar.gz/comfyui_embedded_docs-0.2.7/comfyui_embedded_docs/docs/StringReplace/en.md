> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringReplace/en.md)

The StringReplace node performs text replacement operations on input strings. It searches for a specified substring within the input text and replaces all occurrences with a different substring. This node returns the modified string with all replacements applied.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The input text string where replacements will be performed |
| `find` | STRING | Yes | - | The substring to search for within the input text |
| `replace` | STRING | Yes | - | The replacement text that will substitute all found occurrences |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The modified string with all occurrences of the find text replaced by the replace text |
