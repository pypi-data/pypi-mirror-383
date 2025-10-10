"""Utilities for counting running instances of an application."""

import os
from pathlib import Path
from tempfile import gettempdir

from psutil import AccessDenied, NoSuchProcess, ZombieProcess, process_iter


class CountHelper:
    """Class to count running instances of an application by process and lock files.

    This class provides methods to count how many instances of an application are
    currently running either via checking process command lines or scanning for
    lock files in a specified directory.
    """

    lock_dir: str

    def __init__(self, *, lock_dir: str | None = None) -> None:
        """Initialize the CountHelper instance with a lock directory.

        Args:
            lock_dir: Optional path to the directory where lock files are stored.
                      If not provided, uses the system's temporary directory.

        Example:
            ```python
            print(CountHelper(lock_dir="/tmp/my_app_locks").lock_dir)
            #> /tmp/my_app_locks
            ```

        """
        if not lock_dir:
            self.lock_dir = gettempdir()
        else:
            self.lock_dir = lock_dir

    @classmethod
    def process_count(cls, identifier: str) -> int:
        """Count the number of running processes that match the given identifier.

        Iterates over all running processes and checks if the identifier appears
        in their command-line arguments.

        Args:
            identifier: String to search for in process command lines.

        Returns:
            Number of matching processes.

        Raises:
            Exception:
                Any exception raised by 'psutil.process_iter'.

        Example:
            ```python
            print(CountHelper.process_count("my_app"))
            #> 2
            ```

        """
        count = 0

        for process in process_iter(["cmdline"]):
            try:
                command: list[str] = process.cmdline()
                if command and identifier in " ".join(command):
                    count += 1
            except (NoSuchProcess, AccessDenied, ZombieProcess):
                continue

        return count

    def pid_file_count(self, identifier: str) -> int:
        """Count the number of lock files in the lock directory by identifier.

        Lock files are expected to have names containing `.lock.` and the identifier.

        Args:
            identifier: String to search for in lock file names.

        Returns:
            Number of matching lock files.

        Example:
            ```python
            helper = CountHelper(lock_dir="/tmp/locks")
            print(helper.pid_file_count("my_app"))
            #> 1
            ```

        """
        return len(self._get_pid_files(identifier=identifier))

    def acquire_pid_file(self, filename: str) -> tuple[Path, int]:
        """Create and open a lock file with the given filename, and lock it.

        The file is created with write access and locked using `os.lockf` with `F_LOCK`.

        Args:
            filename: Name of the lock file to create.

        Returns:
            A tuple containing the path to the file and its file descriptor.

        Example:
            ```python
            helper = CountHelper(lock_dir="/tmp/locks")
            path, fd = helper.acquire_pid_file("my_app.lock.123456")
            print(path)
            #> /tmp/locks/my_app.lock.123456
            ```

        """
        path: Path = self.lock_dir / Path(filename)
        f = path.open(mode="x")
        fd: int = f.fileno()
        os.lockf(fd, os.F_LOCK, 0)

        return path, fd

    def is_released_pid_file(self, filename: str) -> bool:
        """Check whether a lock file is available (not locked by another process).

        Tries to test the lock using `os.lockf` with `F_TEST`. Returns `True` if the
        file is available, `False` if it is locked.

        Args:
            filename: Name of the lock file to check.

        Returns:
            True if the file is available, False otherwise.

        Example:
            ```python
            helper = CountHelper(lock_dir="/tmp/locks")
            print(helper.is_released_pid_file("my_app.lock.123456"))
            #> True
            ```

        """
        path: Path = self.lock_dir / Path(filename)
        with path.open(mode="r") as f:
            fd = f.fileno()
            try:
                os.lockf(fd, os.F_TEST, 0)
            except OSError:
                return False
            else:
                return True

    def get_pid_file(self, identifier: str) -> Path | None:
        """Get the first lock file in the lock directory that matches the identifier.

        Args:
            identifier: String to search for in lock file names.

        Returns:
            Path to the first matching lock file, or None if no match found.

        Example:
            ```python
            helper = CountHelper(lock_dir="/tmp/locks")
            print(str(helper.get_pid_file("my_app")))
            #> /tmp/locks/my_app.lock.123456
            ```

        """
        file: Path | None = None
        if files := self._get_pid_files(identifier=identifier):
            file = files[0]

        return file

    def _get_pid_files(self, identifier: str) -> list[Path]:
        """Collect all lock files in the lock directory that match the identifier.

        Lock files are expected to have names containing `.lock.` and the identifier.

        Args:
            identifier: String to search for in lock file names.

        Returns:
            List of paths to matching lock files.

        """
        lock_files = []

        for root, _, files in os.walk(self.lock_dir):
            path_root = Path(root)

            for filename in files:
                if identifier in filename and ".lock." in filename:
                    full_path = path_root / filename
                    lock_files.append(full_path)

        return lock_files
