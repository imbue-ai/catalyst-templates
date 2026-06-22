A starting point training script is provided in the file `train.py`. The training script runs for a fixed time budget of 5 minutes (wall clock training time, excluding startup/compilation).

What you CAN do in experiments:

    Your solutions should be updated copies of the train.py file that performs better than the original one.
    When you propose an experiment, use train.py as a starting point for your script.py, but then modify it to test out the specific hypothesis that you're trying to test.
    You can experiment with any of the following: model architecture, optimizer, hyperparameters, training loop, batch size, model size, etc.

What you CANNOT do:

    Modify prepare.py. It is read-only. It contains the fixed evaluation, data loading, tokenizer, and training constants (time budget, sequence length, etc).
    Install new packages or add dependencies. You can only use what's already in pyproject.toml.
    Modify the evaluation harness. The evaluate_bpb function in prepare.py is the ground truth metric.

VRAM is a soft constraint. Some increase is acceptable for meaningful val_bpb gains, but it should not blow up dramatically.


## Important for setting up experiments and experiment proposals:
* Make a copy of the `train.py` file in the experiment proposal folder and apply your modifications.
* Always include a copy of `prepare.py` in the folder as well (do NOT modify this file). `train.py` imports it.
* The entrypoint you must use is `launch_train.py`. Copy `launch_train.py` to `script.py` in the experiment proposal folder. It will internally import train.py and execute it. The reason you need to use `launch_train.py`: The local machine does not have a GPU, but train.py requires a CUDA GPU. `launch_train.py` will run `train.py` in a remove sandbox that has a GPU available.
