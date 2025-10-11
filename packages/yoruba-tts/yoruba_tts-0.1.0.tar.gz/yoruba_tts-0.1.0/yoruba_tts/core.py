import torch
import numpy as np
import scipy.io.wavfile as wav
from pathlib import Path
from typing import Union, Optional, Dict, Any
from dataclasses import dataclass
import io
import soundfile as sf

from .models.model_manager import ModelManager

@dataclass
class TTSOptions:
    """Options for TTS generation"""
    voice: str = "main"
    speed: float = 1.0
    sample_rate: int = 22050
    output_format: str = "wav"

class YorubaTTS:
    """Main Yoruba TTS class"""
    
    def __init__(self, model_dir: Optional[str] = None):
        self.model_manager = ModelManager(model_dir)
        self.is_initialized = False
        
    def initialize(self):
        """Initialize models (called automatically on first use)"""
        if not self.is_initialized:
            self.model_manager.load_models()
            self.is_initialized = True
    
    def text_to_speech(self, text: str, options: Optional[TTSOptions] = None) -> np.ndarray:
        if not self.is_initialized:
            self.initialize()
            
        if options is None:
            options = TTSOptions()
        
        if not self._validate_text(text):
            raise ValueError("Text cannot be empty")
        
        if options.voice == "main":
            model = self.model_manager.main_model
            tokenizer = self.model_manager.main_tokenizer
        elif options.voice == "fallback":
            if self.model_manager.fallback_model is None:
                print("⚠️  Fallback model not available, using main model")
                model = self.model_manager.main_model
                tokenizer = self.model_manager.main_tokenizer
            else:
                model = self.model_manager.fallback_model
                tokenizer = self.model_manager.fallback_tokenizer
        else:
            raise ValueError(f"Unknown voice: {options.voice}")
        
        inputs = tokenizer(text, return_tensors="pt")
        with torch.no_grad():
            output = model(**inputs)
        
        audio = output.waveform if hasattr(output, 'waveform') else output[0]
        audio_np = audio.squeeze().cpu().numpy()
        
        if np.max(np.abs(audio_np)) > 0:
            audio_np = audio_np / np.max(np.abs(audio_np)) * 0.9
        
        return audio_np
    
    def save_to_file(self, audio: np.ndarray, filename: str, sample_rate: int = 22050):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        wav.write(filename, sample_rate, (audio * 32767).astype(np.int16))
        print(f"✅ Audio saved to: {filename}")
    
    def text_to_speech_file(self, text: str, output_file: str, options: Optional[TTSOptions] = None):
        audio = self.text_to_speech(text, options)
        self.save_to_file(audio, output_file, options.sample_rate if options else 22050)
    
    def get_audio_bytes(self, text: str, options: Optional[TTSOptions] = None) -> bytes:
        audio = self.text_to_speech(text, options)
        buffer = io.BytesIO()
        sf.write(buffer, audio, options.sample_rate if options else 22050, format='WAV')
        return buffer.getvalue()
    
    def _validate_text(self, text: str) -> bool:
        return bool(text and text.strip())
    
    def get_available_voices(self) -> list:
        voices = ["main"]
        if self.model_manager.fallback_model is not None:
            voices.append("fallback")
        return voices
    
    def get_model_info(self) -> Dict[str, Any]:
        if not self.is_initialized:
            return {"status": "Models not initialized yet"}
        return self.model_manager.get_model_info()
    
    def cleanup_cache(self):
        self.model_manager.cleanup_cache()
    
    def test_models(self, test_texts: list = None) -> Dict[str, Any]:
        if not self.is_initialized:
            self.initialize()
            
        if test_texts is None:
            test_texts = ["Ẹ kú àbọ̀", "Báwo ni o se wa?", "Ẹ ṣeun púpò"]
        
        results = {}
        for voice in self.get_available_voices():
            results[voice] = {}
            for text in test_texts:
                try:
                    options = TTSOptions(voice=voice)
                    audio = self.text_to_speech(text, options)
                    duration = len(audio) / 22050
                    results[voice][text] = {
                        "success": True,
                        "duration": f"{duration:.2f}s"
                    }
                    print(f"✅ {voice}: '{text}' → {duration:.2f}s")
                except Exception as e:
                    results[voice][text] = {"success": False, "error": str(e)}
                    print(f"❌ {voice}: '{text}' → Error: {e}")
        return results