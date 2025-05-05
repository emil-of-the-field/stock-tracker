import sys
import json
import datetime
from func import *
from classes import *

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget, QLabel, 
                                QComboBox, QTableWidget, QTableWidgetItem, QPushButton, QHeaderView, QMessageBox, QSpinBox)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Stocks App")
        self.setFixedWidth(900)
        self.setFixedHeight(600)

        #updates default tickers
        timer = QTimer(self)
        current_date = datetime.date.today()
        #won't try to update default tickers when Saturday or Sunday
        if (current_date.isoweekday() != 6) or (current_date.isoweekday() != 7):
            timer.timeout.connect(self.update_tickers)
            #runs every minute
            timer.start(60000)

        #default tickers
        self.dow_ticker = QLabel()
        self.nyse_ticker = QLabel()
        self.nasdaq_ticker = QLabel() 

        #run web scraping
        self.dow_info = do_everything(dow)
        self.nyse_info = do_everything(nyse)
        self.nasdaq_info = do_everything(nasdaq)

        #set text on labels
        self.dow_ticker.setText(f"{self.dow_info[0]} \n{self.dow_info[2]} \n{self.dow_info[3]} "+ f"{self.dow_info[4]}")
        self.nyse_ticker.setText(f"{self.nyse_info[0]} \n{self.nyse_info[2]} \n{self.nyse_info[3]} "+ f"{self.nyse_info[4]}")
        self.nasdaq_ticker.setText(f"{self.nasdaq_info[0]} \n{self.nasdaq_info[2]} \n{self.nasdaq_info[3]} "+ f"{self.nasdaq_info[4]}")

        portfolio = QPushButton("View/Create Portfolio")
        portfolio.clicked.connect(self.open_portfolio_window)
        self.p = None

        self.search_bar = QLineEdit(placeholderText="Search stocks, ETFs or mutual funds")
        self.search_bar.returnPressed.connect(self.search_for_stocks)

        self.options = QComboBox()
        self.options.addItems(['All', 'Stocks', 'ETFs', 'Mutual Funds'])


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

        #MainWindow layouts
        vbox = QVBoxLayout()

        vbox.addLayout(self.default_tickers)
        vbox.addLayout(self.search_line)
        vbox.addWidget(self.search_results)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    #window functions
    #search function
    def search_for_stocks(self):
        url = self.search_bar.text()

        if self.options.currentText() == "All":
            search = f"https://finance.yahoo.com/lookup/?s={url}"

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

    #opens new window when stock is double clicked in search results table
    def open_stock_window(self):
        if self.w is None:
            row_num = self.search_results.currentRow()
            row_symbol = self.search_results.item(row_num,0).text()
            self.w = StockWindow(row_symbol)
            self.w.show()

        else:
            self.w = None


    def open_portfolio_window(self):
        if self.p is None:
            self.p = PortfolioWindow()
            self.p.show()

        else:
            self.p = None

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

        sc = MplCanvas(self, width=5, height=4, dpi=100)
        sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])

        self.stock_info = do_everything(row_symbol)        
        self.stock_name = QLabel()
        self.stock_symbol = QLabel()
        self.stock_price = QLabel()
        self.buy_btn = QPushButton("Buy Stock")
        self.buy_btn.clicked.connect(self.buy_stock)
        self.sell_btn = QPushButton("Sell Stock")
        #self.sell_btn.clicked.connect(self.sell_stock)


        self.stock_name.setText(self.stock_info[0])
        self.stock_symbol.setText(self.stock_info[1])
        self.stock_price.setText(f"{self.stock_info[2]} \n" + f"{self.stock_info[3]}" + f"{self.stock_info[4]}")

        vbox = QVBoxLayout()

        layout = QHBoxLayout()
        layout.addWidget(self.stock_name)
        layout.addWidget(self.stock_symbol)
        layout.addWidget(self.stock_price)
        layout.addWidget(self.buy_btn)
        layout.addWidget(self.sell_btn)
        self.b = None

        self.five_day = QPushButton("5D")
        self.three_month = QPushButton("3M")
        self.six_month = QPushButton("6M")
        self.year_to_date = QPushButton("YTD")
        self.one_year = QPushButton("1Y")
        self.five_year = QPushButton("5Y")

        hist_buttons = QHBoxLayout()
        hist_buttons.addWidget(self.five_day)
        hist_buttons.addWidget(self.three_month)
        hist_buttons.addWidget(self.six_month)
        hist_buttons.addWidget(self.year_to_date)
        hist_buttons.addWidget(self.one_year)
        hist_buttons.addWidget(self.five_year)

        vbox.addWidget(sc)
        vbox.addLayout(layout)
        vbox.addLayout(hist_buttons)

        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)

    def buy_stock(self):
        if self.b is None:
            self.b = BuyWindow(self.stock_symbol, self.stock_info[2])
            self.b.show()

        else:
            self.b = None

    def sell_stock(self):
        if self.b is None:
            self.b = BuyWindow(self.stock_symbol, self.stock_info[2])
            self.b.show()

        else:
            self.b = None


class PortfolioWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Portfolio Window")
        self.setGeometry(400,400,900,600)

        self.portfolio_tbl = QTableWidget()
        self.portfolio_tbl.setColumnCount(7)
        self.portfolio_tbl.verticalHeader().setVisible(False)
        self.portfolio_tbl.setHorizontalHeaderLabels(['Symbol', 'Name','Quantity', 'Market Price', 'Market Price Change', 'Market Price Change %',
                                                      'Cost Basis'])
        #self.portfolio_tbl = self.portfolio_tbl.horizontalHeader()
        #self.portfolio_tbl.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        vbox = QVBoxLayout()
        vbox.addWidget(self.portfolio_tbl)
        self.setLayout(vbox)



class BuyWindow(QWidget):
    def __init__(self, stock_symbol, stock_price):
        super().__init__()

        self.setWindowTitle("Buy or Sell")
        self.setFixedWidth(450)
        self.setFixedHeight(300)
        self.ticker = stock_symbol.text()
        self.price = float(stock_price)

        label = QLabel(f"How many shares of {self.ticker} would you like to buy at {self.price}?", wordWrap=True)

        self.stock_amount = QSpinBox(self)
        self.stock_amount.valueChanged.connect(self.change_value)
        self.num_shares = self.stock_amount.value()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.add_to_portfolio)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(ok_button)
        btn_layout.addWidget(cancel_button)

        vbox = QVBoxLayout()
        vbox.addWidget(label)
        vbox.addWidget(self.stock_amount)
        vbox.addLayout(btn_layout)

        self.setLayout(vbox)

    def change_value(self):
        self.num_shares = self.stock_amount.value()

    def add_to_portfolio(self):
        msg = QMessageBox()
        msg.setText(f"You have bought {self.num_shares} shares of {self.ticker} at {self.price} for a total of {self.num_shares * self.price}")
        msg.exec()

        bought_stock = Stock(self.ticker, self.price, datetime.datetime.now())
        portfolio = Positions(bought_stock, self.num_shares)
        json_portfolio = {
            "Portfolio": [{
                "stock" : {
                    "ticker" : bought_stock.symbol,
                    "price": bought_stock.price,
                    "date_bought": str(bought_stock.time_bought)},
                "num_shares" : self.num_shares}
                ]
        
        } 
        json_position = {"stock" : {
                            "ticker" : bought_stock.symbol,
                            "price": bought_stock.price,
                            "date_bought": str(bought_stock.time_bought)},
                        "num_shares" : self.num_shares
        }
        #checks if portfolio file is empty
        with open("portfolio.json", 'r') as f:
            if not f.read():
                with open("portfolio.json", "a") as f:
                    json.dump(json_portfolio, f, indent=4)
            #if the portfolio isn't empty, append to the end
            else:
                with open("portfolio.json",'r+') as file:
                    # First we load existing data into a dict.
                    file_data = json.load(file)
                    # Join new_data with file_data
                    file_data["Portfolio"].append(json_position)
                    # Sets file's current position at offset.
                    file.seek(0)
                    # convert back to json.
                    json.dump(file_data, file, indent = 4)

        print(bought_stock)
        print(portfolio)
        print(json_portfolio)



    


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()