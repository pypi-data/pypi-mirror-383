
This node is designed to integrate CLIP vision outputs into the conditioning process, adjusting the influence of these outputs based on specified strength and noise augmentation parameters. It enriches the conditioning with visual context, enhancing the generation process.

## Inputs

| Parameter              | Comfy dtype            | Description |
|------------------------|------------------------|-------------|
| `conditioning`         | `CONDITIONING`         | The base conditioning data to which the CLIP vision outputs are to be added, serving as the foundation for further modifications. |
| `clip_vision_output`   | `CLIP_VISION_OUTPUT`   | The output from a CLIP vision model, providing visual context that is integrated into the conditioning. |
| `strength`             | `FLOAT`                | Determines the intensity of the CLIP vision output's influence on the conditioning. |
| `noise_augmentation`   | `FLOAT`                | Specifies the level of noise augmentation to apply to the CLIP vision output before integrating it into the conditioning. |

## Outputs

| Parameter             | Comfy dtype            | Description |
|-----------------------|------------------------|-------------|
| `conditioning`         | `CONDITIONING`         | The enriched conditioning data, now containing integrated CLIP vision outputs with applied strength and noise augmentation. |
