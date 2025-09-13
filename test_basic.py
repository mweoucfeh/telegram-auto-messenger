#!/usr/bin/env python3
"""
基础测试脚本 - 不需要外部依赖

测试项目的基本结构和语法正确性
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_config_syntax():
    """测试配置模块语法"""
    try:
        # 只导入不依赖外部包的部分
        import telegram_auto_messenger.config as config_module
        from telegram_auto_messenger.config import AccountConfig, ScheduleConfig, MonitorConfig
        
        # 测试数据类创建
        account = AccountConfig(
            api_id=123456,
            api_hash="test_hash",
            phone="+1234567890",
            session_name="test"
        )
        assert account.enabled is True
        
        schedule = ScheduleConfig(
            name="test",
            target="@channel",
            message="Hello",
            interval=3600
        )
        assert schedule.auto_delete is False
        
        monitor = MonitorConfig(
            name="test",
            target="@group",
            keywords=["help"],
            reply_message="Reply"
        )
        assert monitor.exact_match is False
        
        print("✅ 配置模块语法测试通过")
        return True
    except Exception as e:
        print(f"❌ 配置模块语法测试失败: {e}")
        return False


def test_utils_syntax():
    """测试工具模块语法"""
    try:
        # 测试数据库模块（不初始化数据库）
        import telegram_auto_messenger.utils.database as db_module
        import telegram_auto_messenger.utils.logger as logger_module
        
        # 检查类是否正确定义
        assert hasattr(db_module, 'DatabaseManager')
        assert hasattr(logger_module, 'setup_logging')
        assert hasattr(logger_module, 'get_logger')
        
        print("✅ 工具模块语法测试通过")
        return True
    except Exception as e:
        print(f"❌ 工具模块语法测试失败: {e}")
        return False


def test_project_structure():
    """测试项目结构"""
    required_files = [
        "src/telegram_auto_messenger/__init__.py",
        "src/telegram_auto_messenger/config/__init__.py",
        "src/telegram_auto_messenger/core/__init__.py",
        "src/telegram_auto_messenger/core/account.py",
        "src/telegram_auto_messenger/core/scheduler.py",
        "src/telegram_auto_messenger/core/monitor.py",
        "src/telegram_auto_messenger/core/manager.py",
        "src/telegram_auto_messenger/utils/__init__.py",
        "src/telegram_auto_messenger/utils/database.py",
        "src/telegram_auto_messenger/utils/logger.py",
        "src/telegram_auto_messenger/cli.py",
        "requirements.txt",
        "pyproject.toml",
        "README.md",
        "LICENSE",
        ".gitignore",
        "docker/Dockerfile",
        "docker/docker-compose.yml",
        "examples/config.yml",
        "docs/configuration.md",
        "docs/docker-deployment.md",
        "tests/test_config.py",
        "tests/test_utils.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not (project_root / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {missing_files}")
        return False
    else:
        print("✅ 项目结构完整")
        return True


def test_configuration_files():
    """测试配置文件语法"""
    try:
        import yaml
        
        config_files = [
            "examples/config.yml",
            "examples/config.production.yml"
        ]
        
        for config_file in config_files:
            path = project_root / config_file
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # 检查必要的配置节
            required_sections = ['app', 'accounts', 'schedules', 'monitors']
            for section in required_sections:
                if section not in data:
                    raise ValueError(f"配置文件 {config_file} 缺少 {section} 节")
        
        print("✅ 配置文件格式正确")
        return True
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 Telegram Auto-Messenger 基础测试")
    print("=" * 50)
    
    tests = [
        ("项目结构", test_project_structure),
        ("配置文件格式", test_configuration_files),
        ("配置模块语法", test_config_syntax),
        ("工具模块语法", test_utils_syntax),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 运行测试: {test_name}")
        print("-" * 30)
        if test_func():
            passed += 1
        
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有基础测试通过！")
        print("\n✨ 项目准备就绪！")
        print("\n📋 下一步操作:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 配置 Telegram API 凭据")
        print("3. 运行程序: telegram-auto-messenger run")
        return True
    else:
        print(f"❌ {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)