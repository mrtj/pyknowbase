from typing import Iterator, Dict, Optional
from pathlib import Path

from pyknowbase.model import Article

from . import StrPath
from .memory import InMemoryKnowledgeBase, MutableInMemoryKnowledgeBase
from ..model import Articles

class JSONFileKnowledgeBase(InMemoryKnowledgeBase):

    _filepath: Path

    def __init__(self, filename: StrPath, name: Optional[str] = None) -> None:
        self._filepath = Path(filename)
        self.name = name or self._filepath.name
        if self._filepath.is_file():
            articles = Articles.model_validate_json(self._filepath.read_text()).root
            self._index = { a.id: a for a in articles }
        else:
            self._index = {}


class MutableJSONFileKnowledgeBase(JSONFileKnowledgeBase, MutableInMemoryKnowledgeBase):

    def save(self, **kwargs) -> None:
        articles = Articles(list(self._index.values()))
        self._filepath.write_text(articles.model_dump_json(**kwargs))
