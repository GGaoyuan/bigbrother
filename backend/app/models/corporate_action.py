from dataclasses import dataclass
from datetime import date
from fractions import Fraction


@dataclass(frozen=True, slots=True)
class CorporateAction:
    """Cash (CNY) and share quantities per ten pre-action shares, rights price per share."""

    ex_date: date
    cash_dividend: Fraction
    bonus_shares: Fraction
    rights_shares: Fraction
    rights_price: Fraction
