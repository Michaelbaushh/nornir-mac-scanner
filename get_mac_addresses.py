#!/usr/bin/env python3
"""
Nornir Script zum Auslesen von MAC-Adressen von Cisco Geräten
Unterstützt Cisco IOS und NX-OS Switches

Autor: Network Automation Script
Datum: September 2025
"""

import sys
import csv
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result


def get_mac_addresses_ios(task):
    """
    Funktion zum Abrufen der MAC-Adressen von Cisco IOS Geräten
    """
    try:
        # MAC Address Table für IOS Geräte abrufen
        result = task.run(
            task=netmiko_send_command,
            command_string="show mac address-table",
            name="MAC Address Table - IOS"
        )
        return result
    except Exception as e:
        task.host["error"] = f"Fehler beim Abrufen der MAC-Tabelle: {str(e)}"
        return None


def get_mac_addresses_nxos(task):
    """
    Funktion zum Abrufen der MAC-Adressen von Cisco NX-OS Geräten  
    """
    try:
        # MAC Address Table für NX-OS Geräte abrufen
        result = task.run(
            task=netmiko_send_command,
            command_string="show mac address-table",
            name="MAC Address Table - NX-OS"
        )
        return result
    except Exception as e:
        task.host["error"] = f"Fehler beim Abrufen der MAC-Tabelle: {str(e)}"
        return None


def parse_mac_table_ios(output):
    """
    Parst die MAC Address Table Ausgabe von IOS Geräten
    """
    mac_entries = []
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        # Typisches Format: VLAN MAC-Adresse Typ Port
        if line and not line.startswith('Mac') and not line.startswith('---') and not line.startswith('Vlan'):
            parts = line.split()
            if len(parts) >= 4:
                try:
                    vlan = parts[0]
                    mac = parts[1] 
                    mac_type = parts[2]
                    port = parts[3]
                    
                    # Nur dynamische MAC-Adressen
                    if 'DYNAMIC' in mac_type.upper():
                        mac_entries.append({
                            'vlan': vlan,
                            'mac': mac,
                            'type': mac_type,
                            'port': port
                        })
                except IndexError:
                    continue
    
    return mac_entries


def parse_mac_table_nxos(output):
    """
    Parst die MAC Address Table Ausgabe von NX-OS Geräten
    """
    mac_entries = []
    lines = output.split('\n')
    
    for line in lines:
        line = line.strip()
        # NX-OS Format kann leicht anders sein
        if line and not line.startswith('VLAN') and not line.startswith('----') and '*' not in line:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    vlan = parts[0]
                    mac = parts[1]
                    mac_type = parts[2] 
                    age = parts[3] if len(parts) > 4 else ''
                    port = parts[-1]  # Letzter Teil ist normalerweise der Port
                    
                    # Nur dynamische MAC-Adressen
                    if 'dynamic' in mac_type.lower():
                        mac_entries.append({
                            'vlan': vlan,
                            'mac': mac,
                            'type': mac_type,
                            'port': port
                        })
                except IndexError:
                    continue
    
    return mac_entries


def export_to_csv(results, console):
    """
    Exportiert die MAC-Adressen Ergebnisse in eine CSV-Datei
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"mac_addresses_{timestamp}.csv"
    
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['hostname', 'ip_address', 'platform', 'vlan', 'mac_address', 'type', 'port']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Header schreiben
            writer.writeheader()
            
            # Daten schreiben
            for hostname, result in results.items():
                if 'mac_entries' in result:
                    for entry in result['mac_entries']:
                        writer.writerow({
                            'hostname': hostname,
                            'ip_address': '',  # Wird später gefüllt
                            'platform': result.get('platform', ''),
                            'vlan': entry['vlan'],
                            'mac_address': entry['mac'],
                            'type': entry['type'], 
                            'port': entry['port']
                        })
        
        console.print(f"[bold green]📁 CSV-Export erfolgreich: {csv_filename}[/bold green]")
        return csv_filename
        
    except Exception as e:
        console.print(f"[bold red]❌ CSV-Export fehlgeschlagen: {str(e)}[/bold red]")
        return None


def display_results(results, console):
    """
    Zeigt die Ergebnisse in einer formattierten Tabelle an
    """
    for hostname, result in results.items():
        console.print(f"\n[bold blue]═══ {hostname.upper()} ═══[/bold blue]")
        
        if 'error' in result:
            console.print(f"[bold red]❌ Fehler: {result['error']}[/bold red]")
            continue
            
        if not result['mac_entries']:
            console.print("[yellow]⚠️  Keine MAC-Adressen gefunden[/yellow]")
            continue
            
        # Tabelle für MAC-Adressen erstellen
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("VLAN", style="cyan")
        table.add_column("MAC-Adresse", style="green")  
        table.add_column("Typ", style="yellow")
        table.add_column("Port/Interface", style="blue")
        
        for entry in result['mac_entries']:
            table.add_row(
                entry['vlan'],
                entry['mac'], 
                entry['type'],
                entry['port']
            )
            
        console.print(table)
        console.print(f"[dim]Gesamt: {len(result['mac_entries'])} MAC-Adressen gefunden[/dim]")


def main():
    """
    Hauptfunktion
    """
    console = Console()
    console.print("[bold green]🚀 Nornir MAC-Adressen Scanner gestartet[/bold green]")
    
    # Überprüfe ob config.yaml existiert
    if not Path("config.yaml").exists():
        console.print("[bold red]❌ Fehler: config.yaml nicht gefunden![/bold red]")
        console.print("Bitte stelle sicher, dass die Nornir Konfiguration vorhanden ist.")
        sys.exit(1)
    
    try:
        # Nornir initialisieren
        nr = InitNornir(config_file="config.yaml")
        console.print(f"[green]✅ {len(nr.inventory.hosts)} Geräte in der Inventarliste geladen[/green]")
        
        # Ergebnis-Dictionary initialisieren  
        results = {}
        
        # IOS Switches verarbeiten
        ios_hosts = nr.filter(lambda host: 'ios_switches' in host.groups)
        if len(ios_hosts.inventory.hosts) > 0:
            console.print(f"[cyan]🔄 Verarbeite {len(ios_hosts.inventory.hosts)} IOS Switch(es)...[/cyan]")
            ios_results = ios_hosts.run(task=get_mac_addresses_ios)
            
            for hostname, task_result in ios_results.items():
                if task_result.failed:
                    results[hostname] = {"error": f"Task fehlgeschlagen: {task_result.exception}"}
                else:
                    # Zugriff auf das netmiko_send_command Result
                    mac_task_result = task_result[0]  # Das netmiko_send_command Result
                    if mac_task_result.failed:
                        results[hostname] = {"error": f"Verbindung fehlgeschlagen: {mac_task_result.exception}"}
                    else:
                        output = mac_task_result.result
                        mac_entries = parse_mac_table_ios(output)
                        results[hostname] = {"mac_entries": mac_entries, "platform": "ios"}
        
        # NX-OS Switches verarbeiten  
        nxos_hosts = nr.filter(lambda host: 'nxos_switches' in host.groups)
        if len(nxos_hosts.inventory.hosts) > 0:
            console.print(f"[cyan]🔄 Verarbeite {len(nxos_hosts.inventory.hosts)} NX-OS Switch(es)...[/cyan]")
            nxos_results = nxos_hosts.run(task=get_mac_addresses_nxos)
            
            for hostname, task_result in nxos_results.items():
                if task_result.failed:
                    results[hostname] = {"error": f"Task fehlgeschlagen: {task_result.exception}"}
                else:
                    # Zugriff auf das netmiko_send_command Result
                    mac_task_result = task_result[0]  # Das netmiko_send_command Result
                    if mac_task_result.failed:
                        results[hostname] = {"error": f"Verbindung fehlgeschlagen: {mac_task_result.exception}"}
                    else:
                        output = mac_task_result.result
                        mac_entries = parse_mac_table_nxos(output)
                        results[hostname] = {"mac_entries": mac_entries, "platform": "nxos"}
        
        # Ergebnisse anzeigen
        console.print("\n[bold yellow]📊 ERGEBNISSE[/bold yellow]")
        display_results(results, console)
        
        # CSV Export
        csv_file = export_to_csv(results, console)
        
        # Zusammenfassung
        total_macs = sum(len(result.get('mac_entries', [])) for result in results.values())
        successful_devices = sum(1 for result in results.values() if 'mac_entries' in result)
        failed_devices = len(results) - successful_devices
        
        console.print(f"\n[bold green]📈 ZUSAMMENFASSUNG[/bold green]")
        console.print(f"[green]✅ Erfolgreich verbundene Geräte: {successful_devices}[/green]")
        console.print(f"[red]❌ Fehlgeschlagene Verbindungen: {failed_devices}[/red]")
        console.print(f"[blue]📋 Gesamt MAC-Adressen gefunden: {total_macs}[/blue]")
        
        if csv_file:
            current_dir = Path().absolute()
            console.print(f"[cyan]💾 CSV-Datei gespeichert unter: {current_dir}/{csv_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]💥 Kritischer Fehler: {str(e)}[/bold red]")
        sys.exit(1)
    
    console.print("\n[bold green]✨ Scanner beendet[/bold green]")


if __name__ == "__main__":
    main()
