# LocalGPT (Jetson Orin Nano)

LocalGPT on Jetson Orin Nano is a fully offline, GPU-accelerated large language model system built for edge deployment. The project uses llama.cpp with CUDA acceleration to run a Llama 3.2 3B GGUF model entirely on an NVIDIA Jetson Orin Nano, providing an interactive, ChatGPT-style terminal interface with real-time streaming responses, persistent chat sessions, and configurable prompt modes. The system is designed as a production-ready application, featuring automatic server startup, systemd integration, and robust process management, demonstrating practical experience in embedded Linux, GPU-accelerated inference, and end-to-end AI system integration without reliance on cloud services.

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
- NVIDIA Jetson Orin Nano 

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
```

## Build llama.cpp with CUDA   
cd ~   
git clone https://github.com/ggml-org/llama.cpp.git   
cd llama.cpp    

cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release   
cmake --build build -j$(nproc)   

Verify:   
ls build/bin   

You should see llama-server and llama-cli.   

## Download a GGUF Instruct model   

Example (Llama 3.2 3B Instruct Uncensored Q4):   

mkdir -p ~/models/llama-3.2-3b   
cd ~/models/llama-3.2-3b   

wget https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-uncensored-GGUF/resolve/main/Llama-3.2-3B-Instruct-uncensored-Q4_K_M.gguf   

## Configure LocalGPT  
   
Edit config.env:   
nano config.env   
Example:   
MODEL=/home/USERNAME/models/llama-3.2-3b/Llama-3.2-3B-Instruct-uncensored-Q4_K_M.gguf   
HOST=127.0.0.1   
PORT=8080   
CTX=2048   
GPU_LAYERS=99   
Replace USERNAME with your Linux username.   

## Install Python dependency   
pip3 install --user rich   
Running LocalGPT   
Run directly   
./run_localgpt.sh   

This will:   
Start llama-server if it is not already running   
Launch the interactive LocalGPT terminal UI   

## Optional: Install a global command   
mkdir -p ~/bin   
ln -s $(pwd)/run_localgpt.sh ~/bin/localgpt   
chmod +x ~/bin/localgpt   

Ensure ~/bin is in your PATH:   
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc   
source ~/.bashrc   

Run from anywhere:   

localgpt   

Terminal Commands   
/help          show help   
/mode coding   coding assistant    
/mode tutor    tutoring mode    
/mode snark    playful mode   
/save          save current chat   
/list          list saved chats   
/load <id>     load saved session   
/temp 0.2      adjust randomness   
/ctx 8000      change context size   
/exit          quit   

## Optional: Auto-Start on Boot (systemd)   

Create the service file:   

sudo nano /etc/systemd/system/localgpt-llama.service   

[Unit]   
Description=LocalGPT llama.cpp server   
After=network.target   

[Service]   
Type=simple   
User=USERNAME   
WorkingDirectory=/home/USERNAME/localgpt   
EnvironmentFile=/home/USERNAME/localgpt/config.env   
ExecStart=/home/USERNAME/localgpt/run_server.sh   
Restart=always   
RestartSec=2   

[Install]   
WantedBy=multi-user.target   

# Enable:   
sudo systemctl daemon-reload   
sudo systemctl enable --now localgpt-llama.service   

Check status:   
systemctl status localgpt-llama.service   
