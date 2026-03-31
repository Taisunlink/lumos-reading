import json
import shutil
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Any, TypeVar

T = TypeVar("T")

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "v2"
SEED_FILE = DATA_DIR / "story-package-release.seed.json"
RUNTIME_FILE = DATA_DIR / "story-package-release.runtime.json"

_STORE_LOCK = Lock()


def _ensure_runtime_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if RUNTIME_FILE.exists():
        return

    shutil.copyfile(SEED_FILE, RUNTIME_FILE)


def reset_story_package_release_state() -> None:
    with _STORE_LOCK:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SEED_FILE, RUNTIME_FILE)


class StoryPackageReleaseStore:
    def load(self) -> dict[str, Any]:
        with _STORE_LOCK:
            _ensure_runtime_file()
            with RUNTIME_FILE.open("r", encoding="utf-8") as handle:
                return json.load(handle)

    def save(self, state: dict[str, Any]) -> None:
        with _STORE_LOCK:
            _ensure_runtime_file()
            with RUNTIME_FILE.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, indent=2, ensure_ascii=False)
                handle.write("\n")

    def update(self, mutator: Callable[[dict[str, Any]], T]) -> T:
        with _STORE_LOCK:
            _ensure_runtime_file()
            with RUNTIME_FILE.open("r", encoding="utf-8") as handle:
                state = json.load(handle)

            result = mutator(state)

            with RUNTIME_FILE.open("w", encoding="utf-8") as handle:
                json.dump(state, handle, indent=2, ensure_ascii=False)
                handle.write("\n")

            return deepcopy(result)
