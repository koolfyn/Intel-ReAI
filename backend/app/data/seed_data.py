from sqlalchemy.orm import Session
from ..models import User, Subreddit, Post, Comment
from .fake_data import (
    FAKE_USERS, FAKE_SUBREDDITS, FAKE_POSTS, FAKE_COMMENTS,
    get_random_date, generate_fake_posts, generate_fake_comments
)
import random

def seed_database(db: Session):
    """Seed the database with fake data"""

    # Clear existing data
    db.query(Comment).delete()
    db.query(Post).delete()
    db.query(Subreddit).delete()
    db.query(User).delete()
    db.commit()

    # Create users
    users = []
    for user_data in FAKE_USERS:
        user = User(**user_data)
        db.add(user)
        users.append(user)
    db.commit()

    # Create subreddits
    subreddits = []
    for subreddit_data in FAKE_SUBREDDITS:
        subreddit = Subreddit(
            **subreddit_data,
            created_by=random.choice(users).id
        )
        db.add(subreddit)
        subreddits.append(subreddit)
    db.commit()

    # Create posts
    posts = []
    for post_data in FAKE_POSTS:
        post = Post(
            **post_data,
            author_id=random.choice(users).id,
            subreddit_id=random.choice(subreddits).id,
            upvotes=random.randint(0, 100),
            downvotes=random.randint(0, 20),
            created_at=get_random_date(30)
        )
        db.add(post)
        posts.append(post)

    # Generate additional fake posts
    additional_posts = generate_fake_posts(20)
    for post_data in additional_posts:
        post = Post(
            **post_data,
            author_id=random.choice(users).id,
            subreddit_id=random.choice(subreddits).id,
            upvotes=random.randint(0, 50),
            downvotes=random.randint(0, 10),
            created_at=get_random_date(30)
        )
        db.add(post)
        posts.append(post)

    db.commit()

    # Create comments
    for post in posts:
        # Each post gets 2-8 comments
        num_comments = random.randint(2, 8)
        for _ in range(num_comments):
            comment = Comment(
                content=random.choice(FAKE_COMMENTS),
                author_id=random.choice(users).id,
                post_id=post.id,
                upvotes=random.randint(0, 20),
                downvotes=random.randint(0, 5),
                created_at=get_random_date(30)
            )
            db.add(comment)

    # Generate additional fake comments
    additional_comments = generate_fake_comments(50)
    for comment_text in additional_comments:
        comment = Comment(
            content=comment_text,
            author_id=random.choice(users).id,
            post_id=random.choice(posts).id,
            upvotes=random.randint(0, 15),
            downvotes=random.randint(0, 3),
            created_at=get_random_date(30)
        )
        db.add(comment)

    db.commit()

    print(f"Seeded database with:")
    print(f"- {len(users)} users")
    print(f"- {len(subreddits)} subreddits")
    print(f"- {len(posts)} posts")
    print(f"- {db.query(Comment).count()} comments")
