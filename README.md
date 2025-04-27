# Backdoor AI: Code Less, Make More

Backdoor AI is a powerful AI assistant that helps you write code, solve problems, and get things done faster. It uses the StarCoder model to provide intelligent code assistance.

## Features

- **Hardcoded StarCoder Model**: Optimized for code generation and understanding
- **GitHub Integration**: Seamlessly work with your GitHub repositories
- **Simple Setup**: Easy to install and configure

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/BackdoorAI.git
cd BackdoorAI
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up vLLM with StarCoder:
```bash
./setup_vllm_starcoder.sh
```

4. Start the vLLM server:
```bash
vllm serve bigcode/starcoder --port 8000
```

5. Start Backdoor AI:
```bash
python -m openhands.server.main
```

## Configuration

The main configuration is in `config.toml`. The default configuration uses the StarCoder model with vLLM.

## GitHub Integration

To use GitHub integration, you need to set up a GitHub token:

1. Go to Settings > Git Settings
2. Enter your GitHub token
3. Save the settings

## License

MIT License
