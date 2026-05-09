import json
import os

_DEFAULT_KB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "guideline_knowledge_base.json")


class RecommendationKnowledgeBase:
    def __init__(self, path=None):
        kb_path = os.path.normpath(path or _DEFAULT_KB_PATH)
        with open(kb_path, encoding="utf-8") as f:
            self._entries = json.load(f)

    def list_entries(self):
        return list(self._entries)

    def match(self, signal):
        return [
            entry
            for entry in self._entries
            if self._matches(entry["trigger_conditions"], signal)
        ]

    def _matches(self, trigger_conditions, signal):
        for key, expected in trigger_conditions.items():
            if key.endswith("_min"):
                signal_key = key[:-4]
                if signal.get(signal_key) is None or signal[signal_key] < expected:
                    return False
                continue

            if key.endswith("_max"):
                signal_key = key[:-4]
                if signal.get(signal_key) is None or signal[signal_key] > expected:
                    return False
                continue

            actual = signal.get(key)
            if actual is None:
                return False

            if isinstance(expected, list):
                if actual not in expected:
                    return False
                continue

            if actual != expected:
                return False

        return True

