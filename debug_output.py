#!/usr/bin/env python3
"""
Debug-Script um zu sehen was die Geräte tatsächlich zurückgeben
"""

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from rich.console import Console

def debug_output(task):
    """Debug-Funktion um Raw-Output zu sehen"""
    try:
        if 'ios' in task.host.platform:
            result = task.run(
                task=netmiko_send_command,
                command_string="show mac address-table",
                name="Debug MAC Table - IOS"
            )
        else:  # nxos
            result = task.run(
                task=netmiko_send_command,
                command_string="show mac address-table",
                name="Debug MAC Table - NX-OS"
            )
        return result
    except Exception as e:
        print(f"Fehler: {e}")
        return None

def main():
    console = Console()
    console.print("[bold blue]🔍 Debug MAC Address Output[/bold blue]")
    
    nr = InitNornir(config_file="config.yaml")
    results = nr.run(task=debug_output)
    
    for hostname, result in results.items():
        console.print(f"\n[bold green]═══ {hostname.upper()} DEBUG ═══[/bold green]")
        if result.failed:
            console.print(f"[red]Fehler: {result.exception}[/red]")
        else:
            # Zugriff auf das netmiko_send_command Result
            mac_result = result[0]  # Das ist das netmiko_send_command Result
            if mac_result.failed:
                console.print(f"[red]Netmiko Fehler: {mac_result.exception}[/red]")
            else:
                output = mac_result.result
                console.print(f"[yellow]Raw Output:[/yellow]")
                console.print(f"[dim]{repr(output)}[/dim]")
                console.print(f"[cyan]Formatted Output:[/cyan]")
                console.print(output)
                console.print("-" * 50)

if __name__ == "__main__":
    main()
