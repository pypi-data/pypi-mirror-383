> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringConcatenate/en.md)

The StringConcatenate node combines two text strings into one by joining them with a specified delimiter. It takes two input strings and a delimiter character or string, then outputs a single string where the two inputs are connected with the delimiter placed between them.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string_a` | STRING | Yes | - | The first text string to concatenate |
| `string_b` | STRING | Yes | - | The second text string to concatenate |
| `delimiter` | STRING | No | - | The character or string to insert between the two input strings (default: empty string) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The combined string with the delimiter inserted between string_a and string_b |
