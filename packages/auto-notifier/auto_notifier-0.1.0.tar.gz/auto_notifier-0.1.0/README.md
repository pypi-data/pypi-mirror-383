# Auto Notifier (Desktop MVP)
Easily notify yourself of task completion or failure in Python scripts with Auto Notifier. Ideal for monitoring long-running jobs or automating workflows. Delivers native desktop notifications using [`notify-py`](https://ms7m.github.io/notify-py/); future support for other channels is planned.

Install from PyPI (or a local source distribution) and the required
`notify-py` dependency will be pulled in automatically:

```bash
pip install auto-notifier
```

Alternatively, you can include the `auto_notifier` directory in your
project and add it to your `PYTHONPATH`; in that case you must ensure
`notify-py` is available in the runtime environment.

## Usage

### Decorator

Use the `notify_when_done` decorator to wrap a long-running function.
When the function returns successfully, a desktop notification will be
sent indicating completion and the elapsed time. If the function
raises an exception, a failure notification will be sent instead and
the exception will be re-raised.

```python
from auto_notifier import notify_when_done

@notify_when_done(
    title="Training finished",
    message="The model training completed successfully",
    error_title="Training failed",
)
def train_model():
    # long running code here
    ...

train_model()  # will send a desktop notification when done or on error
```

### Context manager

You can also wrap arbitrary code using the `notify_on_complete`
context manager:

```python
from auto_notifier import notify_on_complete

with notify_on_complete(title="Processing done"):
    # long running block here
    ...
```

When the block exits, a desktop notification is sent indicating
success or failure.

## Configuration

Both the decorator and context manager accept optional keyword
arguments that are passed directly to `notifypy.Notify` (for
example, `app_name` or `icon_path`). Refer to the
[`notify-py` documentation](https://ms7m.github.io/notify-py/) for
details. A minimal example from the upstream library shows how to
instantiate the notifier and send a message:

```python
from notifypy import Notify
notification = Notify()
notification.title = "Cool Title"
notification.message = "Even cooler message."
notification.send()  # sends a desktop notification on your platform
```

This library uses the same API under the hood.

## Limitations

- This version only supports desktop notifications via `notify-py`. To
  receive notifications over other channels (Slack, email, etc.),
  additional integrations will need to be implemented in future
  versions.
- Desktop notifications may not display on headless servers or
  restricted environments. In such cases, you may wish to extend
  the `send_notification` function to log messages or use another
  backend.
