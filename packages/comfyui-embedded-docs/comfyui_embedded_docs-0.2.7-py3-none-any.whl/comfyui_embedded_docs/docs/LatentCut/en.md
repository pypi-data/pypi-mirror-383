> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LatentCut/en.md)

The LatentCut node extracts a specific section from latent samples along a chosen dimension. It allows you to cut out a portion of the latent representation by specifying the dimension (x, y, or t), starting position, and amount to extract. The node handles both positive and negative indexing and automatically adjusts the extraction amount to stay within the available bounds.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `samples` | LATENT | Yes | - | The input latent samples to extract from |
| `dim` | COMBO | Yes | "x"<br>"y"<br>"t" | The dimension along which to cut the latent samples |
| `index` | INT | No | -16384 to 16384 | The starting position for the cut (default: 0). Positive values count from the start, negative values count from the end |
| `amount` | INT | No | 1 to 16384 | The number of elements to extract along the specified dimension (default: 1) |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `output` | LATENT | The extracted portion of the latent samples |
