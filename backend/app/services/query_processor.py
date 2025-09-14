from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Processes user queries to extract keywords, intent, and search terms
    for improved content retrieval.
    """

    def __init__(self):
        # Common stop words for filtering
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }

        # Query intent patterns
        self.intent_patterns = {
            'question': r'\?|what|how|why|when|where|who|which|can|could|should|would',
            'search': r'find|search|look|show|get|need|want',
            'help': r'help|assist|support|guide|explain|tell'
        }

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query to extract useful information for retrieval.

        Args:
            query: Raw user query string

        Returns:
            Dictionary containing processed query information
        """
        try:
            # Clean and normalize query
            cleaned_query = self._clean_query(query)

            # Extract keywords
            keywords = self._extract_keywords(cleaned_query)

            # Identify query intent
            intent = self._identify_intent(cleaned_query)

            # Generate search terms
            search_terms = self._generate_search_terms(keywords, intent)

            # Extract context hints
            context_hints = self._extract_context_hints(cleaned_query)

            return {
                'original_query': query,
                'cleaned_query': cleaned_query,
                'keywords': keywords,
                'intent': intent,
                'search_terms': search_terms,
                'context_hints': context_hints,
                'query_length': len(cleaned_query.split())
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'original_query': query,
                'cleaned_query': query.lower().strip(),
                'keywords': query.lower().split(),
                'intent': 'search',
                'search_terms': [query.lower().strip()],
                'context_hints': [],
                'query_length': len(query.split())
            }

    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query string."""
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', query.strip())
        # Convert to lowercase
        return cleaned.lower()

    def _extract_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from the query."""
        # Split into words
        words = query.split()

        # Filter out stop words and short words
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) > 2
        ]

        return keywords

    def _identify_intent(self, query: str) -> str:
        """Identify the intent of the query."""
        query_lower = query.lower()

        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, query_lower):
                return intent

        return 'search'  # Default intent

    def _generate_search_terms(self, keywords: List[str], intent: str) -> List[str]:
        """Generate search terms based on keywords and intent."""
        search_terms = keywords.copy()

        # Add variations based on intent
        if intent == 'question':
            # For questions, keep the full query as a search term
            search_terms.append(' '.join(keywords))

        return search_terms

    def _extract_context_hints(self, query: str) -> List[str]:
        """Extract context hints that might help with retrieval."""
        hints = []

        # Look for time references
        time_patterns = [
            r'recent|latest|new|today|yesterday|this week|this month',
            r'old|previous|past|earlier|before'
        ]

        for pattern in time_patterns:
            if re.search(pattern, query):
                hints.append('time_sensitive')
                break

        # Look for specific content types
        content_patterns = {
            'posts': r'post|posts|submission|submissions',
            'comments': r'comment|comments|reply|replies',
            'users': r'user|users|author|authors|person|people'
        }

        for content_type, pattern in content_patterns.items():
            if re.search(pattern, query):
                hints.append(f'content_type_{content_type}')

        return hints
