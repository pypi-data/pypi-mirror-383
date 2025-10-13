> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/LossGraphNode/en.md)

The LossGraphNode creates a visual graph of training loss values over time and saves it as an image file. It takes loss data from training processes and generates a line chart showing how the loss changes across training steps. The resulting graph includes axis labels, min/max loss values, and is automatically saved to the temporary output directory with a timestamp.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `loss` | LOSS | Yes | Multiple options available | The loss data containing loss values to plot (default: empty dictionary) |
| `filename_prefix` | STRING | Yes | - | The prefix for the output image filename (default: "loss_graph") |

**Note:** The `loss` parameter requires a valid loss dictionary containing a "loss" key with loss values. The node automatically scales the loss values to fit the graph dimensions and generates a line plot showing the loss progression over training steps.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `ui.images` | IMAGE | The generated loss graph image saved to the temporary directory |
