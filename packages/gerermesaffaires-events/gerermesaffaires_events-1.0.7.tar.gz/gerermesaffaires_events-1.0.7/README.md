<div align="center">
  <img src="https://github.com/user-attachments/assets/75297aaf-fe2f-4f0b-bd4b-458c07046fc1" />
</div>

<div align="center">

![Version](https://img.shields.io/pypi/v/gerermesaffaires-events?style=for-the-badge&colorA=4c566a&colorB=5382a1&logo=pypi&logoColor=white)
![Code Size](https://img.shields.io/github/languages/code-size/julienbenac/gerermesaffaires-events?style=for-the-badge&colorA=4c566a&colorB=ebcb8b&logo=github&logoColor=white)
![License](https://img.shields.io/github/license/julienbenac/gerermesaffaires-events?style=for-the-badge&colorA=4c566a&colorB=a3be8c)

</div>

`gerermesaffaires-events` is a library designed to provide a flexible event emitter and server for integrating with [GererMesAffaires](https://www.gerermesaffaires.com). It enables developers to build event-driven applications and services that can easily handle and emit custom events in real time.

## Getting started

### Installation

To begin using `gerermesaffaires-events`, you first need to install the package. Select the installation method that best fits your workflow:

<details open>
  <summary><strong>📦 Using pip</strong></summary>

```bash
pip install gerermesaffaires-events
```

</details>

<details>
  <summary><strong>🚀 Using pipx</strong></summary>

```bash
pipx install gerermesaffaires-events
```

</details>

<details>
  <summary><strong>⚡ Using uv</strong></summary>

```bash
uv add gerermesaffaires-events
```

</details>

Once installed, you can import the event emitter into your Python project and start building event-driven logic.

### Usage

After installation, you can import the event emitter and create event handlers in your Python code. The following example demonstrates how to set up an event emitter, register handlers for specific events and respond to incoming data. This approach allows you to build applications that react to events in real time.

```python
# main.py

from gerermesaffaires_events import EventEmitter

emitter = EventEmitter(signature="secret")

@emitter.on("ping")
def handle_ping(data):
    print(f"Received ping event: {data}")

@emitter.on("error")
def handle_error(data):
    print(f"Received error event: {data}")
```
