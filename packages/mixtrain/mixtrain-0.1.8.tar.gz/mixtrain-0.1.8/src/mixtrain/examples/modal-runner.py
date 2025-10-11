from modal.volume import Volume
from modal.stream_type import StreamType


import modal
import uuid
import os
import shutil

app = modal.App.lookup("dk-app", create_if_missing=True)

from mixtrain.client import MixClient

# API_KEY = "mix-c213cf62f7ad75e50e4abc03ccd5176356851c32fd091f482934716581fa03ce" # local
# API_KEY = "mix-8c4d367cdcbafc2fbb9ca8a5ef325955249bd9603ee2db4abb0149ccee0dc067" # morphic-staging
API_KEY = (
    "mix-0ffca1a34c351bc3c3e9a19cfbd9e8f3bc72018fa5e8df5a0a295b12d3162187"  # test-prod
)
mix = MixClient(api_key=API_KEY)


secrets = {"MIXTRAIN_API_KEY": API_KEY}

for secret in mix.get_all_secrets():
    secrets[secret["name"]] = secret["value"]

uuid = str(uuid.uuid4())
print(uuid)
workdir = f"/workdir"
entrypoint = "/Users/dk/code/mixrepo/mixtrain/src/mixtrain/examples/compare_t2i.py"
files = [entrypoint]  # TODO add all files in the folder

local_folder = f"/tmp/mixtrain/{uuid}"
os.makedirs(local_folder, exist_ok=True)
for file in files:
    shutil.copy(file, local_folder)


with modal.Volume.ephemeral() as vol:
    with vol.batch_upload() as f:
        f.put_directory(local_folder, workdir)  # or dir

    sb = modal.Sandbox.create(
        app=app,
        image=modal.Image.debian_slim().uv_pip_install("mixtrain>=0.1.7").env(secrets),
        volumes={workdir: vol},
    )

    p = sb.exec(
        "python",
        "compare_t2i.py",
        workdir=workdir + workdir,
        timeout=30,
    )

    # p = sb.exec("ls", "-lR", workdir=workdir + workdir)
    for line in p.stdout:
        print(line, end="")

    for line in p.stderr:
        print(line, end="")

    # p = sb.exec("python", "-c", "import fal_client; print(fal_client.__version__)")
    # for line in p.stdout:
    #     print(line, end="")
    # for line in p.stderr:
    #     print(line, end="")

    sb.terminate()
