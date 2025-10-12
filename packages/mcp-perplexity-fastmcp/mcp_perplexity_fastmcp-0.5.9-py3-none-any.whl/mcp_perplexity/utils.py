from pathlib import Path

def get_logs_dir():
    """Get the logs directory path.
    
    Returns a path in the user's home directory to ensure it's writable.
    """
    home_dir = Path.home()
    logs_dir = home_dir / ".mcp-perplexity" / "logs"
    return logs_dir 