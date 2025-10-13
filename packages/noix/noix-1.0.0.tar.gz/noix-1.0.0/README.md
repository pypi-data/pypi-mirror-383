# noix – yet another NUT client library

[![Coverage Status](https://coveralls.io/repos/github/Deuchnord/noix/badge.svg?branch=main)](https://coveralls.io/github/Deuchnord/noix?branch=main)

**noix** (French for _nut_, pronounced /nwa/) is a client library that allows to communicate with a compatible Network UPS Tools (NUT) server.

## Installation

To use this package, create a virtual environment and install with PIP:

```bash
python -m venv .venv
source .venv/bin/activate
pip install noix
```

## Usage

First, create a `NUT` object with your server information.
For instance, if your server runs on the same machine and your UPS is named `my_ups`:

```python
from noix import NUT

server = NUT("127.0.0.1", "my_ups", username="myusername", password="myverysecurepassword")
```

You can now use your object to get your UPS information:

```python
# Print the battery charge:
print(await server.get("battery.charge"))
```

To change a variable value:

```python
# Set the battery charge low alert threshold to 15%:
await server.set("battery.charge.low", 15)
```

> [!note]
> The new value in the `set()` method can be of any native type or a stringable object. 

You can also call a command:

```python
# Turn off the UPS:
await server.call("load.off")
```

To get a list of the commands and variables exposed by the UPS:

```python
await server.list_commands()
await server.list_vars()
```
