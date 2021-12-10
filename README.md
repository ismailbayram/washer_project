# Washer Project
This is the REST API code of my startup attemption between 2018-2019.
![Product Design](all_images.jpg?raw=true "Product Design")
### Requirements
- python@3.7
- postgresql@11
- elasticsearch@7.2
- redis@5.0
- celery@4.3
### Installation
- create a virtual environment that has python3.7 interpreter
- create a database in postgres
- `pip install -r reqirements.txt`
- `./manage.py migrate`
- install packages list in the `ubuntu_packages.txt` file
- You should create a file named `settings_local.py` in the settings directory and paste the below snippet into it.
```
DEBUG = True
ALLOWED_HOSTS = ['*']

SHELL_PLUS_PRE_IMPORTS = (
    ('users.service', '*'),
    ('users.enums', '*'),
    ('address.service', '*'),
    ('stores.service', '*'),
    ('cars.service', '*'),
    ('cars.enums', '*'),
    ('products.enums', '*'),
    ('products.service', '*'),
    ('baskets.service', '*'),
    ('baskets.enums', '*'),
    ('reservations.enums', '*'),
    ('reservations.service', '*'),
    ('search.indexer', '*'),
    ('search.service', '*'),
)
``` 
### Documentation
`/api/v1/docs/`
### Dummy data
- Run `python dummy_data.py`
- Write below comands at python shell after running celery; 
```
Store.objecs.all().update(is_approved=True)
from search.indexer import StoreIndexer
from reservations.tasks import create_store_weekly_reservations
StoreIndexer().index_stores()
for store in Store.objects.actives():
    create_store_weekly_reservations.delay(store.id)
``` 

### Development
- Run elasticsearch and redis.
- Celery Worker: `celery -A washer_project worker -l info --concurrency 8` (Async tasks)
- Celery Beat: `celery -A washer_project beat -l info` (Periodic tasks)

### Testing
`./manage.py test --settings=washer_project.settings_test`
