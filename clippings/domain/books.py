from dataclasses import dataclass


@dataclass
class Book:
    id: str
    title: str
    author_id: str


@dataclass
class Author:
    id: str
    name: str
