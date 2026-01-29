import json
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from c3hm.data.rubric import Indicator, Rubric

LEVELS = [
    ("av", "Avancé", "#C8FFC8"),
    ("ac", "Acquis", "#F0FFB0"),
    ("p", "Ça y est presque!", "#FFF8C2"),
    ("ap", "En apprentissage", "#FFE4C8"),
    ("n", "Non démontré", "#FFC8C8"),
]
DEFAULT_BG = "#E0E0E0"
DEFAULT_BORDER = "#B0B0B0"


def launch_gui(gradebook_path: Path) -> None:
    with open(gradebook_path, encoding="utf-8") as f:
        data = json.load(f)
    rubric = Rubric.from_dict(data)

    app = _RubricGui(rubric=rubric, gradebook_path=gradebook_path)
    app.run()


class _RubricGui:
    def __init__(self, rubric: Rubric, gradebook_path: Path):
        self.rubric = rubric
        self.gradebook_path = gradebook_path
        self.root = tk.Tk()
        self.root.title("c3hm — Grille de correction")
        self.status_var = tk.StringVar(value="")
        self.override_var = tk.StringVar(value="" if rubric.grade is None else str(rubric.grade))
        self.grid_grade_var = tk.StringVar(value="—")
        self.final_grade_var = tk.StringVar(value="—")
        self._indicator_cells: list[list[tk.Button]] = []
        self._build_ui()
        self._refresh_grades()

    def run(self) -> None:
        self.root.mainloop()

    def _build_ui(self) -> None:
        self.root.configure(padx=12, pady=12)

        header = ttk.Frame(self.root)
        header.pack(fill="x", pady=(0, 8))

        student_name = "—"
        student_id = "—"
        if self.rubric.student is not None:
            student_name = self.rubric.student.name or "—"
            student_id = self.rubric.student.omnivox_id or "—"

        student_label = ttk.Label(
            header,
            text=f"Étudiant: {student_name} ({student_id})",
            font=("Segoe UI", 11, "bold"),
        )
        student_label.grid(row=0, column=0, sticky="w")

        grade_label = ttk.Label(
            header,
            textvariable=self.final_grade_var,
            font=("Segoe UI", 11, "bold"),
        )
        grade_label.grid(row=0, column=1, sticky="e", padx=(12, 0))

        grid_grade_label = ttk.Label(header, textvariable=self.grid_grade_var)
        grid_grade_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        override_frame = ttk.Frame(header)
        override_frame.grid(row=1, column=1, sticky="e", pady=(4, 0))

        ttk.Label(override_frame, text="Note finale (override):").grid(row=0, column=0, sticky="e")
        override_entry = ttk.Entry(override_frame, textvariable=self.override_var, width=8)
        override_entry.grid(row=0, column=1, sticky="e", padx=(6, 0))

        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        override_entry.bind("<KeyRelease>", self._on_override_change)

        grid_container = ttk.Frame(self.root)
        grid_container.pack(fill="both", expand=True, pady=(4, 8))

        canvas = tk.Canvas(grid_container, borderwidth=0, highlightthickness=0)
        v_scroll = ttk.Scrollbar(grid_container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(grid_container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _configure_scroll_region(event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _resize_canvas(event: tk.Event) -> None:
            canvas.itemconfig(canvas_window, width=event.width)

        scroll_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _resize_canvas)

        self._build_grid(scroll_frame)

        comment_frame = ttk.Frame(self.root)
        comment_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(comment_frame, text="Commentaire:").pack(anchor="w")

        self.comment_text = tk.Text(comment_frame, height=4, wrap="word")
        self.comment_text.pack(fill="x", expand=True)
        if self.rubric.comment:
            self.comment_text.insert("1.0", self.rubric.comment)

        actions = ttk.Frame(self.root)
        actions.pack(fill="x", pady=(8, 0))
        save_button = ttk.Button(actions, text="Sauvegarder", command=self._save)
        save_button.pack(side="right")

        status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="#444444")
        status_label.pack(fill="x", pady=(6, 0))

    def _build_grid(self, parent: ttk.Frame) -> None:
        header_bg = "#F5F5F5"
        tk.Label(parent, text="Indicateur", bg=header_bg, font=("Segoe UI", 10, "bold"), padx=8, pady=6).grid(row=0, column=0, sticky="nsew")

        for col_index, (_, level_label, color) in enumerate(LEVELS, start=1):
            tk.Label(parent, text=level_label, bg=color, font=("Segoe UI", 10, "bold"), padx=8, pady=6, wraplength=120).grid(row=0, column=col_index, sticky="nsew")

        row_index = 1
        for criterion in self.rubric.grid.criteria:
            criterion_label = f"{criterion.label}"
            tk.Label(parent, text=criterion_label, bg="#DDDDDD", font=("Segoe UI", 10, "bold"), padx=8, pady=6).grid(row=row_index, column=0, columnspan=6, sticky="nsew")
            row_index += 1

            for indicator in criterion.indicators:
                tk.Label(parent, text=indicator.label, bg="#FFFFFF", padx=8, pady=6, wraplength=220, justify="left", anchor="w").grid(row=row_index, column=0, sticky="nsew")
                row_cells: list[tk.Button] = []
                for level_index, (_, _, color) in enumerate(LEVELS):
                    desc = indicator.descriptors[level_index]
                    btn = tk.Button(
                        parent,
                        text=desc,
                        bg=DEFAULT_BG,
                        activebackground=color,
                        relief="ridge",
                        bd=1,
                        wraplength=220,
                        justify="left",
                        anchor="w",
                        command=self._make_level_handler(indicator, level_index)
                    )
                    btn.grid(row=row_index, column=level_index + 1, sticky="nsew", padx=1, pady=1)
                    row_cells.append(btn)
                self._indicator_cells.append(row_cells)
                self._apply_indicator_selection(indicator, row_cells)
                row_index += 1

        for col in range(6):
            parent.columnconfigure(col, weight=1)

    def _make_level_handler(self, indicator: Indicator, level_index: int) -> Callable[[], None]:
        def handler() -> None:
            indicator.graded_level = LEVELS[level_index][0]
            self._update_indicator_row(indicator)
            self._refresh_grades()
        return handler

    def _update_indicator_row(self, indicator: Indicator) -> None:
        row_cells = self._find_row_cells(indicator)
        if not row_cells:
            return
        self._apply_indicator_selection(indicator, row_cells)

    def _find_row_cells(self, indicator: Indicator) -> list[tk.Button] | None:
        index = 0
        for criterion in self.rubric.grid.criteria:
            for ind in criterion.indicators:
                if ind is indicator:
                    return self._indicator_cells[index]
                index += 1
        return None

    def _apply_indicator_selection(self, indicator: Indicator, row_cells: list[tk.Button]) -> None:
        selected_index = _level_to_index(indicator.graded_level)
        for idx, cell in enumerate(row_cells):
            if selected_index is not None and idx == selected_index:
                cell.configure(bg=LEVELS[idx][2], relief="solid", bd=2, highlightbackground=DEFAULT_BORDER)
            else:
                cell.configure(bg=DEFAULT_BG, relief="ridge", bd=1)

    def _refresh_grades(self) -> None:
        grid_grade = _safe_grid_grade(self.rubric)
        if grid_grade is None:
            self.grid_grade_var.set("Note (grille): —")
        else:
            self.grid_grade_var.set(f"Note (grille): {grid_grade:.0f} / 100")

        final_grade = self.rubric.grade if self.rubric.grade is not None else grid_grade
        if final_grade is None:
            self.final_grade_var.set("Note finale: — / 100")
        else:
            self.final_grade_var.set(f"Note finale: {final_grade:.0f} / 100")

    def _on_override_change(self, event: tk.Event) -> None:
        value = self.override_var.get().strip()
        if value == "":
            self.rubric.grade = None
            self.status_var.set("")
            self._refresh_grades()
            return
        try:
            parsed = float(value.replace(",", "."))
        except ValueError:
            self.status_var.set("Note invalide: entrez un nombre (ex: 75 ou 75.5).")
            return
        if parsed < 0 or parsed > 100:
            self.status_var.set("Note invalide: la note doit être entre 0 et 100.")
            return
        self.rubric.grade = parsed
        self.status_var.set("")
        self._refresh_grades()

    def _save(self) -> None:
        comment = self.comment_text.get("1.0", "end").strip()
        self.rubric.comment = comment if comment else None
        self._on_override_change(tk.Event())

        rubric_dict = self.rubric.to_dict()
        try:
            with open(self.gradebook_path, "w", encoding="utf-8") as f:
                json.dump(rubric_dict, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            self.status_var.set(f"Erreur lors de la sauvegarde: {exc}")
            return
        self.status_var.set("Sauvegarde réussie.")


def _level_to_index(level: str | None) -> int | None:
    if not level:
        return None
    try:
        pct = Indicator.level_to_percentage(level)
    except (ValueError, TypeError):
        return None
    if pct == 1.0:
        return 0
    if pct == 0.75:
        return 1
    if pct == 0.5:
        return 2
    if pct == 0.25:
        return 3
    if pct == 0.0:
        return 4
    return None


def _safe_grid_grade(rubric: Rubric) -> float | None:
    try:
        return rubric.grid_grade()
    except ValueError:
        return None
