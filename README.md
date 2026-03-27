# echo-sadtalker

SadTalker talking photo service — animates a still portrait photo with audio to produce a lip-synced video.

Running on the Mac mini (Echo) with Apple Silicon MPS acceleration, accessible from the NAS network via Traefik.

## Architecture

```
Browser / NAS apps
      │
      ▼
Traefik (NAS) → sadtalker.192.168.68.52.sslip.io:8090
      │
      ▼
Gradio UI (Mac mini :7863) — app_sadtalker.py
      │  no queue, max_threads=1, direct HTTP POST
      ▼
gradio_demo.py → subprocess → inference.py
                                    │
                                    ▼
                              Apple MPS (GPU)
                              batch_size=1
```

Each request spawns a fresh `inference.py` subprocess with its own MPS context — no cross-thread GPU state issues.

## Performance (Apple M-series, 8GB)

| Audio length | Approx. generation time |
|---|---|
| 5s | ~2–3 min |
| 15s | ~7 min |
| 30s | ~13–14 min |

Speed: ~1 second per video frame at MPS, batch_size=1.

## Access

- **Local:** `http://localhost:7863`
- **Network (via Traefik on NAS):** `http://sadtalker.192.168.68.52.sslip.io:8090`

## Auto-start (LaunchAgent)

The service is managed by a macOS LaunchAgent and starts automatically on login:

```
/Users/merliniferrao/Library/LaunchAgents/com.echo.sadtalker.plist
```

Logs: `/Users/merliniferrao/sadtalker/sadtalker.log`

Restart manually:
```bash
launchctl unload ~/Library/LaunchAgents/com.echo.sadtalker.plist
launchctl load ~/Library/LaunchAgents/com.echo.sadtalker.plist
```

## Input requirements

- **Photo:** portrait with a clear, forward-facing human face. Real people only (not anime/cartoons). Minimum ~500px height. PNG or JPG.
- **Audio:** WAV or MP3. MP3 is auto-converted to WAV at 16kHz.

## Settings

| Setting | Default | Notes |
|---|---|---|
| Preprocess | `crop` | Crops face region. Use `full` + Still Mode for full-body shots |
| Face model resolution | 256 | 512 gives sharper output but uses more memory |
| Still Mode | off | Reduces head movement — good for full-body with `full` preprocess |
| Pose style | 0 | 0–46, controls head movement style |
| Batch size | 1 | Keep at 1 on 8GB Mac. Higher values risk OOM crash |
| GFPGAN enhancer | off | Face enhancement post-process — slower but sharper |

## Checkpoints

Models are stored in `./checkpoints/`. Download with:

```bash
bash scripts/download_models.sh
```

## Key changes from upstream

- **MPS support** — `inference.py` auto-detects Apple Silicon GPU (`torch.backends.mps`)
- **Subprocess architecture** — inference runs in a child process, keeping Gradio lightweight (~338MB) and avoiding MPS thread-context issues
- **No Gradio queue** — long-running inference (7+ min) requires disabling Gradio's queue to avoid the 5-second heartbeat timeout
- **Lower face detection threshold** — 0.97 → 0.5 to handle more portrait photo styles
- **MP3 support** — auto-converts MP3 to WAV before processing
