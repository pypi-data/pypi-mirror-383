#!/usr/bin/env python3
"""Run Docker prune safely with a per-host file lock so that concurrent
invocations on the same machine only execute once.

This mirrors the behavior of Ansible's docker_prune usage:
- Prune dangling images only
- Prune builder cache

Exit codes:
- 0: success or skipped because another prune is in progress
- non-zero: unexpected error
"""

import errno
import fcntl
import os
import subprocess
import sys
from contextlib import contextmanager

LOCK_FILE_PATH = os.environ.get("DOCKER_PRUNE_LOCK_FILE", "/tmp/docker_prune.lock")


@contextmanager
def exclusive_lock(lock_file_path: str):
    os.makedirs(os.path.dirname(lock_file_path), exist_ok=True)
    with open(lock_file_path, "w") as lock_file:
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_file.write(f"pid={os.getpid()}\n")
            lock_file.flush()
            yield
        except OSError as exc:  # Could not acquire lock
            if exc.errno in (errno.EACCES, errno.EAGAIN):
                print(
                    "[docker-prune-once] Skip: another prune is running on this host.",
                )
                sys.exit(0)
            raise
        finally:
            try:
                fcntl.lockf(lock_file, fcntl.LOCK_UN)
            except Exception:
                pass


def run_command(command: list[str]) -> None:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ},
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.returncode != 0:
        if completed.stderr:
            print(completed.stderr, file=sys.stderr, end="")
        raise subprocess.CalledProcessError(
            completed.returncode,
            command,
            completed.stdout,
            completed.stderr,
        )


def main() -> int:
    try:
        with exclusive_lock(LOCK_FILE_PATH):
            print("[docker-prune-once] Acquired lock, running docker prune steps...")
            # Prune dangling images only (match Ansible task behavior)
            run_command(["docker", "image", "prune", "-f", "--filter", "dangling=true"])
            # Prune builder cache
            run_command(["docker", "builder", "prune", "-f"])
            print("[docker-prune-once] Completed successfully.")
        return 0
    except FileNotFoundError as exc:
        print(f"Required binary not found: {exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(
            f"Command failed with exit code {exc.returncode}: {' '.join(exc.cmd)}",
            file=sys.stderr,
        )
        return exc.returncode or 1
    except Exception as exc:  # unexpected
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
