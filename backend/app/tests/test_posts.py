import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, Subreddit, Post

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def test_data(setup_database):
    """Create test data"""
    db = TestingSessionLocal()

    # Create test user
    user = User(username="testuser", email="test@example.com", display_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create test subreddit
    subreddit = Subreddit(
        name="testsub",
        display_name="Test Subreddit",
        description="A test subreddit",
        created_by=user.id
    )
    db.add(subreddit)
    db.commit()
    db.refresh(subreddit)

    # Create test post
    post = Post(
        title="Test Post",
        content="This is a test post",
        author_id=user.id,
        subreddit_id=subreddit.id
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    yield {
        "user": user,
        "subreddit": subreddit,
        "post": post
    }

    db.close()

def test_get_posts(test_data):
    """Test getting posts"""
    client = TestClient(app)
    response = client.get("/api/v1/posts/")

    assert response.status_code == 200
    data = response.json()
    assert "posts" in data
    assert "pagination" in data
    assert len(data["posts"]) > 0

def test_get_post_by_id(test_data):
    """Test getting a specific post"""
    client = TestClient(app)
    post_id = test_data["post"].id
    response = client.get(f"/api/v1/posts/{post_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == post_id
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post"

def test_create_post(test_data):
    """Test creating a new post"""
    client = TestClient(app)
    subreddit_id = test_data["subreddit"].id

    post_data = {
        "title": "New Test Post",
        "content": "This is a new test post",
        "subreddit_id": subreddit_id,
        "post_type": "text"
    }

    response = client.post("/api/v1/posts/", json=post_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Test Post"
    assert data["content"] == "This is a new test post"
    assert data["subreddit_id"] == subreddit_id

def test_create_post_invalid_subreddit():
    """Test creating a post with invalid subreddit"""
    client = TestClient(app)

    post_data = {
        "title": "New Test Post",
        "content": "This is a new test post",
        "subreddit_id": 99999,  # Non-existent subreddit
        "post_type": "text"
    }

    response = client.post("/api/v1/posts/", json=post_data)
    assert response.status_code == 404

def test_update_post(test_data):
    """Test updating a post"""
    client = TestClient(app)
    post_id = test_data["post"].id

    update_data = {
        "title": "Updated Test Post",
        "content": "This is an updated test post"
    }

    response = client.put(f"/api/v1/posts/{post_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Test Post"
    assert data["content"] == "This is an updated test post"

def test_delete_post(test_data):
    """Test deleting a post"""
    client = TestClient(app)
    post_id = test_data["post"].id

    response = client.delete(f"/api/v1/posts/{post_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Post deleted successfully"

def test_upvote_post(test_data):
    """Test upvoting a post"""
    client = TestClient(app)
    post_id = test_data["post"].id

    response = client.post(f"/api/v1/posts/{post_id}/upvote")

    assert response.status_code == 200
    data = response.json()
    assert "upvotes" in data
    assert data["upvotes"] > 0

def test_downvote_post(test_data):
    """Test downvoting a post"""
    client = TestClient(app)
    post_id = test_data["post"].id

    response = client.post(f"/api/v1/posts/{post_id}/downvote")

    assert response.status_code == 200
    data = response.json()
    assert "downvotes" in data
    assert data["downvotes"] > 0
