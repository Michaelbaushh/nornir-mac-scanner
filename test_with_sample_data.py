#!/usr/bin/env python3
"""
Test-Version des MAC-Scanners mit Beispieldaten
"""

import csv
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

def create_test_data():
    """Erstellt Testdaten für die Demo"""
    return {
        's1': {
            'mac_entries': [
                {'vlan': '1', 'mac': '0012.3456.7890', 'type': 'DYNAMIC', 'port': 'Gi0/1'},
                {'vlan': '10', 'mac': '0012.3456.7891', 'type': 'DYNAMIC', 'port': 'Gi0/2'},
                {'vlan': '20', 'mac': '0012.3456.7892', 'type': 'DYNAMIC', 'port': 'Gi0/3'},
            ],
            'platform': 'ios'
        },
        's2': {
            'mac_entries': [
                {'vlan': '1', 'mac': '0012.3456.7893', 'type': 'DYNAMIC', 'port': 'Gi0/5'},
                {'vlan': '30', 'mac': '0012.3456.7894', 'type': 'DYNAMIC', 'port': 'Gi0/6'},
            ],
            'platform': 'ios'
        },
        's3': {
            'mac_entries': [
                {'vlan': '1', 'mac': '0012.3456.7895', 'type': 'dynamic', 'port': 'Eth1/1'},
                {'vlan': '40', 'mac': '0012.3456.7896', 'type': 'dynamic', 'port': 'Eth1/2'},
                {'vlan': '50', 'mac': '0012.3456.7897', 'type': 'dynamic', 'port': 'Eth1/3'},
                {'vlan': '60', 'mac': '0012.3456.7898', 'type': 'dynamic', 'port': 'Eth1/4'},
            ],
            'platform': 'nxos'
        }
    }

def export_to_csv(results, console):
    """Exportiert die MAC-Adressen Ergebnisse in eine CSV-Datei"""
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
                            'ip_address': f"192.168.2.{231 if hostname == 's1' else 232 if hostname == 's2' else 233}",
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
    """Zeigt die Ergebnisse in einer formattierten Tabelle an"""
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
    """Hauptfunktion für Test mit Beispieldaten"""
    console = Console()
    console.print("[bold green]🚀 MAC-Adressen Scanner (TEST-MODUS)[/bold green]")
    console.print("[yellow]📝 Verwende Beispieldaten zur Demonstration[/yellow]")
    
    # Testdaten erstellen
    results = create_test_data()
    
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
    
    console.print("\n[bold green]✨ Scanner beendet[/bold green]")

if __name__ == "__main__":
    main()
