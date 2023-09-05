from typing import Dict, Any
from collections.abc import Mapping, MutableMapping
from pydantic import BaseModel

class Article(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}

class KnowledgeBase(Mapping[str, Article]):
    name: str

class MutableKnowledgeBase(KnowledgeBase, MutableMapping[str, Article]):

    def append(self, article: Article) -> None:
        self[article.id] = article

