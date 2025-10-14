#!/usr/bin/env python3
"""
Notifio - Universal Telegram notification service.
A simple, flexible library for sending Telegram notifications from any application.
"""

import os
import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class Notifio:
    """Universal Telegram notification service."""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Initialize Notifio service.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        """
        Send a message to Telegram.
        
        Args:
            message: Message to send
            parse_mode: Message parsing mode (Markdown or HTML)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Notifio notification sent successfully")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Notifio notification: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Notifio notification: {e}")
            return False
    
    def send_formatted_message(self, title: str, content: Dict[str, Any], 
                             status_emoji: str = "📢", footer: str = None) -> bool:
        """
        Send a formatted message with title and key-value pairs.
        
        Args:
            title: Message title
            content: Dictionary of key-value pairs to display
            status_emoji: Emoji for the status (default: 📢)
            footer: Optional footer text
            
        Returns:
            True if message sent successfully, False otherwise
        """
        message = f"{status_emoji} *{title}*\n\n"
        
        for key, value in content.items():
            message += f"*{key}:* {value}\n"
        
        if footer:
            message += f"\n_{footer}_"
        
        return self.send_message(message)
    
    def send_success(self, title: str, details: Dict[str, Any], footer: str = None) -> bool:
        """Send a success notification."""
        return self.send_formatted_message(title, details, "✅", footer)
    
    def send_warning(self, title: str, details: Dict[str, Any], footer: str = None) -> bool:
        """Send a warning notification."""
        return self.send_formatted_message(title, details, "⚠️", footer)
    
    def send_error(self, title: str, details: Dict[str, Any], footer: str = None) -> bool:
        """Send an error notification."""
        return self.send_formatted_message(title, details, "❌", footer)
    
    def send_info(self, title: str, details: Dict[str, Any], footer: str = None) -> bool:
        """Send an info notification."""
        return self.send_formatted_message(title, details, "ℹ️", footer)
    
    def send_sleep_notification(self, title: str, sleep_duration: float, 
                               wake_up_time: str, details: Dict[str, Any] = None) -> bool:
        """Send a sleep notification with wake-up time."""
        content = {
            "Status": "Going to sleep",
            "Sleep duration": f"{sleep_duration} hours",
            "Wake up time": wake_up_time
        }
        
        if details:
            content.update(details)
        
        return self.send_formatted_message(title, content, "😴", "Will resume after sleep...")
    
    def send_wake_notification(self, title: str, details: Dict[str, Any] = None) -> bool:
        """Send a wake-up notification."""
        content = {
            "Status": "Resumed processing",
            "Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if details:
            content.update(details)
        
        return self.send_formatted_message(title, content, "😴", "Resuming processing...")
    
    def send_summary(self, title: str, summary_data: Dict[str, Any], 
                    total_items: int = None) -> bool:
        """Send a summary notification."""
        content = summary_data.copy()
        
        if total_items is not None:
            content["Total items"] = total_items
        
        content["Summary time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return self.send_formatted_message(title, content, "📊", "Summary completed!")
    
    def send_test_message(self, app_name: str = "Notifio") -> bool:
        """Send a test message."""
        message = f"""
🧪 *{app_name} Test*

This is a test notification to verify that Notifio is working correctly.

⏰ *Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🖥️ *Server:* {os.uname().nodename if hasattr(os, 'uname') else 'Unknown'}

_Test completed successfully!_
        """.strip()
        
        return self.send_message(message)


def get_notifio() -> Optional[Notifio]:
    """
    Create Notifio service from environment variables.
    
    Returns:
        Notifio instance if configured, None otherwise
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logger.warning("Notifio notifications not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID)")
        return None
    
    return Notifio(bot_token, chat_id)


# Test function
def test_notifio():
    """Test Notifio notification functionality."""
    notifier = get_notifio()
    
    if not notifier:
        print("❌ Notifio not configured")
        return False
    
    # Send test message
    success = notifier.send_test_message()
    
    if success:
        print("✅ Notifio test successful")
    else:
        print("❌ Notifio test failed")
    
    return success


if __name__ == "__main__":
    # Test the notification system
    test_notifio()