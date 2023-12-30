# Ruuvi monitor
Lightweight data collector and webui for Ruuvi devices. The idea behind is that this runs fine on Raspberry PI 1B with a handful of Ruuvi tags.

## Usage
### Installation
```
git clone [this-repo]
python -m venv venv
source venv/bin/activate
pip install requirements.txt
```
### Running
Currently the application consists of two different parts:
- collector.py that collects readings from Ruuvi devices to sqlite database.
```
python collector.py
```

- ruuvireader.py that creates a simple web UI with Flask.
```
python ruuvireader.py
```
