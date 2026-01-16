import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget,
    QMenuBar, QMenu, QMessageBox, QFileDialog, QTabWidget, QPushButton, QHBoxLayout
)
from PyQt6.QtGui import QAction, QFont, QKeySequence
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)
        self.setStyleSheet("""
            background: white;
            border-top-left-radius: 16px;
            border-top-right-radius: 16px;
        """)

        title_label = QPushButton("Elegant Notepad")
        title_label.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #5a5a5a;
                font-weight: bold;
                text-align: left;
                padding-left: 8px;
            }
        """)
        title_label.setEnabled(False)

        self.min_btn = QPushButton("–")
        self.close_btn = QPushButton("✕")

        for btn in [self.min_btn, self.close_btn]:
            btn.setFixedSize(45, 40)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 18px;
                    color: #777;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                }
            """)

        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.close_btn.clicked.connect(self.parent.close)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 10, 0)
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)


class TabTextEdit(QWidget):
    tabTextChanged = pyqtSignal(object, str)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Segoe UI", 11))
        self.text_edit.textChanged.connect(self.on_text_changed)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: none;
                background: transparent;
                color: #222;
                selection-background-color: #cce5ff;
                selection-color: #000;
            }
            QScrollBar:vertical {
                background: #f5f5f5;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c5c5c5;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.text_edit)

        self.file_path = None
        self.is_modified = False

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            self.tabTextChanged.emit(self, self.get_title())

    def get_title(self):
        name = os.path.basename(self.file_path) if self.file_path else "Untitled"
        return f"{name}*" if self.is_modified else name

    def set_content(self, text, path=None):
        self.text_edit.setPlainText(text)
        self.file_path = path
        self.is_modified = False
        self.tabTextChanged.emit(self, self.get_title())

    def get_content(self):
        return self.text_edit.toPlainText()


class ElegantNotepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elegant Notepad")
        self.setGeometry(100, 100, 920, 660)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        central = QWidget()
        central.setStyleSheet("background: white; border-radius: 16px;")
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; top: -1px; }
            QTabBar::tab {
                background: #f8f8f8;
                padding: 8px 20px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                color: #444;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
            }
            QTabBar::tab:!selected {
                background: #f0f0f0;
            }
        """)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(32, 32)
        add_btn.clicked.connect(self.add_new_tab)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #e8e8e8;
                border: none;
                border-radius: 16px;
                font-size: 18px;
                color: #666;
            }
            QPushButton:hover {
                background: #dcdcdc;
            }
        """)

        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(12, 6, 12, 6)
        tab_layout.addWidget(self.tabs)
        tab_layout.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addLayout(tab_layout)
        self.setCentralWidget(central)

        # === МЕНЮ "ФАЙЛ" ===
        menubar = QMenuBar()
        menubar.setStyleSheet("background: transparent; color: #555; font-family: 'Segoe UI'; font-size: 10pt;")
        
        file_menu = QMenu("Файл", self)

        new_action = QAction("Новый", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.add_new_tab)

        open_action = QAction("Открыть...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)

        save_action = QAction("Сохранить", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_current)

        save_as_action = QAction("Сохранить как...", self)
        save_as_action.triggered.connect(self.save_current_as)

        close_tab_action = QAction("Закрыть вкладку", self)
        close_tab_action.setShortcut("Ctrl+W")
        close_tab_action.triggered.connect(self.close_current_tab)

        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(close_tab_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        menubar.addMenu(file_menu)
        self.setMenuBar(menubar)

        self.add_new_tab()

        # Анимация появления
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(400)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        start = QRect(self.x() + self.width() // 2, self.y() + self.height() // 2, 0, 0)
        end = QRect(self.x(), self.y(), self.width(), self.height())
        self.setGeometry(start)
        self.show()
        self.anim.setStartValue(start)
        self.anim.setEndValue(end)
        self.anim.start()

        self.drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self.drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def add_new_tab(self):
        editor = TabTextEdit()
        editor.tabTextChanged.connect(self.update_title)
        idx = self.tabs.addTab(editor, "Untitled")
        self.tabs.setCurrentIndex(idx)

    def update_title(self, editor, title):
        idx = self.tabs.indexOf(editor)
        if idx >= 0:
            self.tabs.setTabText(idx, title)

    def close_current_tab(self):
        idx = self.tabs.currentIndex()
        if idx >= 0:
            self.close_tab(idx)

    def close_tab(self, index):
        if self.tabs.count() <= 1:
            return
        widget = self.tabs.widget(index)
        if isinstance(widget, TabTextEdit) and widget.is_modified:
            res = QMessageBox.question(
                self, "Сохранить изменения?",
                f"Документ '{widget.get_title()}' содержит несохранённые изменения. Сохранить перед закрытием?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            if res == QMessageBox.StandardButton.Yes:
                self.save_tab(widget)
                if widget.is_modified:
                    return
            elif res == QMessageBox.StandardButton.Cancel:
                return
        self.tabs.removeTab(index)
        widget.deleteLater()

    def current_editor(self):
        w = self.tabs.currentWidget()
        return w if isinstance(w, TabTextEdit) else None

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Текстовые файлы (*.txt)")
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            editor = TabTextEdit()
            editor.set_content(content, path)
            editor.tabTextChanged.connect(self.update_title)
            idx = self.tabs.addTab(editor, editor.get_title())
            self.tabs.setCurrentIndex(idx)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл:\n{e}")

    def save_current(self):
        editor = self.current_editor()
        if editor:
            self.save_tab(editor)

    def save_current_as(self):
        editor = self.current_editor()
        if editor:
            self.save_as(editor)

    def save_tab(self, editor):
        if editor.file_path:
            try:
                with open(editor.file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.get_content())
                editor.is_modified = False
                self.update_title(editor, editor.get_title())
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")
        else:
            self.save_as(editor)

    def save_as(self, editor):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить как", "", "Текстовые файлы (*.txt)")
        if path:
            if not path.lower().endswith('.txt'):
                path += '.txt'
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(editor.get_content())
                editor.file_path = path
                editor.is_modified = False
                self.update_title(editor, editor.get_title())
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ElegantNotepad()
    sys.exit(app.exec())