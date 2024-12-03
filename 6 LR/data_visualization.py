import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel,
    QComboBox, QFileDialog, QLineEdit, QHBoxLayout, QTableWidget, QTableWidgetItem
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class DataVisualizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data = None
        self.init_ui()

    def init_ui(self):
        # Настройка интерфейса
        self.setWindowTitle("Визуализация данных")
        self.setGeometry(100, 100, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Кнопка загрузки данных
        self.load_button = QPushButton("Загрузить CSV")
        self.load_button.clicked.connect(self.load_data)
        layout.addWidget(self.load_button)

        # Таблица для отображения статистики
        self.stats_table = QTableWidget()
        layout.addWidget(self.stats_table)

        # Выпадающий список выбора типа графика
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Линейный график", "Гистограмма", "Круговая диаграмма"])
        layout.addWidget(self.chart_type_combo)

        # Область отображения графика
        self.canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.canvas)

        # Поля для добавления данных
        add_data_layout = QHBoxLayout()
        self.data_input = QLineEdit()
        self.data_input.setPlaceholderText("Введите строку в формате: Date,Value1,Value2,Category")
        self.add_data_button = QPushButton("Добавить данные")
        self.add_data_button.clicked.connect(self.add_data)
        add_data_layout.addWidget(self.data_input)
        add_data_layout.addWidget(self.add_data_button)
        layout.addLayout(add_data_layout)

        # Кнопка построения графика
        self.plot_button = QPushButton("Построить график")
        self.plot_button.clicked.connect(self.plot_data)
        layout.addWidget(self.plot_button)

    def load_data(self):
        # Загрузка данных из CSV
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            self.data = pd.read_csv(file_path)
            self.update_statistics()

    def update_statistics(self):
        if self.data is not None:
            numeric_data = self.data.select_dtypes(include=["number"])  # Только числовые данные
            stats = {
                "Параметр": ["Минимум", "Максимум", "Среднее", "Медиана"],
            }
            for col in numeric_data.columns:
                stats[col] = [
                    numeric_data[col].min(),
                    numeric_data[col].max(),
                    numeric_data[col].mean(),
                    numeric_data[col].median(),
                ]

            # Обновление таблицы
            self.stats_table.setRowCount(len(stats["Параметр"]))
            self.stats_table.setColumnCount(len(stats))
            self.stats_table.setHorizontalHeaderLabels(stats.keys())

            # Заполнение таблицы
            for row_idx, param in enumerate(stats["Параметр"]):
                self.stats_table.setItem(row_idx, 0, QTableWidgetItem(param))
                for col_idx, col_name in enumerate(numeric_data.columns, start=1):
                    value = stats[col_name][row_idx]
                    self.stats_table.setItem(row_idx, col_idx, QTableWidgetItem(
                        f"{value:.2f}" if isinstance(value, float) else str(value)))

    def plot_data(self):
        if self.data is not None:
            plt.clf()  # Полное очищение текущей фигуры
            chart_type = self.chart_type_combo.currentText()

            if chart_type == "Линейный график":
                if "Date" in self.data.columns and "Value1" in self.data.columns:
                    plt.plot(self.data["Date"], self.data["Value1"], label="Value1")
                    plt.xlabel("Date")
                    plt.ylabel("Value1")
                    plt.title("Линейный график")
                    plt.legend()
                else:
                    self.stats_label.setText("Нужные столбцы не найдены: Date, Value1")

            elif chart_type == "Гистограмма":
                if "Date" in self.data.columns and "Value2" in self.data.columns:
                    plt.bar(self.data["Date"], self.data["Value2"], color="orange")
                    plt.xlabel("Date")
                    plt.ylabel("Value2")
                    plt.title("Гистограмма")
                else:
                    self.stats_label.setText("Нужные столбцы не найдены: Date, Value2")

            elif chart_type == "Круговая диаграмма":
                if "Category" in self.data.columns:
                    category_counts = self.data["Category"].value_counts()
                    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%')
                    plt.title("Круговая диаграмма")
                else:
                    self.stats_label.setText("Нужный столбец не найден: Category")

            self.canvas.draw()

    def add_data(self):
        # Добавление новой строки данных
        if self.data is not None:
            new_row = self.data_input.text().split(",")
            if len(new_row) == len(self.data.columns):
                new_data = pd.DataFrame([new_row], columns=self.data.columns)
                self.data = pd.concat([self.data, new_data], ignore_index=True)
                self.update_statistics()
            else:
                self.stats_label.setText("Неверный формат данных для добавления!")


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = DataVisualizationApp()
    main_window.show()
    sys.exit(app.exec_())
