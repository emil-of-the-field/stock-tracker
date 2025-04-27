import sys
import datetime
from func import *
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QLabel, 
                                QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Stocks App")
        self.setFixedWidth(900)
        self.setFixedHeight(600)

        timer = QTimer(self)
        current_date = datetime.date.today()
        if (current_date.isoweekday() != 6) or (current_date.isoweekday() != 7):
            timer.timeout.connect(self.update_tickers)
            timer.start(60000)

        self.dow_ticker = QLabel()
        self.nyse_ticker = QLabel()
        self.nasdaq_ticker = QLabel() 

        self.dow_info = do_everything(dow)
        self.nyse_info = do_everything(nyse)
        self.nasdaq_info = do_everything(nasdaq)

        self.dow_ticker.setText(f"{self.dow_info[0]} \n{self.dow_info[2]} \n{self.dow_info[3]} "+ f"{self.dow_info[4]}")
        self.nyse_ticker.setText(f"{self.nyse_info[0]} \n{self.nyse_info[2]} \n{self.nyse_info[3]} "+ f"{self.nyse_info[4]}")
        self.nasdaq_ticker.setText(f"{self.nasdaq_info[0]} \n{self.nasdaq_info[2]} \n{self.nasdaq_info[3]} "+ f"{self.nasdaq_info[4]}")

        portfolio = QPushButton("View/Create Portfolio")
        portfolio.clicked.connect(self.open_portfolio_window)
        self.p = None

        self.search_bar = QLineEdit(placeholderText="Search stocks, ETFs or mutual funds")
        self.search_bar.returnPressed.connect(self.search_for_stocks)

        self.options = QComboBox()
        self.options.addItems(['Stocks', 'ETFs', 'Mutual Funds'])


        self.default_tickers = QHBoxLayout()
        self.default_tickers.addWidget(self.dow_ticker)
        self.default_tickers.addWidget(self.nyse_ticker)
        self.default_tickers.addWidget(self.nasdaq_ticker)
        self.default_tickers.addWidget(portfolio)

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
        self.search_results.itemDoubleClicked.connect(self.open_stock_window)
        self.w = None


        

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
        
        headers = {'User-Agent' : random.choice(userAgents)}
        page = requests.get(search, headers=headers)

        soup = BeautifulSoup(page.content, "html.parser")

        #main body we're looking at
        results = soup.find("tbody")


        try:
            rows = list(results.find_all("tr"))
            for row in range(len(rows)):
                td = rows[row].find_all("td")
                for col in range(len(td)):
                    text = td[col].get_text()
                    item = QTableWidgetItem(text)
                    self.search_results.setItem(row, col, item)

        except AttributeError:
            msg = QMessageBox()
            msg.setText("No results found")
            msg.exec()


    def open_stock_window(self):
        row_num = self.search_results.currentRow()
        row_symbol = self.search_results.item(row_num,0).text()
        if self.w is None:
            self.w = StockWindow(row_symbol)
        self.w.show()



    def open_portfolio_window(self):
        if self.p is None:
            self.p = PortfolioWindow()
        self.p.show()

    def update_tickers(self):
        self.dow_ticker.setText('')
        self.nyse_ticker.setText('')
        self.nasdaq_ticker.setText('')

        self.dow_info = do_everything(dow)
        self.nyse_info = do_everything(nyse)
        self.nasdaq_info = do_everything(nasdaq)

        self.dow_ticker.setText(f"{self.dow_info[0]} \n{self.dow_info[2]} \n{self.dow_info[3]} "+ f"{self.dow_info[4]}")
        self.nyse_ticker.setText(f"{self.nyse_info[0]} \n{self.nyse_info[2]} \n{self.nyse_info[3]} "+ f"{self.nyse_info[4]}")
        self.nasdaq_ticker.setText(f"{self.nasdaq_info[0]} \n{self.nasdaq_info[2]} \n{self.nasdaq_info[3]} "+ f"{self.nasdaq_info[4]}")


class StockWindow(QMainWindow):
    def __init__(self, row_symbol):
        super().__init__()

        self.setWindowTitle("Stock Info Window")
        self.setFixedWidth(900)
        self.setFixedHeight(600)
        self.row_symbol = row_symbol

        self.stock_info = do_everything(row_symbol)        
        self.stock_name = QLabel()
        self.stock_symbol = QLabel()
        self.stock_price = QLabel()
        self.buy_sell = QPushButton("Buy/Sell Stock")

        self.stock_name.setText(self.stock_info[0])
        self.stock_symbol.setText(self.stock_info[1])
        self.stock_price.setText(f"{self.stock_info[2]} \n" + f"{self.stock_info[3]}" + f"{self.stock_info[4]}")


        layout = QHBoxLayout()
        layout.addWidget(self.stock_name)
        layout.addWidget(self.stock_symbol)
        layout.addWidget(self.stock_price)
        layout.addWidget(self.buy_sell)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

class PortfolioWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Portfolio Window")
        self.setGeometry(200,200,900,600)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()