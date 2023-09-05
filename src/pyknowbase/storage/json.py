from typing import Iterator, Union, List, Dict, Optional
import os
from pathlib import Path

from pydantic import RootModel

from pyknowbase.model import Article

from ..model import KnowledgeBase, MutableKnowledgeBase, Article

StrPath = Union[str, os.PathLike]
Articles = RootModel[List[Article]]

class JSONFileKnowledgeBase(KnowledgeBase):

    _index: Dict[str, Article]
    _filepath: Path

    def __init__(self, filename: StrPath, name: Optional[str] = None) -> None:
        self._filepath = Path(filename)
        self.name = name or self._filepath.name
        articles = Articles.model_validate_json(self._filepath.read_text()).root
        self._index = { a.id: a for a in articles }

    def __iter__(self) -> Iterator[str]:
        return iter(self._index.keys())

    def __len__(self) -> int:
        return len(self._index)

    def __getitem__(self, __key: str) -> Article:
        return self._index[__key]


class MutableJSONFileKnowledgeBase(JSONFileKnowledgeBase, MutableKnowledgeBase):

    def __setitem__(self, __key: str, __value: Article) -> None:
        self._index[__key] = __value

    def __delitem__(self, __key: str) -> None:
        del self._index[__key]

    def save(self, **kwargs) -> None:
        articles = Articles(list(self._index.values()))
        self._filepath.write_text(articles.model_dump_json(**kwargs))
