from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ButtonDTO:
    label: str
    url: str


@dataclass
class SelectOptionDTO:
    label: str
    value: str


@dataclass
class SelectDTO:
    label: str
    options: list[SelectOptionDTO]
