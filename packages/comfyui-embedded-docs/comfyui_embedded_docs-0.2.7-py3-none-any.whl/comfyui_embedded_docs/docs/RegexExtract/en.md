> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/RegexExtract/en.md)

The RegexExtract node searches for patterns in text using regular expressions. It can find the first match, all matches, specific groups from matches, or all groups across multiple matches. The node supports various regex flags for case sensitivity, multiline matching, and dotall behavior.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `string` | STRING | Yes | - | The input text to search for patterns |
| `regex_pattern` | STRING | Yes | - | The regular expression pattern to search for |
| `mode` | COMBO | Yes | "First Match"<br>"All Matches"<br>"First Group"<br>"All Groups" | The extraction mode determines what parts of matches are returned |
| `case_insensitive` | BOOLEAN | No | - | Whether to ignore case when matching (default: True) |
| `multiline` | BOOLEAN | No | - | Whether to treat the string as multiple lines (default: False) |
| `dotall` | BOOLEAN | No | - | Whether the dot (.) matches newlines (default: False) |
| `group_index` | INT | No | 0-100 | The capture group index to extract when using group modes (default: 1) |

**Note:** When using "First Group" or "All Groups" modes, the `group_index` parameter specifies which capture group to extract. Group 0 represents the entire match, while groups 1+ represent the numbered capture groups in your regex pattern.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | STRING | The extracted text based on the selected mode and parameters |
