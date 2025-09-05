#!/usr/bin/env python3
"""
Hybrid Nornir MAC-Adressen Scanner 
NAPALM für IOS, Netmiko für NX-OS (wenn NXAPI nicht verfügbar)

Autor: Network Automation Script (Hybrid Version)
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
from nornir_napalm.plugins.tasks import napalm_get
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result


def get_mac_addresses_hybrid(task):
    """
    Hybrid-Funktion: NAPALM für IOS, Netmiko für NX-OS
    """
    try:
        if 'nxos' in task.host.platform.lower():
            # NX-OS: Verwende Netmiko wegen NXAPI-Problemen
            result = task.run(
                task=netmiko_send_command,
                command_string="show mac address-table",
                name="MAC Address Table - NX-OS (Netmiko)"
            )
            return result
        else:
            # IOS: Verwende NAPALM für strukturierte Daten
            result = task.run(
                task=napalm_get,
                getters=["mac_address_table"],
                name="MAC Address Table - IOS (NAPALM)"
            )
            return result
    except Exception as e:
        task.host["error"] = f"Fehler beim Abrufen der MAC-Tabelle: {str(e)}"
        return None


def process_mac_data_hybrid(result, platform):
    """
    Verarbeitet MAC-Daten je nach Quelle (NAPALM JSON oder Netmiko String)
    """
    mac_entries = []
    
    if 'nxos' in platform.lower():
        # NX-OS Netmiko String-Parsing
        if hasattr(result, 'result') and isinstance(result.result, str):
            output = result.result
            lines = output.split('\n')
            
            for line in lines:
                line = line.strip()
                # NX-OS Format: "*    1     000c.2937.a1ae   dynamic  NA         F      F    Eth1/1"
                if line and line.startswith('*') and 'dynamic' in line.lower():
                    parts = line.split()
                    if len(parts) >= 7:  # Mindestens: * VLAN MAC Type Age Secure NTFY Port
                        try:
                            vlan = parts[1]
                            mac_addr = parts[2] 
                            port = parts[-1]  # Letzter Part ist der Port
                            
                            # Validiere MAC-Adresse Format (xxxx.xxxx.xxxx)
                            if '.' in mac_addr and len(mac_addr.replace('.', '')) == 12:
                                mac_entries.append({
                                    'vlan': vlan,
                                    'mac': mac_addr,
                                    'type': 'dynamic',
                                    'port': port
                                })
                        except (IndexError, ValueError):
                            continue
    else:
        # IOS NAPALM JSON-Verarbeitung
        if hasattr(result, 'result') and isinstance(result.result, dict):
            mac_address_table = result.result.get('mac_address_table', [])
            
            for entry in mac_address_table:
                if entry.get('active', True):
                    # MAC-Adresse von aa:bb:cc:dd:ee:ff zu aabb.ccdd.eeff
                    mac_raw = entry.get('mac', '').lower()
                    if ':' in mac_raw:
                        parts = mac_raw.split(':')
                        if len(parts) == 6:
                            mac_cisco = f"{parts[0]}{parts[1]}.{parts[2]}{parts[3]}.{parts[4]}{parts[5]}"
                        else:
                            mac_cisco = mac_raw.replace(':', '')
                    else:
                        mac_cisco = mac_raw
                    
                    mac_entries.append({
                        'vlan': str(entry.get('vlan', 1)),
                        'mac': mac_cisco,
                        'type': 'static' if entry.get('static', False) else 'dynamic',
                        'port': entry.get('interface', 'unknown')
                    })
    
    return mac_entries


def export_to_csv(results, console, nr):
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
                    host = nr.inventory.hosts[hostname]
                    for entry in result['mac_entries']:
                        writer.writerow({
                            'hostname': hostname,
                            'ip_address': host.hostname,
                            'platform': result.get('platform', host.platform),
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
        method = "NAPALM (JSON)" if 'ios' in result.get('platform', '').lower() else "Netmiko (String)"
        console.print(f"[dim]Gesamt: {len(result['mac_entries'])} MAC-Adressen gefunden - {method}[/dim]")


def main():
    """
    Hauptfunktion
    """
    console = Console()
    console.print("[bold green]🚀 Hybrid MAC-Adressen Scanner[/bold green]")
    console.print("[cyan]🔧 NAPALM für IOS, Netmiko für NX-OS[/cyan]")
    
    # Überprüfe ob config.yaml existiert
    if not Path("config.yaml").exists():
        console.print("[bold red]❌ Fehler: config.yaml nicht gefunden![/bold red]")
        console.print("Bitte stelle sicher, dass die Nornir Konfiguration vorhanden ist.")
        sys.exit(1)
    
    try:
        # Nornir initialisieren
        nr = InitNornir(config_file="config.yaml")
        console.print(f"[green]✅ {len(nr.inventory.hosts)} Switches in der Inventarliste geladen[/green]")
        
        # Ergebnis-Dictionary initialisieren  
        results = {}
        
        # Alle Switches mit Hybrid-Methode verarbeiten
        console.print(f"[cyan]🔄 Verarbeite {len(nr.inventory.hosts)} Switch(es) hybrid...[/cyan]")
        hybrid_results = nr.run(task=get_mac_addresses_hybrid)
        
        for hostname, task_result in hybrid_results.items():
            if task_result.failed:
                results[hostname] = {"error": f"Task fehlgeschlagen: {task_result.exception}"}
            else:
                host = nr.inventory.hosts[hostname]
                platform = host.platform
                
                # Zugriff auf das Result je nach Platform
                try:
                    if 'nxos' in platform.lower():
                        # NX-OS Netmiko Result (verschachtelt wie bei der Debug-Ausgabe)
                        netmiko_multiresult = task_result[0]  # Erster Task
                        if len(netmiko_multiresult.result) > 0:
                            actual_netmiko_result = netmiko_multiresult.result[0]  # Verschachteltes Result
                            if actual_netmiko_result.failed:
                                results[hostname] = {"error": f"Netmiko-Fehler: {actual_netmiko_result.exception}"}
                            else:
                                mac_entries = process_mac_data_hybrid(actual_netmiko_result, platform)
                                results[hostname] = {
                                    "mac_entries": mac_entries,
                                    "platform": platform,
                                    "method": "Netmiko"
                                }
                        else:
                            results[hostname] = {"error": "Leeres Netmiko Result"}
                    else:
                        # IOS NAPALM Result (verschachtelt)
                        nested_multiresult = task_result[0].result
                        napalm_result = nested_multiresult[0]
                        
                        if napalm_result.failed:
                            results[hostname] = {"error": f"NAPALM-Fehler: {napalm_result.exception}"}
                        else:
                            mac_entries = process_mac_data_hybrid(napalm_result, platform)
                            results[hostname] = {
                                "mac_entries": mac_entries,
                                "platform": platform,
                                "method": "NAPALM"
                            }
                except Exception as e:
                    results[hostname] = {"error": f"Result-Verarbeitung fehlgeschlagen: {str(e)}"}
        
        # Ergebnisse anzeigen
        console.print("\n[bold yellow]📊 ERGEBNISSE[/bold yellow]")
        display_results(results, console)
        
        # CSV Export
        csv_file = export_to_csv(results, console, nr)
        
        # Zusammenfassung
        total_macs = sum(len(result.get('mac_entries', [])) for result in results.values())
        successful_devices = sum(1 for result in results.values() if 'mac_entries' in result)
        failed_devices = len(results) - successful_devices
        
        console.print(f"\n[bold green]📈 ZUSAMMENFASSUNG[/bold green]")
        console.print(f"[green]✅ Erfolgreich verbundene Switches: {successful_devices}[/green]")
        console.print(f"[red]❌ Fehlgeschlagene Verbindungen: {failed_devices}[/red]")
        console.print(f"[blue]📋 Gesamt MAC-Adressen gefunden: {total_macs}[/blue]")
        console.print(f"[magenta]🔧 Methode: Hybrid (NAPALM + Netmiko)[/magenta]")
        
        if csv_file:
            current_dir = Path().absolute()
            console.print(f"[cyan]💾 CSV-Datei gespeichert unter: {current_dir}/{csv_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]💥 Kritischer Fehler: {str(e)}[/bold red]")
        sys.exit(1)
    
    console.print("\n[bold green]✨ Scanner beendet[/bold green]")


if __name__ == "__main__":
    main()
