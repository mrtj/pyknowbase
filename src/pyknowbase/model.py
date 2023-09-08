from typing import Dict, Any, Iterator, List, Optional
from abc import ABC, abstractmethod
from collections.abc import Iterable

from datetime import datetime, timezone

from pydantic import BaseModel, RootModel, Field

class Article(BaseModel):
    """Knowledge base article."""
    id: str
    text: str
    metadata: Dict[str, Any] = {}
    last_modified: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


Articles = RootModel[List[Article]]


class KnowledgeBase(Iterable[Article]):
    """Abstract base class for knowledge bases.

    A knowledge base should implement the Iterable protocol, and provide access to the articles
    based on their identifier via the __getitem__ method.
    """
    name: str
    metadata: Dict[str, Any] = {}

    def __getitem__(self, __key: str) -> Article:
        raise NotImplementedError("KnowledgeBase.__getitem__ is an abstract method.")

    def __iter__(self) -> Iterator[Article]:
        raise NotImplementedError("KnowledgeBase.__iter__ is an abstract method.")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}, metadata={self.metadata}>"


class MutableKnowledgeBase(KnowledgeBase):
    """Abstract base class for mutable knowledge bases.

    A mutable knowledge base can mutate the managed articles implementing the __setitem__ and
    __getitem__ methods.
    """

    @abstractmethod
    def __setitem__(self, __key: str, __value: Article) -> None:
        ...

    @abstractmethod
    def __delitem__(self, __key: str) -> None:
        ...

    def add(self, article: Article) -> None:
        """Adds a new article to the knowledge base.

        If the knowledge base already contains an article with the same identifier, the existing
        article will be overwritten.

        Args:
            article (Article): An article to be added to the knowledge base.
        """
        self[article.id] = article

    def copy_from(self, other: KnowledgeBase) -> None:
        """Copies all articles from another knowledge base to this one.

        Args:
            other (KnowledgeBase): The other knowledge base.
        """
        for article in other:
            self.add(article)
