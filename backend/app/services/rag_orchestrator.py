from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from ..models import Post, Subreddit, Comment
from .query_processor import QueryProcessor
from .retrieval_engine import RetrievalEngine
from .context_builder import ContextBuilder
from .claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class RAGOrchestrator:
    """
    Main orchestration layer for the RAG pipeline.
    Coordinates query processing, content retrieval, context building,
    and response generation.
    """

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.retrieval_engine = RetrievalEngine()
        self.context_builder = ContextBuilder()
        self.claude_service = ClaudeService()

    async def process_query(
        self,
        query: str,
        subreddit_id: Optional[int] = None,
        context: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query: User query string
            subreddit_id: Optional subreddit ID to limit search
            context: Optional additional context
            db: Database session

        Returns:
            Dictionary containing response, citations, and sources
        """
        try:
            # Step 1: Process the query
            processed_query = self.query_processor.process_query(query)
            logger.info(f"Processed query: {processed_query['intent']} - {processed_query['keywords']}")

            # Step 2: Retrieve content from database
            posts, comments = await self._retrieve_content_from_db(
                subreddit_id, db, processed_query
            )
            logger.info(f"Retrieved {len(posts)} posts and {len(comments)} comments")

            # Step 3: Rank and filter content
            ranked_content = self.retrieval_engine.retrieve_relevant_content(
                processed_query, posts, comments
            )
            logger.info(f"Ranked {len(ranked_content)} content items")

            # Step 4: Build context
            context_data = self.context_builder.build_context(
                query, ranked_content
            )
            logger.info(f"Built context with {context_data['item_count']} items")

            # Step 5: Generate response with Claude
            response = await self._generate_response(
                query, context_data, processed_query
            )

            return response

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now.",
                "citations": [],
                "sources": []
            }

    async def _retrieve_content_from_db(
        self,
        subreddit_id: Optional[int],
        db: Session,
        processed_query: Dict[str, Any]
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Retrieve posts and comments from database."""
        try:
            # Get posts
            if subreddit_id:
                posts_query = db.query(Post).filter(Post.subreddit_id == subreddit_id)
            else:
                posts_query = db.query(Post)

            # Apply basic filtering based on query hints
            if 'time_sensitive' in processed_query['context_hints']:
                # For time-sensitive queries, limit to recent posts
                from datetime import datetime, timedelta
                recent_date = datetime.now() - timedelta(days=7)
                posts_query = posts_query.filter(Post.created_at >= recent_date)

            # Order by score and limit
            posts_query = posts_query.order_by(Post.score.desc()).limit(50)
            posts = posts_query.all()

            # Format posts
            formatted_posts = []
            for post in posts:
                formatted_posts.append({
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "author": post.author.username,
                    "score": post.score,
                    "created_at": post.created_at.isoformat(),
                    "subreddit_id": post.subreddit_id
                })

            # Get comments for top posts
            comments = []
            for post in posts[:20]:  # Limit to top 20 posts
                post_comments = db.query(Comment).filter(
                    Comment.post_id == post.id
                ).order_by(Comment.score.desc()).limit(10).all()

                for comment in post_comments:
                    comments.append({
                        "id": comment.id,
                        "content": comment.content,
                        "author": comment.author.username,
                        "post_id": comment.post_id,
                        "score": comment.score,
                        "created_at": comment.created_at.isoformat()
                    })

            return formatted_posts, comments

        except Exception as e:
            logger.error(f"Error retrieving content from database: {e}")
            return [], []

    async def _generate_response(
        self,
        query: str,
        context_data: Dict[str, Any],
        processed_query: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate response using Claude with the built context."""
        try:
            # Build the prompt for Claude
            prompt = self._build_claude_prompt(query, context_data, processed_query)

            # Generate response
            response_text = await self.claude_service.generate_response(
                prompt, max_tokens=1200, temperature=0.7
            )

            # Parse response if it's JSON, otherwise use as-is
            try:
                import json
                response_data = json.loads(response_text)
                if isinstance(response_data, dict) and 'response' in response_data:
                    return response_data
            except json.JSONDecodeError:
                pass

            # Return structured response
            return {
                "response": response_text,
                "citations": context_data['citations'],
                "sources": context_data['sources']
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I'm sorry, I couldn't generate a proper response.",
                "citations": context_data.get('citations', []),
                "sources": context_data.get('sources', [])
            }

    def _build_claude_prompt(
        self,
        query: str,
        context_data: Dict[str, Any],
        processed_query: Dict[str, Any]
    ) -> str:
        """Build the prompt for Claude."""
        context_text = context_data['context_text']
        citations = context_data['citations']

        prompt = f"""
You are an AI assistant helping users find information in a Reddit-like community.
Based on the following context, answer the user's question clearly and helpfully.

User Question: {query}

Context from community posts and comments:
{context_text}

Instructions:
1. Answer the question based on the provided context
2. Cite specific posts/comments when relevant using the citation information
3. If the context doesn't contain enough information, say so
4. Be helpful and conversational
5. Include relevant excerpts from the sources

Citation format: [Source X] where X is the citation number

Please provide a JSON response with:
- "response": your answer to the question
- "citations": array of citation objects with post_id, post_title, relevance_score, excerpt
- "sources": array of source objects with type, id, title, url

Available citations:
"""

        # Add citation information
        for i, citation in enumerate(citations, 1):
            prompt += f"""
Citation {i}:
- Post ID: {citation['post_id']}
- Title: {citation['post_title']}
- Author: {citation['author']}
- Score: {citation['score']}
- Excerpt: {citation['excerpt']}
- Relevance: {citation['relevance_score']}
"""

        return prompt
