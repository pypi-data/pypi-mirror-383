import csv
import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import Statement, StatementLine


class PrestiaPlugin(Plugin):
    """Prestia (SMBC Trust Bank) Japan CSV statement plugin"""

    def get_parser(self, filename: str) -> "PrestiaParser":
        # Get encoding from settings, default to cp932 (Shift-JIS for Japanese Windows)
        encoding = self.settings.get("encoding", "cp932")
        return PrestiaParser(filename, encoding=encoding)


class PrestiaParser(StatementParser[list[str]]):
    def __init__(self, filename: str, encoding: str = "cp932") -> None:
        super().__init__()
        self.filename = filename
        self.encoding = encoding
        self.statement = Statement()
        self.line_counter = 0

    def parse(self) -> Statement:
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        with open(self.filename, "r", encoding=self.encoding) as f:
            self.fin = f
            return super().parse()

    def split_records(self) -> Iterable[list[str]]:
        """Return iterable object consisting of a row per transaction"""
        reader = csv.reader(self.fin)
        for row in reader:
            # Skip empty rows
            if not row or len(row) < 4:
                continue
            yield row

    def parse_record(self, row: list[str]) -> StatementLine:
        """Parse given transaction row and return StatementLine object

        CSV format:
        - Column 0: Date (YYYY/MM/DD)
        - Column 1: Description
        - Column 2: Amount (e.g., "-1,590 JPY" or "1,590 JPY")
        - Column 3: Account number
        """
        line = StatementLine()

        # Parse date
        date_str = row[0].strip()
        line.date = datetime.strptime(date_str, "%Y/%m/%d")

        # Parse description
        line.memo = row[1].strip()

        # Parse amount - remove commas and " JPY" suffix
        amount_str = row[2].strip()
        # Remove " JPY" suffix
        amount_str = amount_str.replace(" JPY", "")
        # Remove commas
        amount_str = amount_str.replace(",", "")
        line.amount = Decimal(amount_str)

        # Extract account number (remove quotes)
        account = row[3].strip().strip("'")
        if not self.statement.account_id:
            self.statement.account_id = account

        # Generate a unique ID for the transaction using hash of key fields
        self.line_counter += 1
        unique_string = f"{date_str}:{line.memo}:{amount_str}:{self.line_counter}"
        line.id = hashlib.md5(unique_string.encode()).hexdigest()

        return line
