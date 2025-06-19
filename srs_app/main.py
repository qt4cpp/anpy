import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTextEdit, QDialog, QHBoxLayout, QMessageBox
)

from .srs import SRS, Card


class AddCardDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Add Card")
        self.question = QTextEdit()
        self.answer = QTextEdit()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Question"))
        layout.addWidget(self.question)
        layout.addWidget(QLabel("Answer"))
        layout.addWidget(self.answer)
        layout.addWidget(save_btn)
        self.setLayout(layout)

    def get_data(self) -> tuple[str, str]:
        return self.question.toPlainText(), self.answer.toPlainText()


class ReviewWidget(QWidget):
    def __init__(self, srs: SRS, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.srs = srs
        self.current: Card | None = None

        self.question = QLabel()
        self.answer = QLabel()
        self.answer.hide()

        self.show_answer_btn = QPushButton("Show Answer")
        self.correct_btn = QPushButton("Correct")
        self.wrong_btn = QPushButton("Wrong")

        self.show_answer_btn.clicked.connect(self.show_answer)
        self.correct_btn.clicked.connect(lambda: self.finish(True))
        self.wrong_btn.clicked.connect(lambda: self.finish(False))

        buttons = QHBoxLayout()
        buttons.addWidget(self.show_answer_btn)
        buttons.addWidget(self.correct_btn)
        buttons.addWidget(self.wrong_btn)

        layout = QVBoxLayout()
        layout.addWidget(self.question)
        layout.addWidget(self.answer)
        layout.addLayout(buttons)
        self.setLayout(layout)
        self.load_next()

    def load_next(self) -> None:
        card = self.srs.next_due()
        if not card:
            QMessageBox.information(self, "Done", "No cards due.")
            self.parent().setCurrentIndex(0)  # type: ignore[attr-defined]
            return
        self.current = card
        self.question.setText(card.question)
        self.answer.setText(card.answer)
        self.answer.hide()

    def show_answer(self) -> None:
        self.answer.show()

    def finish(self, correct: bool) -> None:
        if self.current:
            self.srs.update_card(self.current, correct)
        self.load_next()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.srs = SRS(Path("cards.json"))

        self.stack = QWidget()
        self.setCentralWidget(self.stack)
        self.layout = QVBoxLayout()
        self.stack.setLayout(self.layout)

        add_btn = QPushButton("Add Card")
        review_btn = QPushButton("Start Review")
        add_btn.clicked.connect(self.add_card)
        review_btn.clicked.connect(self.start_review)

        self.layout.addWidget(add_btn)
        self.layout.addWidget(review_btn)

    def add_card(self) -> None:
        dialog = AddCardDialog()
        if dialog.exec() == QDialog.Accepted:
            q, a = dialog.get_data()
            if q and a:
                self.srs.add_card(q, a)

    def start_review(self) -> None:
        review = ReviewWidget(self.srs, self.stack)
        # Replace layout
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.setParent(None)
        self.layout.addWidget(review)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
