


class Transaction:
    def __init__(self):
        super().__init__()

    def update_buy(self, code, date, amount, amount_krw):
        raise NotImplementedError()

    def update_sell(self, code, date, amount, amount_krw):
        raise NotImplementedError()