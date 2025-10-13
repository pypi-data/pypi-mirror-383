#!/usr/bin/env python3
"""Tenzro Cortex CLI - Fine-tune and deploy AI models"""

import click
import requests
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
CONFIG_DIR = Path.home() / ".tenzro"
CONFIG_FILE = CONFIG_DIR / "config.json"

def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)

def save_config(config):
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_api_config():
    config = load_config()
    api_url = config.get('api_url')
    api_key = config.get('api_key')
    if not api_url or not api_key:
        console.print("[red]Error: Not configured. Run 'tenzro-cortex configure' first[/red]")
        raise click.Abort()
    return api_url, api_key

@click.group()
def cli():
    """Tenzro Cortex - Fine-tune and deploy AI models"""
    pass

@cli.command()
@click.option('--api-key', prompt='API Key')
def configure(api_key):
    """Configure Tenzro Cortex"""
    config = {'api_url': 'https://cortex.tenzro.network', 'api_key': api_key}
    save_config(config)
    console.print("[green]✓ Configuration saved[/green]")

@cli.command()
def quickstart():
    """Quick start guide"""
    console.print(Panel("""
[bold]Tenzro Cortex Quick Start[/bold]

1. Configure
   tenzro-cortex configure

2. Create data.jsonl
   {"messages": [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}]}

3. Train
   tenzro-cortex train -f data.jsonl -m microsoft/phi-2

4. Check status
   tenzro-cortex status

5. Use model
   tenzro-cortex infer -m microsoft/phi-2 -p "Hello!"
""", title="Quick Start"))

@cli.command()
def models():
    """List popular models"""
    table = Table(title="Popular Models")
    table.add_column("Name", style="cyan")
    table.add_column("HuggingFace ID", style="green")
    table.add_column("Size", style="yellow")
    table.add_column("Best For", style="magenta")
    
    models_list = [
        ("Phi-2", "microsoft/phi-2", "2.7B", "Fast & Efficient"),
        ("Phi-4", "microsoft/phi-4", "14B", "Balanced"),
        ("Llama 3.1", "meta-llama/Llama-3.1-8B", "8B", "General purpose"),
        ("Mistral", "mistralai/Mistral-7B-v0.1", "7B", "Production"),
        ("Qwen", "Qwen/Qwen2.5-7B", "7B", "Multilingual"),
    ]
    
    for name, hf_id, size, best_for in models_list:
        table.add_row(name, hf_id, size, best_for)
    console.print(table)

@cli.command()
@click.option('-f', '--file', required=True, help='Training data (JSONL)')
@click.option('-m', '--model', default='microsoft/phi-2', help='Base model')
@click.option('-e', '--epochs', default=1, help='Epochs')
@click.option('-n', '--name', help='Job name')
def train(file, model, epochs, name):
    """Train a custom model"""
    api_url, api_key = get_api_config()
    
    file_path = Path(file)
    if not file_path.exists():
        console.print(f"[red]Error: File not found: {file}[/red]")
        return
    
    training_data = file_path.read_text()
    
    console.print(f"[cyan]Submitting training job...[/cyan]")
    console.print(f"  Model: {model}")
    console.print(f"  Data: {len(training_data.splitlines())} samples")
    console.print(f"  Epochs: {epochs}")
    
    response = requests.post(
        f"{api_url}/jobs/enhanced",
        headers={"X-API-Key": api_key, "Content-Type": "application/json"},
        json={
            "config": {
                "model": {"name_or_path": model},
                "training": {"num_epochs": epochs, "per_device_train_batch_size": 1},
                "data": {"train_file": training_data, "format": "chat"},
                "lora": {"rank": 8, "alpha": 16}
            },
            "job_name": name
        }
    )
    
    if response.status_code == 200:
        job = response.json()
        console.print(f"[green]✓ Job submitted: {job['job_id']}[/green]")
        console.print(f"\nCheck status: tenzro-cortex status {job['job_id']}")
    else:
        console.print(f"[red]Error: {response.text}[/red]")

@cli.command()
@click.argument('job_id', required=False)
def status(job_id):
    """Check job status"""
    api_url, api_key = get_api_config()
    
    if job_id:
        response = requests.get(f"{api_url}/jobs/{job_id}", headers={"X-API-Key": api_key})
        if response.status_code == 200:
            job = response.json()
            console.print(f"Job: {job['job_id']}")
            console.print(f"Status: {job['status']}")
            console.print(f"Progress: {job.get('progress', 0)*100:.0f}%")
        else:
            console.print(f"[red]Error: {response.text}[/red]")
    else:
        response = requests.get(f"{api_url}/jobs?limit=10", headers={"X-API-Key": api_key})
        if response.status_code == 200:
            jobs = response.json().get('jobs', [])
            table = Table(title="Recent Jobs")
            table.add_column("Job ID")
            table.add_column("Status")
            table.add_column("Name")
            for job in jobs:
                table.add_row(job['job_id'], job['status'], job.get('job_name', 'N/A'))
            console.print(table)

@cli.command()
@click.option('-m', '--model', default='microsoft/phi-2', help='Model')
@click.option('-p', '--prompt', required=True, help='Prompt')
def infer(model, prompt):
    """Run inference"""
    inference_url = "https://cortex.tenzro.network"
    
    response = requests.post(
        f"{inference_url}/v1/chat/completions",
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        console.print(result['choices'][0]['message']['content'])
    else:
        console.print(f"[red]Error: {response.text}[/red]")

if __name__ == "__main__":
    cli()
