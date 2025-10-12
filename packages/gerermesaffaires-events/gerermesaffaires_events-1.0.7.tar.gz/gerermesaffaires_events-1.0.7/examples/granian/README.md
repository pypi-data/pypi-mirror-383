# Granian 🐴

This folder shows how to use the event server with [Granian](https://github.com/emmett-framework/granian), a high-performance ASGI/WSGI server for Python.

## Getting started

### What is Granian?

Granian is a Rust-based ASGI/WSGI server that provides excellent performance for Python web applications. It is especially useful for:

- High-performance web applications requiring maximum throughput.
- Production deployments where performance is critical.
- Applications requiring WebSockets, streaming, or asynchronous tasks.
- Running event-driven servers like the one provided in this project.

In the context of `gerermesaffaires-events`, Granian exposes the event emitter as an ASGI application, allowing you to receive and emit events in real time with excellent performance.

### Example usage

Below you will find practical examples to help you get started with Granian and the event server.

#### Command line usage

You can run the event server directly from the command line using Granian. This is useful for quick testing or deployment without writing additional code.

```bash
uv run --with granian granian main:app --interface asgi --host 127.0.0.1 --port 8003
```

#### Programmatic usage

To use Granian programmatically, first install it in your environment. This step ensures that Granian is available for your Python scripts.

```bash
uv add granian
```

The [`main.py`](./main.py) file contains the event emitter setup and event handlers. The following Python code demonstrates how to launch the ASGI application using Granian programmatically. This approach gives you more control and flexibility for integrating event-driven logic into your application.

```python
# examples/granian/test.py

from granian import Granian

if __name__ == "__main__":
    granian = Granian("main:app", interface="asgi", address="127.0.0.1", port=8003)
    granian.serve()
```

Once your script is ready, you can start the server using the following command. This will launch your event server and make it accessible for handling events.

```bash
uv run test.py
```
