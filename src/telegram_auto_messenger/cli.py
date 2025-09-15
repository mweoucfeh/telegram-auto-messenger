"""
Command-line interface for Telegram Auto-Messenger.
"""

import asyncio
import click
import json
from pathlib import Path

from .core.manager import TelegramManager
from .utils.logger import setup_logging


@click.group()
@click.option('--config', '-c', default='config/config.yml',
              help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--quiet', '-q', is_flag=True, help='Disable logging output')
@click.pass_context
def cli(ctx, config, verbose, quiet):
    """Telegram Auto-Messenger - Multi-account automation tool."""
    ctx.ensure_object(dict)
    ctx.obj['config_path'] = config
    ctx.obj['verbose'] = verbose
    ctx.obj['quiet'] = quiet
    
    # Setup logging based on flags
    if quiet:
        setup_logging(False)
    elif verbose:
        setup_logging(True, 'DEBUG')
    else:
        setup_logging(True, 'INFO')


@cli.command()
@click.option('--quick', '-q', is_flag=True, help='Start with cultivation enabled immediately')
@click.pass_context
def run(ctx, quick):
    """Run the Telegram Auto-Messenger."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        
        if await manager.initialize():
            # If quick start, enable cultivation
            if quick:
                await manager.start_cultivation()
                
            await manager.start()
        else:
            click.echo("Failed to initialize, exiting...")
            return 1
            
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        click.echo("\nShutdown requested, exiting...")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return 1


@cli.command()
@click.pass_context  
def status(ctx):
    """Show application status."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            status_info = manager.get_status()
            click.echo(json.dumps(status_info, indent=2, default=str))
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cli.command()
@click.argument('target')
@click.argument('message')
@click.pass_context
def send(ctx, target, message):
    """Send a test message to a target."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.send_test_message(target, message)
            if success:
                click.echo(f"Message sent to {target}")
            else:
                click.echo(f"Failed to send message to {target}", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cli.command()
@click.argument('schedule_name')
@click.pass_context
def execute(ctx, schedule_name):
    """Execute a schedule immediately."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.execute_schedule_now(schedule_name)
            if success:
                click.echo(f"Schedule '{schedule_name}' executed")
            else:
                click.echo(f"Failed to execute schedule '{schedule_name}'", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command('validate')
@click.option('--config', '-c', default='config/config.yml',
              help='Configuration file path')
def validate_config(config):
    """Validate configuration file."""
    from .config import ConfigManager
    
    try:
        config_manager = ConfigManager(config)
        config_manager.load_config()
        errors = config_manager.validate_config()
        
        if errors:
            click.echo("Configuration validation failed:", err=True)
            for error in errors:
                click.echo(f"  - {error}", err=True)
            return 1
        else:
            click.echo("Configuration is valid ✓")
            
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        return 1


@config.command('generate')
@click.option('--output', '-o', default='config/config.yml',
              help='Output file path')
def generate_config(output):
    """Generate a sample configuration file."""
    from .config import ConfigManager
    
    output_path = Path(output)
    if output_path.exists():
        if not click.confirm(f"File {output} already exists. Overwrite?"):
            return
            
    try:
        config_manager = ConfigManager(output)
        config_manager._create_default_config()
        click.echo(f"Sample configuration generated: {output}")
        click.echo("Please edit the file with your actual values before running.")
    except Exception as e:
        click.echo(f"Error generating configuration: {e}", err=True)
        return 1


@cli.group()
def schedule():
    """Schedule management commands."""
    pass


@schedule.command('list')
@click.pass_context
def list_schedules(ctx):
    """List all schedules."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            schedules = manager.message_scheduler.get_schedule_status()
            if schedules:
                for sched in schedules:
                    click.echo(f"Schedule: {sched['name']}")
                    click.echo(f"  Target: {sched['target']}")
                    click.echo(f"  Interval: {sched['interval']}s")
                    click.echo(f"  Enabled: {sched['enabled']}")
                    if sched['next_run']:
                        click.echo(f"  Next run: {sched['next_run']}")
                    if sched['last_sent']:
                        click.echo(f"  Last sent: {sched['last_sent']}")
                    click.echo()
            else:
                click.echo("No schedules configured")
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@schedule.command('pause')
@click.argument('schedule_name')
@click.pass_context
def pause_schedule(ctx, schedule_name):
    """Pause a specific schedule."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = manager.pause_schedule(schedule_name)
            if success:
                click.echo(f"Schedule '{schedule_name}' paused")
            else:
                click.echo(f"Failed to pause schedule '{schedule_name}'", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@schedule.command('resume')
@click.argument('schedule_name')
@click.pass_context
def resume_schedule(ctx, schedule_name):
    """Resume a specific schedule."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = manager.resume_schedule(schedule_name)
            if success:
                click.echo(f"Schedule '{schedule_name}' resumed")
            else:
                click.echo(f"Failed to resume schedule '{schedule_name}'", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cli.group()
def cultivation():
    """Cultivation bot management commands."""
    pass


@cultivation.command('start')
@click.option('--account', '-a', help='Account name to use')
@click.option('--channel', '-c', help='Channel to send commands to')
@click.pass_context
def start_cultivation(ctx, account, channel):
    """Start cultivation automation."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.start_cultivation(account, channel)
            if success:
                click.echo("Cultivation started successfully!")
                # Keep running
                while True:
                    await asyncio.sleep(1)
            else:
                click.echo("Failed to start cultivation", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        click.echo("\nCultivation stopped.")


@cultivation.command('stop')
@click.option('--account', '-a', help='Account name')
@click.option('--channel', '-c', help='Channel name')
@click.pass_context
def stop_cultivation(ctx, account, channel):
    """Stop cultivation automation."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.stop_cultivation(account, channel)
            if success:
                click.echo("Cultivation stopped")
            else:
                click.echo("Failed to stop cultivation", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cultivation.command('execute')
@click.option('--account', '-a', help='Account name to use')
@click.option('--channel', '-c', help='Channel to send command to')
@click.option('--command', help='Custom command to send (default: .闭关修炼)')
@click.pass_context
def execute_cultivation(ctx, account, channel, command):
    """Execute cultivation command immediately."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.execute_cultivation_now(account, channel, command)
            if success:
                click.echo("Cultivation command sent successfully!")
            else:
                click.echo("Failed to send cultivation command", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cultivation.command('status')
@click.pass_context
def cultivation_status(ctx):
    """Show cultivation status."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            status = manager.cultivation_manager.get_status()
            
            click.echo("Cultivation Status:")
            click.echo(f"  Running: {status['running']}")
            click.echo(f"  Total Sessions: {status['total_sessions']}")
            click.echo(f"  Active Sessions: {status['active_sessions']}")
            
            for session in status['sessions']:
                click.echo(f"\nSession: {session['account']} -> {session['channel']}")
                click.echo(f"  Active: {session['is_active']}")
                click.echo(f"  Command: {session['command']}")
                click.echo(f"  Ready: {session['is_ready']}")
                click.echo(f"  Success Count: {session['success_count']}")
                click.echo(f"  Failure Count: {session['failure_count']}")
                if session['next_attempt']:
                    click.echo(f"  Next Attempt: {session['next_attempt']}")
                if session['last_attempt']:
                    click.echo(f"  Last Attempt: {session['last_attempt']}")
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@cli.group()
def monitor():
    """Monitor management commands."""
    pass


@monitor.command('list')
@click.pass_context
def list_monitors(ctx):
    """List all monitors."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            monitors = manager.monitor_manager.get_monitor_status()
            if monitors:
                for mon in monitors:
                    click.echo(f"Monitor: {mon['name']}")
                    click.echo(f"  Target: {mon['target']}")
                    click.echo(f"  Keywords: {', '.join(mon['keywords'])}")
                    click.echo(f"  Enabled: {mon['enabled']}")
                    click.echo(f"  Monitoring: {mon['is_monitoring']}")
                    click.echo(f"  Processed: {mon['processed_count']} messages")
                    click.echo()
            else:
                click.echo("No monitors configured")
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@monitor.command('pause')
@click.argument('monitor_name')
@click.pass_context
def pause_monitor(ctx, monitor_name):
    """Pause a specific monitor."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.pause_monitor(monitor_name)
            if success:
                click.echo(f"Monitor '{monitor_name}' paused")
            else:
                click.echo(f"Failed to pause monitor '{monitor_name}'", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


@monitor.command('resume')
@click.argument('monitor_name')
@click.pass_context
def resume_monitor(ctx, monitor_name):
    """Resume a specific monitor."""
    config_path = ctx.obj['config_path']
    
    async def main():
        manager = TelegramManager(config_path)
        if await manager.initialize():
            success = await manager.resume_monitor(monitor_name)
            if success:
                click.echo(f"Monitor '{monitor_name}' resumed")
            else:
                click.echo(f"Failed to resume monitor '{monitor_name}'", err=True)
        else:
            click.echo("Failed to initialize", err=True)
            
    asyncio.run(main())


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()