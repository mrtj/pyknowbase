from typing import Dict, Iterator

from ..model import KnowledgeBase, MutableKnowledgeBase, Article

class InMemoryKnowledgeBase(KnowledgeBase):

    _index: Dict[str, Article]

    def __init__(self, name: str) -> None:
        self.name = name
        self._index = {}

    def __iter__(self) -> Iterator[str]:
        return iter(self._index.keys())

    def __len__(self) -> int:
        return len(self._index)

    def __getitem__(self, __key: str) -> Article:
        return self._index[__key]


class MutableInMemoryKnowledgeBase(InMemoryKnowledgeBase, MutableKnowledgeBase):

    def __setitem__(self, __key: str, __value: Article) -> None:
        self._index[__key] = __value

    def __delitem__(self, __key: str) -> None:
        del self._index[__key]
