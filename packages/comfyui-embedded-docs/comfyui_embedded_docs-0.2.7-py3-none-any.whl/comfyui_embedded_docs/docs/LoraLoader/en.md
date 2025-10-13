This node automatically detects models located in the LoRA folder (including subfolders) with the corresponding model path being `ComfyUI\models\loras`. For more information, please refer to Installing LoRA Models

The LoRA Loader node is primarily used to load LoRA models. You can think of LoRA models as filters that can give your images specific styles, content, and details:

- Apply specific artistic styles (like ink painting)
- Add characteristics of certain characters (like game characters)
- Add specific details to the image
All of these can be achieved through LoRA.

If you need to load multiple LoRA models, you can directly chain multiple nodes together, as shown below:

## Inputs

| Parameter | Data Type | Description |
| --- | --- | --- |
| `model` | MODEL | Typically used to connect to the base model |
| `clip` | CLIP | Typically used to connect to the CLIP model |
| `lora_name` | COMBO[STRING] | Select the name of the LoRA model to use |
| `strength_model` | FLOAT | Value range from -100.0 to 100.0, typically used between 0~1 for daily image generation. Higher values result in more pronounced model adjustment effects |
| `strength_clip` | FLOAT | Value range from -100.0 to 100.0, typically used between 0~1 for daily image generation. Higher values result in more pronounced model adjustment effects |

## Outputs

| Parameter | Data Type | Description |
| --- | --- | --- |
| `model` | MODEL | The model with LoRA adjustments applied |
| `clip` | CLIP | The CLIP instance with LoRA adjustments applied |
