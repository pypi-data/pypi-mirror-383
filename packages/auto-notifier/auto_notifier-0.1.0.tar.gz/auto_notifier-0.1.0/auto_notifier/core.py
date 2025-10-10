"""Core logic for Auto Notifier (desktop MVP).

This module defines the primitives used by the auto_notifier package:

- `send_notification` - send a desktop notification using `notifypy`.
- `notify_when_done` - a decorator for functions that sends a
  notification on success or failure.
- `notify_on_complete` - a context manager for arbitrary blocks of
  code with similar behavior.

The goal is to make it trivial to notify yourself when long-running
Python jobs complete or fail, without having to duplicate boilerplate
notification code.
"""
from __future__ import annotations

import functools
import logging
import time
from contextlib import ContextDecorator
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


def _import_notifier() -> "Notify":
    """Import Notify class from notifypy.

    We import lazily to avoid import errors during package import when
    `notifypy` is not installed. This function raises an informative
    error if the dependency is missing.
    """
    try:
        from notifypy import Notify  # type: ignore
    except ImportError as exc:
        raise ImportError(
            "Auto Notifier requires the 'notify-py' package for desktop notifications. "
            "Install it with 'pip install notify-py'."
        ) from exc
    return Notify


def send_notification(
    title: str,
    message: str,
    **notify_kwargs: Any,
) -> None:
    """Send a desktop notification.

    Parameters
    ----------
    title:
        Title of the notification.
    message:
        Body text of the notification.
    **notify_kwargs:
        Additional keyword arguments passed to the `Notify` constructor.

    Raises
    ------
    ImportError:
        If the required `notify-py` package is not installed.

    Notes
    -----
    This function leverages the `notify-py` library, which sends
    native notifications on multiple platforms.
    """
    Notify = _import_notifier()
    notification = Notify(**notify_kwargs)
    notification.title = title
    notification.message = message
    notification.send()


def notify_when_done(
    title: str = "Task completed",
    message: str = "The task finished successfully",
    error_title: str = "Task failed",
    error_message: str = "The task failed with an error",
    include_duration: bool = True,
    **notify_kwargs: Any,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to send a desktop notification when a function finishes.

    Parameters
    ----------
    title:
        Title for the success notification.
    message:
        Message for the success notification.
    error_title:
        Title for the failure notification.
    error_message:
        Message prefix for the failure notification. The exception
        message will be appended to this string.
    include_duration:
        Whether to append the elapsed time to the notification message.
    **notify_kwargs:
        Additional keyword arguments forwarded to `send_notification`.

    Returns
    -------
    Callable:
        A decorator that wraps a function, sending a notification on
        completion or failure.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                elapsed = time.perf_counter() - start
                err_msg = f"{error_message}: {exc}"
                if include_duration:
                    err_msg = f"{err_msg} (after {elapsed:.2f} seconds)"
                try:
                    send_notification(title=error_title, message=err_msg, **notify_kwargs)
                except Exception as notify_exc:
                    logger.warning(
                        "auto_notifier could not send failure notification for %s: %s",
                        func.__name__,
                        notify_exc,
                        exc_info=True,
                    )
                raise
            else:
                elapsed = time.perf_counter() - start
                msg = message
                if include_duration:
                    msg = f"{message} (elapsed {elapsed:.2f} seconds)"
                try:
                    send_notification(title=title, message=msg, **notify_kwargs)
                except Exception as notify_exc:
                    logger.warning(
                        "auto_notifier could not send completion notification for %s: %s",
                        func.__name__,
                        notify_exc,
                        exc_info=True,
                    )
                return result

        return wrapper

    return decorator


class NotifyOnComplete(ContextDecorator):
    """Context manager that sends a desktop notification on exit.

    This class can be used directly or via the convenience function
    `notify_on_complete`. When entering the context, it records the
    start time. On exit it sends a notification indicating success
    (no exception) or failure (exception occurred), including the
    elapsed time if requested.
    """

    def __init__(
        self,
        title: str = "Task completed",
        message: str = "The task finished successfully",
        error_title: str = "Task failed",
        error_message: str = "The task failed with an error",
        include_duration: bool = True,
        **notify_kwargs: Any,
    ) -> None:
        self.title = title
        self.message = message
        self.error_title = error_title
        self.error_message = error_message
        self.include_duration = include_duration
        self.notify_kwargs = notify_kwargs
        self._start_time: Optional[float] = None

    def __enter__(self) -> "NotifyOnComplete":
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        assert self._start_time is not None
        elapsed = time.perf_counter() - self._start_time
        if exc is None:
            msg = self.message
            if self.include_duration:
                msg = f"{msg} (elapsed {elapsed:.2f} seconds)"
            try:
                send_notification(self.title, msg, **self.notify_kwargs)
            except Exception as notify_exc:
                logger.warning(
                    "auto_notifier could not send completion notification from context manager: %s",
                    notify_exc,
                    exc_info=True,
                )
        else:
            err_msg = f"{self.error_message}: {exc}"
            if self.include_duration:
                err_msg = f"{err_msg} (after {elapsed:.2f} seconds)"
            try:
                send_notification(self.error_title, err_msg, **self.notify_kwargs)
            except Exception as notify_exc:
                logger.warning(
                    "auto_notifier could not send failure notification from context manager: %s",
                    notify_exc,
                    exc_info=True,
                )
        # Returning False will re-raise any exception that occurred
        return False


def notify_on_complete(
    title: str = "Task completed",
    message: str = "The task finished successfully",
    error_title: str = "Task failed",
    error_message: str = "The task failed with an error",
    include_duration: bool = True,
    **notify_kwargs: Any,
) -> NotifyOnComplete:
    """Factory function to create a ``NotifyOnComplete`` context manager.

    Example usage::

        with notify_on_complete(title="Processing done"):
            ...  # your code here

    Parameters are the same as those for ``NotifyOnComplete``.
    """
    return NotifyOnComplete(
        title=title,
        message=message,
        error_title=error_title,
        error_message=error_message,
        include_duration=include_duration,
        **notify_kwargs,
    )
