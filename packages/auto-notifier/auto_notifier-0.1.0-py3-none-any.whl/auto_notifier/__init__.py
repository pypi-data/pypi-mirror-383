"""Auto Notifier (Desktop).

This module provides decorators and context managers to simplify
sending desktop notifications when a long‑running function or code
block finishes executing.  It relies on the `notify-py` package,
which sends native cross‑platform notifications on Windows, macOS
and Linux【945027759752671†L24-L31】.

Example:

```python
from auto_notifier import notify_when_done

@notify_when_done(title="Job complete", message="The task finished.")
def do_work():
    ...

do_work()
```

If the function raises an exception, a failure notification will be
sent and the exception re‑raised.
"""

from .core import notify_when_done, notify_on_complete, send_notification

__all__ = [
    "notify_when_done",
    "notify_on_complete",
    "send_notification",
]