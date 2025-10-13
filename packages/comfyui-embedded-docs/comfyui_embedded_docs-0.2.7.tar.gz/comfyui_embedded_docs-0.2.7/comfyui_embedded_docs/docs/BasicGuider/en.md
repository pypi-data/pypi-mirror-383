> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/BasicGuider/en.md)

The BasicGuider node creates a simple guidance mechanism for the sampling process. It takes a model and conditioning data as inputs and produces a guider object that can be used to guide the generation process during sampling. This node provides the fundamental guidance functionality needed for controlled generation.

## Inputs

| Parameter | Data Type | Input Type | Default | Range | Description |
|-----------|-----------|------------|---------|-------|-------------|
| `model` | MODEL | required | - | - | The model to be used for guidance |
| `conditioning` | CONDITIONING | required | - | - | The conditioning data that guides the generation process |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `GUIDER` | GUIDER | A guider object that can be used during the sampling process to guide generation |
