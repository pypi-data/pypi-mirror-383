#!/usr/bin/env python3
"""
Example usage of universal Notifio service.
Shows how to use Notifio in any application.
"""

import os
from dotenv import load_dotenv
from notifio import get_notifio

# Load environment variables
load_dotenv()

def main():
    """Example usage of Notifio."""
    # Initialize Notifio
    notifio = get_notifio()
    
    if not notifio:
        print("❌ Notifio not configured")
        print("Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return
    
    print("✅ Notifio configured, sending example notifications...")
    
    # Example 1: Basic message
    notifio.send_message("🚀 Application started successfully!")
    
    # Example 2: Success notification
    notifio.send_success("Data Processing Complete", {
        "Records processed": 1500,
        "Processing time": "2.5 minutes",
        "Status": "Success"
    }, "All data has been processed successfully!")
    
    # Example 3: Warning notification
    notifio.send_warning("High Memory Usage", {
        "Current usage": "85%",
        "Threshold": "80%",
        "Action": "Monitoring"
    }, "Consider restarting the service")
    
    # Example 4: Error notification
    notifio.send_error("Database Connection Failed", {
        "Error": "Connection timeout",
        "Retry attempts": 3,
        "Last attempt": "2025-01-27 14:30:00"
    }, "Check database server status")
    
    # Example 5: Info notification
    notifio.send_info("System Status", {
        "CPU usage": "45%",
        "Memory usage": "2.1GB",
        "Disk usage": "60%",
        "Uptime": "5 days"
    })
    
    # Example 6: Sleep notification
    notifio.send_sleep_notification("Background Task", 8.5, "2025-01-28 08:00:00", {
        "Processed items": 200,
        "Daily limit": 200
    })
    
    # Example 7: Wake notification
    notifio.send_wake_notification("Background Task", {
        "Resumed at": "2025-01-28 08:00:00",
        "Items to process": 150
    })
    
    # Example 8: Summary notification
    notifio.send_summary("Daily Report", {
        "Tasks completed": 25,
        "Errors": 0,
        "Warnings": 2
    }, 25)
    
    # Example 9: Test message
    notifio.send_test_message("My Application")
    
    print("✅ All example notifications sent!")

if __name__ == "__main__":
    main()
