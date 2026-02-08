# LocalGPT (Jetson Orin Nano)

LocalGPT is a fully offline, GPU-accelerated “ChatGPT-style” assistant that runs entirely on an NVIDIA Jetson Orin Nano. It uses **llama.cpp with CUDA acceleration** to run a local Large Language Model (Llama 3.2 3B GGUF) and provides an interactive, streaming terminal interface with chat history, session saving/loading, and multiple prompt modes.

All inference happens locally on the Jetson — **no cloud APIs, no internet required at runtime**. This project demonstrates real-world edge AI deployment by combining embedded systems, GPU acceleration, and modern LLM tooling into a polished, user-facing application.

---

## Features

- Fully offline LLM inference  
- NVIDIA Jetson GPU acceleration (CUDA)  
- Streaming responses (token-by-token like ChatGPT)  
- Interactive terminal UI  
- Persistent chat sessions (save/load)  
- Prompt modes (default, coding, tutor, snark)  
- Optional auto-start of `llama-server` via systemd  

---

## Requirements

### Hardware
- NVIDIA Jetson Orin Nano (8GB or 16GB recommended)

### Software
- JetPack 6 (L4T R36.x)
- Ubuntu (JetPack default)
- Python 3.9+
- `llama.cpp` built with CUDA support

---

## Repository Layout

```text
localgpt/
├── localgpt.py        # Streaming terminal chat client
├── run_server.sh      # Starts llama-server
├── run_localgpt.sh    # Starts server (if needed) + CLI
├── config.env         # Model + runtime configuration
├── README.md

