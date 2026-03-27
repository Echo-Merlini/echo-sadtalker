FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    ffmpeg libsndfile1 libgl1 libglib2.0-0 wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY req.txt requirements.txt requirements3d.txt ./
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r req.txt
RUN pip install --no-cache-dir gradio

COPY . .

VOLUME ["/app/checkpoints", "/app/gfpgan/weights", "/app/results"]

EXPOSE 7862

CMD ["python3", "app_sadtalker.py"]
