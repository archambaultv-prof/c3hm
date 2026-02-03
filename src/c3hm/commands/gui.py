import contextlib
import json
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import ttk

from c3hm.data.rubric import Criterion, Indicator, Rubric

LEVELS = [
    ("Avancé", "#C8FFC8"),
    ("Acquis", "#F0FFB0"),
    ("Ça y est presque!", "#FFF8C2"),
    ("En apprentissage", "#FFE4C8"),
    ("Non démontré", "#FFC8C8"),
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
        self.grid_grade_label: ttk.Label | None = None
        self.final_grade_label: ttk.Label | None = None
        self.position_var = tk.StringVar(value=f"1 / {len(self.json_files)}")
        self.student_selector_var = tk.StringVar(value="")
        self._indicator_cells: list[list[tk.Button]] = []
        self._criterion_override_vars: list[tuple[tk.StringVar, Criterion]] = []
        self._criterion_label_vars: list[tuple[tk.StringVar, Criterion]] = []
        self._criterion_labels: list[tuple[tk.Label, Criterion]] = []
        self.rubric: Rubric = Rubric(course="", session="", evaluation="", grid=None)  # type: ignore
        self.current_path: Path = Path("")
        self.comment_text: tk.Text | None = None
        self.teammates_combo: ttk.Combobox | None = None
        self.teammates_combo_var: tk.StringVar = tk.StringVar()
        self.teammates_widgets_frame: ttk.Frame | None = None
        self.paned_window: ttk.PanedWindow | None = None
        self.teammates_frame: ttk.Frame | None = None
        self.teammates_header: ttk.Frame | None = None
        self.teammates_list_frame: ttk.Frame | None = None
        self.teammates_toggle_btn: ttk.Button | None = None
        self.teammates_sync_button: ttk.Button | None = None
        self._teammates_collapsed: bool = True
        self._teammates_pane_height: int | None = None
        self.all_students_names: list[str] = []
        self.all_students: list[tuple[str, Path]] = []
        self._load_all_students()
        self._load_file(0)
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self) -> None:
        self.root.mainloop()

    def _on_close(self) -> None:
        self._save_current()
        self.root.destroy()

    def _load_all_students(self) -> None:
        """Charge tous les étudiants depuis les fichiers JSON pour construire la liste des coéquipiers possibles."""
        self.all_students = []
        for json_file in self.json_files:
            try:
                with open(json_file, encoding="utf-8") as f:
                    data = json.load(f)
                rubric = Rubric.from_dict(data)
                if rubric.student:
                    self.all_students.append((rubric.student.fullname(surname_first=True), json_file))
            except Exception:
                print(f"Erreur lors du chargement du fichier {json_file} pour la liste des étudiants.")
        # Sort by surname (already surname_first format)
        self.all_students.sort(key=lambda x: x[0].lower())

    def _load_file(self, index: int) -> None:
        self.current_index = index
        self.current_path = self.json_files[index]
        with open(self.current_path, encoding="utf-8") as f:
            data = json.load(f)
        self.rubric = Rubric.from_dict(data)
        self.override_var.set("" if self.rubric.grade_override is None else str(self.rubric.grade_override))
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

        # Create PanedWindow for resizable sections
        self.paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill="both", expand=True, pady=(0, 8))
        self.paned_window.bind("<ButtonRelease-1>", lambda _event: self._store_teammates_pane_height())

        # Coéquipiers section
        self.teammates_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.teammates_frame, weight=0)

        self.teammates_header = ttk.Frame(self.teammates_frame)
        self.teammates_header.pack(fill="x", pady=(0, 4))

        self.teammates_toggle_btn = ttk.Button(
            self.teammates_header,
            text="Afficher coéquipiers",
            command=self._toggle_teammates_section,
        )
        self.teammates_toggle_btn.pack(side="left", padx=(0, 6))

        # Initialize all_students_names before creating combobox
        self.all_students_names = [
            fullname for fullname, _ in self.all_students
            if self.rubric.student is None or fullname != self.rubric.student.fullname(surname_first=True)
        ]

        ttk.Label(self.teammates_header, text="Ajouter:").pack(side="left", padx=(12, 4))

        self.teammates_combo_var = tk.StringVar()
        self.teammates_combo = ttk.Combobox(
            self.teammates_header,
            textvariable=self.teammates_combo_var,
            values=self.all_students_names,
            width=30,
            state="readonly"
        )
        self.teammates_combo.pack(side="left", padx=(0, 4))

        ttk.Button(
            self.teammates_header,
            text="Ajouter coéquipier",
            command=self._add_teammate_from_combo
        ).pack(side="left", padx=(0, 8))

        self.teammates_sync_button = ttk.Button(self.teammates_header, text="Synchroniser avec coéquipiers", command=self._sync_with_teammates)
        self.teammates_sync_button.pack(side="left", padx=(8, 0))

        self.teammates_list_frame = ttk.Frame(self.teammates_frame)
        self.teammates_list_frame.pack(fill="both", expand=True, padx=4, pady=4)

        # Create scrollable canvas for teammates
        teammates_canvas = tk.Canvas(self.teammates_list_frame, borderwidth=0, highlightthickness=0)
        teammates_scroll = ttk.Scrollbar(self.teammates_list_frame, orient="vertical", command=teammates_canvas.yview)
        self.teammates_widgets_frame = ttk.Frame(teammates_canvas)
        teammates_canvas.configure(yscrollcommand=teammates_scroll.set)

        teammates_canvas_window = teammates_canvas.create_window((0, 0), window=self.teammates_widgets_frame, anchor="nw")

        def _configure_teammates_scroll(event: tk.Event) -> None:  # noqa: ARG001
            teammates_canvas.configure(scrollregion=teammates_canvas.bbox("all"))

        def _resize_teammates_canvas(event: tk.Event) -> None:  # noqa: ARG001
            teammates_canvas.itemconfig(teammates_canvas_window, width=event.width)

        self.teammates_widgets_frame.bind("<Configure>", _configure_teammates_scroll)
        teammates_canvas.bind("<Configure>", _resize_teammates_canvas)

        # Enable mouse wheel scrolling
        def _on_teammates_mousewheel(event: tk.Event) -> None:
            teammates_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_teammates_mousewheel(event: tk.Event) -> None:  # noqa: ARG001
            teammates_canvas.bind_all("<MouseWheel>", _on_teammates_mousewheel)

        def _unbind_teammates_mousewheel(event: tk.Event) -> None:  # noqa: ARG001
            teammates_canvas.unbind_all("<MouseWheel>")

        teammates_canvas.bind("<Enter>", _bind_teammates_mousewheel)
        teammates_canvas.bind("<Leave>", _unbind_teammates_mousewheel)

        teammates_scroll.pack(side="right", fill="y")
        teammates_canvas.pack(side="left", fill="both", expand=True)

        # Populate teammates display
        self._refresh_teammates_display()

        # Apply saved teammates section state
        self._apply_teammates_state()

        self.grid_grade_label = ttk.Label(header, textvariable=self.grid_grade_var)
        self.grid_grade_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

        override_frame = ttk.Frame(header)
        override_frame.grid(row=1, column=1, sticky="e", pady=(4, 0))

        ttk.Label(override_frame, text="Note ajustée :").grid(row=0, column=0, sticky="e")
        override_entry = ttk.Entry(override_frame, textvariable=self.override_var, width=8)
        override_entry.grid(row=0, column=1, sticky="e", padx=(6, 0))

        header.columnconfigure(0, weight=1)
        header.columnconfigure(1, weight=0)

        override_entry.bind("<KeyRelease>", self._on_override_change)

        # Store final grade label for coloring
        self.final_grade_label = grade_label

        grid_container = ttk.Frame(self.paned_window)
        self.paned_window.add(grid_container, weight=1)

        canvas = tk.Canvas(grid_container, borderwidth=0, highlightthickness=0)
        v_scroll = ttk.Scrollbar(grid_container, orient="vertical", command=canvas.yview)
        h_scroll = ttk.Scrollbar(grid_container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side="right", fill="y")
        h_scroll.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        scroll_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def _configure_scroll_region(event: tk.Event) -> None:  # noqa: ARG001
            canvas.configure(scrollregion=canvas.bbox("all"))

        scroll_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _configure_scroll_region)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _bind_mousewheel(event: tk.Event) -> None:  # noqa: ARG001
            canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def _unbind_mousewheel(event: tk.Event) -> None:  # noqa: ARG001
            canvas.unbind_all("<MouseWheel>")

        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

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

        # Configure columns to expand with window but keep minimum size
        parent.columnconfigure(0, weight=0, minsize=220)  # Indicator label column
        for col_index in range(1, 6):
            parent.columnconfigure(col_index, weight=1, minsize=120)  # Level columns

        for col_index, (level_label, color) in enumerate(LEVELS, start=1):
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

            criterion_label_widget = tk.Label(header_frame, textvariable=criterion_label_var, bg="#DDDDDD", font=("Segoe UI", 10, "bold"), padx=8, pady=6)
            criterion_label_widget.grid(row=0, column=0, sticky="nsew")
            self._criterion_labels.append((criterion_label_widget, criterion))

            override_var = tk.StringVar(value="" if criterion.grade_override is None else str(criterion.grade_override))
            self._criterion_override_vars.append((override_var, criterion))
            ttk.Label(header_frame, text="Note ajustée :").grid(row=0, column=1, sticky="e", padx=(8, 4))
            override_entry = ttk.Entry(header_frame, textvariable=override_var, width=8)
            override_entry.grid(row=0, column=2, sticky="e", padx=(0, 8))
            override_entry.bind("<KeyRelease>", self._make_criterion_override_handler(criterion, override_var))

            row_index += 1

            for indicator in criterion.indicators:
                tk.Label(parent, text=indicator.label, bg="#FFFFFF", padx=8, pady=6, wraplength=220, justify="left", anchor="w").grid(row=row_index, column=0, sticky="nsew")
                row_cells: list[tk.Button] = []
                for level_index, (_, color) in enumerate(LEVELS):
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
                cell.configure(bg=LEVELS[idx][1], relief="solid", bd=2, highlightbackground=DEFAULT_BORDER)
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

        final_grade = self.rubric.grade_override if self.rubric.grade_override is not None else grid_grade
        if final_grade is None:
            self.final_grade_var.set("Note finale: — / 100")
        else:
            self.final_grade_var.set(f"Note finale: {final_grade:.0f} / 100")

        # Update colors based on grade_override
        if self.grid_grade_label:
            if self.rubric.grade_override is not None:
                self.grid_grade_label.configure(foreground="#FF8800")  # Warning orange
            else:
                self.grid_grade_label.configure(foreground="#000000")  # Default black

        if self.final_grade_label:
            if self.rubric.grade_override is not None:
                self.final_grade_label.configure(foreground="#FF8800")  # Warning orange
            else:
                self.final_grade_label.configure(foreground="#000000")  # Default black

    def _on_override_change(self, event: tk.Event | None = None) -> None:  # noqa: ARG002
        if self.rubric is None:
            return
        value = self.override_var.get().strip()
        if value == "":
            self.rubric.grade_override = None
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
        self.rubric.grade_override = parsed
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

        # Update teammates from rubric.student.teammates with symmetric relationship
        current_student_fullname = None
        old_teammates = []
        if self.rubric.student:
            current_student_fullname = self.rubric.student.fullname(surname_first=True)
            old_teammates = self.rubric.student.teammates.copy()

        if self.rubric.student:
            selected_teammates = self.rubric.student.teammates

            # Update symmetrically: ensure every teammate has the full group list
            group = [name for name in [current_student_fullname, *selected_teammates] if name]
            for teammate_name in selected_teammates:
                self._set_teammate_group(teammate_name, group)

            # Remove current student from teammates who are no longer selected
            for old_teammate in old_teammates:
                if old_teammate not in selected_teammates:
                    self._remove_teammate_symmetrically(old_teammate, current_student_fullname)

        rubric_dict = self.rubric.to_dict()
        try:
            with open(self.current_path, "w", encoding="utf-8") as f:
                json.dump(rubric_dict, f, ensure_ascii=False, indent=4)
        except OSError as exc:
            self.status_var.set(f"Erreur lors de la sauvegarde: {exc}")

    def _add_teammate_symmetrically(self, teammate_name: str, current_student_fullname: str | None) -> None:
        """Ajoute le student actuel à la liste des coéquipiers du coéquipier."""
        if not current_student_fullname:
            return

        teammate_path = None
        for fullname, path in self.all_students:
            if fullname == teammate_name:
                teammate_path = path
                break

        if not teammate_path or not teammate_path.exists():
            return

        try:
            with open(teammate_path, encoding="utf-8") as f:
                teammate_data = json.load(f)
            teammate_rubric = Rubric.from_dict(teammate_data)

            if teammate_rubric.student and current_student_fullname not in teammate_rubric.student.teammates:
                teammate_rubric.student.teammates.append(current_student_fullname)

                with open(teammate_path, "w", encoding="utf-8") as f:
                    json.dump(teammate_rubric.to_dict(), f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def _set_teammate_group(self, teammate_name: str, group: list[str]) -> None:
        """Assure que le coéquipier a la liste complète des autres membres du groupe."""
        teammate_path = None
        for fullname, path in self.all_students:
            if fullname == teammate_name:
                teammate_path = path
                break

        if not teammate_path or not teammate_path.exists():
            return

        try:
            with open(teammate_path, encoding="utf-8") as f:
                teammate_data = json.load(f)
            teammate_rubric = Rubric.from_dict(teammate_data)

            if teammate_rubric.student:
                teammate_rubric.student.teammates = [name for name in group if name != teammate_name]

                with open(teammate_path, "w", encoding="utf-8") as f:
                    json.dump(teammate_rubric.to_dict(), f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def _remove_teammate_symmetrically(self, teammate_name: str, current_student_fullname: str | None) -> None:
        """Retire le student actuel de la liste des coéquipiers du coéquipier."""
        if not current_student_fullname:
            return

        teammate_path = None
        for fullname, path in self.all_students:
            if fullname == teammate_name:
                teammate_path = path
                break

        if not teammate_path or not teammate_path.exists():
            return

        try:
            with open(teammate_path, encoding="utf-8") as f:
                teammate_data = json.load(f)
            teammate_rubric = Rubric.from_dict(teammate_data)

            if teammate_rubric.student and current_student_fullname in teammate_rubric.student.teammates:
                teammate_rubric.student.teammates.remove(current_student_fullname)

                with open(teammate_path, "w", encoding="utf-8") as f:
                    json.dump(teammate_rubric.to_dict(), f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def _refresh_teammates_display(self) -> None:
        """Affiche les coéquipiers actuellement sélectionnés."""
        if not self.teammates_widgets_frame:
            return

        # Clear existing widgets
        for widget in self.teammates_widgets_frame.winfo_children():
            widget.destroy()

        if not self.rubric.student or not self.rubric.student.teammates:
            ttk.Label(
                self.teammates_widgets_frame,
                text="Aucun coéquipier sélectionné",
                foreground="#888888"
            ).pack(pady=4)
            return

        # Display each teammate with a remove button
        for teammate_name in sorted(self.rubric.student.teammates):
            row_frame = ttk.Frame(self.teammates_widgets_frame)
            row_frame.pack(fill="x", pady=2)

            ttk.Label(row_frame, text=teammate_name).pack(side="left", padx=(4, 8))

            ttk.Button(
                row_frame,
                text="Retirer",
                command=lambda name=teammate_name: self._remove_teammate(name),
                width=8
            ).pack(side="right", padx=4)

    def _add_teammate_from_combo(self) -> None:
        """Ajoute le coéquipier sélectionné dans le combobox."""
        if not self.teammates_combo or not self.rubric.student:
            return

        teammate_name = self.teammates_combo_var.get().strip()
        if not teammate_name:
            self.status_var.set("Veuillez sélectionner un coéquipier.")
            return

        if teammate_name in self.rubric.student.teammates:
            self.status_var.set("Ce coéquipier est déjà dans la liste.")
            return

        self.rubric.student.teammates.append(teammate_name)
        self.teammates_combo_var.set("")
        self._refresh_teammates_display()
        self.status_var.set("")

    def _remove_teammate(self, teammate_name: str) -> None:
        """Retire un coéquipier de la liste."""
        if not self.rubric.student:
            return

        if teammate_name in self.rubric.student.teammates:
            self.rubric.student.teammates.remove(teammate_name)
            self._refresh_teammates_display()
            self.status_var.set("")

    def _store_teammates_pane_height(self) -> None:
        if self._teammates_collapsed or not self.paned_window:
            return
        if len(self.paned_window.panes()) > 1:
            self._teammates_pane_height = self.paned_window.sashpos(0)

    def _apply_teammates_state(self) -> None:
        # Update combobox values for current student
        if self.teammates_combo:
            self.all_students_names = [
                fullname for fullname, _ in self.all_students
                if self.rubric.student is None or fullname != self.rubric.student.fullname(surname_first=True)
            ]
            self.teammates_combo['values'] = self.all_students_names
        self._set_teammates_collapsed(self._teammates_collapsed)
        if not self._teammates_collapsed and self._teammates_pane_height is None:
            self.root.update_idletasks()
            if self.teammates_frame:
                height = self.teammates_frame.winfo_height()
                if height > 0:
                    self._teammates_pane_height = height
        if (
            not self._teammates_collapsed
            and self._teammates_pane_height
            and self.paned_window
            and len(self.paned_window.panes()) > 1
        ):
            target = self._teammates_pane_height
            paned = self.paned_window
            self.root.after(0, lambda: paned.sashpos(0, target))

    def _set_teammates_collapsed(self, collapsed: bool) -> None:
        self._teammates_collapsed = collapsed
        if not self.teammates_list_frame or not self.paned_window or not self.teammates_frame:
            return
        if collapsed:
            self.teammates_list_frame.pack_forget()
            if self.teammates_toggle_btn:
                self.teammates_toggle_btn.config(text="Afficher coéquipiers")
            # Hide all widgets in header except toggle button
            if self.teammates_header:
                for widget in self.teammates_header.winfo_children():
                    if widget != self.teammates_toggle_btn:
                        with contextlib.suppress(AttributeError):
                            widget.pack_forget()  # type: ignore
            self.root.update_idletasks()
            header_height = 0
            if self.teammates_header:
                header_height = self.teammates_header.winfo_reqheight()
            if len(self.paned_window.panes()) > 1:
                self.paned_window.sashpos(0, max(0, header_height + 6))
        else:
            if self.teammates_toggle_btn:
                self.teammates_toggle_btn.config(text="Masquer coéquipiers")
            # Re-pack widgets in correct order after toggle button
            if self.teammates_header:
                for widget in self.teammates_header.winfo_children():
                    if widget == self.teammates_toggle_btn:
                        continue
                    if isinstance(widget, ttk.Label):
                        widget.pack(side="left", padx=(12, 4))
                    elif isinstance(widget, ttk.Combobox):
                        widget.pack(side="left", padx=(0, 4))
                    elif isinstance(widget, ttk.Button):
                        if "Synchroniser" in widget.cget("text"):
                            widget.pack(side="left", padx=(8, 0))
                        else:
                            widget.pack(side="left", padx=(0, 8))
            self.teammates_list_frame.pack(fill="both", expand=True, padx=4, pady=4)
            self.root.update_idletasks()
            header_height = 0
            if self.teammates_header:
                header_height = self.teammates_header.winfo_reqheight()
            list_height = self.teammates_list_frame.winfo_reqheight()
            target_height = self._teammates_pane_height or max(0, header_height + list_height)
            if len(self.paned_window.panes()) > 1:
                self.paned_window.sashpos(0, target_height)

    def _toggle_teammates_section(self) -> None:
        self._set_teammates_collapsed(not self._teammates_collapsed)

    def _save_and_next(self) -> None:
        self._save_current()
        self.status_var.set("Sauvegarde réussie.")
        if self.current_index < len(self.json_files) - 1:
            self._next_student()
        else:
            self.status_var.set("Dernier étudiant. Sauvegarde réussie.")

    def _rebuild_ui(self) -> None:
        self._store_teammates_pane_height()
        for widget in self.root.winfo_children():
            widget.destroy()
        self._indicator_cells = []
        self._criterion_override_vars = []
        self._criterion_label_vars = []
        self._criterion_labels = []
        self.teammates_combo = None
        self.teammates_widgets_frame = None
        self.paned_window = None
        self.teammates_frame = None
        self.teammates_header = None
        self.teammates_list_frame = None
        self.teammates_toggle_btn = None
        self.teammates_sync_button = None
        self._build_ui()

    def _refresh_criterion_labels(self) -> None:
        for label_var, criterion in self._criterion_label_vars:
            indicators_grade = _safe_criterion_indicators_grade(criterion)
            indicators_text = "—" if indicators_grade is None else f"{indicators_grade:.0f} / {criterion.points():.0f}"
            label_var.set(f"{criterion.label}  —  Note (indicateurs) : {indicators_text}")

        # Update background colors based on grade_override
        for label_widget, criterion in self._criterion_labels:
            if criterion.grade_override is not None:
                label_widget.configure(bg="#FFEB99")  # Warning yellow
            else:
                label_widget.configure(bg="#DDDDDD")  # Default gray

    def _sync_with_teammates(self) -> None:
        """Synchronise la grille actuelle avec tous les coéquipiers sélectionnés."""
        if not self.rubric.student or not self.rubric.student.teammates:
            self.status_var.set("Aucun coéquipier sélectionné.")
            return

        # Save current first
        self._save_current()

        synced_count = 0
        for teammate_name in self.rubric.student.teammates:
            # Find the teammate's file
            teammate_path = None
            for fullname, path in self.all_students:
                if fullname == teammate_name:
                    teammate_path = path
                    break

            if not teammate_path or not teammate_path.exists():
                continue

            try:
                # Load teammate's rubric
                with open(teammate_path, encoding="utf-8") as f:
                    teammate_data = json.load(f)
                teammate_rubric = Rubric.from_dict(teammate_data)

                # Copy all grading info
                for i, criterion in enumerate(self.rubric.grid.criteria):
                    if i < len(teammate_rubric.grid.criteria):
                        teammate_criterion = teammate_rubric.grid.criteria[i]
                        teammate_criterion.grade_override = criterion.grade_override

                        for j, indicator in enumerate(criterion.indicators):
                            if j < len(teammate_criterion.indicators):
                                teammate_criterion.indicators[j].graded_level = indicator.graded_level

                # Copy comment and grade override
                teammate_rubric.comment = self.rubric.comment
                teammate_rubric.grade_override = self.rubric.grade_override

                # Save teammate's rubric
                with open(teammate_path, "w", encoding="utf-8") as f:
                    json.dump(teammate_rubric.to_dict(), f, ensure_ascii=False, indent=4)

                synced_count += 1
            except Exception as e:
                self.status_var.set(f"Erreur lors de la synchronisation avec {teammate_name}: {e}")
                return

        self.status_var.set(f"Synchronisé avec {synced_count} coéquipier(s).")


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
