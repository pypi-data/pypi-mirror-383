> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringContains/en.md)

The StringContains node checks if a given string contains a specified substring. It can perform this check with either case-sensitive or case-insensitive matching, returning a boolean result indicating whether the substring was found within the main string.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The main text string to search within |
| `substring` | STRING | Yes | - | The text to search for within the main string |
| `case_sensitive` | BOOLEAN | No | - | Determines whether the search should be case-sensitive (default: true) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `contains` | BOOLEAN | Returns true if the substring is found in the string, false otherwise |
