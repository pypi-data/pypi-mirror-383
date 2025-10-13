> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/StringCompare/en.md)

The StringCompare node compares two text strings using different comparison methods. It can check if one string starts with another, ends with another, or if both strings are exactly equal. The comparison can be performed with or without considering letter case differences.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string_a` | STRING | Yes | - | The first string to compare |
| `string_b` | STRING | Yes | - | The second string to compare against |
| `mode` | COMBO | Yes | "Starts With"<br>"Ends With"<br>"Equal" | The comparison method to use |
| `case_sensitive` | BOOLEAN | No | - | Whether to consider letter case during comparison (default: true) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | BOOLEAN | Returns true if the comparison condition is met, false otherwise |
