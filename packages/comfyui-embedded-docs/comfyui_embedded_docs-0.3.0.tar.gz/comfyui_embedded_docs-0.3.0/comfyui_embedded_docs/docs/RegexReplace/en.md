> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RegexReplace/en.md)

The RegexReplace node finds and replaces text in strings using regular expression patterns. It allows you to search for text patterns and replace them with new text, with options to control how the pattern matching works including case sensitivity, multiline matching, and limiting the number of replacements.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The input text string to search and replace within |
| `regex_pattern` | STRING | Yes | - | The regular expression pattern to search for in the input string |
| `replace` | STRING | Yes | - | The replacement text to substitute for matched patterns |
| `case_insensitive` | BOOLEAN | No | - | When enabled, makes the pattern matching ignore case differences (default: True) |
| `multiline` | BOOLEAN | No | - | When enabled, changes the behavior of ^ and $ to match at the start/end of each line rather than just the start/end of the entire string (default: False) |
| `dotall` | BOOLEAN | No | - | When enabled, the dot (.) character will match any character including newline characters. When disabled, dots won't match newlines (default: False) |
| `count` | INT | No | 0-100 | Maximum number of replacements to make. Set to 0 to replace all occurrences (default). Set to 1 to replace only the first match, 2 for the first two matches, etc. (default: 0) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The modified string with the specified replacements applied |
