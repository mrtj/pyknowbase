from typing import Iterable, Iterator, Dict, List, Optional
from pathlib import Path

from pyknowbase.model import Article

from .file import FileKnowledgeBase, MutableFileKnowledgeBase
from ..model import Articles

class JsonKnowledgeBase(FileKnowledgeBase):

    def load(self, **kwargs) -> List[Article]:
        return Articles.model_validate_json(self.filepath.read_text(), **kwargs).root


class MutableJSONFileKnowledgeBase(JsonKnowledgeBase, MutableFileKnowledgeBase):

    def do_save(self, articles: Iterable[Article], **kwargs) -> None:
        arts =  Articles(list(articles))
        self.filepath.write_text(arts.model_dump_json(**kwargs))
