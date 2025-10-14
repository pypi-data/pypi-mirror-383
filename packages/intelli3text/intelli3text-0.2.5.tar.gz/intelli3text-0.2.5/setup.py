import hashlib, os, tempfile, urllib.request
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py

# === CONFIG: use o .FTZ oficial do fastText ===
MODEL_URL = os.environ.get(
    "INTELLI3TEXT_LID_URL",
    "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
)
MODEL_SHA256 = os.environ.get(
    "INTELLI3TEXT_LID_SHA256",
    # Coloque aqui o SHA256 real do lid.176.ftz (recomendado)
    ""
)

# Destino DENTRO do pacote (src-layout ⇒ build_lib/intelli3text/...)
RELATIVE_MODEL_PATH = os.path.join("intelli3text", "lid", "models", "lid.176.ftz")

def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

class build_py(_build_py):
    def run(self):
        dst_path = os.path.join(self.build_lib, RELATIVE_MODEL_PATH)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)

        with tempfile.TemporaryDirectory() as td:
            tmp = os.path.join(td, "lid.176.ftz")
            print(f"[intelli3text] Downloading model: {MODEL_URL}")
            # Download robusto com User-Agent (evita bloqueios esporádicos)
            req = urllib.request.Request(MODEL_URL, headers={"User-Agent":"intelli3text-installer/1.0"})
            with urllib.request.urlopen(req) as r, open(tmp, "wb") as w:
                w.write(r.read())

            if MODEL_SHA256:
                dig = _sha256(tmp)
                if dig.lower() != MODEL_SHA256.lower():
                    raise RuntimeError(f"Invalid SHA256 for lid.176.ftz.\nExpected: {MODEL_SHA256}\nGot     : {dig}")

            self.copy_file(tmp, dst_path)
            print(f"[intelli3text] Model embedded at: {dst_path}")

        super().run()

setup(cmdclass={"build_py": build_py})
