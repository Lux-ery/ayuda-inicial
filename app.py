#!/usr/bin/env python3
"""Organizador personal con UI mejorada, notificaciones y guardado local."""

from __future__ import annotations

import json
import platform
import subprocess
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk

APP_DIR = Path.home() / ".organizador"
TASKS_FILE = APP_DIR / "tasks.json"
DATE_FMT = "%Y-%m-%d"


class OrganizadorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Organizador Diario")
        self.geometry("860x560")
        self.minsize(760, 500)

        self.tasks: list[dict[str, str | bool]] = []
        self.notified_today: set[str] = set()

        self._configure_style()
        self._build_ui()
        self._load_tasks()
        self._refresh_tree()
        self._update_stats()
        self._schedule_notifications()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        self.configure(bg="#f3f6fb")
        style.configure("Card.TLabelframe", background="#ffffff", bordercolor="#d8dee9")
        style.configure("Card.TLabelframe.Label", background="#ffffff", foreground="#2f3b52", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"))
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)

        header = ttk.Frame(root)
        header.pack(fill="x")

        ttk.Label(header, text="🗂️ Organizador Diario", font=("Segoe UI", 18, "bold")).pack(side="left")
        self.stats_var = tk.StringVar(value="0 pendientes · 0 completadas")
        ttk.Label(header, textvariable=self.stats_var, font=("Segoe UI", 10)).pack(side="right", pady=8)

        form = ttk.LabelFrame(root, text="Nueva tarea", padding=12, style="Card.TLabelframe")
        form.pack(fill="x", pady=(12, 10))

        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar(value="General")
        self.deadline_var = tk.StringVar(value=datetime.now().strftime(DATE_FMT))
        self.priority_var = tk.StringVar(value="Media")

        ttk.Label(form, text="Título").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.title_var).grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 10), pady=(2, 8))

        ttk.Label(form, text="Categoría").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.category_var).grid(row=1, column=2, sticky="ew", padx=(0, 10), pady=(2, 8))

        ttk.Label(form, text="Fecha límite (YYYY-MM-DD)").grid(row=0, column=3, sticky="w")
        ttk.Entry(form, textvariable=self.deadline_var).grid(row=1, column=3, sticky="ew", padx=(0, 10), pady=(2, 8))

        ttk.Label(form, text="Prioridad").grid(row=0, column=4, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.priority_var,
            values=["Alta", "Media", "Baja"],
            state="readonly",
        ).grid(row=1, column=4, sticky="ew", pady=(2, 8))

        ttk.Button(form, text="Agregar tarea", style="Primary.TButton", command=self._add_task).grid(row=1, column=5, padx=(10, 0), sticky="ew")

        for col in range(5):
            form.columnconfigure(col, weight=1)

        table_frame = ttk.LabelFrame(root, text="Mis tareas", padding=10, style="Card.TLabelframe")
        table_frame.pack(fill="both", expand=True)

        columns = ("titulo", "categoria", "prioridad", "fecha", "estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        for col, txt in zip(columns, ["Título", "Categoría", "Prioridad", "Fecha límite", "Estado"]):
            self.tree.heading(col, text=txt)

        self.tree.column("titulo", width=270)
        self.tree.column("categoria", width=140)
        self.tree.column("prioridad", width=100, anchor="center")
        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("estado", width=100, anchor="center")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(actions, text="✓ Marcar completada", command=self._mark_done).pack(side="left")
        ttk.Button(actions, text="🗑 Eliminar", command=self._delete_task).pack(side="left", padx=8)
        ttk.Button(actions, text="💾 Guardar", command=self._save_tasks).pack(side="right")

    def _add_task(self) -> None:
        title = self.title_var.get().strip()
        category = self.category_var.get().strip() or "General"
        deadline = self.deadline_var.get().strip()
        priority = self.priority_var.get().strip() or "Media"

        if not title:
            messagebox.showwarning("Campo requerido", "El título no puede estar vacío.")
            return

        if deadline:
            try:
                datetime.strptime(deadline, DATE_FMT)
            except ValueError:
                messagebox.showwarning("Fecha inválida", "Usa formato YYYY-MM-DD.")
                return

        self.tasks.append(
            {
                "title": title,
                "category": category,
                "priority": priority,
                "deadline": deadline,
                "done": False,
            }
        )
        self.title_var.set("")
        self._refresh_tree()
        self._update_stats()
        self._save_tasks()

    def _selected_index(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selecciona una tarea", "Debes seleccionar una tarea.")
            return None

        values = self.tree.item(selected[0], "values")
        for i, task in enumerate(self.tasks):
            if task["title"] == values[0] and task["deadline"] == values[3]:
                return i
        return None

    def _mark_done(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.tasks[idx]["done"] = True
        self._refresh_tree()
        self._update_stats()
        self._save_tasks()

    def _delete_task(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        del self.tasks[idx]
        self._refresh_tree()
        self._update_stats()
        self._save_tasks()

    def _refresh_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())

        priority_order = {"Alta": 0, "Media": 1, "Baja": 2}
        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (
                bool(t.get("done", False)),
                priority_order.get(str(t.get("priority", "Media")), 1),
                str(t.get("deadline", "9999-12-31")),
            ),
        )

        for task in sorted_tasks:
            done = bool(task.get("done", False))
            self.tree.insert(
                "",
                "end",
                values=(
                    task.get("title", ""),
                    task.get("category", "General"),
                    task.get("priority", "Media"),
                    task.get("deadline", ""),
                    "Hecha" if done else "Pendiente",
                ),
            )

    def _update_stats(self) -> None:
        done = sum(1 for t in self.tasks if t.get("done", False))
        pending = len(self.tasks) - done
        self.stats_var.set(f"{pending} pendientes · {done} completadas")

    def _send_desktop_notification(self, title: str, body: str) -> None:
        system = platform.system()
        try:
            if system == "Linux":
                subprocess.run(["notify-send", title, body], check=False)
            elif system == "Darwin":
                script = f'display notification "{body}" with title "{title}"'
                subprocess.run(["osascript", "-e", script], check=False)
            elif system == "Windows":
                # Fallback visual si no hay integración de toasts.
                self.after(0, lambda: messagebox.showinfo(title, body))
        except OSError:
            pass

    def _schedule_notifications(self) -> None:
        today = datetime.now().strftime(DATE_FMT)

        for task in self.tasks:
            if task.get("done", False):
                continue
            if str(task.get("deadline", "")).strip() != today:
                continue

            signature = f"{task.get('title','')}::{today}"
            if signature in self.notified_today:
                continue

            self.notified_today.add(signature)
            self._send_desktop_notification(
                "Tarea vence hoy",
                f"{task.get('title', 'Tarea sin título')} ({task.get('priority', 'Media')})",
            )

        self.after(60_000, self._schedule_notifications)

    def _load_tasks(self) -> None:
        if not TASKS_FILE.exists():
            self.tasks = []
            return
        try:
            self.tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
            if not isinstance(self.tasks, list):
                self.tasks = []
        except (json.JSONDecodeError, OSError):
            self.tasks = []

    def _save_tasks(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        TASKS_FILE.write_text(json.dumps(self.tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    app = OrganizadorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
