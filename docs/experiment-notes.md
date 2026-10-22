# Experiment notes

This repository preserves research notebooks and a saved model from different stages of ConnectAbility. These notes describe the existing artifacts and help a reviewer choose a consistent configuration.

## Hand-focused experiment

[`Action Detection Tutorial.ipynb`](../Action%20Detection%20Tutorial.ipynb) contains a hand-landmark extractor that concatenates 21 three-dimensional landmarks from each hand into a 126-value frame vector. The model definition takes 30 frames per sequence.

The notebook's saved outputs report a `(100, 30, 126)` feature array and the label map `{'Vsih vitay': 0, 'Diakuy vam': 1}`. The stored [`action.h5`](../action.h5) configuration also has a `(None, 30, 126)` input and a two-unit softmax output. It was saved with Keras 3.9.0.

The saved model does not include a separate class-name mapping. Use the label ordering associated with the matching training run when interpreting its outputs.

## Earlier full-body experiment

[`Action Detection Refined.ipynb`](../Action%20Detection%20Refined.ipynb) uses:

| Landmark group | Values per frame |
| :--- | ---: |
| Pose: 33 landmarks × 4 values | 132 |
| Face: 468 landmarks × 3 coordinates | 1,404 |
| Left hand: 21 landmarks × 3 coordinates | 63 |
| Right hand: 21 landmarks × 3 coordinates | 63 |
| **Total** | **1,662** |

Its saved outputs show 180 sequences and three labels: `hello`, `thanks`, and `iloveyou`. This configuration has a different input size and output vocabulary from the bundled two-class model.

## Before rerunning the notebooks

The notebooks contain alternative and debugging cells alongside saved results:

- In `Action Detection Tutorial.ipynb`, the later data-collection cell redefines the gesture list to three English labels and replaces `extract_keypoints` with a placeholder returning 1,662 zeros. It also replaces the landmark-drawing helper with an empty function. For the hand-focused experiment, restore the earlier real hand extractor and keep the two-class labels consistent before collecting data.
- In `Action Detection Refined.ipynb`, an exploratory multiline conditional assignment to `face` is not valid as a standalone Python cell. The later `extract_keypoints` function contains the complete extraction logic.
- Both experiments expect locally collected arrays under `MP_Data/`, which is not tracked in this repository. Existing training logs and notebook outputs do not replace those arrays.
- Installation cells refer to different TensorFlow generations. Establish a compatible environment for the selected experiment before training or loading the checkpoint; the repository does not contain an environment lock file.

The original notebooks and model are preserved. This documentation update does not change their training or prediction behavior.

## Evaluation context

The notebooks use a random 95/5 sequence split. Their saved test sets contain only five examples in the hand-focused experiment and nine in the earlier full-body experiment. These runs are development checks and do not establish recognition performance on new signers.

A stronger evaluation would keep signers or recording sessions separate between training and testing, expand the dataset, and assess gesture-level precision and recall under varied recording conditions.
