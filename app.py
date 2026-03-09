#!/usr/bin/env python3
"""Mini app de organización personal con autoguardado en JSON."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_DIR = Path.home() / ".organizador"
TASKS_FILE = APP_DIR / "tasks.json"


class OrganizadorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Organizador Diario")
        self.geometry("760x500")
        self.minsize(680, 420)

        self.tasks: list[dict[str, str | bool]] = []

        self._build_ui()
        self._load_tasks()
        self._refresh_tree()

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=12)
        root.pack(fill="both", expand=True)

        # Formulario de tarea
        form = ttk.LabelFrame(root, text="Nueva tarea", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Título:").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=4)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(form, textvariable=self.title_var)
        self.title_entry.grid(row=0, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Categoría:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.category_var = tk.StringVar(value="General")
        self.category_entry = ttk.Entry(form, textvariable=self.category_var)
        self.category_entry.grid(row=1, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="Fecha límite:").grid(row=0, column=2, sticky="w", padx=(16, 8), pady=4)
        self.deadline_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.deadline_entry = ttk.Entry(form, textvariable=self.deadline_var)
        self.deadline_entry.grid(row=0, column=3, sticky="ew", pady=4)

        ttk.Label(form, text="Prioridad:").grid(row=1, column=2, sticky="w", padx=(16, 8), pady=4)
        self.priority_var = tk.StringVar(value="Media")
        self.priority_combo = ttk.Combobox(
            form,
            textvariable=self.priority_var,
            values=["Alta", "Media", "Baja"],
            state="readonly",
        )
        self.priority_combo.grid(row=1, column=3, sticky="ew", pady=4)

        add_btn = ttk.Button(form, text="Agregar tarea", command=self._add_task)
        add_btn.grid(row=0, column=4, rowspan=2, padx=(16, 0), sticky="ns")

        form.columnconfigure(1, weight=2)
        form.columnconfigure(3, weight=1)

        # Tabla de tareas
        table_frame = ttk.LabelFrame(root, text="Tareas", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(12, 0))

        columns = ("titulo", "categoria", "prioridad", "fecha", "estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("titulo", text="Título")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("prioridad", text="Prioridad")
        self.tree.heading("fecha", text="Fecha límite")
        self.tree.heading("estado", text="Estado")

        self.tree.column("titulo", width=220)
        self.tree.column("categoria", width=120)
        self.tree.column("prioridad", width=90, anchor="center")
        self.tree.column("fecha", width=110, anchor="center")
        self.tree.column("estado", width=90, anchor="center")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")

        # Botones de acción
        actions = ttk.Frame(root)
        actions.pack(fill="x", pady=(10, 0))

        ttk.Button(actions, text="Marcar completada", command=self._mark_done).pack(side="left")
        ttk.Button(actions, text="Eliminar seleccionada", command=self._delete_task).pack(side="left", padx=8)
        ttk.Button(actions, text="Guardar ahora", command=self._save_tasks).pack(side="right")

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
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                messagebox.showwarning(
                    "Fecha inválida",
                    "Usa el formato YYYY-MM-DD para la fecha límite.",
                )
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
        self.category_var.set("General")
        self.priority_var.set("Media")
        self._refresh_tree()
        self._save_tasks()

    def _selected_index(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selecciona una tarea", "Debes seleccionar una tarea primero.")
            return None

        values = self.tree.item(selected[0], "values")
        title = values[0]
        for i, task in enumerate(self.tasks):
            if task["title"] == title and task["deadline"] == values[3]:
                return i
        return None

    def _mark_done(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        self.tasks[idx]["done"] = True
        self._refresh_tree()
        self._save_tasks()

    def _delete_task(self) -> None:
        idx = self._selected_index()
        if idx is None:
            return
        del self.tasks[idx]
        self._refresh_tree()
        self._save_tasks()

    def _refresh_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        priority_order = {"Alta": 0, "Media": 1, "Baja": 2}

        sorted_tasks = sorted(
            self.tasks,
            key=lambda t: (
                t.get("done", False),
                priority_order.get(str(t.get("priority", "Media")), 1),
                str(t.get("deadline", "")),
            ),
        )

        for task in sorted_tasks:
            self.tree.insert(
                "",
                "end",
                values=(
                    task.get("title", ""),
                    task.get("category", "General"),
                    task.get("priority", "Media"),
                    task.get("deadline", ""),
                    "Hecha" if task.get("done", False) else "Pendiente",
                ),
            )

    def _load_tasks(self) -> None:
        if not TASKS_FILE.exists():
            self.tasks = []
            return

        try:
            with TASKS_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.tasks = data
            else:
                self.tasks = []
        except (json.JSONDecodeError, OSError):
            self.tasks = []

    def _save_tasks(self) -> None:
        APP_DIR.mkdir(parents=True, exist_ok=True)
        with TASKS_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)


def main() -> None:
    app = OrganizadorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
