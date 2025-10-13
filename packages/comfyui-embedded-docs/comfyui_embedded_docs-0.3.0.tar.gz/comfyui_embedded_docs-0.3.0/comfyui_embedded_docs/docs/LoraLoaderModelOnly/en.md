
This node will detect models located in the `ComfyUI/models/loras` folder, and it will also read models from additional paths configured in the extra_model_paths.yaml file. Sometimes, you may need to **refresh the ComfyUI interface** to allow it to read the model files from the corresponding folder.

This node specializes in loading a LoRA model without requiring a CLIP model, focusing on enhancing or modifying a given model based on LoRA parameters. It allows for the dynamic adjustment of the model's strength through LoRA parameters, facilitating fine-tuned control over the model's behavior.

## Inputs

| Field             | Comfy dtype       | Description                                                                                   |
|-------------------|-------------------|-----------------------------------------------------------------------------------------------|
| `model`           | `MODEL`           | The base model for modifications, to which LoRA adjustments will be applied.                   |
| `lora_name`       | `COMBO[STRING]`   | The name of the LoRA file to be loaded, specifying the adjustments to apply to the model.      |
| `strength_model`  | `FLOAT`           | Determines the intensity of the LoRA adjustments, with higher values indicating stronger modifications. |

## Outputs

| Field   | Data Type | Description                                                              |
|---------|-------------|--------------------------------------------------------------------------|
| `model` | `MODEL`     | The modified model with LoRA adjustments applied, reflecting changes in model behavior or capabilities. |
