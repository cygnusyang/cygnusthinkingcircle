"""增量构建状态管理。"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class BuildState:
    """构建状态管理器。"""

    def __init__(self, cache_path: Path) -> None:
        self.cache_path = cache_path
        self.state: dict = {}
        self._load()

    def _load(self) -> None:
        """加载缓存文件。"""
        if self.cache_path.exists():
            try:
                self.state = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                self.state = {}

    def _save(self) -> None:
        """保存缓存文件。"""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def needs_build(self, source_file: Path, platform: str = "all") -> bool:
        """检查是否需要重新构建。"""
        key = str(source_file)
        if key not in self.state:
            return True

        entry = self.state[key]
        current_hash = _file_hash(source_file)

        if platform == "all":
            # 检查文件是否变化
            return entry.get("hash") != current_hash

        # 检查特定平台是否变化
        platform_state = entry.get("platforms", {}).get(platform)
        if not platform_state:
            return True
        return platform_state.get("hash") != current_hash

    def mark_built(self, source_file: Path, platform: str = "all") -> None:
        """标记已构建。"""
        key = str(source_file)
        current_hash = _file_hash(source_file)

        if key not in self.state:
            self.state[key] = {"hash": current_hash, "platforms": {}}

        self.state[key]["hash"] = current_hash
        if platform not in self.state[key]["platforms"]:
            self.state[key]["platforms"][platform] = {}
        self.state[key]["platforms"][platform]["hash"] = current_hash

        import time
        self.state[key]["platforms"][platform]["built_at"] = time.time()

    def save(self) -> None:
        """持久化状态。"""
        self._save()

    def summary(self) -> dict:
        """返回构建状态摘要。"""
        total = len(self.state)
        platforms: dict[str, int] = {}
        for entry in self.state.values():
            for p in entry.get("platforms", {}):
                platforms[p] = platforms.get(p, 0) + 1
        return {"total_entries": total, "platforms": platforms}


def _file_hash(file_path: Path) -> str:
    """计算文件内容的 SHA256 hash。"""
    h = hashlib.sha256()
    try:
        h.update(file_path.read_bytes())
    except (IOError, OSError):
        return ""
    return h.hexdigest()[:12]
