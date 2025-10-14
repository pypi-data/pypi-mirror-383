# notifier-ctk

Animated notification widget for **CustomTkinter**, featuring emoji icons, looping GIFs, and sounds.

## Installation

```bash
pip install notifier-ctk
```

## Example
```python
from notifier import Notifier

Notifier(
    title="🚀 Launching",
    message="Mission ready!",
    button="⚡ Click me!"
    beep=True
).show()
```