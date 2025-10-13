> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/TextEncodeAceStepAudio/en.md)

The TextEncodeAceStepAudio node processes text inputs for audio conditioning by combining tags and lyrics into tokens, then encoding them with adjustable lyrics strength. It takes a CLIP model along with text descriptions and lyrics, tokenizes them together, and generates conditioning data suitable for audio generation tasks. The node allows fine-tuning the influence of lyrics through a strength parameter that controls their impact on the final output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `clip` | CLIP | Yes | - | The CLIP model used for tokenization and encoding |
| `tags` | STRING | Yes | - | Text tags or descriptions for audio conditioning (supports multiline input and dynamic prompts) |
| `lyrics` | STRING | Yes | - | Lyrics text for audio conditioning (supports multiline input and dynamic prompts) |
| `lyrics_strength` | FLOAT | No | 0.0 - 10.0 | Controls the strength of lyrics influence on the conditioning output (default: 1.0, step: 0.01) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `conditioning` | CONDITIONING | The encoded conditioning data containing processed text tokens with applied lyrics strength |
