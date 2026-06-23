import os
import subprocess
import modal

app = modal.App("autoresearch_train")

gpu = "H100"

# Define the container's environment (packages, etc.)
workspace_dir = os.path.dirname(os.getenv("VIRTUAL_ENV", "."))
image = (
  modal.Image.debian_slim(python_version="3.11")
       .pip_install("uv")
       .add_local_file(f"{workspace_dir}/pyproject_launch.toml", remote_path="/root/pyproject.toml", copy=True)
       .run_commands("uv pip install --system -r /root/pyproject.toml", gpu=gpu)
       .add_local_file("prepare.py", remote_path="/root/prepare.py", copy=True)
       .run_commands("uv run python /root/prepare.py", gpu=gpu)
       .add_local_file("train.py", remote_path="/root/train.py")
)

# Decorate the function with the desired GPU
@app.function(image=image, cpu=4, gpu=gpu, memory=16384, timeout=1800)
def run_autoresearch_train():
    import train
    train.run()

# Entry point for local execution
if __name__ == "__main__":
    current_file_path = os.path.abspath(__file__)
    subprocess.run(
        [
            "modal", "run", f"{current_file_path}::run_autoresearch_train"
        ],
        check=True
    )
