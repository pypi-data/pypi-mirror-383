from bridge_events import EventEmitter

emitter = EventEmitter(signature="secret")
app = emitter.app


@emitter.on("item.created")
def handle_item_created(data):
    print(f"Received item created event: {data}")


@emitter.on("item.refreshed")
def handle_item_refreshed(data):
    print(f"Received item refreshed event: {data}")


@emitter.on("payment.transaction.created")
def handle_payment_transaction_created(data):
    print(f"Received payment transaction created event: {data}")


@emitter.on("payment.transaction.updated")
def handle_payment_transaction_updated(data):
    print(f"Received payment transaction updated event: {data}")


@emitter.on("error")
def handle_error(data):
    print(f"Received error event: {data}")
