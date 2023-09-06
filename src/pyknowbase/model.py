from typing import Dict, Any, List, Optional
from collections.abc import Mapping, MutableMapping

from datetime import datetime, timezone

from pydantic import BaseModel, RootModel

class Article(BaseModel):
    """Knowledge base article."""
    id: str
    text: str
    metadata: Optional[Dict[str, Any]] = None
    last_modified: datetime = datetime.now(timezone.utc)


Articles = RootModel[List[Article]]


class KnowledgeBase(Mapping[str, Article]):
    """Abstract base class for knowledge bases.

    A knowledge base should implement the Mapping protocol, and provide access to the articles
    based on their identifier.
    """
    name: str


class MutableKnowledgeBase(KnowledgeBase, MutableMapping[str, Article]):
    """Abstract base class for mutable knowledge bases.

    A mutable knowledge base can mutate the managed articles implementing the MutableMapping
    protocol.
    """

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
        for article in other.values():
            self.add(article)
