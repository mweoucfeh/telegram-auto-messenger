#!/usr/bin/env python3
"""
修仙自动化演示脚本
Simple demonstration of cultivation automation features.
"""

import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from telegram_auto_messenger.core.manager import TelegramManager
from telegram_auto_messenger.config import ConfigManager


async def demo_cultivation():
    """演示修仙自动化功能"""
    print("🧘 修仙自动化演示")
    print("=" * 50)
    
    # 检查配置文件
    config_path = "config/config.yml"
    if not os.path.exists(config_path):
        print("❌ 配置文件不存在，请先运行: telegram-auto-messenger config generate")
        return
    
    # 创建管理器
    manager = TelegramManager(config_path)
    
    try:
        # 初始化
        print("📋 正在初始化...")
        if not await manager.initialize():
            print("❌ 初始化失败，请检查配置文件")
            return
        
        # 检查配置
        config = manager.config_manager.get_config()
        
        if not config.cultivation.enabled:
            print("⚠️  修仙功能未启用，请在配置文件中设置 cultivation.enabled: true")
            return
        
        if not config.accounts or not any(acc.enabled for acc in config.accounts):
            print("⚠️  没有可用的账号，请配置至少一个启用的账号")
            return
        
        print(f"✅ 配置检查通过")
        print(f"   账号: {config.cultivation.account_name}")
        print(f"   频道: {config.cultivation.channel}")
        print(f"   命令: {config.cultivation.command}")
        print()
        
        # 显示菜单
        while True:
            print("请选择操作:")
            print("1. 立即执行一次修炼")
            print("2. 启动自动修仙（持续运行）")
            print("3. 查看修仙状态")
            print("4. 测试消息解析")
            print("0. 退出")
            
            choice = input("\n请输入选择 (0-4): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                await demo_single_cultivation(manager)
            elif choice == "2":
                await demo_auto_cultivation(manager)
            elif choice == "3":
                await demo_status(manager)
            elif choice == "4":
                demo_message_parsing()
            else:
                print("❌ 无效选择，请重新输入")
            
            print()
    
    except Exception as e:
        print(f"❌ 发生错误: {e}")
    finally:
        # 清理
        print("\n🧹 正在清理资源...")
        await manager.stop()
        print("✅ 演示结束")


async def demo_single_cultivation(manager):
    """演示单次修炼"""
    print("\n🎯 执行单次修炼...")
    
    success = await manager.execute_cultivation_now()
    if success:
        print("✅ 修炼命令发送成功！请查看频道中的机器人回复。")
    else:
        print("❌ 修炼命令发送失败，请检查账号连接和频道设置。")


async def demo_auto_cultivation(manager):
    """演示自动修仙"""
    print("\n🔄 启动自动修仙...")
    print("⚠️  这将持续运行，按 Ctrl+C 停止")
    
    success = await manager.start_cultivation()
    if not success:
        print("❌ 启动失败")
        return
    
    print("✅ 自动修仙已启动！")
    print("💡 工具将自动:")
    print("   - 发送修炼命令")
    print("   - 解析机器人回复")
    print("   - 根据等待时间自动重试")
    print()
    
    try:
        # 保持运行
        while True:
            await asyncio.sleep(10)
            
            # 显示状态
            status = manager.cultivation_manager.get_status()
            if status['sessions']:
                session = status['sessions'][0]
                print(f"📊 状态更新: 成功{session['success_count']}次, "
                      f"失败{session['failure_count']}次, "
                      f"准备状态: {'✅' if session['is_ready'] else '⏳'}")
    
    except KeyboardInterrupt:
        print("\n⏹️  停止自动修仙...")
        await manager.stop_cultivation()
        print("✅ 已停止")


async def demo_status(manager):
    """显示修仙状态"""
    print("\n📊 修仙状态:")
    
    status = manager.cultivation_manager.get_status()
    print(f"运行状态: {'🟢 运行中' if status['running'] else '🔴 已停止'}")
    print(f"会话总数: {status['total_sessions']}")
    print(f"活跃会话: {status['active_sessions']}")
    
    if status['sessions']:
        for i, session in enumerate(status['sessions'], 1):
            print(f"\n会话 {i}:")
            print(f"  账号: {session['account']}")
            print(f"  频道: {session['channel']}")
            print(f"  命令: {session['command']}")
            print(f"  状态: {'🟢 活跃' if session['is_active'] else '🔴 停止'}")
            print(f"  准备状态: {'✅ 就绪' if session['is_ready'] else '⏳ 等待中'}")
            print(f"  成功次数: {session['success_count']}")
            print(f"  失败次数: {session['failure_count']}")
            
            if session['last_attempt']:
                print(f"  最后尝试: {session['last_attempt']}")
            if session['next_attempt']:
                print(f"  下次尝试: {session['next_attempt']}")
    else:
        print("  暂无活动会话")


def demo_message_parsing():
    """演示消息解析功能"""
    print("\n🧠 消息解析演示:")
    
    from telegram_auto_messenger.core.cultivation import CultivationSession
    
    session = CultivationSession("demo", "@demo")
    
    # 测试消息
    test_messages = [
        ("成功回复（带等待时间）", """【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。
因【星宫】灵脉加持，你额外获得了 29 点修为！
本次闭关，你的修为最终增加了 78 点。

当前境界: 筑基后期
当前修为: 1298 / 30000

你感到一阵疲惫，需要打坐调息 13 分钟方可再次闭关。"""),
        
        ("失败回复", "灵气尚未平复，无法立即再次闭关。请在 11分钟36秒 后再试。"),
        
        ("简单等待", "你感到一阵疲惫，需要打坐调息 5 分钟方可再次闭关。"),
        
        ("纯成功（无等待）", """【闭关成功】
你福至心灵，成功炼化灵气，基础修为增加了 49 点。""")
    ]
    
    for title, message in test_messages:
        print(f"\n📝 {title}:")
        wait_seconds = session.parse_response(message)
        
        if wait_seconds is not None:
            if wait_seconds == 0:
                print(f"   解析结果: ✅ 成功，无需等待")
            else:
                minutes = wait_seconds // 60
                seconds = wait_seconds % 60
                print(f"   解析结果: ⏱️  等待 {minutes}分{seconds}秒 ({wait_seconds}秒)")
        else:
            print(f"   解析结果: ❌ 无法解析")
    
    print(f"\n📊 解析统计:")
    print(f"   成功次数: {session.success_count}")
    print(f"   失败次数: {session.failure_count}")


if __name__ == "__main__":
    print("🚀 Telegram Auto-Messenger 修仙演示")
    print("请确保已经配置好 Telegram API 凭据和修仙频道设置")
    print()
    
    try:
        asyncio.run(demo_cultivation())
    except KeyboardInterrupt:
        print("\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()