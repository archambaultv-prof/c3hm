import json
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from c3hm.data.rubric import Criterion, Indicator, Rubric

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
    if gradebook_path.is_file():
        json_files = [gradebook_path]
    else:
        json_files = sorted(gradebook_path.glob("*.json"))
        if not json_files:
            raise FileNotFoundError(f"Aucun fichier .json trouvé dans le dossier {gradebook_path}")
    app = _RubricGui(json_files=json_files)
    app.run()


class _RubricGui:
    def __init__(self, json_files: list[Path]):
        self.json_files = json_files
        self.current_index = 0
        self.root = tk.Tk()
        self.root.title("c3hm — Grille de correction")
        self.status_var = tk.StringVar(value="")
        self.override_var = tk.StringVar(value="")
        self.grid_grade_var = tk.StringVar(value="—")
        self.final_grade_var = tk.StringVar(value="—")
        self.position_var = tk.StringVar(value=f"1 / {len(self.json_files)}")
        self.student_selector_var = tk.StringVar(value="")
        self._indicator_cells: list[list[tk.Button]] = []
        self._criterion_override_vars: list[tuple[tk.StringVar, Criterion]] = []
        self._criterion_label_vars: list[tuple[tk.StringVar, Criterion]] = []
        self.rubric: Rubric = Rubric(course="", session="", evaluation="", grid=None)  # type: ignore
        self.current_path: Path = Path("")
        self.comment_text: tk.Text | None = None
        self._load_file(0)
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.root.mainloop()

    def _on_close(self) -> None:
        self._save_current()
        self.root.destroy()

    def _load_file(self, index: int) -> None:
        self.current_index = index
        self.current_path = self.json_files[index]
        with open(self.current_path, encoding="utf-8") as f:
            data = json.load(f)
        self.rubric = Rubric.from_dict(data)
        self.override_var.set("" if self.rubric.grade is None else str(self.rubric.grade))
        self.position_var.set(f"{index + 1} / {len(self.json_files)}")
        self.student_selector_var.set(self.current_path.stem)

    def _build_ui(self) -> None:
        self.root.configure(padx=12, pady=12)

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", pady=(0, 8))

        ttk.Label(top_frame, text="Étudiant:").grid(row=0, column=0, sticky="w")
        selector = ttk.Combobox(top_frame, textvariable=self.student_selector_var, state="readonly", width=40)
        selector["values"] = [f.stem for f in self.json_files]
        selector.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        selector.bind("<<ComboboxSelected>>", self._on_student_selected)
        top_frame.columnconfigure(1, weight=1)

        if len(self.json_files) > 1:
            nav_frame = ttk.Frame(self.root)
            nav_frame.pack(fill="x", pady=(0, 8))
            ttk.Button(nav_frame, text="< Précédent", command=self._prev_student).pack(side="left")
            ttk.Label(nav_frame, textvariable=self.position_var).pack(side="left", padx=(12, 0))
            ttk.Button(nav_frame, text="Suivant >", command=self._next_student).pack(side="left", padx=(12, 0))

        header = ttk.Frame(self.root)
        header.pack(fill="x", pady=(0, 8))

        student_name = "—"
        student_id = "—"
        if self.rubric.student is not None:
            student_name = self.rubric.student.fullname() or "—"
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

        def _configure_scroll_region(event: tk.Event) -> None:  # noqa: ARG001
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _resize_canvas(event: tk.Event) -> None:  # noqa: ARG001
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
        if len(self.json_files) > 1:
            ttk.Button(actions, text="Sauvegarder & Suivant", command=self._save_and_next).pack(side="right")
        else:
            ttk.Button(actions, text="Sauvegarder", command=self._save_current).pack(side="right")

        status_label = ttk.Label(self.root, textvariable=self.status_var, foreground="#444444")
        status_label.pack(fill="x", pady=(6, 0))

        self._refresh_grades()

    def _build_grid(self, parent: ttk.Frame) -> None:
        header_bg = "#F5F5F5"
        tk.Label(parent, text="Indicateur", bg=header_bg, font=("Segoe UI", 10, "bold"), padx=8, pady=6).grid(row=0, column=0, sticky="nsew")

        for col_index, (_, level_label, color) in enumerate(LEVELS, start=1):
            tk.Label(parent, text=level_label, bg=color, font=("Segoe UI", 10, "bold"), padx=8, pady=6, wraplength=120).grid(row=0, column=col_index, sticky="nsew")

        row_index = 1
        for criterion in self.rubric.grid.criteria:
            indicators_grade = _safe_criterion_indicators_grade(criterion)
            indicators_text = "—" if indicators_grade is None else f"{indicators_grade:.0f} / {criterion.points():.0f}"
            criterion_label = f"{criterion.label}  —  Note (indicateurs) : {indicators_text}"
            criterion_label_var = tk.StringVar(value=criterion_label)
            self._criterion_label_vars.append((criterion_label_var, criterion))

            header_frame = ttk.Frame(parent)
            header_frame.grid(row=row_index, column=0, columnspan=6, sticky="nsew")
            header_frame.columnconfigure(0, weight=1)

            tk.Label(header_frame, textvariable=criterion_label_var, bg="#DDDDDD", font=("Segoe UI", 10, "bold"), padx=8, pady=6).grid(row=0, column=0, sticky="nsew")

            override_var = tk.StringVar(value="" if criterion.grade_override is None else str(criterion.grade_override))
            self._criterion_override_vars.append((override_var, criterion))
            ttk.Label(header_frame, text="Ajustement:").grid(row=0, column=1, sticky="e", padx=(8, 4))
            override_entry = ttk.Entry(header_frame, textvariable=override_var, width=8)
            override_entry.grid(row=0, column=2, sticky="e", padx=(0, 8))
            override_entry.bind("<KeyRelease>", self._make_criterion_override_handler(criterion, override_var))

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

    def _make_criterion_override_handler(self, criterion: Criterion, override_var: tk.StringVar) -> Callable[[tk.Event], None]:
        def handler(event: tk.Event | None = None) -> None:  # noqa: ARG001
            self._apply_criterion_override(criterion, override_var)

        return handler

    def _apply_criterion_override(self, criterion: Criterion, override_var: tk.StringVar) -> None:
        value = override_var.get().strip()
        if value == "":
            criterion.grade_override = None
            self.status_var.set("")
            self._refresh_grades()
            return
        try:
            parsed = float(value.replace(",", "."))
        except ValueError:
            self.status_var.set("Note invalide: entrez un nombre (ex: 12.5).")
            return
        if parsed < 0 or parsed > criterion.points():
            self.status_var.set(
                f"Note invalide: la note du critère doit être entre 0 et {criterion.points():.0f}."
            )
            return
        criterion.grade_override = parsed
        self.status_var.set("")
        self._refresh_grades()

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
        if self.rubric is None:
            return
        grid_grade = _safe_grid_grade(self.rubric)
        if grid_grade is None:
            self.grid_grade_var.set("Note (grille): —")
        else:
            self.grid_grade_var.set(f"Note (grille): {grid_grade:.0f} / 100")

        self._refresh_criterion_labels()

        final_grade = self.rubric.grade if self.rubric.grade is not None else grid_grade
        if final_grade is None:
            self.final_grade_var.set("Note finale: — / 100")
        else:
            self.final_grade_var.set(f"Note finale: {final_grade:.0f} / 100")

    def _on_override_change(self, event: tk.Event | None = None) -> None:  # noqa: ARG002
        if self.rubric is None:
            return
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

    def _on_student_selected(self, event: tk.Event) -> None:  # noqa: ARG002
        selected_stem = self.student_selector_var.get()
        for idx, path in enumerate(self.json_files):
            if path.stem == selected_stem:
                self._save_current()
                self._load_file(idx)
                self._rebuild_ui()
                break

    def _prev_student(self) -> None:
        if self.current_index > 0:
            self._save_current()
            self._load_file(self.current_index - 1)
            self._rebuild_ui()

    def _next_student(self) -> None:
        if self.current_index < len(self.json_files) - 1:
            self._save_current()
            self._load_file(self.current_index + 1)
            self._rebuild_ui()

    def _save_current(self) -> None:
        if self.comment_text is None or self.rubric is None:
            return
        comment = self.comment_text.get("1.0", "end").strip()
        self.rubric.comment = comment if comment else None
        self._on_override_change()
        for override_var, criterion in self._criterion_override_vars:
            self._apply_criterion_override(criterion, override_var)

        rubric_dict = self.rubric.to_dict()
        try:
            with open(self.current_path, "w", encoding="utf-8") as f:
                json.dump(rubric_dict, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            self.status_var.set(f"Erreur lors de la sauvegarde: {exc}")

    def _save_and_next(self) -> None:
        self._save_current()
        self.status_var.set("Sauvegarde réussie.")
        if self.current_index < len(self.json_files) - 1:
            self._next_student()
        else:
            self.status_var.set("Dernier étudiant. Sauvegarde réussie.")

    def _rebuild_ui(self) -> None:
        for widget in self.root.winfo_children():
            widget.destroy()
        self._indicator_cells = []
        self._criterion_override_vars = []
        self._criterion_label_vars = []
        self._build_ui()

    def _refresh_criterion_labels(self) -> None:
        for label_var, criterion in self._criterion_label_vars:
            indicators_grade = _safe_criterion_indicators_grade(criterion)
            indicators_text = "—" if indicators_grade is None else f"{indicators_grade:.0f} / {criterion.points():.0f}"
            label_var.set(f"{criterion.label}  —  Note (indicateurs) : {indicators_text}")


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


def _safe_criterion_indicators_grade(criterion: Criterion) -> float | None:
    try:
        return sum(indicator.grade() for indicator in criterion.indicators)
    except ValueError:
        return None
