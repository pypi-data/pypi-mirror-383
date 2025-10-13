# Find the configure function and replace it with:

@cli.command()
@click.option('--api-key', prompt='API Key', help='Your Tenzro API key')
def configure(api_key):
    """Configure Tenzro Cortex"""
    config = {
        'api_url': 'https://cortex.tenzro.network',  # Fixed, no prompt
        'api_key': api_key
    }
    save_config(config)
    console.print("[green]✓ Configuration saved[/green]")
    console.print(f"API URL: {config['api_url']}")
