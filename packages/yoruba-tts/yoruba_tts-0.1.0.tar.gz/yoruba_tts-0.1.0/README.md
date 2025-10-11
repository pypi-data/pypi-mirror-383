Add a note about the download behavior:

markdown
## Installation

```bash
pip install yoruba-tts
Features
🎯 Main model included - No download required for basic usage

📥 Fallback model auto-download - Additional voice available on first use

🗣️ Multiple voice options

📦 Lightweight package

🎵 High-quality audio output

First Use
The fallback model will be automatically downloaded on first use:

python
from yoruba_tts import YorubaTTS

tts = YorubaTTS()
# First use of fallback voice will trigger download
audio = tts.text_to_speech("Ẹ kú àbọ̀", options=TTSUptions(voice="fallback"))
Cache Management
Downloaded models are cached in ~/.yoruba_tts/. To clean the cache:

bash
yoruba-tts --cleanup-cache
text

## 6. Build and Test

Now rebuild with the smaller package:

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build new package
python -m build

# Check package size
ls -lh dist/

# Install locally to test
pip install dist/yoruba_tts-0.1.0-py3-none-any.whl

# Test
yoruba-tts --model-info
yoruba-tts --test
This approach should give you a much smaller package size (probably under 100MB) while still providing both voice options. The fallback model will be downloaded automatically when first used.