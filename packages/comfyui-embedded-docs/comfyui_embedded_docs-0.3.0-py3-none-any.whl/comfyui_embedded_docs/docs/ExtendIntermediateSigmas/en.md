> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/ExtendIntermediateSigmas/en.md)

The ExtendIntermediateSigmas node takes an existing sequence of sigma values and inserts additional intermediate sigma values between them. It allows you to specify how many extra steps to add, the spacing method for interpolation, and optional start and end sigma boundaries to control where the extension occurs within the sigma sequence.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `sigmas` | SIGMAS | Yes | - | The input sigma sequence to extend with intermediate values |
| `steps` | INT | Yes | 1-100 | Number of intermediate steps to insert between existing sigmas (default: 2) |
| `start_at_sigma` | FLOAT | Yes | -1.0 to 20000.0 | Upper sigma boundary for extension - only extend sigmas below this value (default: -1.0, which means infinity) |
| `end_at_sigma` | FLOAT | Yes | 0.0 to 20000.0 | Lower sigma boundary for extension - only extend sigmas above this value (default: 12.0) |
| `spacing` | COMBO | Yes | "linear"<br>"cosine"<br>"sine" | The interpolation method for spacing the intermediate sigma values |

**Note:** The node only inserts intermediate sigmas between existing sigma pairs where both the current sigma is less than or equal to `start_at_sigma` and greater than or equal to `end_at_sigma`. When `start_at_sigma` is set to -1.0, it's treated as infinity, meaning only the `end_at_sigma` lower boundary applies.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sigmas` | SIGMAS | The extended sigma sequence with additional intermediate values inserted |
