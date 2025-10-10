import os
from decimal import Decimal

from ofxstatement.ui import UI

from ofxstatement_japan.prestia import PrestiaPlugin


def test_prestia() -> None:
    # Test with CP932 encoded file (same encoding as real Prestia files)
    plugin = PrestiaPlugin(UI(), {})
    here = os.path.dirname(__file__)
    sample_filename = os.path.join(here, "prestia-statement.csv")

    parser = plugin.get_parser(sample_filename)
    statement = parser.parse()

    assert statement is not None
    assert statement.account_id == "12345678"
    assert len(statement.lines) == 9

    # Test first transaction (debit)
    line = statement.lines[0]
    assert line.date.strftime("%Y/%m/%d") == "2025/10/10"
    assert "GLOBAL PASS SHOPPING SEQ#517156" in line.memo
    assert line.amount == Decimal("-1590")

    # Test last transaction (credit)
    line = statement.lines[-1]
    assert line.date.strftime("%Y/%m/%d") == "2025/09/30"
    assert "SALARY DEPOSIT" in line.memo
    assert line.amount == Decimal("500000")
