#!/usr/bin/env python3
"""
示例脚本：演示如何使用 Telegram Auto-Messenger

本脚本展示了如何：
1. 加载配置
2. 初始化管理器
3. 检查状态
4. 发送测试消息（需要有效配置）

注意：运行此脚本前，请确保：
- 已安装所有依赖：pip install -r requirements.txt
- 已配置有效的 config/config.yml 文件
- 已完成 Telegram 账号授权
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目路径到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

try:
    from telegram_auto_messenger.core.manager import TelegramManager
    from telegram_auto_messenger.config import ConfigManager
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所有依赖：pip install -r requirements.txt")
    sys.exit(1)


async def demo_config_management():
    """演示配置管理功能"""
    print("📋 配置管理演示")
    print("-" * 40)
    
    # 创建配置管理器
    config_manager = ConfigManager("examples/config.yml")
    
    try:
        # 加载配置
        config = config_manager.load_config()
        print(f"✅ 配置加载成功")
        print(f"   - 数据库路径: {config.database_path}")
        print(f"   - 日志级别: {config.log_level}")
        print(f"   - 热重载: {config.hot_reload}")
        print(f"   - 账号数量: {len(config.accounts)}")
        print(f"   - 定时任务数量: {len(config.schedules)}")
        print(f"   - 监控器数量: {len(config.monitors)}")
        
        # 验证配置
        errors = config_manager.validate_config()
        if errors:
            print(f"⚠️  配置验证发现问题:")
            for error in errors[:3]:  # 只显示前3个错误
                print(f"   - {error}")
            if len(errors) > 3:
                print(f"   - ... 还有 {len(errors) - 3} 个错误")
        else:
            print("✅ 配置验证通过")
            
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
    
    print()


async def demo_basic_functionality():
    """演示基本功能（需要有效配置）"""
    print("🚀 基本功能演示")
    print("-" * 40)
    
    # 检查配置文件是否存在
    config_path = "config/config.yml"
    if not Path(config_path).exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("请先复制并编辑示例配置：")
        print(f"   cp examples/config.yml {config_path}")
        print(f"   nano {config_path}")
        return
    
    # 创建管理器
    manager = TelegramManager(config_path)
    
    try:
        # 初始化（这需要有效的 Telegram 配置）
        print("🔧 正在初始化...")
        success = await manager.initialize()
        
        if success:
            print("✅ 初始化成功")
            
            # 获取状态
            status = manager.get_status()
            print(f"📊 应用状态:")
            print(f"   - 运行状态: {status['running']}")
            print(f"   - 已连接账号: {status['accounts']['connected']}/{status['accounts']['total_configured']}")
            print(f"   - 活跃定时任务: {len(status['schedules'])}")
            print(f"   - 活跃监控器: {len(status['monitors'])}")
            
            # 如果有账号连接，可以尝试发送测试消息
            if status['accounts']['connected'] > 0:
                print("\n💬 可以尝试发送测试消息:")
                print("   manager.send_test_message('@channel', 'Hello from script!')")
            else:
                print("\n⚠️  没有已连接的账号，无法发送消息")
                
        else:
            print("❌ 初始化失败")
            print("可能的原因:")
            print("   - Telegram API 凭据无效")
            print("   - 网络连接问题")
            print("   - 配置文件格式错误")
            
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")
    finally:
        # 清理
        try:
            await manager.stop()
        except:
            pass
    
    print()


async def demo_configuration_generation():
    """演示配置文件生成"""
    print("⚙️  配置文件生成演示")
    print("-" * 40)
    
    # 生成示例配置到临时位置
    temp_config = "/tmp/demo_config.yml"
    
    try:
        config_manager = ConfigManager(temp_config)
        config_manager._create_default_config()
        
        print(f"✅ 示例配置已生成: {temp_config}")
        print("配置文件内容预览:")
        print("-" * 20)
        
        with open(temp_config, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 显示前20行
            for i, line in enumerate(lines[:20], 1):
                print(f"{i:2d}: {line.rstrip()}")
        
        if len(lines) > 20:
            print(f"... (还有 {len(lines) - 20} 行)")
            
        print(f"\n💡 提示: 将此文件复制到 config/config.yml 并编辑其中的值")
        
    except Exception as e:
        print(f"❌ 生成配置文件失败: {e}")
    
    print()


def print_header():
    """打印程序头部信息"""
    print("🚀 Telegram Auto-Messenger 演示脚本")
    print("=" * 50)
    print("本脚本演示项目的主要功能和使用方法")
    print()


def print_requirements():
    """打印运行要求"""
    print("📋 运行要求:")
    print("-" * 20)
    print("1. 安装依赖包: pip install -r requirements.txt")
    print("2. 获取 Telegram API 凭据:")
    print("   - 访问 https://my.telegram.org")
    print("   - 创建应用获取 api_id 和 api_hash")
    print("3. 配置账号信息:")
    print("   - 复制 examples/config.yml 到 config/config.yml")
    print("   - 编辑配置文件填入真实的 API 凭据")
    print("4. 首次运行时需要手机验证码授权")
    print()


def print_usage_examples():
    """打印使用示例"""
    print("💡 使用示例:")
    print("-" * 20)
    print("# 命令行工具")
    print("telegram-auto-messenger run                    # 运行程序")
    print("telegram-auto-messenger status                 # 查看状态")
    print("telegram-auto-messenger config validate        # 验证配置")
    print("telegram-auto-messenger send '@channel' 'Hi'   # 发送消息")
    print()
    print("# Docker 部署")
    print("cd docker && docker-compose up -d              # 启动服务")
    print("docker-compose logs -f                         # 查看日志")
    print()


async def main():
    """主函数"""
    print_header()
    print_requirements()
    print_usage_examples()
    
    # 运行演示
    await demo_configuration_generation()
    await demo_config_management()
    
    # 只有在配置文件存在时才演示基本功能
    if Path("config/config.yml").exists():
        await demo_basic_functionality()
    else:
        print("🔄 基本功能演示")
        print("-" * 40)
        print("❌ 跳过基本功能演示（缺少有效配置文件）")
        print("请先创建并配置 config/config.yml 文件")
        print()
    
    print("✨ 演示完成！")
    print()
    print("🎯 下一步:")
    print("1. 安装依赖: pip install -r requirements.txt")
    print("2. 配置 Telegram API: 编辑 config/config.yml")
    print("3. 运行程序: telegram-auto-messenger run")
    print()
    print("📚 更多信息请查看:")
    print("- 配置说明: docs/configuration.md")
    print("- Docker 部署: docs/docker-deployment.md")
    print("- 项目文档: README.md")


if __name__ == "__main__":
    asyncio.run(main())