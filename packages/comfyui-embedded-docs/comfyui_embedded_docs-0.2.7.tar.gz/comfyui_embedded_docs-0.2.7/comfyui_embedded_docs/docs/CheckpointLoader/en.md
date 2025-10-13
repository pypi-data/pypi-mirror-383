> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/CheckpointLoader/en.md)

The CheckpointLoader node loads a pre-trained model checkpoint along with its configuration file. It takes a configuration file and a checkpoint file as inputs and returns the loaded model components including the main model, CLIP model, and VAE model for use in the workflow.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `config_name` | STRING | COMBO | - | Available config files | The configuration file that defines the model architecture and settings |
| `ckpt_name` | STRING | COMBO | - | Available checkpoint files | The checkpoint file containing the trained model weights and parameters |

**Note:** This node requires both a configuration file and a checkpoint file to be selected. The configuration file must match the architecture of the checkpoint file being loaded.

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `MODEL` | MODEL | The loaded main model component ready for inference |
| `CLIP` | CLIP | The loaded CLIP model component for text encoding |
| `VAE` | VAE | The loaded VAE model component for image encoding and decoding |

**Important Note:** This node has been marked as deprecated and may be removed in future versions. Consider using alternative loading nodes for new workflows.
