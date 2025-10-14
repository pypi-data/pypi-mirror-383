"""speedtune - lightweight utilities for patching causal LMs

This package contains helpers to compress token embeddings into patches
and to run patched embeddings through a causal language model.
"""

__version__ = "0.1.0"

# Re-export the public API from the package root.
from .patch import AutoPatchModelForCausalLM, AutoPatchModelForSeq2SeqLM  # noqa: E402

__all__ = [
    "__version__",
    "AutoPatchModelForCausalLM",
    "AutoPatchModelForSeq2SeqLM",
]
