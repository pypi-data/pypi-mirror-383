
This node is designed for generating conditioning data for video generation tasks, specifically tailored for use with SVD_img2vid models. It takes various inputs including initial images, video parameters, and a VAE model to produce conditioning data that can be used to guide the generation of video frames.

## Inputs

| Parameter             | Comfy dtype        | Description |
|----------------------|--------------------|-------------|
| `clip_vision`         | `CLIP_VISION`      | Represents the CLIP vision model used for encoding visual features from the initial image, playing a crucial role in understanding the content and context of the image for video generation. |
| `init_image`          | `IMAGE`            | The initial image from which the video will be generated, serving as the starting point for the video generation process. |
| `vae`                 | `VAE`              | A Variational Autoencoder (VAE) model used for encoding the initial image into a latent space, facilitating the generation of coherent and continuous video frames. |
| `width`               | `INT`              | The desired width of the video frames to be generated, allowing for customization of the video's resolution. |
| `height`              | `INT`              | The desired height of the video frames, enabling control over the video's aspect ratio and resolution. |
| `video_frames`        | `INT`              | Specifies the number of frames to be generated for the video, determining the video's length. |
| `motion_bucket_id`    | `INT`              | An identifier for categorizing the type of motion to be applied in the video generation, aiding in the creation of dynamic and engaging videos. |
| `fps`                 | `INT`              | The frames per second (fps) rate for the video, influencing the smoothness and realism of the generated video. |
| `augmentation_level`  | `FLOAT`            | A parameter controlling the level of augmentation applied to the initial image, affecting the diversity and variability of the generated video frames. |

## Outputs

| Parameter     | Comfy dtype        | Description |
|---------------|--------------------|-------------|
| `positive`    | `CONDITIONING`     | The positive conditioning data, consisting of encoded features and parameters for guiding the video generation process in a desired direction. |
| `negative`    | `CONDITIONING`     | The negative conditioning data, providing a contrast to the positive conditioning, which can be used to avoid certain patterns or features in the generated video. |
| `latent`      | `LATENT`           | Latent representations generated for each frame of the video, serving as a foundational component for the video generation process. |
