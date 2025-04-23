import sys
from func import *
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QLabel, 
                                QComboBox, QTableWidget, QTableWidgetItem, QTableView, QHeaderView, QStyle)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Stocks App")
        self.setFixedWidth(900)
        self.setFixedHeight(600)

        dow_ticker = QLabel()
        nyse_ticker = QLabel()
        nasdaq_ticker = QLabel() 

        dow_info = do_everything(dow)
        nyse_info = do_everything(nyse)
        nasdaq_info = do_everything(nasdaq)

        dow_ticker.setText(f"{dow_info[0]} \n{dow_info[2]} \n{dow_info[3]} "+ f"{dow_info[4]}")
        nyse_ticker.setText(f"{nyse_info[0]} \n{nyse_info[2]} \n{nyse_info[3]} "+ f"{nyse_info[4]}")
        nasdaq_ticker.setText(f"{nasdaq_info[0]} \n{nasdaq_info[2]} \n{nasdaq_info[3]} "+ f"{nasdaq_info[4]}")

        self.search_bar = QLineEdit(placeholderText="Search stocks, ETFs or mutual funds")
        self.search_bar.returnPressed.connect(self.search_for_stocks)

        self.options = QComboBox()
        self.options.addItems(['Stocks', 'ETFs', 'Mutual Funds'])
        print(self.options.currentText())

        self.default_tickers = QHBoxLayout()
        self.default_tickers.addWidget(dow_ticker)
        self.default_tickers.addWidget(nyse_ticker)
        self.default_tickers.addWidget(nasdaq_ticker)

        self.search_line = QHBoxLayout()
        self.search_line.addWidget(self.search_bar)
        self.search_line.addWidget(self.options)

        self.search_results = QTableWidget()
        self.search_results.setColumnCount(6)
        self.search_results.setRowCount(25)
        self.search_results.verticalHeader().setVisible(False)
        self.search_results.setHorizontalHeaderLabels(['Symbol', 'Name','Last Price', 'Category', 'Type', 'Exchange'])
        self.search_header = self.search_results.horizontalHeader()
        self.search_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        

        vbox = QVBoxLayout()

        vbox.addLayout(self.default_tickers)
        vbox.addLayout(self.search_line)
        vbox.addWidget(self.search_results)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    def search_for_stocks(self):
        url = self.search_bar.text()
        
        if self.options.currentText() == "Stocks":
            search = f"https://finance.yahoo.com/lookup/equity/?s={url}"

        if self.options.currentText() == "ETFs":
            search = f"https://finance.yahoo.com/lookup/etfs/?s={url}"

        if self.options.currentText() == "Mutual Funds":
            search = f"https://finance.yahoo.com/lookup/mutualfund/?s={url}"
        
        page = requests.get(search, headers=headers)

        soup = BeautifulSoup(page.content, "html.parser")

        #main body we're looking at
        results = soup.find("tbody")

        rows = list(results.find_all("tr"))

        for row in range(len(rows)):
            td = rows[row].find_all("td")
            for col in range(len(td)):
                text = td[col].get_text()
                item = QTableWidgetItem(text)
                self.search_results.setItem(row, col, item)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()