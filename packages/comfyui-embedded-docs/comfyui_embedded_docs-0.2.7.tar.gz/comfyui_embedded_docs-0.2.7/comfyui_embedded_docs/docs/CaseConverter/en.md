> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CaseConverter/en.md)

The Case Converter node transforms text strings into different letter case formats. It takes an input string and converts it based on the selected mode, producing an output string with the specified case formatting applied. The node supports four different case conversion options to modify the capitalization of your text.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `string` | STRING | String | - | - | The text string to be converted to a different case format |
| `mode` | STRING | Combo | - | ["UPPERCASE", "lowercase", "Capitalize", "Title Case"] | The case conversion mode to apply: UPPERCASE converts all letters to uppercase, lowercase converts all letters to lowercase, Capitalize capitalizes only the first letter, Title Case capitalizes the first letter of each word |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The input string converted to the specified case format |
