# Washer Project
### Requirements
- python3.7
- postgresql
- elasticsearch@7.2
- redis@5.0
- celery@4.3
### Installation
- create a virtual environment that has python3.7 interpreter
- create a database in postgres
- `pip install -r reqirements.txt`
- `./manage.py migrate`
- install packages list in the `ubuntu_packages.txt` file
### Dummy data
- Run `python dummy_data.py`
- Run celery and write below comands at python shell; 
```
from search.indexer import StoreIndexer
from reservations.tasks import create_store_weekly_reservations
StoreIndexer().index_stores()
create_store_weekly_reservations.delay()
``` 