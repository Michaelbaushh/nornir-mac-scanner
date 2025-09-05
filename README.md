# Nornir MAC Address Scanner

Ein modernisierter Python-basierter MAC-Adressen Scanner für Cisco-Switches using Nornir, NAPALM und Netmiko.

## 🚀 Features

- **Hybrid-Architektur**: NAPALM für IOS (strukturierte JSON-Daten), Netmiko für NX-OS (String-Parsing)
- **Multi-Platform Support**: Cisco IOS und NX-OS Switches
- **CSV Export**: Automatischer Export in CSV-Format mit Zeitstempel
- **Rich Terminal Output**: Formatierte Tabellen mit Farben
- **Connectivity Testing**: Integrierter Verbindungstest
- **Moderne APIs**: Nutzt NAPALM wo möglich für strukturierte Datenabfrage

## 🔧 Technologie Stack

- **[Nornir](https://nornir.readthedocs.io/)** - Network automation framework
- **[NAPALM](https://napalm.readthedocs.io/)** - Network abstraction layer (IOS devices)
- **[Netmiko](https://github.com/ktbyers/netmiko)** - SSH library (NX-OS fallback)
- **[Rich](https://rich.readthedocs.io/)** - Terminal formatting

## 📋 Voraussetzungen

- Python 3.7+
- SSH-Zugang zu Cisco-Switches
- Netzwerk-Konnektivität zu den Switches

## �️ Installation

1. **Repository klonen:**
   ```bash
   git clone https://github.com/Michaelbaushh/nornir-mac-scanner.git
   cd nornir-mac-scanner
   ```

2. **Dependencies installieren:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Inventar konfigurieren:**
   Bearbeite die Dateien im `inventory/` Verzeichnis:
   - `hosts.yaml` - Switch-IP-Adressen und Plattformen
   - `groups.yaml` - Platform-Gruppen und Connection-Optionen
   - `defaults.yaml` - Standard-Credentials

## 🚦 Usage

### Konnektivitätstest
```bash
python3 test_connectivity.py
```

### MAC-Adressen scannen
```bash
python3 get_mac_addresses.py
```

### Beispiel-Output
```
🚀 Hybrid MAC-Adressen Scanner
🔧 NAPALM für IOS, Netmiko für NX-OS
✅ 3 Switches in der Inventarliste geladen
🔄 Verarbeite 3 Switch(es) hybrid...

📊 ERGEBNISSE

═══ S1 ═══
┏━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ VLAN ┃ MAC-Adresse    ┃ Typ     ┃ Port/Interface ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 1    │ 000c.2937.a1ae │ dynamic │ Gi0/0          │
│ 1    │ 000c.299f.fe01 │ dynamic │ Gi0/0          │
│ ...  │ ...            │ ...     │ ...            │
└──────┴────────────────┴─────────┴────────────────┘
Gesamt: 24 MAC-Adressen gefunden - NAPALM (JSON)

📈 ZUSAMMENFASSUNG
✅ Erfolgreich verbundene Switches: 3
📋 Gesamt MAC-Adressen gefunden: 73
🔧 Methode: Hybrid (NAPALM + Netmiko)
```

## � Projektstruktur

```
nornir-mac-scanner/
├── get_mac_addresses.py     # Hauptskript (Hybrid NAPALM + Netmiko)
├── test_connectivity.py     # Verbindungstest-Utility
├── config.yaml             # Nornir-Konfiguration
├── requirements.txt        # Python Dependencies
├── inventory/              # Switch-Inventar
│   ├── hosts.yaml         #   - Switch-Definitionen
│   ├── groups.yaml        #   - Platform-Gruppen
│   └── defaults.yaml      #   - Standard-Einstellungen
└── versions/              # Legacy-Versionen
    ├── get_mac_addresses_napalm.py      # Reine NAPALM-Version
    ├── get_mac_addresses_netmiko_backup.py # Original Netmiko-Version
    └── get_mac_addresses_hybrid.py      # Entwicklungsversion
```

## ⚙️ Konfiguration

### Inventar-Beispiel

**hosts.yaml:**
```yaml
---
s1:
  hostname: 192.168.2.231
  groups:
    - ios_switches
    
s2:
  hostname: 192.168.2.232
  groups:
    - ios_switches

s3:
  hostname: 192.168.2.233
  groups:
    - nxos_switches
```

**groups.yaml:**
```yaml
---
ios_switches:
  platform: "cisco_ios"
  connection_options:
    napalm:
      platform: "ios"
      
nxos_switches: 
  platform: "cisco_nxos"
```

**defaults.yaml:**
```yaml
---
username: admin
password: cisco
```

## 🔄 Modernisierung Details

### Warum Hybrid-Ansatz?

- **IOS-Switches**: Nutzen NAPALM für strukturierte JSON-APIs
- **NX-OS-Switches**: Verwenden Netmiko da NXAPI oft nicht aktiviert ist
- **Automatische Platform-Erkennung**: Script wählt optimale Methode

### NAPALM vs Netmiko

| Feature | NAPALM (IOS) | Netmiko (NX-OS) |
|---------|--------------|-----------------|
| Datenformat | JSON (strukturiert) | String (geparst) |
| API | Standardisierte Getter | Raw CLI Commands |
| Wartung | Einfacher | String-Parsing nötig |
| Performance | Besser | Ausreichend |

## �📊 Ausgabe

Das Script zeigt für jeden Switch eine Tabelle mit:
- **VLAN**: VLAN-Nummer
- **MAC-Adresse**: Hardware-Adresse  
- **Typ**: Adresstyp (Dynamic/Static)
- **Port/Interface**: Zugewiesener Port

Zusätzlich wird eine Zusammenfassung mit der Gesamtanzahl gefundener MAC-Adressen angezeigt.

## 🗂️ Projektstruktur

```
get-macs/
├── config.yaml              # Nornir Hauptkonfiguration
├── requirements.txt         # Python-Abhängigkeiten
├── get_mac_addresses.py     # Haupt-Scanner Script
├── test_connectivity.py     # Konnektivitätstest
├── inventory/
│   ├── hosts.yaml          # Switch-Inventar
│   ├── groups.yaml         # Switch-Gruppen
│   └── defaults.yaml       # Standard-Anmeldedaten
└── README.md               # Diese Datei
```

## 🔍 Unterstützte Plattformen

- **Cisco IOS** - Catalyst und andere Layer-2/3 Switches
- **Cisco NX-OS** - Nexus Switches

## ⚠️ Troubleshooting

### Häufige Probleme:

1. **SSH Timeout/Connection refused:**
   - Überprüfe IP-Adressen in `hosts.yaml`
   - Stelle sicher, dass SSH aktiviert ist: `ip ssh version 2`

2. **Authentication Failed:**
   - Überprüfe Benutzername/Passwort in `defaults.yaml`
   - Teste manuelle SSH-Verbindung

3. **Leere MAC-Tabelle:**
   - Überprüfe ob Switches aktiv im Netzwerk sind
   - Teste manuell: `show mac address-table`

### Debug-Modus aktivieren:

In der `config.yaml` das Log-Level auf DEBUG setzen:

```yaml
logging:
  enabled: True
  level: DEBUG
```

## 📝 Anpassungen

Das Script kann einfach für andere Switch-Plattformen erweitert werden:

1. Neue Plattform in `groups.yaml` hinzufügen
2. Entsprechende Parse-Funktion implementieren
3. Switch-spezifische Show-Befehle anpassen

## 🤝 Beitrag

Bei Fragen, Problemen oder Verbesserungsvorschlägen erstelle bitte ein Issue oder Pull Request.

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
