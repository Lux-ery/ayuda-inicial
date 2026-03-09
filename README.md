# Organizador Diario (auto inicio + notificaciones)

Aplicación de escritorio en Python (Tkinter) para organizar tareas personales, con mejor diseño visual, notificaciones de vencimiento y opción de instalación.

## Funciones

- Diseño más limpio con cabecera, tarjetas y estado de tareas.
- Crear tareas con título, categoría, prioridad y fecha límite.
- Marcar tareas como completadas y eliminar tareas.
- Indicador de estadísticas (`pendientes` y `completadas`).
- Orden automático por estado, prioridad y fecha.
- Guardado automático en `~/.organizador/tasks.json`.
- Notificaciones para tareas que vencen hoy:
  - Linux: `notify-send`
  - macOS: `osascript`
  - Windows: mensaje emergente dentro de la app.

## Requisitos

- Python 3.10+
- Tkinter
- (Linux, opcional) `notify-send` para notificaciones del escritorio.

## Ejecutar en modo desarrollo

```bash
python3 app.py
```

## Instalar la aplicación (pip)

Instalación local como app ejecutable:

```bash
python3 -m pip install .
```

Después podrás iniciarla con:

```bash
organizador-diario
```

## Crear ejecutable instalable (opcional)

Si quieres un binario para distribuir:

```bash
python3 -m pip install pyinstaller
pyinstaller --name organizador-diario --onefile --windowed app.py
```

Se genera en `dist/organizador-diario` (o `.exe` en Windows).

## Abrir automáticamente al encender la computadora

### Linux (systemd --user)

1. Crea `~/.config/systemd/user/organizador.service`:

```ini
[Unit]
Description=Organizador Diario

[Service]
Type=simple
ExecStart=/usr/bin/env organizador-diario
Restart=on-failure

[Install]
WantedBy=default.target
```

2. Activa el servicio:

```bash
systemctl --user daemon-reload
systemctl --user enable --now organizador.service
```

### Windows (carpeta Inicio)

1. Pulsa `Win + R` y abre: `shell:startup`
2. Crea `organizador.bat` con:

```bat
@echo off
organizador-diario
```

### macOS (LaunchAgents)

1. Crea `~/Library/LaunchAgents/com.usuario.organizador.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.usuario.organizador</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/env</string>
        <string>organizador-diario</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

2. Carga el agente:

```bash
launchctl load ~/Library/LaunchAgents/com.usuario.organizador.plist
```
