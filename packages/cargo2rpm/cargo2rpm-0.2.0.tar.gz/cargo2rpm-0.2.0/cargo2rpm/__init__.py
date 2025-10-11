import os

__version__ = "0.2.0"

# if the "CARGO" environment variable is not defined, fall back to "cargo"
if _cargo := os.environ.get("CARGO"):
    CARGO = _cargo
else:
    CARGO = "cargo"
