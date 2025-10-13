> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RegexMatch/en.md)

The RegexMatch node checks if a text string matches a specified regular expression pattern. It searches the input string for any occurrence of the regex pattern and returns whether a match was found. You can configure various regex flags like case sensitivity, multiline mode, and dotall mode to control how the pattern matching behaves.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The text string to search for matches |
| `regex_pattern` | STRING | Yes | - | The regular expression pattern to match against the string |
| `case_insensitive` | BOOLEAN | No | - | Whether to ignore case when matching (default: True) |
| `multiline` | BOOLEAN | No | - | Whether to enable multiline mode for regex matching (default: False) |
| `dotall` | BOOLEAN | No | - | Whether to enable dotall mode for regex matching (default: False) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `matches` | BOOLEAN | Returns True if the regex pattern matches any part of the input string, False otherwise |
