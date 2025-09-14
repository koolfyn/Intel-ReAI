from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """
    Smart content retrieval engine using TF-IDF similarity scoring
    and multi-criteria ranking for relevant content selection.
    """

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents='unicode'
        )
        self.is_fitted = False

    def retrieve_relevant_content(
        self,
        processed_query: Dict[str, Any],
        posts: List[Dict[str, Any]],
        comments: List[Dict[str, Any]],
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rank relevant content based on query similarity.

        Args:
            processed_query: Processed query from QueryProcessor
            posts: List of post dictionaries
            comments: List of comment dictionaries
            max_results: Maximum number of results to return

        Returns:
            List of ranked content items with relevance scores
        """
        try:
            # Combine posts and comments
            all_content = self._combine_content(posts, comments)

            if not all_content:
                return []

            # Calculate TF-IDF similarity
            similarity_scores = self._calculate_similarity(
                processed_query, all_content
            )

            # Apply multi-criteria ranking
            ranked_content = self._rank_content(
                all_content, similarity_scores, processed_query
            )

            # Apply diversity filter
            diverse_content = self._apply_diversity_filter(
                ranked_content, max_results
            )

            return diverse_content

        except Exception as e:
            logger.error(f"Error retrieving relevant content: {e}")
            return []

    def _combine_content(
        self,
        posts: List[Dict[str, Any]],
        comments: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine posts and comments into a unified content list."""
        all_content = []

        # Add posts
        for post in posts:
            all_content.append({
                'id': post['id'],
                'type': 'post',
                'title': post.get('title', ''),
                'content': post.get('content', ''),
                'author': post.get('author', 'Unknown'),
                'score': post.get('score', 0),
                'created_at': post.get('created_at', ''),
                'subreddit_id': post.get('subreddit_id'),
                'searchable_text': f"{post.get('title', '')} {post.get('content', '')}"
            })

        # Add comments
        for comment in comments:
            all_content.append({
                'id': comment['id'],
                'type': 'comment',
                'title': '',  # Comments don't have titles
                'content': comment.get('content', ''),
                'author': comment.get('author', 'Unknown'),
                'score': comment.get('score', 0),
                'created_at': comment.get('created_at', ''),
                'post_id': comment.get('post_id'),
                'searchable_text': comment.get('content', '')
            })

        return all_content

    def _calculate_similarity(
        self,
        processed_query: Dict[str, Any],
        content: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Calculate TF-IDF similarity between query and content."""
        try:
            # Prepare texts for TF-IDF
            query_text = processed_query['cleaned_query']
            content_texts = [item['searchable_text'] for item in content]

            # Combine query and content for fitting
            all_texts = [query_text] + content_texts

            # Fit TF-IDF vectorizer
            if not self.is_fitted:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
                self.is_fitted = True
            else:
                tfidf_matrix = self.tfidf_vectorizer.transform(all_texts)

            # Calculate similarity
            query_vector = tfidf_matrix[0:1]
            content_vectors = tfidf_matrix[1:]

            similarity_scores = cosine_similarity(query_vector, content_vectors)[0]

            return similarity_scores

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return np.zeros(len(content))

    def _rank_content(
        self,
        content: List[Dict[str, Any]],
        similarity_scores: np.ndarray,
        processed_query: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply multi-criteria ranking to content."""
        ranked_content = []

        for i, item in enumerate(content):
            # Base similarity score
            similarity_score = float(similarity_scores[i])

            # Recency score (newer content gets higher score)
            recency_score = self._calculate_recency_score(item['created_at'])

            # Popularity score (higher score content gets higher score)
            popularity_score = self._calculate_popularity_score(item['score'])

            # Content type bonus
            type_bonus = 1.2 if item['type'] == 'post' else 1.0

            # Calculate final score
            final_score = (
                similarity_score * 0.5 +  # 50% similarity
                recency_score * 0.2 +     # 20% recency
                popularity_score * 0.2 +  # 20% popularity
                type_bonus * 0.1          # 10% type bonus
            )

            # Add scores to item
            item['similarity_score'] = similarity_score
            item['recency_score'] = recency_score
            item['popularity_score'] = popularity_score
            item['final_score'] = final_score

            ranked_content.append(item)

        # Sort by final score
        ranked_content.sort(key=lambda x: x['final_score'], reverse=True)

        return ranked_content

    def _calculate_recency_score(self, created_at: str) -> float:
        """Calculate recency score based on creation time."""
        try:
            if not created_at:
                return 0.5  # Default score for missing dates

            # Parse datetime
            if isinstance(created_at, str):
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            else:
                created_dt = created_at

            # Calculate days since creation
            days_ago = (datetime.now(created_dt.tzinfo) - created_dt).days

            # Score decreases with age (exponential decay)
            if days_ago <= 1:
                return 1.0
            elif days_ago <= 7:
                return 0.8
            elif days_ago <= 30:
                return 0.6
            elif days_ago <= 90:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.error(f"Error calculating recency score: {e}")
            return 0.5

    def _calculate_popularity_score(self, score: int) -> float:
        """Calculate popularity score based on post/comment score."""
        try:
            # Normalize score to 0-1 range
            # Use sigmoid function for smooth scaling
            normalized_score = 1 / (1 + np.exp(-score / 10))
            return float(normalized_score)
        except Exception as e:
            logger.error(f"Error calculating popularity score: {e}")
            return 0.5

    def _apply_diversity_filter(
        self,
        ranked_content: List[Dict[str, Any]],
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Apply diversity filter to avoid duplicate topics."""
        if len(ranked_content) <= max_results:
            return ranked_content

        diverse_content = []
        used_authors = set()
        used_posts = set()

        for item in ranked_content:
            # Skip if we already have content from this author
            if item['author'] in used_authors and len(diverse_content) >= max_results // 2:
                continue

            # Skip if we already have a comment from this post
            if item['type'] == 'comment' and item['post_id'] in used_posts:
                continue

            diverse_content.append(item)
            used_authors.add(item['author'])

            if item['type'] == 'post':
                used_posts.add(item['id'])
            elif item['type'] == 'comment':
                used_posts.add(item['post_id'])

            if len(diverse_content) >= max_results:
                break

        return diverse_content
