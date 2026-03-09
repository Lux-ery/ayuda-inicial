# Organizador Diario (auto inicio)

Aplicación simple en Python (Tkinter) para organizar tareas personales con persistencia local.

## Funciones

- Crear tareas con título, categoría, prioridad y fecha límite.
- Marcar tareas como completadas.
- Eliminar tareas.
- Orden automático por estado y prioridad.
- Guardado automático en `~/.organizador/tasks.json`.

## Requisitos

- Python 3.10+
- Tkinter (normalmente incluido con Python en Windows/macOS y en muchos Linux).

## Ejecutar la aplicación

```bash
python3 app.py
```

## Abrir automáticamente al encender la computadora

### Linux (systemd --user)

1. Crea el archivo `~/.config/systemd/user/organizador.service` con este contenido:

```ini
[Unit]
Description=Organizador Diario

[Service]
Type=simple
WorkingDirectory=/workspace/ayuda-inicial
ExecStart=/usr/bin/python3 /workspace/ayuda-inicial/app.py
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
2. Crea un archivo `organizador.bat` con:

```bat
@echo off
python "C:\ruta\a\ayuda-inicial\app.py"
```

3. Reinicia sesión para comprobar.

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
        <string>/usr/bin/python3</string>
        <string>/ruta/a/ayuda-inicial/app.py</string>
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

---

Si quieres, te la adapto para que tenga calendario, recordatorios con notificaciones, o sincronización con Google Calendar.
