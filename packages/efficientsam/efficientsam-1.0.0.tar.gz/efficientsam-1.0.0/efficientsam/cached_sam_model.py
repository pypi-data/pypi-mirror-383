from pathlib import Path

import torch

from efficientsam.models.efficientvit.sam import EfficientViTSamPredictor
from efficientsam.sam_model_zoo import create_efficientvit_sam_model

SAM_MODEL_REGISTRY = {
    "efficientvit-sam-l0": "https://huggingface.co/mit-han-lab/efficientvit-sam/resolve/main/efficientvit_sam_l0.pt",
    "efficientvit-sam-l1": "https://huggingface.co/mit-han-lab/efficientvit-sam/resolve/main/efficientvit_sam_l1.pt",
    "efficientvit-sam-l2": "https://huggingface.co/mit-han-lab/efficientvit-sam/resolve/main/efficientvit_sam_l2.pt",
    "efficientvit-sam-xl0": "https://huggingface.co/mit-han-lab/efficientvit-sam/resolve/main/efficientvit_sam_xl0.pt",
    "efficientvit-sam-xl1": "https://huggingface.co/mit-han-lab/efficientvit-sam/resolve/main/efficientvit_sam_xl1.pt",
}


class CachedSamModel:
    """Cached SAM model."""

    model_name: str = ""
    """The name of the model from the SAM_MODEL_REGISTRY."""
    device: str = ""
    """The device to run the model on, if not specified, the model will be loaded on the GPU if available, otherwise on the CPU."""
    checkpoint_dir: Path
    """The directory to save the checkpoint."""
    sam: EfficientViTSamPredictor = None
    """The SAM model predictor."""

    def __init__(self, model_name: str, device: str = "", checkpoint_dir: Path | None = None) -> None:
        """Initialize the CachedSAM model.

        Args:
            model_name: The name of the model from the SAM_MODEL_REGISTRY.
            device: The device to run the model on. If not specified, the model will be loaded on the GPU if available,
                otherwise on the CPU.
        """
        if device == "":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        if checkpoint_dir is None:
            checkpoint_dir = Path("~/.cache/efficientsam/checkpoints").expanduser()
        if model_name != CachedSamModel.model_name or checkpoint_dir != CachedSamModel.checkpoint_dir:
            CachedSamModel.model_name = model_name
            CachedSamModel.device = device
            CachedSamModel.checkpoint_dir = checkpoint_dir
            CachedSamModel.sam = load_sam_predictor(model_name, device, checkpoint_dir)
        if device != CachedSamModel.device:
            CachedSamModel.device = device
            CachedSamModel.sam.model = CachedSamModel.sam.model.to(device)

    def __call__(self) -> EfficientViTSamPredictor:
        """Get the SAM model predictor of the current model and device.

        Returns:
            The SAM model predictor.
        """
        return CachedSamModel.sam


def download_sam_checkpoint(model_name: str, checkpoint_path: Path) -> None:
    """Download the SAM model checkpoint.

    Args:
        model_name: The name of the model from the SAM_MODEL_REGISTRY.
        checkpoint_path: The destination path to save the checkpoint.
    """
    import requests

    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    url = SAM_MODEL_REGISTRY[model_name]
    response = requests.get(url, stream=True, timeout=10)
    response.raise_for_status()

    # Get file size if available
    total_size = int(response.headers.get("content-length", 0))
    block_size = 8192  # 8KB chunks

    with checkpoint_path.open("wb") as f:
        if total_size:
            for data in response.iter_content(block_size):
                f.write(data)
        else:
            f.write(response.content)


def load_sam_predictor(model_name: str, device: str, checkpoint_dir: Path) -> EfficientViTSamPredictor:
    """Load the SAM model predictor.

    Args:
        model_name: The name of the model from the SAM_MODEL_REGISTRY.
        device: The device to run the model on.

    Returns:
        The SAM model predictor.
    """
    checkpoint_name = Path(SAM_MODEL_REGISTRY[model_name]).name
    checkpoint_path = checkpoint_dir / checkpoint_name
    if not checkpoint_path.exists():
        try:
            download_sam_checkpoint(model_name, checkpoint_path)
        except Exception as e:
            raise RuntimeError(f"Failed to download the SAM model checkpoint: {e}")
    efficientvit_sam = create_efficientvit_sam_model(name=model_name, weight_url=str(checkpoint_path))
    efficientvit_sam = efficientvit_sam.to(device).eval()
    efficientvit_sam_predictor = EfficientViTSamPredictor(efficientvit_sam)
    return efficientvit_sam_predictor
