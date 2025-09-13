#!/usr/bin/env python3
"""
Simple demo of Telegram Auto-Messenger with basic text messaging.

This demo shows how to use the simplified version with:
- No database logging 
- Simple print-based logging with on/off control
- Anti-ban safety measures
- Cross-platform compatibility
- Text messages only

Usage:
1. Copy config/config.yml from examples and edit with your API credentials
2. Run: python demo_simple.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for demo
sys.path.insert(0, str(Path(__file__).parent / "src"))

from telegram_auto_messenger.core.manager import TelegramManager
from telegram_auto_messenger.utils.logger import setup_logging


async def main():
    """Run a simple demo."""
    
    # Setup logging with control
    print("=== Telegram Auto-Messenger Simple Demo ===")
    print("Features:")
    print("- No database required")
    print("- Simple print logging (controllable)")
    print("- Anti-ban safety measures")
    print("- Cross-platform (Windows/macOS/Linux)")
    print("- Text messages only")
    print()
    
    # Check if config exists
    config_path = "config/config.yml"
    if not Path(config_path).exists():
        print(f"❌ Config file not found: {config_path}")
        print(f"Please copy examples/config.yml to {config_path} and edit with your API credentials.")
        return
    
    print(f"📁 Using config: {config_path}")
    
    # Initialize manager
    manager = TelegramManager(config_path)
    
    print("\n🔧 Initializing...")
    if not await manager.initialize():
        print("❌ Failed to initialize. Check your configuration.")
        return
    
    print("✅ Initialized successfully!")
    
    # Show status
    status = manager.get_status()
    print(f"\n📊 Status:")
    print(f"   - Logging enabled: {status['logging_enabled']}")
    print(f"   - Accounts connected: {status['accounts']['connected']}/{status['accounts']['total_configured']}")
    print(f"   - Schedules: {len(status['schedules'])}")
    print(f"   - Monitors: {len(status['monitors'])}")
    
    if status['accounts']['connected'] == 0:
        print("\n⚠️  No accounts connected. Please check your API credentials.")
        print("   Make sure you have:")
        print("   1. Valid api_id and api_hash from https://my.telegram.org")
        print("   2. Correct phone number")
        print("   3. Account marked as enabled: true")
        return
    
    print(f"\n🔗 Connected accounts: {', '.join(status['accounts']['account_names'])}")
    
    # Demo sending a test message (commented out for safety)
    print("\n💬 To send a test message, uncomment the lines in demo_simple.py")
    print("   Example: await manager.send_test_message('@your_channel', 'Hello from Auto-Messenger!')")
    
    # Uncomment to send a test message:
    # target = input("\nEnter target (@username or chat_id): ").strip()
    # message = input("Enter message: ").strip()
    # if target and message:
    #     print(f"📤 Sending message to {target}...")
    #     success = await manager.send_test_message(target, message)
    #     if success:
    #         print("✅ Message sent successfully!")
    #     else:
    #         print("❌ Failed to send message.")
    
    # Start main loop for a short demo
    print("\n🚀 Starting demo for 10 seconds...")
    print("   (In real usage, this would run indefinitely)")
    print("   Press Ctrl+C to stop early")
    
    try:
        # Start the manager in the background
        start_task = asyncio.create_task(manager.start())
        
        # Wait for 10 seconds or until stopped
        await asyncio.sleep(10)
        
        print("\n⏰ Demo time finished!")
        
    except KeyboardInterrupt:
        print("\n⛔ Stopped by user")
    finally:
        print("🛑 Stopping...")
        await manager.stop()
        print("✅ Stopped successfully!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")