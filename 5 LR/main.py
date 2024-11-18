import sys
import sqlite3
import asyncio
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTableView, QLineEdit, QPushButton, QVBoxLayout,
    QWidget, QMessageBox, QDialog, QFormLayout, QDialogButtonBox, QHBoxLayout, QProgressBar
)
import requests


class DataLoader:
    async def fetch_data(self, url):
        try:
            print(f"Запрос данных с {url}...")
            response = await asyncio.to_thread(requests.get, url)
            response.raise_for_status()  # Это поднимет исключение, если запрос не удался
            data = response.json()
            print(f"Получено {len(data)} записей с сервера.")
            return data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return []
        except Exception as e:
            print(f"Ошибка: {e}")
            return []


class DataLoadThread(QThread):
    data_loaded = pyqtSignal(list)

    def run(self):
        print("Запуск потока загрузки данных...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Получаем данные с сервера
        data = loop.run_until_complete(DataLoader().fetch_data("https://jsonplaceholder.typicode.com/posts"))

        if data:
            print("Данные успешно загружены, передача в основной поток...")
            self.data_loaded.emit(data)
        else:
            print("Не удалось загрузить данные.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Редактор базы данных")
        self.setGeometry(100, 100, 1270, 720)
        self.setWindowIcon(QIcon("db-file.png"))

        # Подключение к бд
        db_path = "../3 LR/posts.db"
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_path)

        if not self.db.open():
            QMessageBox.critical(self, "Ошибка базы данных",
                                 f"Не удается подключиться к базе данных: {self.db.lastError().text()}")
            sys.exit(1)

        # интерфейс
        self.table_view = QTableView()
        self.model = QSqlTableModel()
        self.model.setTable("posts")
        self.model.select()
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "ID пользователя")
        self.model.setHeaderData(2, Qt.Horizontal, "Название")
        self.model.setHeaderData(3, Qt.Horizontal, "Текст")
        self.table_view.setModel(self.model)  # привязка модели к таблице

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск по названию")

        # строка поиска
        self.search_bar.setFixedWidth(425)
        self.search_bar.setFixedHeight(25)

        self.search_bar.textChanged.connect(self.search)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_data)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.open_add_dialog)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_record)

        self.load_data_button = QPushButton("Загрузить данные")
        self.load_data_button.clicked.connect(self.load_data)

        # Добавление прогресс-бара для загрузки данных
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout = QVBoxLayout()

        layout.addWidget(self.search_bar)
        layout.addWidget(self.table_view)
        layout.addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.load_data_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.setStyleSheet("""
            QPushButton {
                background-color: #005EB8;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #007FFF;
            }
            QPushButton:pressed {
                background-color: #003D80;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 22px 0 22px 0;
            }
            QScrollBar::handle:vertical {
                background: #005EB8;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def search(self):
        search_text = self.search_bar.text()
        filter_str = f"title LIKE '%{search_text}%'"
        self.model.setFilter(filter_str)

    def refresh_data(self):
        self.model.setFilter("")
        self.model.select()

    def open_add_dialog(self):
        dialog = AddRecordDialog(self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_data()

    def delete_record(self):
        selected_indexes = self.table_view.selectionModel().selectedRows()
        if not selected_indexes:
            QMessageBox.warning(self, "Нет выбора", "Пожалуйста, выберите запись для удаления.")
            return

        confirmation = QMessageBox.question(self, "Подтвердите удаление",
                                            "Вы уверены, что хотите удалить выбранную запись?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            for index in selected_indexes:
                self.model.removeRow(index.row())
            self.model.submitAll()
            self.refresh_data()

    def load_data(self):
        print("Нажата кнопка загрузки данных.")
        self.progress_bar.setValue(0)
        self.load_thread = DataLoadThread()
        self.load_thread.data_loaded.connect(self.on_data_loaded)
        self.load_thread.start()

    def on_data_loaded(self, data):
        print(f"Данные получены: {len(data)} записей.")
        if data:
            self.save_data_to_db(data)

    def save_data_to_db(self, data):
        print("Сохранение данных в базу...")
        try:
            conn = sqlite3.connect("../3 LR/posts.db")
            cursor = conn.cursor()
            for post in data:
                cursor.execute("INSERT INTO posts (user_id, title, body) VALUES (?, ?, ?)",
                               (post["userId"], post["title"], post["body"]))
            conn.commit()
            conn.close()
            print("Данные успешно сохранены в базе данных.")
            self.refresh_data()
            self.progress_bar.setValue(100)
        except Exception as e:
            print(f"Ошибка при сохранении данных в базу: {e}")
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось сохранить данные: {e}")


class AddRecordDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Добавление записи")
        self.setFixedWidth(250)
        self.setFixedHeight(150)

        self.user_id_input = QLineEdit()
        self.title_input = QLineEdit()
        self.body_input = QLineEdit()

        form_layout = QFormLayout()
        form_layout.addRow("ID пользователя:", self.user_id_input)
        form_layout.addRow("Название:", self.title_input)
        form_layout.addRow("Текст:", self.body_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        user_id = self.user_id_input.text()
        title = self.title_input.text()
        body = self.body_input.text()

        if not user_id or not title or not body:
            QMessageBox.warning(self, "Ошибка ввода", "Все поля должны быть заполнены.")
            return

        query = QSqlDatabase.database().exec(
            f"INSERT INTO posts (user_id, title, body) VALUES ({user_id}, '{title}', '{body}')")
        if query.lastError().isValid():
            QMessageBox.critical(self, "Ошибка базы данных", f"Не удалось добавить запись: {query.lastError().text()}")
        else:
            super().accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
