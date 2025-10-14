import gc
import logging
import os
from typing import Dict, Any
import json

import torch
from bark.model import GPTConfig, GPT
from bark.model_fine import FineGPT, FineGPTConfig
from huggingface_hub import hf_hub_download
from transformers import BertTokenizer

logger = logging.getLogger(__name__)


def _cast_bool_env_var(s: str) -> bool:
    return s.lower() in ("true", "1", "t")


USE_SMALL_MODELS = _cast_bool_env_var(os.environ.get("SUNO_USE_SMALL_MODELS", "False"))

REMOTE_MODEL_PATHS: Dict[str, Dict[str, str]] = {
    "text_small": {"repo_id": "suno/bark", "file_name": "text.pt"},
    "coarse_small": {"repo_id": "suno/bark", "file_name": "coarse.pt"},
    "fine_small": {"repo_id": "suno/bark", "file_name": "fine.pt"},
    "text": {"repo_id": "suno/bark", "file_name": "text_2.pt"},
    "coarse": {"repo_id": "suno/bark", "file_name": "coarse_2.pt"},
    "fine": {"repo_id": "suno/bark", "file_name": "fine_2.pt"},
}

default_cache_dir = os.path.join(os.path.expanduser("~"), ".cache")
CACHE_DIR = os.path.join(
    os.getenv("XDG_CACHE_HOME", default_cache_dir), "suno", "bark_v0"
)


def _download(from_hf_path: str, file_name: str) -> None:
    CACHE_DIR = "data/models/bark"
    os.makedirs(CACHE_DIR, exist_ok=True)
    hf_hub_download(repo_id=from_hf_path, filename=file_name, local_dir=CACHE_DIR)


def _clear_cuda_cache() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def clean_models(model_key: str = None) -> None:
    global models
    model_keys = [model_key] if model_key is not None else list(models.keys())
    for k in model_keys:
        if k in models:
            del models[k]
    _clear_cuda_cache()
    gc.collect()


def _load_model(
    ckpt_path: str, device: str, use_small: bool = False, model_type: str = "text"
) -> Any:
    if model_type == "text":
        ConfigClass = GPTConfig
        ModelClass = GPT
    elif model_type == "coarse":
        ConfigClass = GPTConfig
        ModelClass = GPT
    elif model_type == "fine":
        ConfigClass = FineGPTConfig
        ModelClass = FineGPT
    else:
        raise NotImplementedError()
    model_key = f"{model_type}_small" if use_small or USE_SMALL_MODELS else model_type
    model_info = REMOTE_MODEL_PATHS[model_key]
    if not os.path.exists(ckpt_path):
        logger.info(f"{model_type} model not found, downloading into `{CACHE_DIR}`.")
        _download(model_info["repo_id"], model_info["file_name"])
    checkpoint = torch.load(ckpt_path, map_location=device)
    # this is a hack
    model_args = checkpoint["model_args"]
    if "input_vocab_size" not in model_args:
        model_args["input_vocab_size"] = model_args["vocab_size"]
        model_args["output_vocab_size"] = model_args["vocab_size"]
        del model_args["vocab_size"]
    gptconf = ConfigClass(**checkpoint["model_args"])
    model = ModelClass(gptconf)
    state_dict = checkpoint["model"]
    # fixup checkpoint
    unwanted_prefix = "_orig_mod."
    for k, v in list(state_dict.items()):
        if k.startswith(unwanted_prefix):
            state_dict[k[len(unwanted_prefix) :]] = state_dict.pop(k)
    extra_keys = set(state_dict.keys()) - set(model.state_dict().keys())
    extra_keys = set([k for k in extra_keys if not k.endswith(".attn.bias")])
    missing_keys = set(model.state_dict().keys()) - set(state_dict.keys())
    missing_keys = set([k for k in missing_keys if not k.endswith(".attn.bias")])
    if len(extra_keys) != 0:
        raise ValueError(f"extra keys found: {extra_keys}")
    if len(missing_keys) != 0:
        raise ValueError(f"missing keys: {missing_keys}")
    model.load_state_dict(state_dict, strict=False)
    n_params = model.get_num_params()
    val_loss = checkpoint["best_val_loss"].item()
    logger.info(
        f"model loaded: {round(n_params/1e6,1)}M params, {round(val_loss,3)} loss"
    )
    model.eval()
    model.to(device)
    del checkpoint, state_dict
    _clear_cuda_cache()
    if model_type == "text":
        tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
        return {
            "model": model,
            "tokenizer": tokenizer,
        }
    return model


def _load_filtered_model(
    config_path: str,
    weights_path: str,
    device: str = "cpu",
) -> Any:
    """
    Load a model from separate config and weights files.
    This is the replacement for _load_model_pth that works with the split files.

    Args:
        config_path: Path to the config JSON file
        weights_path: Path to the weights PTH file
        device: Device to load the model onto ("cpu", "cuda", etc.)

    Returns:
        The loaded model or a dict containing model and tokenizer if applicable
    """
    # Check if files exist
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    if not os.path.exists(weights_path):
        raise FileNotFoundError(f"Weights file not found: {weights_path}")

    # Load the config
    logger.info(f"Loading model config from {config_path}")
    with open(config_path, "r") as f:
        config_data = json.load(f)

    # Extract the model args
    model_args = config_data["model_config"]
    model_type = config_data.get("model_type", "text")

    # This is just an example - you'd need to adjust based on actual imports
    if model_type == "text":
        from bark.model import GPTConfig as ConfigClass, GPT as ModelClass
    elif model_type == "coarse":
        from bark.model import GPTConfig as ConfigClass, GPT as ModelClass
    elif model_type == "fine":
        from bark.model_fine import (
            FineGPTConfig as ConfigClass,
            FineGPT as ModelClass,
        )
    else:
        raise NotImplementedError(f"Model type {model_type} not supported")

    # Initialize model with config
    logger.info(f"Initializing {model_type} model")
    gptconf = ConfigClass(**model_args)
    model = ModelClass(gptconf)
    model.to(device)

    # Load the state dict
    logger.info(f"Loading model weights from {weights_path}")
    if weights_path.endswith(".safetensors"):
        from safetensors.torch import load_file

        state_dict = load_file(weights_path, device=device)
    else:
        state_dict = torch.load(weights_path, map_location=device)

    # Load state dict into model
    model.load_state_dict(state_dict, strict=False)

    if config_data.get("torch_dtype", "float32") == "bfloat16":
        model.bfloat16()

    # Get model stats
    n_params = sum(p.numel() for p in model.parameters())
    val_loss = model_args.get("best_val_loss", "N/A")
    logger.info(f"Model loaded: {round(n_params/1e6, 1)}M params, {val_loss} loss")

    # Set model to eval mode and move to device
    model.eval()

    # Clear memory
    del state_dict
    torch.cuda.empty_cache() if torch.cuda.is_available() else None

    # Special handling for text models that need tokenizers
    if model_type == "text":
        from transformers import BertTokenizer

        tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
        return {
            "model": model,
            "tokenizer": tokenizer,
        }
    return model


def _load_models(ckpt_dir: str, device: str = "cuda"):
    extension = ".pth" if ckpt_dir.endswith("-pth") else ".safetensors"

    model_text_big = _load_filtered_model(
        ckpt_dir + "text_model_config.json",
        ckpt_dir + "text" + extension,
        device=device,
    )

    model_coarse_big = _load_filtered_model(
        ckpt_dir + "coarse_model_config.json",
        ckpt_dir + "coarse" + extension,
        device=device,
    )

    model_fine_big = _load_filtered_model(
        ckpt_dir + "fine_model_config.json",
        ckpt_dir + "fine" + extension,
        device=device,
    )
    return model_text_big, model_coarse_big, model_fine_big


def load_models_into_bark(ckpt_dir: str):
    model_text_big, model_coarse_big, model_fine_big = _load_models(ckpt_dir)
    from bark.generation import models

    models["text"] = model_text_big
    models["coarse"] = model_coarse_big
    models["fine"] = model_fine_big
    _clear_cuda_cache()


def models_to_dtype(models, dtype):
    models["text"]["model"].to(dtype)
    models["coarse"].to(dtype)
    models["fine"].to(dtype)


if __name__ == "__main__":
    ckpt_dir = "data/models/bark/small/"

    load_models_into_bark(ckpt_dir)
