from typing import Iterable, List, Optional
from pathlib import Path

from pyknowbase.model import Article

from . import StrPath
from .file import FileKnowledgeBase, MutableFileKnowledgeBase
from ..model import Articles


class YamlKnowledgeBase(FileKnowledgeBase):

    def __init__(self, filename: StrPath, name: Optional[str] = None) -> None:
        super().__init__(filename=filename, name=name)
        try:
            import yaml
        except ImportError:
            raise ValueError(
                "Could not import pyyaml python package. "
                "Please install it with `pip install pyyaml`."
            )
        self.yaml = yaml

    def load(self, **kwargs) -> List[Article]:
        data = self.yaml.safe_load(self.filepath.read_text())
        return Articles.model_validate(data).root


class MutableYamlKnowledgeBase(YamlKnowledgeBase, MutableFileKnowledgeBase):

    def do_save(self, articles: Iterable[Article], **kwargs) -> None:
        arts = Articles(list(articles))
        data = arts.model_dump()
        with open(self.filepath, 'w') as f:
            self.yaml.dump(data, f)
