# echo-sadtalker

SadTalker talking photo service — animates a still photo with audio to produce a lip-synced video.

## Usage

```bash
docker compose up --build
```

Access the Gradio UI at `http://localhost:7862`

## How it works

Upload a photo + audio file → get a lip-synced video output.

## Volumes

Mount model checkpoints before running:

| Host path | Container path | Description |
|-----------|----------------|-------------|
| `./checkpoints` | `/app/checkpoints` | SadTalker model checkpoints |
| `./gfpgan_weights` | `/app/gfpgan/weights` | GFPGAN face enhancement weights |
| `./results` | `/app/results` | Output videos |

Download checkpoints with:
```bash
bash scripts/download_models.sh
```

## Port

`7862` (Gradio UI)

## Device

CPU mode by default. For GPU support, modify the Dockerfile to use a CUDA base image and adjust pip install accordingly.
