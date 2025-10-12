<div align="center">
  <img src="https://github.com/user-attachments/assets/933780a4-7e5c-4730-bd8b-6bfc83ead5f1" />
</div>

<div align="center">

![Version](https://img.shields.io/pypi/v/bridge-events?style=for-the-badge&colorA=4c566a&colorB=5382a1&logo=pypi&logoColor=white)
![Code Size](https://img.shields.io/github/languages/code-size/julienbenac/bridge-events?style=for-the-badge&colorA=4c566a&colorB=ebcb8b&logo=github&logoColor=white)
![License](https://img.shields.io/github/license/julienbenac/bridge-events?style=for-the-badge&colorA=4c566a&colorB=a3be8c)

</div>

`bridge-events` is a library designed to provide a flexible event emitter and server for integrating with [Bridge](https://www.bridgeapi.io). It enables developers to build event-driven applications and services that can easily handle and emit custom events in real time.

## Getting started

### Installation

To begin using `bridge-events`, you first need to install the package. Select the installation method that best fits your workflow:

<details open>
  <summary><strong>📦 Using pip</strong></summary>

```bash
pip install bridge-events
```

</details>

<details>
  <summary><strong>🚀 Using pipx</strong></summary>

```bash
pipx install bridge-events
```

</details>

<details>
  <summary><strong>⚡ Using uv</strong></summary>

```bash
uv add bridge-events
```

</details>

Once installed, you can import the event emitter into your Python project and start building event-driven logic.

### Usage

After installation, you can import the event emitter and create event handlers in your Python code. The following example demonstrates how to set up an event emitter, register handlers for specific events and respond to incoming data. This approach allows you to build applications that react to events in real time.

```python
# main.py

from bridge_events import EventEmitter

emitter = EventEmitter(signature="secret")

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
```
