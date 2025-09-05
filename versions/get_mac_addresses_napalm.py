#!/usr/bin/env python3
"""
Modernized Nornir MAC-Address Scanner with NAPALM
Strukturierte JSON-Daten statt String-Parsing

Autor: Network Automation Script (NAPALM Version)
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
from nornir_utils.plugins.functions import print_result


def get_mac_addresses(task):
    """
    Funktion zum Abrufen der MAC-Adressen mit NAPALM (JSON)
    Funktioniert für alle unterstützten Plattformen (IOS, NX-OS, etc.)
    """
    try:
        # NAPALM MAC Address Table abrufen - gibt strukturierte Daten zurück
        result = task.run(
            task=napalm_get,
            getters=["mac_address_table"],
            name="NAPALM MAC Address Table"
        )
        return result
    except Exception as e:
        task.host["error"] = f"Fehler beim Abrufen der MAC-Tabelle: {str(e)}"
        return None


def process_napalm_mac_data(mac_data, platform):
    """
    Verarbeitet NAPALM MAC-Address-Daten (JSON) zu unserem Format
    
    NAPALM Format:
    [
      {
        "mac": "aa:bb:cc:dd:ee:ff",
        "interface": "Ethernet1/1", 
        "vlan": 100,
        "static": false,
        "active": true,
        "moves": 0,
        "last_move": 0.0
      }
    ]
    """
    mac_entries = []
    
    for entry in mac_data:
        # Nur aktive MAC-Adressen (static können interessant sein, also auch inkludieren)
        if entry.get('active', True):
            # MAC-Adresse normalisieren - NAPALM gibt bereits Standard-Format
            mac_raw = entry.get('mac', '').lower()
            
            # Von aa:bb:cc:dd:ee:ff zu aabb.ccdd.eeff (Cisco-Format für CSV)
            if ':' in mac_raw:
                parts = mac_raw.split(':')
                if len(parts) == 6:
                    mac_cisco = f"{parts[0]}{parts[1]}.{parts[2]}{parts[3]}.{parts[4]}{parts[5]}"
                else:
                    mac_cisco = mac_raw.replace(':', '')  # fallback
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
        console.print(f"[dim]Gesamt: {len(result['mac_entries'])} MAC-Adressen gefunden[/dim]")


def main():
    """
    Hauptfunktion
    """
    console = Console()
    console.print("[bold green]🚀 Nornir MAC-Adressen Scanner (NAPALM)[/bold green]")
    console.print("[cyan]🔧 Verwendet strukturierte JSON-Daten statt String-Parsing[/cyan]")
    
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
        
        # Alle Geräte mit NAPALM verarbeiten
        console.print(f"[cyan]🔄 Verarbeite {len(nr.inventory.hosts)} Gerät(e) mit NAPALM...[/cyan]")
        napalm_results = nr.run(task=get_mac_addresses)
        
        for hostname, task_result in napalm_results.items():
            if task_result.failed:
                results[hostname] = {"error": f"Task fehlgeschlagen: {task_result.exception}"}
            else:
                # Zugriff auf das NAPALM-Result - mehrfach verschachtelt!
                try:
                    # task_result ist MultiResult -> [0] ist Result -> .result ist MultiResult -> [0] ist Result -> .result ist dict
                    nested_multiresult = task_result[0].result  # Erste Verschachtelung
                    napalm_result = nested_multiresult[0]       # Zweite Verschachtelung
                    
                    if napalm_result.failed:
                        results[hostname] = {"error": f"NAPALM-Fehler: {napalm_result.exception}"}
                    else:
                        # NAPALM gibt strukturierte JSON-Daten zurück!
                        napalm_data = napalm_result.result
                        mac_address_table = napalm_data.get('mac_address_table', [])
                        
                        # Verarbeite JSON zu unserem Format
                        host = nr.inventory.hosts[hostname]
                        mac_entries = process_napalm_mac_data(mac_address_table, host.platform)
                        results[hostname] = {
                            "mac_entries": mac_entries, 
                            "platform": host.platform,
                            "napalm_data_count": len(mac_address_table)
                        }
                except Exception as e:
                    results[hostname] = {"error": f"Result-Zugriff fehlgeschlagen: {str(e)}"}
        
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
        console.print(f"[green]✅ Erfolgreich verbundene Geräte: {successful_devices}[/green]")
        console.print(f"[red]❌ Fehlgeschlagene Verbindungen: {failed_devices}[/red]")
        console.print(f"[blue]📋 Gesamt MAC-Adressen gefunden: {total_macs}[/blue]")
        console.print(f"[magenta]🔧 Methode: NAPALM (JSON-basiert)[/magenta]")
        
        if csv_file:
            current_dir = Path().absolute()
            console.print(f"[cyan]💾 CSV-Datei gespeichert unter: {current_dir}/{csv_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]💥 Kritischer Fehler: {str(e)}[/bold red]")
        sys.exit(1)
    
    console.print("\n[bold green]✨ Scanner beendet[/bold green]")


if __name__ == "__main__":
    main()
