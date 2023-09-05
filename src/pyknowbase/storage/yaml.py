from typing import Optional
from pathlib import Path

from . import StrPath
from .memory import InMemoryKnowledgeBase, MutableInMemoryKnowledgeBase
from ..model import Articles


class YamlKnowledgeBase(InMemoryKnowledgeBase):

    _filepath: Optional[Path] = None

    def __init__(self, filename: StrPath, name: Optional[str] = None) -> None:
        try:
            import yaml
        except ImportError:
            raise ValueError(
                "Could not import pyyaml python package. "
                "Please install it with `pip install pyyaml`."
            )
        self.yaml = yaml
        self._filepath = Path(filename)
        self.name = name or self._filepath.name
        if self._filepath.is_file():
            data = self.yaml.safe_load(self._filepath.read_text())
            articles = Articles.model_validate(data).root
            self._index = { a.id: a for a in articles }
        else:
            self._index = {}


class MutableYamlKnowledgeBase(YamlKnowledgeBase, MutableInMemoryKnowledgeBase):

    def save(self):
        articles = Articles(list(self._index.values()))
        data = articles.model_dump()
        with open(self._filepath, 'w') as f:
            self.yaml.dump(data, f)
