from datetime import datetime

from app.logic import TransactionService, transaction_reports, transactions


class TestTransactionService:
    def test_create_and_get_transactions(self):
        TransactionService.create_transaction(1, 100, 'Пополнение')
        TransactionService.create_transaction(1, 300, 'Снятие')
        TransactionService.create_transaction(1, 1000, 'Пополнение')
        TransactionService.create_transaction(2, 100, 'Пополнение')
        TransactionService.create_transaction(1000, 1000, 'Снятие')

        TransactionService.get_transactions(
            1, datetime(2024, 1, 1), datetime(2124, 1, 1),
        )
        TransactionService.get_transactions(
            2, datetime(2024, 1, 1), datetime(2124, 1, 1),
        )
        TransactionService.get_transactions(
            1000, datetime(2024, 1, 1), datetime(2124, 1, 1),
        )

        report_1 = transaction_reports[1][0]
        report_2 = transaction_reports[2][0]
        report_1000 = transaction_reports[1000][0]

        assert report_1.date_start == datetime(2024, 1, 1)
        assert report_1.date_end == datetime(2124, 1, 1)
        assert report_1.transactions == transactions[1]

        assert report_2.date_start == datetime(2024, 1, 1)
        assert report_2.date_end == datetime(2124, 1, 1)
        assert report_2.transactions == transactions[2]

        assert report_1000.date_start == datetime(2024, 1, 1)
        assert report_1000.date_end == datetime(2124, 1, 1)
        assert report_1000.transactions == transactions[1000]
