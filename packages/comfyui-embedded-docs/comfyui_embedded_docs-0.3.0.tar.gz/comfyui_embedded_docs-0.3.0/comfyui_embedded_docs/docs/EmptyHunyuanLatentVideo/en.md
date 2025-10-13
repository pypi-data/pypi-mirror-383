The `EmptyHunyuanLatentVideo` node is similar to the `EmptyLatentImage` node. You can consider it as a blank canvas for video generation, where width, height, and length define the properties of the canvas, and the batch size determines the number of canvases to create. This node creates empty canvases ready for subsequent video generation tasks.

## Inputs

| Parameter    | Comfy Type | Description                                                                                |
| ----------- | ---------- | ------------------------------------------------------------------------------------------ |
| `width`     | `INT`      | Video width, default 848, minimum 16, maximum `nodes.MAX_RESOLUTION`, step size 16.        |
| `height`    | `INT`      | Video height, default 480, minimum 16, maximum `nodes.MAX_RESOLUTION`, step size 16.       |
| `length`    | `INT`      | Video length, default 25, minimum 1, maximum `nodes.MAX_RESOLUTION`, step size 4.          |
| `batch_size`| `INT`      | Batch size, default 1, minimum 1, maximum 4096.                                           |

## Outputs

| Parameter | Comfy Type | Description                                                                               |
| --------- | ---------- | ----------------------------------------------------------------------------------------- |
| `samples` | `LATENT`   | Generated latent video samples containing zero tensors, ready for processing and generation tasks. |
