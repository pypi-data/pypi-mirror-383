from gerermesaffaires_events import EventEmitter

emitter = EventEmitter(signature="secret")
app = emitter.app


@emitter.on("ping")
def handle_ping(data):
    print(f"Received ping event: {data}")


@emitter.on("error")
def handle_error(data):
    print(f"Received error event: {data}")
