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
    async def fetch_data(self, url, progress_callback):
        try:
            print(f"Запрос данных с {url}...")
            await asyncio.sleep(2)
            response = await asyncio.to_thread(requests.get, url)
            response.raise_for_status()
            data = response.json()
            print(f"Получено {len(data)} записей с сервера.")
            progress_callback(50)
            return data
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при запросе: {e}")
            return []
        except Exception as e:
            print(f"Ошибка: {e}")
            return []


class DataSaveThread(QThread):
    progress_updated = pyqtSignal(int)
    save_finished = pyqtSignal(bool)
    all_data_exists = pyqtSignal()

    def __init__(self, data, db_path):
        super().__init__()
        self.data = data
        self.db_path = db_path

    def run(self):
        print("Сохранение данных в фоновом потоке...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()


            all_exist = True
            for post in self.data:
                cursor.execute("SELECT 1 FROM posts WHERE id = ?", (post["id"],))
                if not cursor.fetchone():
                    all_exist = False
                    break

            if all_exist:
                print("Все данные уже есть в базе. Сохранение не требуется.")
                self.all_data_exists.emit()
                conn.close()
                return


            for index, post in enumerate(self.data):
                cursor.execute("SELECT 1 FROM posts WHERE id = ?", (post["id"],))
                if cursor.fetchone():
                    continue

                cursor.execute(
                    "INSERT INTO posts (id, user_id, title, body) VALUES (?, ?, ?, ?)",
                    (post["id"], post["userId"], post["title"], post["body"])
                )
                conn.commit()


                progress = int((index + 1) / len(self.data) * 50) + 50
                self.progress_updated.emit(progress)

            conn.close()
            print("Данные успешно сохранены в базе данных.")
            self.save_finished.emit(True)
        except Exception as e:
            print(f"Ошибка при сохранении данных в базу: {e}")
            self.save_finished.emit(False)



class DataLoadThread(QThread):
    data_loaded = pyqtSignal(list)
    progress_updated = pyqtSignal(int)

    def run(self):
        print("Запуск потока загрузки данных...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        data = loop.run_until_complete(DataLoader().fetch_data(
            "https://jsonplaceholder.typicode.com/posts",
            self.progress_updated.emit
        ))
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


        db_path = "../3 LR/posts.db"
        self.db_path = db_path
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(db_path)

        if not self.db.open():
            QMessageBox.critical(self, "Ошибка базы данных",
                                 f"Не удается подключиться к базе данных: {self.db.lastError().text()}")
            sys.exit(1)


        self.table_view = QTableView()
        self.model = QSqlTableModel()
        self.model.setTable("posts")
        self.model.select()
        self.model.setHeaderData(0, Qt.Horizontal, "ID")
        self.model.setHeaderData(1, Qt.Horizontal, "ID пользователя")
        self.model.setHeaderData(2, Qt.Horizontal, "Название")
        self.model.setHeaderData(3, Qt.Horizontal, "Текст")
        self.table_view.setModel(self.model)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Поиск по названию")
        self.search_bar.textChanged.connect(self.search)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_data)

        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.open_add_dialog)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_record)

        self.load_data_button = QPushButton("Загрузить данные")
        self.load_data_button.clicked.connect(self.load_data)


        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)

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


        self.timer = QTimer()
        self.timer.timeout.connect(self.load_data)
        self.timer.start(60000)

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
        self.load_thread.progress_updated.connect(self.progress_bar.setValue)
        self.load_thread.data_loaded.connect(self.on_data_loaded)
        self.load_thread.start()

    def on_data_loaded(self, data):
        if data:
            self.save_data_in_background(data)

    def save_data_in_background(self, data):
        self.save_thread = DataSaveThread(data, self.db_path)
        self.save_thread.progress_updated.connect(self.progress_bar.setValue)
        self.save_thread.save_finished.connect(self.on_save_finished)
        self.save_thread.all_data_exists.connect(self.on_all_data_exists)  # Новый сигнал
        self.save_thread.start()

    def on_all_data_exists(self):
        print("Все данные уже есть в базе. Ничего не нужно сохранять.")
        QMessageBox.information(self, "Информация", "Все данные уже есть в базе.")

    def on_save_finished(self, success):
        if success:
            QMessageBox.information(self, "Успех", "Данные успешно загружены и сохранены!")
            self.refresh_data()
        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось сохранить данные в базу.")


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
