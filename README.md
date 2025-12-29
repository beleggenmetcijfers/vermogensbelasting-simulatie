# Vermogensbelasting simulatie

```python
usage: main.py [-h] -d DATA [-y MAX_YEARS] [-a ATH_PERCENTAGE] {static,transition,long_term}

Dutch Wealth-tax simulation

positional arguments:
  {static,transition,long_term}
                        mode

options:
  -h, --help            show this help message and exit
  -d DATA, --data DATA  market_data csv
  -y MAX_YEARS, --max-years MAX_YEARS
                        max number of years to run
  -a ATH_PERCENTAGE, --ath-percentage ATH_PERCENTAGE
                        if set, only include start-points within given ATH percentage (default=100)
```

## Examples

Run transition comparison for 20 years:

```python
python3 main.py transition -d ie_data.csv -y 20
```

Run full tax system comparison for 20 years:

```python
python3 main.py long_term -d ie_data.csv -y 20
```

Graphs are outputted in './output'

## Dataset

The dataset (ie_data.csv) is originating from Shiller data (`ie_data.xls`). The Excel file is exported
to CSV and added to the repo. The dataset can be found here: [https://shillerdata.com/](https://shillerdata.com/).
