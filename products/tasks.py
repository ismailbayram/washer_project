from washer_project.celery import app


@app.task(name="products.update_product_price")
def update_product_price(product_id):
    from products.models import Product
    from search.indexer import ReservationIndexer

    product = Product.objects.get(pk=product_id)
    res_indexer = ReservationIndexer()
    res_indexer.update_price_on_reservations(product.store, product)
