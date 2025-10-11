import numpy as np

def normalize_audio(audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
    """Normalize audio to target level"""
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        return audio / max_val * target_level
    return audio