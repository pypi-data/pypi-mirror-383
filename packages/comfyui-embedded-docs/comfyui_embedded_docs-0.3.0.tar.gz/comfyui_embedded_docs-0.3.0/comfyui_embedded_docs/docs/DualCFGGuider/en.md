> This documentation was AI-generated. If you find any errors or have suggestions for improvement, please feel free to contribute! [Edit on GitHub](https://github.com/Comfy-Org/embedded-docs/blob/main/comfyui_embedded_docs/docs/DualCFGGuider/en.md)

The DualCFGGuider node creates a guidance system for dual classifier-free guidance sampling. It combines two positive conditioning inputs with one negative conditioning input, applying different guidance scales to each conditioning pair to control the influence of each prompt on the generated output.

## Inputs

| Parameter | Data Type | Required | Range | Description |
|-----------|-----------|----------|-------|-------------|
| `model` | MODEL | Yes | - | The model to use for guidance |
| `cond1` | CONDITIONING | Yes | - | The first positive conditioning input |
| `cond2` | CONDITIONING | Yes | - | The second positive conditioning input |
| `negative` | CONDITIONING | Yes | - | The negative conditioning input |
| `cfg_conds` | FLOAT | Yes | 0.0 - 100.0 | Guidance scale for the first positive conditioning (default: 8.0) |
| `cfg_cond2_negative` | FLOAT | Yes | 0.0 - 100.0 | Guidance scale for the second positive and negative conditioning (default: 8.0) |
| `style` | COMBO | Yes | "regular"<br>"nested" | The guidance style to apply (default: "regular") |

## Outputs

| Output Name | Data Type | Description |
|-------------|-----------|-------------|
| `GUIDER` | GUIDER | A configured guidance system ready for use with sampling |
