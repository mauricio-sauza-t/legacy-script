"""
Task Manager CLI Application.

A simple command-line task manager with basic credential authentication.
Supports adding items to an in-memory store, listing them, and persisting
them to a plain-text file.

Usage::

    python refactored.py
"""

import datetime
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class TaskItem:
    """A single task item held in the store.

    Attributes:
        id: Auto-assigned sequential identifier (1-based).
        value: User-supplied text content of the task.
        created_at: Timestamp string (``YYYY-MM-DD HH:MM:SS``) captured
            when the item was added.
    """

    id: int
    value: str
    created_at: str


# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------


class TaskStore:
    """In-memory store for :class:`TaskItem` objects with file persistence.

    Items are kept in insertion order. The store does not survive process
    restart unless :meth:`save` is called first.
    """

    def __init__(self) -> None:
        """Initialise an empty task store."""
        self._items: list[TaskItem] = []

    def add(self, value: str) -> TaskItem:
        """Create and store a new task item stamped with the current time.

        Args:
            value: Non-empty text content for the task.

        Returns:
            The newly created :class:`TaskItem`.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = TaskItem(id=len(self._items) + 1, value=value, created_at=timestamp)
        self._items.append(item)
        return item

    def all(self) -> list[TaskItem]:
        """Return a snapshot of all stored task items (oldest first).

        Returns:
            A new list containing every :class:`TaskItem` in insertion order.
        """
        return list(self._items)

    def save(self, path: Path = Path("data.txt")) -> None:
        """Persist all items to a CSV-like plain-text file.

        Each line has the format ``id,value,created_at``. The file is
        overwritten on every call. Uses a context manager to guarantee the
        file handle is closed even on error.

        Args:
            path: Destination file path. Defaults to ``data.txt`` in the
                current working directory.
        """
        with path.open("w", encoding="utf-8") as fh:
            for item in self._items:
                fh.write(f"{item.id},{item.value},{item.created_at}\n")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


class AuthService:
    """Credential-based authentication service.

    .. warning::
        Credentials are stored in plain text to stay faithful to the
        original implementation. In production use a secrets manager and
        hashed passwords (e.g. ``bcrypt``).
    """

    def __init__(self, username: str, password: str) -> None:
        """Initialise the service with the single valid credential pair.

        Args:
            username: The accepted username.
            password: The accepted plain-text password.
        """
        self._username = username
        self._password = password

    def authenticate(self, username: str, password: str) -> bool:
        """Verify a credential pair against the stored values.

        Args:
            username: Username submitted by the user.
            password: Password submitted by the user.

        Returns:
            ``True`` when both values match, ``False`` otherwise.
        """
        return username == self._username and password == self._password


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class TaskCLI:
    """Interactive REPL for the task manager.

    Reads commands from stdin and delegates each one to the appropriate
    :class:`TaskStore` operation.
    """

    VALID_COMMANDS = ("add", "show", "save", "exit")

    def __init__(self, store: TaskStore) -> None:
        """Initialise the CLI with the backing store.

        Args:
            store: :class:`TaskStore` instance that this CLI operates on.
        """
        self._store = store

    def run(self) -> None:
        """Start the interactive loop; exits when the user types ``exit``."""
        print("Welcome")
        while True:
            cmd = input("What to do? (add/show/save/exit): ").strip().lower()
            if cmd == "exit":
                break
            elif cmd == "add":
                self._handle_add()
            elif cmd == "show":
                self._handle_show()
            elif cmd == "save":
                self._handle_save()
            else:
                valid = ", ".join(self.VALID_COMMANDS)
                print(f"Unknown command '{cmd}'. Valid commands: {valid}")

    def _handle_add(self) -> None:
        """Prompt for a value and add it to the store."""
        value = input("Value: ").strip()
        if not value:
            print("Value cannot be empty.")
            return
        item = self._store.add(value)
        print(f"Added item #{item.id}.")

    def _handle_show(self) -> None:
        """Print every item in the store to stdout."""
        items = self._store.all()
        if not items:
            print("No items yet.")
            return
        for item in items:
            print(f"Item {item.id} - {item.value} at {item.created_at}")

    def _handle_save(self) -> None:
        """Persist the store to disk and confirm success."""
        self._store.save()
        print("Saved.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Authenticate the user, then launch the task-manager REPL."""
    auth = AuthService(username="admin", password="12345")

    username = input("User: ").strip()
    password = input("Pass: ").strip()

    if not auth.authenticate(username, password):
        print("Wrong!")
        return

    cli = TaskCLI(TaskStore())
    cli.run()


if __name__ == "__main__":
    main()
