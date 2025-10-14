import os
import json
import torch
import logging
from typing import Dict, Any, Tuple, Optional, Union

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_model(
    input_path: str,
    output_dir: str,
    model_type: str,
    big_model: bool = False,
    dtype: str = "float32",
) -> Tuple[str, str]:
    """
    Convert a .pt model file into separate config JSON and weights PTH files
    with all necessary fixes applied.

    Args:
        input_path: Path to the input .pt file
        output_dir: Directory to save the output files
        config_name: Name for the config JSON file
        weights_name: Name for the weights PTH file

    Returns:
        Tuple of (config_path, weights_path)
    """
    output_dir = os.path.join(output_dir, "big" if big_model else "small")
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define output paths
    # config_path = os.path.join(output_dir, config_name)
    config_path = os.path.join(output_dir, f"{model_type}_model_config.json")
    weights_path = os.path.join(output_dir, f"{model_type}.pth")

    # Load the checkpoint
    logger.info(f"Loading checkpoint from {input_path}")
    checkpoint = torch.load(input_path, map_location="cpu")

    # Extract model arguments and fix them
    model_args = checkpoint["model_args"].copy()

    # Apply the same fixes as in the original function
    if "input_vocab_size" not in model_args:
        logger.info("Fixing vocab_size in model args")
        model_args["input_vocab_size"] = model_args["vocab_size"]
        model_args["output_vocab_size"] = model_args["vocab_size"]
        del model_args["vocab_size"]

    # Extract and fix state dict
    state_dict = checkpoint["model"]

    # Fix unwanted prefix in state dict keys
    unwanted_prefix = "_orig_mod."
    prefix_keys = [k for k in state_dict.keys() if k.startswith(unwanted_prefix)]

    if prefix_keys:
        logger.info(f"Fixing {len(prefix_keys)} keys with unwanted prefix")
        for k in prefix_keys:
            state_dict[k[len(unwanted_prefix) :]] = state_dict.pop(k)

    # Add some metadata
    metadata = {
        "model_config": model_args,
        "model_type": model_type,
        "parameter_count": sum(tensor.numel() for tensor in state_dict.values()),
        "needs_tokenizer": model_args.get("model_type", "text") == "text",
        "best_val_loss": checkpoint.get("best_val_loss", None),
        "torch_dtype": dtype,
    }
    if metadata["best_val_loss"] is not None:
        metadata["best_val_loss"] = metadata["best_val_loss"].item()

    # Save the config to JSON
    logger.info(f"Saving model config to {config_path}")
    with open(config_path, "w") as f:
        json.dump(metadata, f, indent=2)

    # Save the state dict to PTH
    logger.info(f"Saving model weights to {weights_path}")
    torch.save(state_dict, weights_path)

    # Log parameter count if available
    param_count = sum(tensor.numel() for tensor in state_dict.values())
    logger.info(f"Model converted: {round(param_count/1e6, 1)}M parameters")

    # Clear memory
    del checkpoint, state_dict

    return config_path, weights_path


if __name__ == "__main__":
    from bark.generation import _get_ckpt_path

    # convert big models
    config_path, weights_path = convert_model(
        _get_ckpt_path("text", False), "data/models/bark/", "text", big_model=True
    )

    config_path, weights_path = convert_model(
        _get_ckpt_path("coarse", False), "data/models/bark/", "coarse", big_model=True
    )

    config_path, weights_path = convert_model(
        _get_ckpt_path("fine", False), "data/models/bark/", "fine", big_model=True
    )
