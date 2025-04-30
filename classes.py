class Stock():
    def __init__(self, symbol, price, time_bought):
        
        self.symbol = symbol
        self.price = price
        self.time_bought = time_bought
        

class Positions():
    def __init__(self, stock, num_stocks):

        self.stock = Stock
        self.num_stocks = num_stocks

