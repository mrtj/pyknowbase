from typing import Dict, Any, List
from collections.abc import Mapping, MutableMapping
from pydantic import BaseModel, RootModel

class Article(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = {}

Articles = RootModel[List[Article]]

class KnowledgeBase(Mapping[str, Article]):
    name: str

class MutableKnowledgeBase(KnowledgeBase, MutableMapping[str, Article]):

    def append(self, article: Article) -> None:
        self[article.id] = article

    def copy_from(self, other: KnowledgeBase) -> None:
        for article in other.values():
            self.append(article)
