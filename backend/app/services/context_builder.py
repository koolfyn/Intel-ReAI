from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Builds and formats context from retrieved content for Claude prompts.
    Handles citation extraction and context optimization.
    """

    def __init__(self):
        self.max_context_length = 4000  # Max characters for context
        self.max_items = 5  # Maximum number of items to include

    def build_context(
        self,
        query: str,
        ranked_items: List[Dict[str, Any]],
        max_context: int = 5
    ) -> Dict[str, Any]:
        """
        Build context from ranked content items for Claude prompt.

        Args:
            query: Original user query
            ranked_items: List of ranked content items
            max_context: Maximum number of items to include

        Returns:
            Dictionary containing formatted context and citations
        """
        try:
            # Select top items
            selected_items = ranked_items[:max_context]

            # Extract citations
            citations = self._extract_citations(selected_items)

            # Build context text
            context_text = self._build_context_text(query, selected_items)

            # Build sources list
            sources = self._build_sources_list(selected_items)

            return {
                'context_text': context_text,
                'citations': citations,
                'sources': sources,
                'item_count': len(selected_items),
                'context_length': len(context_text)
            }

        except Exception as e:
            logger.error(f"Error building context: {e}")
            return {
                'context_text': f"Query: {query}\n\nNo relevant content found.",
                'citations': [],
                'sources': [],
                'item_count': 0,
                'context_length': 0
            }

    def _extract_citations(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract citation information from content items."""
        citations = []

        for item in items:
            # Extract relevant excerpt (first 200 chars of content)
            excerpt = self._extract_excerpt(item['content'])

            citation = {
                'post_id': item.get('post_id', item['id']),
                'post_title': item.get('title', 'Comment'),
                'relevance_score': round(item.get('similarity_score', 0), 3),
                'excerpt': excerpt,
                'author': item.get('author', 'Unknown'),
                'score': item.get('score', 0),
                'created_at': item.get('created_at', ''),
                'type': item.get('type', 'content')
            }

            citations.append(citation)

        return citations

    def _extract_excerpt(self, content: str, max_length: int = 200) -> str:
        """Extract a relevant excerpt from content."""
        if not content:
            return ""

        # Clean content
        cleaned = content.strip()

        # Truncate if too long
        if len(cleaned) <= max_length:
            return cleaned

        # Try to find a good breaking point
        truncated = cleaned[:max_length]
        last_period = truncated.rfind('.')
        last_space = truncated.rfind(' ')

        # Use the last period if it's in the last 50 characters
        if last_period > max_length - 50:
            return truncated[:last_period + 1] + "..."

        # Otherwise use the last space
        if last_space > max_length - 30:
            return truncated[:last_space] + "..."

        # Fallback to hard truncation
        return truncated + "..."

    def _build_context_text(
        self,
        query: str,
        items: List[Dict[str, Any]]
    ) -> str:
        """Build the main context text for Claude prompt."""
        context_parts = [f"User Query: {query}\n"]

        for i, item in enumerate(items, 1):
            item_type = item.get('type', 'content')
            title = item.get('title', '')
            content = item.get('content', '')
            author = item.get('author', 'Unknown')
            score = item.get('score', 0)

            # Format based on type
            if item_type == 'post':
                context_parts.append(
                    f"Post {i}: {title}\n"
                    f"Author: {author} | Score: {score}\n"
                    f"Content: {content}\n"
                )
            else:  # comment
                context_parts.append(
                    f"Comment {i}:\n"
                    f"Author: {author} | Score: {score}\n"
                    f"Content: {content}\n"
                )

        return "\n".join(context_parts)

    def _build_sources_list(
        self,
        items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Build sources list for response."""
        sources = []

        for item in items:
            source = {
                'type': item.get('type', 'content'),
                'id': item['id'],
                'title': item.get('title', 'Comment'),
                'url': self._generate_url(item)
            }
            sources.append(source)

        return sources

    def _generate_url(self, item: Dict[str, Any]) -> str:
        """Generate URL for content item."""
        item_type = item.get('type', 'content')
        item_id = item['id']

        if item_type == 'post':
            return f"/posts/{item_id}"
        else:  # comment
            post_id = item.get('post_id', item_id)
            return f"/posts/{post_id}#comment-{item_id}"

    def optimize_context_length(
        self,
        context: Dict[str, Any],
        max_length: int = None
    ) -> Dict[str, Any]:
        """Optimize context length if it exceeds limits."""
        if max_length is None:
            max_length = self.max_context_length

        if context['context_length'] <= max_length:
            return context

        # Truncate context text
        context_text = context['context_text']
        if len(context_text) > max_length:
            truncated_text = context_text[:max_length]
            # Find last complete sentence
            last_period = truncated_text.rfind('.')
            if last_period > max_length - 100:
                context_text = truncated_text[:last_period + 1]
            else:
                context_text = truncated_text + "..."

        return {
            **context,
            'context_text': context_text,
            'context_length': len(context_text)
        }
