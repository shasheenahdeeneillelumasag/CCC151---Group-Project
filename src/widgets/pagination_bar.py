from PyQt6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal


class PaginationBar(QFrame):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._page = 0
        self._total_items = 0
        self._page_size = 10

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        self.prev_btn = QPushButton("Prev")
        self.prev_btn.setFixedSize(60, 28)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background: #E3F5EE; color: #0D6B52; font-size: 11px;
                font-weight: bold; border: none; border-radius: 6px;
            }
            QPushButton:hover { background: #C8E9DB; }
            QPushButton:disabled { background: #F0F0F0; color: #AAA; }
        """)
        self.prev_btn.clicked.connect(self._prev)

        self.page_label = QLabel("Page 0 of 0")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.page_label.setStyleSheet("font-size: 11px; color: #546860;")

        self.next_btn = QPushButton("Next")
        self.next_btn.setFixedSize(60, 28)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: #E3F5EE; color: #0D6B52; font-size: 11px;
                font-weight: bold; border: none; border-radius: 6px;
            }
            QPushButton:hover { background: #C8E9DB; }
            QPushButton:disabled { background: #F0F0F0; color: #AAA; }
        """)
        self.next_btn.clicked.connect(self._next)

        layout.addStretch()
        layout.addWidget(self.prev_btn)
        layout.addWidget(self.page_label)
        layout.addWidget(self.next_btn)
        layout.addStretch()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.hide()

    def set_total_items(self, total: int, page_size: int = 10):
        self._total_items = total
        self._page_size = page_size
        self._page = 0
        self._update()
        self.setVisible(total > page_size)

    def _total_pages(self) -> int:
        if self._total_items <= 0:
            return 0
        return (self._total_items - 1) // self._page_size + 1

    def _update(self):
        total = self._total_pages()
        self.page_label.setText(f"Page {self._page + 1} of {total}")
        self.prev_btn.setEnabled(self._page > 0)
        self.next_btn.setEnabled(self._page < total - 1)

    def _prev(self):
        if self._page > 0:
            self._page -= 1
            self._update()
            self.page_changed.emit(self._page)

    def _next(self):
        total = self._total_pages()
        if self._page < total - 1:
            self._page += 1
            self._update()
            self.page_changed.emit(self._page)

    def current_page(self) -> int:
        return self._page

    def page_size(self) -> int:
        return self._page_size

    def reset(self):
        self._page = 0
        self.hide()
