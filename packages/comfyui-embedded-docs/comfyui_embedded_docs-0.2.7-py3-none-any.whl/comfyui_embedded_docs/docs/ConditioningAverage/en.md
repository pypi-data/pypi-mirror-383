The `ConditioningAverage` node is used to blend two different sets of conditioning (such as text prompts) according to a specified weight, generating a new conditioning vector that lies between the two. By adjusting the weight parameter, you can flexibly control the influence of each conditioning on the final result. This is especially suitable for prompt interpolation, style fusion, and other advanced use cases.

As shown below, by adjusting the strength of `conditioning_to`, you can output a result between the two conditionings.

![example](./asset/example.webp)

## Inputs

| Parameter               | Comfy dtype    | Description |
|------------------------|---------------|-------------|
| `conditioning_to`      | `CONDITIONING`| The target conditioning vector, serving as the main base for the weighted average. |
| `conditioning_from`    | `CONDITIONING`| The source conditioning vector, which will be blended into the target according to a certain weight. |
| `conditioning_to_strength` | `FLOAT`    | The strength of the target conditioning, range 0.0-1.0, default 1.0, step 0.01. |

## Outputs

| Parameter        | Comfy dtype    | Description |
|------------------|---------------|-------------|
| `conditioning`   | `CONDITIONING`| The resulting conditioning vector after blending, reflecting the weighted average. |

## Typical Use Cases

- **Prompt Interpolation:** Smoothly transition between two different text prompts, generating content with intermediate style or semantics.
- **Style Fusion:** Combine different artistic styles or semantic conditions to create novel effects.
- **Strength Adjustment:** Precisely control the influence of a particular conditioning on the result by adjusting the weight.
- **Creative Exploration:** Explore diverse generative effects by mixing different prompts.
