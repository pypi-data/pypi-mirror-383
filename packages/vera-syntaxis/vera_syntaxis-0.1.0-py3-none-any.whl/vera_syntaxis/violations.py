"""Data models for representing architectural violations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True)
class Violation:
    """Represents a single architectural rule violation."""
    rule_id: str
    message: str
    file_path: Path
    line_number: int
    column_number: Optional[int] = None

    def __str__(self) -> str:
        location = f"{self.file_path}:{self.line_number}"
        if self.column_number:
            location += f":{self.column_number}"
        return f"[{self.rule_id}] {location} - {self.message}"
