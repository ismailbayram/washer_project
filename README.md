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
for store in Store.objects.all():
    create_store_weekly_reservations.delay(store.id)
``` 
### Testing
- touch another settings file in washer_project directory and write the below code into it.
```
from washer_project.settings import *

ES_STORE_INDEX = 'test_stores'
ES_RESERVATION_INDEX = 'test_reservations'
```
- `./manage.py test --settings=washer_project.settings_test`
### Development
- Run elasticsearch and redis.
- Celery Worker: `celery -A washer_project worker -l info --concurrency 8` (Async tasks)
- Celery Beat: `celery -A washer_project beat -l info` (Periodic tasks)
