"""Модуль обучения — запоминает, когда показывать и скрывать клавиатуру."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from touchflow.config import LEARNING_PATH, ensure_config_dir

log = logging.getLogger(__name__)


@dataclass
class AppPattern:
    app_id: str = ""
    window_class: str = ""
    show_count: int = 0
    dismiss_count: int = 0
    immediate_hide_count: int = 0
    last_seen: float = 0.0
    score: float = 0.5  # 0 = никогда не показывать, 1 = всегда показывать

    def update_score(self, show_weight: float, dismiss_weight: float) -> None:
        total = self.show_count + self.dismiss_count + self.immediate_hide_count
        if total == 0:
            self.score = 0.5
            return
        positive = self.show_count * show_weight
        negative = (self.dismiss_count + self.immediate_hide_count * 2) * dismiss_weight
        self.score = max(0.0, min(1.0, (positive + 1) / (positive + negative + 2)))


@dataclass
class LearningStore:
    patterns: dict[str, AppPattern] = field(default_factory=dict)
    global_dismiss_streak: int = 0

    def key(self, app_id: str, window_class: str) -> str:
        return f"{app_id}|{window_class}"

    def get_pattern(self, app_id: str, window_class: str) -> AppPattern:
        k = self.key(app_id, window_class)
        if k not in self.patterns:
            self.patterns[k] = AppPattern(app_id=app_id, window_class=window_class)
        return self.patterns[k]

    def should_show(
        self,
        app_id: str,
        window_class: str,
        threshold: float = 0.35,
    ) -> bool:
        pattern = self.get_pattern(app_id, window_class)
        return pattern.score >= threshold

    def record_show(self, app_id: str, window_class: str, show_weight: float, dismiss_weight: float) -> None:
        p = self.get_pattern(app_id, window_class)
        p.show_count += 1
        p.last_seen = time.time()
        p.update_score(show_weight, dismiss_weight)
        self.global_dismiss_streak = 0
        self._save()

    def record_dismiss(self, app_id: str, window_class: str, immediate: bool, show_weight: float, dismiss_weight: float) -> None:
        p = self.get_pattern(app_id, window_class)
        p.dismiss_count += 1
        if immediate:
            p.immediate_hide_count += 1
            self.global_dismiss_streak += 1
        else:
            self.global_dismiss_streak = 0
        p.last_seen = time.time()
        p.update_score(show_weight, dismiss_weight)
        self._save()

    def record_manual_show(self, app_id: str, window_class: str, show_weight: float, dismiss_weight: float) -> None:
        self.record_show(app_id, window_class, show_weight * 1.5, dismiss_weight)

    def reset(self) -> None:
        self.patterns.clear()
        self.global_dismiss_streak = 0
        self._save()

    def to_dict(self) -> dict:
        return {
            "patterns": {k: p.__dict__ for k, p in self.patterns.items()},
            "global_dismiss_streak": self.global_dismiss_streak,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearningStore":
        store = cls()
        store.global_dismiss_streak = data.get("global_dismiss_streak", 0)
        for k, v in data.get("patterns", {}).items():
            store.patterns[k] = AppPattern(**v)
        return store

    def _save(self) -> None:
        ensure_config_dir()
        tmp = LEARNING_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        tmp.replace(LEARNING_PATH)

    @classmethod
    def load(cls) -> "LearningStore":
        if not LEARNING_PATH.exists():
            return cls()
        try:
            data = json.loads(LEARNING_PATH.read_text(encoding="utf-8"))
            return cls.from_dict(data)
        except (json.JSONDecodeError, TypeError) as e:
            log.warning("Corrupt learning data, resetting: %s", e)
            return cls()


class LearningEngine:
    def __init__(self, enabled: bool = True, show_weight: float = 0.5, dismiss_weight: float = 1.0):
        self.enabled = enabled
        self.show_weight = show_weight
        self.dismiss_weight = dismiss_weight
        self.store = LearningStore.load()

    def should_auto_show(self, app_id: str, window_class: str) -> bool:
        if not self.enabled:
            return True
        return self.store.should_show(app_id, window_class)

    def on_auto_show(self, app_id: str, window_class: str) -> None:
        if self.enabled:
            self.store.record_show(app_id, window_class, self.show_weight, self.dismiss_weight)

    def on_dismiss(self, app_id: str, window_class: str, immediate: bool = False) -> None:
        if self.enabled:
            self.store.record_dismiss(app_id, window_class, immediate, self.show_weight, self.dismiss_weight)

    def on_manual_show(self, app_id: str, window_class: str) -> None:
        if self.enabled:
            self.store.record_manual_show(app_id, window_class, self.show_weight, self.dismiss_weight)

    def reset(self) -> None:
        self.store.reset()
