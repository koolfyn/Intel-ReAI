from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Post, Subreddit, Comment
from .claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class AICompanionService:
    def __init__(self):
        self.claude_service = ClaudeService()

    async def query_companion(
        self,
        query: str,
        subreddit_id: Optional[int] = None,
        context: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Query the AI companion with context from posts and comments"""
        try:
            # Get relevant posts based on query
            if subreddit_id:
                posts = db.query(Post).filter(Post.subreddit_id == subreddit_id).all()
            else:
                posts = db.query(Post).all()

            # Get relevant comments
            comments = []
            for post in posts[:10]:  # Limit to avoid too much context
                post_comments = db.query(Comment).filter(Comment.post_id == post.id).limit(5).all()
                comments.extend(post_comments)

            # Format posts for AI
            formatted_posts = []
            for post in posts[:10]:
                formatted_posts.append({
                    "id": post.id,
                    "title": post.title,
                    "content": post.content,
                    "author": post.author.username,
                    "score": post.score,
                    "created_at": post.created_at.isoformat()
                })

            # Format comments for AI
            formatted_comments = []
            for comment in comments[:20]:
                formatted_comments.append({
                    "id": comment.id,
                    "content": comment.content,
                    "author": comment.author.username,
                    "post_id": comment.post_id,
                    "score": comment.score,
                    "created_at": comment.created_at.isoformat()
                })

            # Use Claude service to search and respond
            result = await self.claude_service.search_and_respond(
                query=query,
                posts=formatted_posts,
                comments=formatted_comments
            )

            return result

        except Exception as e:
            logger.error(f"Error in AI companion query: {e}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now.",
                "citations": [],
                "sources": []
            }

    async def generate_faq(
        self,
        subreddit: Subreddit,
        posts: List[Post]
    ) -> List[Dict[str, Any]]:
        """Generate FAQ for a subreddit based on recent posts"""
        try:
            # Extract common questions from posts
            post_titles = [post.title for post in posts]
            post_contents = [post.content for post in posts]

            context = f"""
            Subreddit: {subreddit.display_name}
            Description: {subreddit.description or 'No description'}

            Recent post titles:
            {chr(10).join(post_titles[:10])}

            Recent post contents:
            {chr(10).join([content[:200] + '...' for content in post_contents[:5]])}
            """

            prompt = f"""
            Based on the following subreddit context, generate 5-10 frequently asked questions that would be helpful for new users:

            {context}

            Please provide a JSON response with an array of FAQ objects, each containing:
            - "question": string
            - "answer": string (brief, helpful answer)
            - "category": string (e.g., "Getting Started", "Technical", "Community")
            """

            response = await self.claude_service.generate_response(prompt, max_tokens=1000)

            # Try to parse JSON response
            import json
            try:
                faqs = json.loads(response)
                if isinstance(faqs, list):
                    return faqs
                else:
                    return []
            except json.JSONDecodeError:
                # Fallback: return basic FAQ
                return [
                    {
                        "question": f"What is r/{subreddit.name} about?",
                        "answer": subreddit.description or f"Discussion about {subreddit.display_name}",
                        "category": "Getting Started"
                    },
                    {
                        "question": "What are the community rules?",
                        "answer": subreddit.rules or "Please be respectful and follow reddiquette",
                        "category": "Community"
                    }
                ]

        except Exception as e:
            logger.error(f"Error generating FAQ: {e}")
            return []

    async def analyze_trending_topics(
        self,
        subreddit: Subreddit,
        posts: List[Post]
    ) -> List[Dict[str, Any]]:
        """Analyze trending topics in a subreddit"""
        try:
            # Extract keywords and topics from posts
            post_titles = [post.title for post in posts]
            post_contents = [post.content for post in posts]

            context = f"""
            Subreddit: {subreddit.display_name}

            Recent post titles:
            {chr(10).join(post_titles)}

            Recent post contents (first 200 chars each):
            {chr(10).join([content[:200] + '...' for content in post_contents[:10]])}
            """

            prompt = f"""
            Analyze the following posts to identify trending topics and themes:

            {context}

            Please provide a JSON response with an array of trending topic objects, each containing:
            - "topic": string (the trending topic)
            - "frequency": number (how often it appears, 1-10)
            - "description": string (brief description of why it's trending)
            - "related_posts": array of post titles that relate to this topic
            """

            response = await self.claude_service.generate_response(prompt, max_tokens=800)

            # Try to parse JSON response
            import json
            try:
                topics = json.loads(response)
                if isinstance(topics, list):
                    return topics
                else:
                    return []
            except json.JSONDecodeError:
                # Fallback: return basic topics
                return [
                    {
                        "topic": "General Discussion",
                        "frequency": 5,
                        "description": "General posts and discussions",
                        "related_posts": post_titles[:3]
                    }
                ]

        except Exception as e:
            logger.error(f"Error analyzing trending topics: {e}")
            return []
