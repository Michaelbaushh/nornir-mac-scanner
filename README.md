# MAC-Adressen Scanner mit Nornir

Ein Python-Script zum automatisierten Auslesen von MAC-Adressen von Cisco Netzwerkgeräten unter Verwendung von Nornir.

## 🚀 Funktionen

- **Automatisiertes MAC-Adressen Auslesen** von Cisco IOS und NX-OS Switches
- **Parallele Verarbeitung** mehrerer Geräte gleichzeitig  
- **Strukturierte Ausgabe** mit Rich-Tabellen
- **Konnektivitätstest** vor dem eigentlichen Scan
- **Fehlerbehandlung** und detaillierte Logging

## 📋 Voraussetzungen

- Python 3.7 oder höher
- Netzwerkzugriff zu den Cisco Geräten
- SSH-Zugriff aktiviert auf den Geräten

## 🔧 Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Abhängigkeiten installieren:**
```bash
pip install -r requirements.txt
```

## ⚙️ Konfiguration

### Geräte-Inventar anpassen

Bearbeite die Datei `inventory/hosts.yaml` und trage deine Geräte ein:

```yaml
---
s1:
  hostname: "192.168.2.231"
  platform: "cisco_ios"
  groups: ["ios_switches"]

s2:
  hostname: "192.168.2.232"  
  platform: "cisco_ios"
  groups: ["ios_switches"]

s3:
  hostname: "192.168.2.233"
  platform: "cisco_nxos"
  groups: ["nxos_switches"]
```

### Anmeldedaten anpassen

Die Anmeldedaten können in `inventory/defaults.yaml` geändert werden:

```yaml
---
username: "admin"
password: "cisco"
port: 22
timeout: 60
```

## 🚦 Verwendung

### 1. Konnektivitätstest (empfohlen)

Teste zuerst die Verbindung zu allen Geräten:

```bash
python test_connectivity.py
```

### 2. MAC-Adressen Scanner ausführen

```bash
python get_mac_addresses.py
```

## 📊 Ausgabe

Das Script zeigt für jedes Gerät eine Tabelle mit:
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
│   ├── hosts.yaml          # Geräte-Inventar
│   ├── groups.yaml         # Geräte-Gruppen
│   └── defaults.yaml       # Standard-Anmeldedaten
└── README.md               # Diese Datei
```

## 🔍 Unterstützte Plattformen

- **Cisco IOS** - Switches und Router
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
   - Überprüfe ob Geräte aktiv im Netzwerk sind
   - Teste manuell: `show mac address-table`

### Debug-Modus aktivieren:

In der `config.yaml` das Log-Level auf DEBUG setzen:

```yaml
logging:
  enabled: True
  level: DEBUG
```

## 📝 Anpassungen

Das Script kann einfach für andere Netzwerkgeräte erweitert werden:

1. Neue Plattform in `groups.yaml` hinzufügen
2. Entsprechende Parse-Funktion implementieren
3. Gerätespezifische Show-Befehle anpassen

## 🤝 Beitrag

Bei Fragen, Problemen oder Verbesserungsvorschlägen erstelle bitte ein Issue oder Pull Request.

## 📄 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
