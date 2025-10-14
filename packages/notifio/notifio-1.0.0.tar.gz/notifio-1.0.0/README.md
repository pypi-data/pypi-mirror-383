# Notifio

[![PyPI version](https://badge.fury.io/py/notifio.svg)](https://badge.fury.io/py/notifio)
[![Python Support](https://img.shields.io/pypi/pyversions/notifio.svg)](https://pypi.org/project/notifio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Universal Telegram notification service for Python applications. Send formatted messages, alerts, and status updates to Telegram with minimal setup.

## Features

- 🚀 **Simple Setup** - Configure with just two environment variables
- 📱 **Rich Notifications** - Send formatted messages with emojis and structured data
- 🔄 **Multiple Message Types** - Success, error, warning, info, and custom notifications
- ⏰ **Sleep/Wake Notifications** - Perfect for background tasks and scheduled jobs
- 📊 **Summary Reports** - Send detailed summaries with statistics
- 🛡️ **Error Handling** - Graceful fallback when notifications fail
- 🔧 **Easy Integration** - Works with any Python application

## Quick Start

### Installation

```bash
pip install notifio
```

### Basic Usage

```python
from notifio import get_notifio

# Initialize Notifio (uses environment variables)
notifio = get_notifio()

if notifio:
    # Send a simple message
    notifio.send_message("🚀 Application started successfully!")
    
    # Send a formatted success notification
    notifio.send_success("Data Processing Complete", {
        "Records processed": 1500,
        "Processing time": "2.5 minutes",
        "Status": "Success"
    })
```

### Setup

1. **Create a Telegram Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Use `/newbot` command and follow instructions
   - Save the bot token

2. **Get Your Chat ID:**
   - Message your bot or add it to a group
   - Use the provided `get_chat_id.py` script or visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

3. **Set Environment Variables:**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token_here"
   export TELEGRAM_CHAT_ID="your_chat_id_here"
   ```

   Or create a `.env` file:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

## Message Types

### Basic Message
```python
notifio.send_message("Hello from Notifio!")
```

### Success Notification
```python
notifio.send_success("Task Completed", {
    "Items processed": 100,
    "Success rate": "98%",
    "Duration": "5.2 minutes"
})
```

### Error Notification
```python
notifio.send_error("Database Connection Failed", {
    "Error": "Connection timeout",
    "Retry attempts": 3,
    "Last attempt": "2025-01-27 14:30:00"
})
```

### Warning Notification
```python
notifio.send_warning("High Memory Usage", {
    "Current usage": "85%",
    "Threshold": "80%",
    "Action": "Monitoring"
})
```

### Info Notification
```python
notifio.send_info("System Status", {
    "CPU usage": "45%",
    "Memory usage": "2.1GB",
    "Uptime": "5 days"
})
```

### Sleep/Wake Notifications
```python
# Before going to sleep
notifio.send_sleep_notification("Background Task", 8.5, "2025-01-28 08:00:00", {
    "Processed items": 200,
    "Daily limit": 200
})

# When waking up
notifio.send_wake_notification("Background Task", {
    "Resumed at": "2025-01-28 08:00:00",
    "Items to process": 150
})
```

### Summary Notification
```python
notifio.send_summary("Daily Report", {
    "Total tasks": 25,
    "Completed": 23,
    "Failed": 2,
    "Success rate": "92%"
}, "All systems operational")
```

## Advanced Usage

### Custom Formatted Messages
```python
notifio.send_formatted_message("Custom Alert", {
    "Level": "CRITICAL",
    "Service": "API Gateway",
    "Response time": "5.2s"
}, "🚨", "Immediate attention required")
```

### Error Handling
```python
from notifio import get_notifio

notifio = get_notifio()

if not notifio:
    print("Notifio not configured - notifications disabled")
    # Your app continues without notifications
else:
    # Send notifications
    notifio.send_message("App started")
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Yes |
| `TELEGRAM_CHAT_ID` | Target chat ID for notifications | Yes |

### Optional Configuration

You can also initialize Notifio directly:

```python
from notifio import Notifio

notifio = Notifio(
    bot_token="your_bot_token",
    chat_id="your_chat_id"
)
```

## Examples

### Background Job Monitoring
```python
import time
from notifio import get_notifio

notifio = get_notifio()

def process_data():
    if notifio:
        notifio.send_info("Data Processing Started", {
            "Start time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "Status": "Running"
        })
    
    try:
        # Your data processing logic here
        result = process_large_dataset()
        
        if notifio:
            notifio.send_success("Data Processing Completed", {
                "Records processed": result['count'],
                "Duration": f"{result['duration']:.1f} seconds",
                "Status": "Success"
            })
            
    except Exception as e:
        if notifio:
            notifio.send_error("Data Processing Failed", {
                "Error": str(e),
                "Status": "Failed"
            })
        raise
```

### System Monitoring
```python
import psutil
from notifio import get_notifio

notifio = get_notifio()

def check_system_health():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    if cpu_percent > 80:
        notifio.send_warning("High CPU Usage", {
            "CPU usage": f"{cpu_percent}%",
            "Memory usage": f"{memory.percent}%",
            "Action": "Monitoring"
        })
    
    if memory.percent > 90:
        notifio.send_error("Critical Memory Usage", {
            "Memory usage": f"{memory.percent}%",
            "Available": f"{memory.available / (1024**3):.1f} GB",
            "Action": "Immediate attention required"
        })
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Building Package
```bash
python -m build
```

### Publishing to PyPI
```bash
python -m twine upload dist/*
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 📖 [Documentation](https://github.com/yourusername/notifio#readme)
- 🐛 [Issue Tracker](https://github.com/yourusername/notifio/issues)
- 💬 [Discussions](https://github.com/yourusername/notifio/discussions)

## Changelog

### 1.0.0
- Initial release
- Basic notification functionality
- Multiple message types
- Environment variable configuration
- Error handling and graceful fallback
