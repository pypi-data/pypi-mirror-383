#!/usr/bin/env python3
"""
Command-line interface for Yoruba TTS
"""

import argparse
import sys
from .core import YorubaTTS, TTSOptions

def main():
    parser = argparse.ArgumentParser(description="Yoruba Text-to-Speech CLI")
    parser.add_argument("text", nargs="?", help="Yoruba text to convert to speech")
    parser.add_argument("-o", "--output", help="Output audio file")
    parser.add_argument("-v", "--voice", choices=["main", "fallback"], default="main", 
                       help="Voice to use (default: main)")
    parser.add_argument("--test", action="store_true", help="Test all models")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    parser.add_argument("--cleanup-cache", action="store_true", help="Clean downloaded models cache")
    parser.add_argument("--model-info", action="store_true", help="Show model information")
    
    args = parser.parse_args()
    
    tts = YorubaTTS()
    
    if args.cleanup_cache:
        tts.cleanup_cache()
        return
    
    if args.model_info:
        info = tts.get_model_info()
        print("📊 Model Information:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        return
    
    if args.list_voices:
        voices = tts.get_available_voices()
        print("Available voices:")
        for voice in voices:
            print(f"  - {voice}")
        return
    
    if args.test:
        print("🧪 Testing Yoruba TTS models...")
        tts.test_models()
        return
    
    if not args.text:
        print("Error: No text provided")
        parser.print_help()
        sys.exit(1)
    
    try:
        options = TTSOptions(voice=args.voice)
        if args.output:
            tts.text_to_speech_file(args.text, args.output, options)
        else:
            output_file = f"yoruba_tts_{args.voice}.wav"
            tts.text_to_speech_file(args.text, output_file, options)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()