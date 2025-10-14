#!/usr/bin/env python3
"""
Test script for Notifio - Telegram notification service.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from notifio import get_notifio, test_notifio

# Load environment variables from .env file if it exists (for local development)
# On server, environment variables are passed directly
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)

def main():
    """Test Notifio functionality."""
    print("🧪 Testing Notifio - Telegram notification service...")
    print()
    
    # Check if environment variables are set
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        print("   Set it in your .env file or environment variables")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not set")
        print("   Set it in your .env file or environment variables")
        return False
    
    print("✅ Environment variables found")
    print(f"   Bot token: {bot_token[:10]}...")
    print(f"   Chat ID: {chat_id}")
    print()
    
    # Test basic functionality
    print("📤 Sending test notification...")
    success = test_notifio()
    
    if success:
        print("✅ Notifio test completed successfully!")
        print("   Check your Telegram chat for the test message.")
    else:
        print("❌ Notifio test failed!")
        print("   Check your bot token and chat ID.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)