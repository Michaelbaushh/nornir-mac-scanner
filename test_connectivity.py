#!/usr/bin/env python3
"""
Hilfsskript zum Testen der Konnektivität zu den Netzwerkgeräten
vor dem Ausführen des MAC-Address Scanners
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command


def test_connectivity(task):
    """
    Testet die grundlegende Konnektivität zu einem Gerät
    """
    try:
        # Einfachen Show-Befehl ausführen
        if 'ios' in task.host.platform:
            result = task.run(
                task=netmiko_send_command,
                command_string="show version | include Software",
                name="Connectivity Test - IOS"
            )
        else:  # nxos
            result = task.run(
                task=netmiko_send_command,
                command_string="show version | head -10",
                name="Connectivity Test - NX-OS"
            )
        return result
    except Exception as e:
        task.host["error"] = f"Verbindungstest fehlgeschlagen: {str(e)}"
        return None


def main():
    """
    Hauptfunktion für Konnektivitätstest
    """
    console = Console()
    console.print("[bold blue]🔌 Netzwerk-Konnektivitätstest[/bold blue]")
    
    if not Path("config.yaml").exists():
        console.print("[bold red]❌ Fehler: config.yaml nicht gefunden![/bold red]")
        sys.exit(1)
    
    try:
        nr = InitNornir(config_file="config.yaml")
        console.print(f"[green]📋 Teste Verbindung zu {len(nr.inventory.hosts)} Geräte(n)...[/green]")
        
        # Konnektivitätstest ausführen
        results = nr.run(task=test_connectivity)
        
        # Ergebnisse in Tabelle darstellen
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Hostname", style="cyan")
        table.add_column("IP-Adresse", style="blue")  
        table.add_column("Plattform", style="yellow")
        table.add_column("Status", style="green")
        
        success_count = 0
        
        for hostname, result in results.items():
            host = nr.inventory.hosts[hostname]
            status = "✅ Erfolgreich" if not result[0].failed else "❌ Fehlgeschlagen"
            
            if not result[0].failed:
                success_count += 1
            
            table.add_row(
                hostname,
                host.hostname,
                host.platform,
                status
            )
        
        console.print(table)
        console.print(f"\n[bold green]📊 Zusammenfassung: {success_count}/{len(nr.inventory.hosts)} Geräte erreichbar[/bold green]")
        
        if success_count == len(nr.inventory.hosts):
            console.print("[bold green]🎉 Alle Geräte sind erreichbar! Du kannst den MAC-Scanner ausführen.[/bold green]")
        else:
            console.print("[bold yellow]⚠️  Einige Geräte sind nicht erreichbar. Überprüfe die Konfiguration.[/bold yellow]")
            
    except Exception as e:
        console.print(f"[bold red]💥 Fehler: {str(e)}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
