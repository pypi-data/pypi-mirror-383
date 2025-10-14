#!/usr/bin/env python3
"""
Helper script to get your Telegram chat ID.
Make sure to start your bot first by sending /start to it.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_chat_id():
    """Get chat ID from Telegram bot updates."""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment")
        return None
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ API Error: {data.get('description', 'Unknown error')}")
            return None
        
        updates = data.get('result', [])
        
        if not updates:
            print("❌ No updates found. Make sure to:")
            print("   1. Start your bot by sending /start to it")
            print("   2. Send any message to the bot")
            print("   3. Run this script again")
            return None
        
        print("✅ Found updates:")
        print()
        
        chat_ids = set()
        for update in updates:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat['type']
                username = chat.get('username', 'N/A')
                first_name = chat.get('first_name', 'N/A')
                
                chat_ids.add(chat_id)
                
                print(f"📱 Chat ID: {chat_id}")
                print(f"   Type: {chat_type}")
                print(f"   Username: @{username}")
                print(f"   Name: {first_name}")
                print(f"   Message: {update['message'].get('text', 'N/A')}")
                print()
        
        if chat_ids:
            print(f"🎯 Use this Chat ID: {list(chat_ids)[0]}")
            print()
            print("Update your .env file:")
            print(f"TELEGRAM_CHAT_ID={list(chat_ids)[0]}")
        
        return list(chat_ids)[0] if chat_ids else None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🔍 Getting Telegram Chat ID...")
    print()
    print("Make sure you have:")
    print("1. Started your bot by sending /start to it")
    print("2. Sent at least one message to the bot")
    print()
    
    chat_id = get_chat_id()
    
    if chat_id:
        print("✅ Chat ID found successfully!")
    else:
        print("❌ Could not find chat ID")