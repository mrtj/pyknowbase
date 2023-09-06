from typing import Union, Optional, List, Iterable
from abc import ABC, abstractmethod
import os
from pathlib import Path

from .memory import InMemoryKnowledgeBase, MutableInMemoryKnowledgeBase
from ..model import Article

StrPath = Union[str, os.PathLike]

class FileKnowledgeBase(InMemoryKnowledgeBase):
    """Abstract base class for knowledge bases that load the articles from a local file.

    The FileKnowledgeBase maintains a cache of the articles in the memory.

    Args:
        filename (StrPath): The file name
        name (Optional[str]): The name of the knowledge base. If None, FileKnowledgeBase will
            generate a name based on the file name. Defaults to None.
    """

    filepath: Path

    def __init__(self, filename: StrPath, name: Optional[str] = None) -> None:
        self.filepath = Path(filename)
        self.name = name or self.filepath.name
        if self.filepath.is_file():
            articles = self.load()
            self.index = { a.id: a for a in articles }
        else:
            self.index = {}

    @abstractmethod
    def load(self, **kwargs) -> List[Article]:
        """Abstract method to load the articles from the file.

        Returns:
            List[Article]: A list of the loaded articles.
        """
        ...


class MutableFileKnowledgeBase(FileKnowledgeBase, MutableInMemoryKnowledgeBase):
    """Abstract base class for knowledge bases that loads and save articles from local files.

    Mutating the knowledge base changes the articles only in the in-memory cache and they are not
    saved automatically. Users should explicitly call the save method.
    """

    def save(self, **kwargs) -> None:
        """Saves the in-memory copy of the articles to the file."""
        self.do_save(articles=self.index.values(), **kwargs)

    @abstractmethod
    def do_save(self, articles: Iterable[Article], **kwargs) -> None:
        """Abstract method to save the articles to the file.

        Args:
            articles (Iterable[Article]): The articles to be saved.
        """
        ...
