# Financial OS — Configuration

Edit these values before first use. This file is read by the financial-os skill
at the start of every session.

---

## Goal parameters

```
annual_spend_retirement:  40000      # projected annual spend in retirement (your currency)
withdrawal_rate:          0.04       # safe withdrawal rate (4% is the common default)
expected_annual_return:   0.07       # expected portfolio growth rate (pre-inflation)
annual_savings:           20000      # amount added to investments per year
target_fi_year:           2035       # when you want to reach financial independence
```

## Net worth inputs

```
input_folder:  ~/Finance/Statements/   # where statement files are stored
currency:      USD                     # your reporting currency
```

## Platforms to aggregate

Add one row per account. The skill will look for a matching file in input_folder.

| Platform | Account type | Notes |
|---|---|---|
| Vanguard | Brokerage | Download CSV from account portal |
| Fidelity | 401(k) | Download PDF statement quarterly |
| Chase | Savings | Download CSV from online banking |
| [Add your own] | | |

## Asset allocation targets

| Asset class | Target % |
|---|---|
| Equities (domestic) | 40% |
| Equities (international) | 30% |
| Bonds | 20% |
| Cash | 5% |
| Other | 5% |

## Liabilities

| Liability | Balance | Notes |
|---|---|---|
| [Mortgage / Loan] | $0 | |
| [Credit cards] | $0 | Pay in full — list only if carrying balance |

---

## Notes

- Update `annual_spend_retirement` as your lifestyle plans evolve
- Review `expected_annual_return` if your asset mix changes significantly
- The skill uses these figures as-is — it doesn't validate them against market data
