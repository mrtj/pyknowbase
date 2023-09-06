from typing import Dict, Iterator

from pyknowbase.model import Article

from ..model import KnowledgeBase, MutableKnowledgeBase, Article

class InMemoryKnowledgeBase(KnowledgeBase):

    index: Dict[str, Article]

    def __init__(self, name: str) -> None:
        self.name = name
        self.index = {}

    def __iter__(self) -> Iterator[Article]:
        return iter(self.index.values())

    def __getitem__(self, __key: str) -> Article:
        return self.index[__key]


class MutableInMemoryKnowledgeBase(InMemoryKnowledgeBase, MutableKnowledgeBase):

    def __setitem__(self, __key: str, __value: Article) -> None:
        self.index[__key] = __value

    def __delitem__(self, __key: str) -> None:
        del self.index[__key]
