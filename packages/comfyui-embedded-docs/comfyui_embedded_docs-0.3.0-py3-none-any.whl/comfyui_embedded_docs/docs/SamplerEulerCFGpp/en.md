> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/SamplerEulerCFGpp/en.md)

The SamplerEulerCFGpp node provides an Euler CFG++ sampling method for generating outputs. This node offers two different implementation versions of the Euler CFG++ sampler that can be selected based on user preference.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `version` | STRING | Yes | `"regular"`<br>`"alternative"` | The implementation version of the Euler CFG++ sampler to use |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `sampler` | SAMPLER | Returns a configured Euler CFG++ sampler instance |
