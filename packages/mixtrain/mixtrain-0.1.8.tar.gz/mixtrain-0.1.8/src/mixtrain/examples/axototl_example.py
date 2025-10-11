import subprocess
import modal
# from .train import Framework


app = modal.App(name="axolotl-app", image=modal.Image.from_registry("axolotlai/axolotl-cloud:main-20250701-py3.11-cu124-2.6.0").env({
    # "AXOLOTL_DATA_DIR": "/data/axolotl",
    "JUPYTER_DISABLE": "1",
}))

@app.cls(gpu="T4")
class AxolotlApp:
    extra_libs: list[str] = modal.parameter()
    
    @modal.method()
    def run_framework(self):
        import torch
        ALLOW_WANDB = False
        print("Running axolotl")
        # line_as_bytes = subprocess.check_output("nvidia-smi -L", shell=True)
        line_as_bytes = subprocess.check_output("python -c 'import torch; print(torch.cuda.get_device_name())'", shell=True)
        line = line_as_bytes.decode("ascii")
        print(line)
        line_as_bytes = subprocess.check_output("python -c 'import duckdb; print(duckdb.__version__)'", shell=True)
        line = line_as_bytes.decode("ascii")
        print(line)
        
        # run python, import torch, print(torch.cuda.get_device_name())
        # subprocess.Popen(["python", "-c", "import torch; print(torch.cuda.get_device_name())"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # subprocess.Popen(["axolotl", "fetch", "examples"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # subprocess.run([
        #     "axolotl", "train", "examples/llama-3.1-8b-instruct.jsonl", 
        #     "--model", "llama3.1-8b-instruct", "--batch-size", "16", "--epochs", "1", 
        #     "--learning-rate", "1e-4", "--warmup-ratio", "0.03", "--gradient-accumulation-steps", "1", "--save-dir", "models"],
        #     shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cmd = f"accelerate launch --num_processes {torch.cuda.device_count()} --num_machines 1 --mixed_precision no --dynamo_backend no -m axolotl.cli.train ./config.yml {'--wandb_mode disabled' if not ALLOW_WANDB else ''}"
        # subprocess.run(cmd, shell=True)

def get_framework_image(path: str, framework: Framework):
    pass
# def get_app(path: str, framework: Framework):
#     """
#     Prepare the training data.
#     """
#     if framework == Framework.oxen:
#         pass
#     elif framework == Framework.pytorch:
#         pass
#     elif framework == Framework.tensorflow:
#         pass
#     elif framework == Framework.axolotl:
#         return AxolotlApp.with_options(gpu="L4")
#         # return app
#         # return AxolotlApp
#     return None