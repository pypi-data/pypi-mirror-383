
The RebatchImages node is designed to reorganize a batch of images into a new batch configuration, adjusting the batch size as specified. This process is essential for managing and optimizing the processing of image data in batch operations, ensuring that images are grouped according to the desired batch size for efficient handling.

## Inputs

| Field       | Data Type | Description                                                                         |
|-------------|-------------|-------------------------------------------------------------------------------------|
| `images`    | `IMAGE`     | A list of images to be rebatched. This parameter is crucial for determining the input data that will undergo the rebatching process. |
| `batch_size`| `INT`       | Specifies the desired size of the output batches. This parameter directly influences how the input images are grouped and processed, impacting the structure of the output. |

## Outputs

| Field | Data Type | Description                                                                   |
|-------|-------------|-------------------------------------------------------------------------------|
| `image`| `IMAGE`     | The output consists of a list of image batches, reorganized according to the specified batch size. This allows for flexible and efficient processing of image data in batch operations. |
