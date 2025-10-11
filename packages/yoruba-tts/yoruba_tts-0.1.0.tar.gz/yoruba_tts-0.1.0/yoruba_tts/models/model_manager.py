import torch
from transformers import AutoTokenizer, AutoModelForTextToWaveform
from pathlib import Path
from typing import Optional, Dict, Any

class ModelManager:
    """Download models on first use - no local files needed"""
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = Path(model_dir) if model_dir else Path.home() / ".yoruba_tts"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        self.main_model = None
        self.main_tokenizer = None
        self.fallback_model = None
        self.fallback_tokenizer = None
        self.models_loaded = False
        
    def load_models(self):
        """Download models on first use"""
        if self.models_loaded:
            return
            
        print("🔧 Downloading Yoruba TTS models (this may take a few minutes)...")
        
        try:
            # Download main model
            print("📥 Downloading main model from Humphery7/tts-models-yoruba...")
            self.main_tokenizer = AutoTokenizer.from_pretrained("Humphery7/tts-models-yoruba")
            self.main_model = AutoModelForTextToWaveform.from_pretrained("Humphery7/tts-models-yoruba")
            self.main_model = self.main_model.eval()
            
            # Download fallback model
            print("📥 Downloading fallback model from Workhelio/yoruba_tts...")
            self.fallback_tokenizer = AutoTokenizer.from_pretrained("Workhelio/yoruba_tts")
            self.fallback_model = AutoModelForTextToWaveform.from_pretrained("Workhelio/yoruba_tts")
            self.fallback_model = self.fallback_model.eval()
            
            print("✅ All models downloaded successfully!")
            self.models_loaded = True
            
        except Exception as e:
            print(f"❌ Error downloading models: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "main_model_loaded": self.main_model is not None,
            "fallback_model_loaded": self.fallback_model is not None,
            "models_loaded": self.models_loaded,
            "model_source": "huggingface_hub"
        }
    
    def cleanup_cache(self):
        """Clean up downloaded models"""
        import shutil
        if self.model_dir.exists():
            shutil.rmtree(self.model_dir)
            print("✅ Cache cleaned up")