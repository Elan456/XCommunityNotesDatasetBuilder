# Steps System Outline

## Overview
The steps system is designed to provide a structured approach for processing and updating datasets. Each step represents a specific operation or transformation applied to the dataset.

## Getting Started
```bash
python -m misleading_image.dataset_updater.update --step_name initialize --output_path <output_path> --checkpoint_name <checkpoint_name>
```

Above is the command to initialize an empty checkpoint in the folder, <output_path>. From here, you can complete operations on the checkpoint. Steps should be ran as 

```bash
python -m misleading_image.dataset_updater.update --checkpoint_path='<checkpoint_path>' --step_name='<step_name>' --kwargs '<kwargs, if needed>>' --checkpoint_name='<checkpoint_name>'
```

Any argument that is step specific should be passed in kwargs. 

To view a checkpoint's dataset, run 
```bash
python -m viewCheckpoint --checkpoint_path '<path>' --output_file '<name>'
```



## List of Possible Steps
1. **Filter Community Notes**
     - Description: Takes in a community notes file and filters it according to our defined parameters
     - Input: checkpoint, path to notes file

2. **Remove Existing Notes**
     - Description: Remove notes that have already been collected, using either an existing dataset or an existing checkpoint as a reference
     - Input: checkpoint, current_dataset (optional), current_checkpoint (optional)

3. **Collect Tweets**
     - Description: Collect novel tweets
     - Input: checkpoint

4. **Add Image Labels**
     - Description: Adds labels of 'contextual' or 'misleading' to the tweet
     - Input: checkpoint

5. **Reverse Image Search**
     - Description: Gets reverse image search results for a tweet. The
        ```misleading_image/dataset_updater/google_cloud/client_file_googlevision.json``` file must be present for web entity detection to work
     - Input: checkpoint

6. **Dememe Reverse Image Search**
     - Description: Gets reverse image search results for a tweet, using a heuristic to crop meme text. The```misleading_image/dataset_updater/google_cloud/client_file_googlevision.json``` file must be present for web entity detection to work
     - Input: checkpoint

7. **Image Link Annotation**
     - Description: Gets the top search results from each link found in the  reverse image search result. The ```misleading_image/dataset_updater/google_cloud/google_cloud.key``` File needs to be set up as a list of ```{"api_key: '\<key>', "engine_id":'\<id>'}```
     - Input: checkpoint, dememe (true or false)

8. **Add Author Information**
     - Description: Add information about the note author
     - Input: checkpoint, authorInfoFile

9. **Add Note Status Information**
     - Description: Add information about the note's history
     - Input: checkpoint, noteStatusFile

10. **Combine Datasets**
     - Description: Combine the existing checkpoint's data with data from another source (either a file or a checkpoint), they are expected to have the same top-level keys
     - Input: checkpoint, current_dataset (optional), current_checkpoint (optional), check_steps (optional)
