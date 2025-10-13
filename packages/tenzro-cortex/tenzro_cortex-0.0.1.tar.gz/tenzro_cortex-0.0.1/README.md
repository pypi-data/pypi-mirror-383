# Tenzro Cortex

Universal LLM training and inference platform.

## Installation

```bash
pip install tenzro-cortex
```

## Quick Start

```bash
# Configure
tenzro-cortex configure
# Enter your API key from team@tenzro.network

# Create training data (JSONL format)
cat > training.jsonl << 'EOF'
{"messages": [{"role": "user", "content": "What is AI?"}, {"role": "assistant", "content": "Artificial Intelligence"}]}
{"messages": [{"role": "user", "content": "What is ML?"}, {"role": "assistant", "content": "Machine Learning"}]}
EOF

# Train a model
tenzro-cortex train -f training.jsonl -m microsoft/phi-2 -e 1

# Check status
tenzro-cortex status

# Run inference
tenzro-cortex infer -m microsoft/phi-2 -p "What is deep learning?"
```

## CLI Commands

### configure
Configure API credentials.

```bash
tenzro-cortex configure
```

### train
Submit a training job.

```bash
tenzro-cortex train -f <file> -m <model> -e <epochs> -n <name>
```

Options:
- `-f, --file`: Training data file (JSONL format, required)
- `-m, --model`: Base model from HuggingFace (default: microsoft/phi-2)
- `-e, --epochs`: Number of training epochs (default: 1)
- `-n, --name`: Job name (optional)

### status
Check job status.

```bash
# List recent jobs
tenzro-cortex status

# Check specific job
tenzro-cortex status <job_id>
```

### infer
Run inference on a model.

```bash
tenzro-cortex infer -m <model> -p <prompt>
```

Options:
- `-m, --model`: Model to use (default: microsoft/phi-2)
- `-p, --prompt`: Input prompt (required)

### models
List popular models.

```bash
tenzro-cortex models
```

### quickstart
Show quick start guide.

```bash
tenzro-cortex quickstart
```

## Training Data Format

Training data must be in JSONL (JSON Lines) format with chat messages:

```json
{"messages": [{"role": "user", "content": "question"}, {"role": "assistant", "content": "answer"}]}
{"messages": [{"role": "user", "content": "question"}, {"role": "assistant", "content": "answer"}]}
```

Each line is a separate training example.

## API Endpoints

Base URL: `https://cortex.tenzro.network`

### Submit Training Job
```bash
POST /jobs/enhanced
Content-Type: application/json
X-API-Key: your_key

{
  "config": {
    "model": {"name_or_path": "microsoft/phi-2"},
    "training": {"num_epochs": 1},
    "data": {"train_file": "...", "format": "chat"},
    "lora": {"rank": 8, "alpha": 16}
  },
  "job_name": "my_job"
}
```

### Check Job Status
```bash
GET /jobs/{job_id}
X-API-Key: your_key
```

### List Jobs
```bash
GET /jobs?limit=10
X-API-Key: your_key
```

### Inference (OpenAI-compatible)
```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "model": "microsoft/phi-2",
  "messages": [{"role": "user", "content": "Hello"}],
  "max_tokens": 100
}
```

## System Architecture

- **API**: FastAPI service managing jobs and authentication
- **Training**: LoRA fine-tuning via HuggingFace transformers
- **Inference**: Transformers-based inference service
- **Queue**: FoundationDB for job coordination
- **Compute**: NVIDIA GPU (tested on A100)

## Training Details

- **Method**: LoRA (Low-Rank Adaptation)
- **Output**: Small adapter files (~46MB for phi-2)
- **Trainable params**: ~0.4-0.6% of model parameters
- **Speed**: ~15-20 seconds per epoch (phi-2, small dataset)

## Tested Models

- microsoft/phi-2 (2.7B) - Verified working
- Other HuggingFace models may work but are untested

## Known Issues

- Multi-worker race condition can cause some jobs to fail (~20%)
- Only single-GPU tested
- Limited model compatibility testing

## Support

- Email: team@tenzro.network
- API: https://cortex.tenzro.network

## License

Apache License 2.0

## Development

Add trainer node:
```bash
curl -fsSL https://cortex.tenzro.network/add-trainer.sh | bash -s <NODE_IP>
```

Add inference node:
```bash
curl -fsSL https://cortex.tenzro.network/add-inference.sh | bash -s <NODE_IP> <MODEL>
```

Admin CLI:
```bash
tenzro-cortex-admin status          # Check system
tenzro-cortex-admin grid list       # List GPU nodes
tenzro-cortex-admin admin list-keys # List API keys
```
