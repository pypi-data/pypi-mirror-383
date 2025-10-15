"""Widgets for selecting and filtering variables."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)

from .utils import _matches_terms, _parse_search_terms

class VariableRowWidget(QWidget):
    rename_requested = Signal(str, str)

    def __init__(self, varname, allow_rename=False, parent=None):
        super().__init__(parent)
        self._name = varname

        layout = QHBoxLayout(self)
        self.checkbox = QCheckBox()
        self.checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.input = QLineEdit()
        self.input.setFixedWidth(70)
        self.label = QLabel(varname)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.input)
        layout.addWidget(self.label)

        if allow_rename:
            self.rename_btn = QPushButton("Rename")
            self.rename_btn.setFixedWidth(70)
            self.rename_btn.clicked.connect(self._prompt_rename)
            layout.addWidget(self.rename_btn)

        layout.addStretch(1)
        layout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(layout)

    def _prompt_rename(self):
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Variable",
            "New variable name",
            text=self._name,
        )
        if ok and new_name and new_name != self._name:
            self.rename_requested.emit(self._name, new_name)

class VariableTab(QWidget):
    """VariableTab with search and select-all functionality."""
    checklist_updated = Signal()

    def __init__(self, label, variables, user_var_set=None, allow_rename=False, rename_callback=None):
        super().__init__()
        self.all_vars = sorted(list(variables))
        self.user_var_set = user_var_set or set()
        self.allow_rename = allow_rename
        self.rename_callback = rename_callback
        self.checkboxes = {}
        self.inputs = {}
        self._checked_state = {}
        self._input_state = {}
        layout = QVBoxLayout(self)
        # -- Search and Select All row --
        top_row = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search…")
        top_row.addWidget(self.search_box)
        self.select_all_btn = QPushButton("Select All")
        self.unselect_all_btn = QPushButton("Unselect All")

        for btn in (self.select_all_btn, self.unselect_all_btn):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(28)
            top_row.addWidget(btn)
        layout.addLayout(top_row)
        # -- Scrollable area for variable checkboxes --
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.inner = QWidget()
        self.inner.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.inner_layout = QVBoxLayout(self.inner)
        self._populate_checkboxes(self.all_vars)
        scroll.setWidget(self.inner)
        layout.addWidget(scroll)
        layout.setStretch(0, 0)
        layout.setStretch(1, 1)
        # Connections
        self.select_all_btn.clicked.connect(lambda: self.set_all(True))
        self.unselect_all_btn.clicked.connect(lambda: self.set_all(False))
        self.search_box.textChanged.connect(self._search_update)
    def _populate_checkboxes(self, vars_to_show):
        """Populate the scroll area with VariableRowWidget entries."""
        # Preserve existing states
        for var, cb in self.checkboxes.items():
            self._checked_state[var] = cb.isChecked()
            self._input_state[var] = self.inputs[var].text()

        # Clear layout
        for i in reversed(range(self.inner_layout.count())):
            widget = self.inner_layout.takeAt(i).widget()
            if widget:
                widget.deleteLater()
        self.checkboxes.clear()
        self.inputs.clear()

        for var in vars_to_show:
            row = VariableRowWidget(var, allow_rename=self.allow_rename)
            if var in self.user_var_set:
                row.label.setStyleSheet("color: #2277bb;")
            if self.allow_rename and self.rename_callback:
                row.rename_requested.connect(self.rename_callback)
            self.inner_layout.addWidget(row)
            self.checkboxes[var] = row.checkbox
            self.inputs[var] = row.input
            if var in self._checked_state:
                row.checkbox.setChecked(self._checked_state[var])
            if var in self._input_state:
                row.input.setText(self._input_state[var])

        self.inner_layout.addStretch()
        self.checklist_updated.emit()
    def _search_update(self, text):
        terms = _parse_search_terms(text)
        if not terms:
            vars_to_show = self.all_vars
        else:
            vars_to_show = [v for v in self.all_vars if _matches_terms(v, terms)]
        self._populate_checkboxes(vars_to_show)
    def selected_variables(self):
        return [var for var, cb in self.checkboxes.items() if cb.isChecked()]
    def set_all(self, value):
        for cb in self.checkboxes.values():
            cb.setChecked(value)

__all__ = ['VariableRowWidget', 'VariableTab']

