import sys
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget,
    QFileDialog, QTableWidget, QTableWidgetItem, QLabel, QComboBox,
    QLineEdit, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class DataApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data = None

    def initUI(self):
        self.setWindowTitle("Data Visualization App")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Кнопка загрузки данных
        self.load_button = QPushButton("Загрузить данные")
        self.load_button.clicked.connect(self.load_data)
        layout.addWidget(self.load_button)

        # Поле для отображения таблицы статистики
        self.stats_table = QTableWidget()
        layout.addWidget(self.stats_table)

        # Выбор типа графика
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Линейный график", "Гистограмма", "Круговая диаграмма"])
        self.graph_type_combo.currentIndexChanged.connect(self.toggle_input_fields)
        self.graph_type_combo.currentIndexChanged.connect(self.update_graph)
        layout.addWidget(self.graph_type_combo)

        # Поле для отображения графика
        self.figure_canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.figure_canvas)

        # Поле для добавления данных
        add_data_layout = QHBoxLayout()
        self.add_date_field = QLineEdit()
        self.add_date_field.setPlaceholderText("Дата (YYYY-MM-DD)")
        add_data_layout.addWidget(self.add_date_field)

        self.add_value1_field = QLineEdit()
        self.add_value1_field.setPlaceholderText("Value1")
        add_data_layout.addWidget(self.add_value1_field)

        self.add_value2_field = QLineEdit()
        self.add_value2_field.setPlaceholderText("Value2")
        add_data_layout.addWidget(self.add_value2_field)

        self.add_category_field = QLineEdit()
        self.add_category_field.setPlaceholderText("Category")
        add_data_layout.addWidget(self.add_category_field)

        self.add_button = QPushButton("Добавить данные")
        self.add_button.clicked.connect(self.add_data)
        add_data_layout.addWidget(self.add_button)
        layout.addLayout(add_data_layout)

        # Скрытие полей по умолчанию
        self.add_date_field.setVisible(False)
        self.add_value1_field.setVisible(False)
        self.add_value2_field.setVisible(False)
        self.add_category_field.setVisible(False)

        central_widget.setLayout(layout)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            self.data = pd.read_csv(file_path)
            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')
            self.display_stats()
            self.update_graph()
            self.toggle_input_fields()

    def display_stats(self):
        if self.data is not None:
            numeric_data = self.data.select_dtypes(include=['number'])
            stats = pd.DataFrame({
                "Минимум": numeric_data.min(),
                "Максимум": numeric_data.max(),
            })
            row_count, column_count = len(self.data), len(self.data.columns)
            self.stats_table.setRowCount(stats.shape[0] + 1)
            self.stats_table.setColumnCount(stats.shape[1])
            self.stats_table.setHorizontalHeaderLabels(stats.columns)
            self.stats_table.setVerticalHeaderLabels(list(stats.index.astype(str)) + ["Общая информация"])
            
            for i in range(stats.shape[0]):
                for j in range(stats.shape[1]):
                    self.stats_table.setItem(i, j, QTableWidgetItem(str(round(stats.iloc[i, j], 2))))

            # Добавление общей информации
            info_texts = [
                f"Строк: {row_count}",
                f"Столбцов: {column_count}"
            ]
            self.stats_table.setItem(stats.shape[0], 0, QTableWidgetItem(", ".join(info_texts)))
            self.stats_table.resizeColumnsToContents()

    def toggle_input_fields(self):
        graph_type = self.graph_type_combo.currentText()
        self.add_date_field.setVisible(graph_type in ["Линейный график", "Гистограмма"])
        self.add_value1_field.setVisible(graph_type == "Линейный график")
        self.add_value2_field.setVisible(graph_type == "Гистограмма")
        self.add_category_field.setVisible(graph_type == "Круговая диаграмма")

    def add_data(self):
        graph_type = self.graph_type_combo.currentText()
        if graph_type == "Линейный график":
            date = self.add_date_field.text()
            value1 = self.add_value1_field.text()
            if date and value1:
                self.data = pd.concat([self.data, pd.DataFrame({"Date": [date], "Value1": [float(value1)]})],
                                      ignore_index=True)
        elif graph_type == "Гистограмма":
            date = self.add_date_field.text()
            value2 = self.add_value2_field.text()
            if date and value2:
                self.data = pd.concat([self.data, pd.DataFrame({"Date": [date], "Value2": [float(value2)]})],
                                      ignore_index=True)
        elif graph_type == "Круговая диаграмма":
            category = self.add_category_field.text()
            if category:
                self.data = pd.concat([self.data, pd.DataFrame({"Category": [category]})], ignore_index=True)

        if 'Date' in self.data.columns:
            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')

        self.update_graph()

    def update_graph(self):
        self.figure_canvas.figure.clear()
        ax = self.figure_canvas.figure.add_subplot(111)
        graph_type = self.graph_type_combo.currentText()

        if graph_type == "Линейный график" and "Date" in self.data.columns and "Value1" in self.data.columns:
            self.data = self.data.sort_values(by="Date")
            ax.plot(self.data["Date"], self.data["Value1"])
            ax.set_xlabel("Дата")
            ax.set_ylabel("Value1")
            ax.tick_params(axis='x', rotation=20)
        elif graph_type == "Гистограмма" and "Date" in self.data.columns and "Value2" in self.data.columns:
            self.data = self.data.sort_values(by="Date")
            ax.bar(self.data["Date"], self.data["Value2"])
            ax.set_xlabel("Дата")
            ax.set_ylabel("Value2")
            ax.tick_params(axis='x', rotation=20)
        elif graph_type == "Круговая диаграмма" and "Category" in self.data.columns:
            category_counts = self.data["Category"].value_counts()
            ax.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%")

        self.figure_canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = DataApp()
    main.show()
    sys.exit(app.exec_())
