# Clone repository
git clone https://github.com/avraniel/audio-converter-pro.git
cd audio-converter-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install and run
pip install -r requirements.txt
python src/audio_converter_pro.py
