from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Domain:
    id: str
    name: str = ""
    perspective: str = ""
    files: list[str] = field(default_factory=list)
    vocabulary: list[str] = field(default_factory=list)


@dataclass
class Ontology:
    id: str
    name: str = ""
    label: str = ""
    perspective: str = ""
    description: str = ""
    pattern: str = ""
    source_files: list[str] = field(default_factory=list)


@dataclass
class Instance:
    id: str
    ontology: str = ""
    subject: str = ""
    source: str = ""
    article: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class Relation:
    id: str
    source_ontology: str = ""
    target_ontology: str = ""
    source_instance: str = ""
    target_instance: str = ""
    relation: str = ""
    description: str = ""
    detail: str = ""
