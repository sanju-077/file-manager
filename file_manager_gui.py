from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QInputDialog, QMessageBox
)
import sys
from main import FileManager  # Assumes your FileManager class is in main.py

class FileManagerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = FileManager()
        self.setWindowTitle("File Management Automation Tool")
        self.setGeometry(100, 100, 400, 200)
        layout = QVBoxLayout()

        self.rename_btn = QPushButton("Bulk Rename Files")
        self.rename_btn.clicked.connect(self.bulk_rename)
        layout.addWidget(self.rename_btn)

        self.sort_btn = QPushButton("Sort Files into Categories")
        self.sort_btn.clicked.connect(self.sort_files)
        layout.addWidget(self.sort_btn)

        self.dup_btn = QPushButton("Find Duplicate Files")
        self.dup_btn.clicked.connect(self.find_duplicates)
        layout.addWidget(self.dup_btn)

        self.remove_dup_btn = QPushButton("Remove Duplicate Files")
        self.remove_dup_btn.clicked.connect(self.remove_duplicates)
        layout.addWidget(self.remove_dup_btn)

        self.setLayout(layout)

    def bulk_rename(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not directory:
            return
        pattern, ok1 = QInputDialog.getText(self, "Pattern", "Enter pattern to replace:")
        if not ok1:
            return
        replacement, ok2 = QInputDialog.getText(self, "Replacement", "Enter replacement text:")
        if not ok2:
            return
        use_regex, ok3 = QInputDialog.getItem(self, "Regex", "Use regex matching?", ["No", "Yes"], 0, False)
        self.manager.bulk_rename(directory, pattern, replacement, use_regex == "Yes")
        QMessageBox.information(self, "Bulk Rename", "\n".join(self.manager.report))

    def sort_files(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not directory:
            return
        self.manager.sort_files(directory)
        QMessageBox.information(self, "Sort Files", "\n".join(self.manager.report))

    def find_duplicates(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not directory:
            return
        self.manager.find_duplicates(directory, remove_duplicates=False)
        QMessageBox.information(self, "Find Duplicates", "\n".join(self.manager.report))

    def remove_duplicates(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not directory:
            return
        reply = QMessageBox.question(
            self, "Remove Duplicates",
            "This will permanently delete duplicate files. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.manager.find_duplicates(directory, remove_duplicates=True)
            QMessageBox.information(self, "Remove Duplicates", "\n".join(self.manager.report))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManagerGUI()
    window.show()
    sys.exit(app.exec())