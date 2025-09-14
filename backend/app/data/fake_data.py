import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

# Sample users
FAKE_USERS = [
    {"username": "tech_guru", "email": "tech@example.com", "display_name": "Tech Guru"},
    {"username": "code_master", "email": "code@example.com", "display_name": "Code Master"},
    {"username": "ai_enthusiast", "email": "ai@example.com", "display_name": "AI Enthusiast"},
    {"username": "python_dev", "email": "python@example.com", "display_name": "Python Developer"},
    {"username": "web_designer", "email": "web@example.com", "display_name": "Web Designer"},
    {"username": "data_scientist", "email": "data@example.com", "display_name": "Data Scientist"},
    {"username": "startup_founder", "email": "startup@example.com", "display_name": "Startup Founder"},
    {"username": "open_source", "email": "opensource@example.com", "display_name": "Open Source Contributor"},
]

# Sample subreddits
FAKE_SUBREDDITS = [
    {
        "name": "programming",
        "display_name": "Programming",
        "description": "A community for discussing programming languages, frameworks, and best practices.",
        "rules": "1. Be respectful\n2. No spam\n3. Use proper code formatting\n4. Search before posting"
    },
    {
        "name": "artificial_intelligence",
        "display_name": "Artificial Intelligence",
        "description": "Discussion about AI, machine learning, and the future of technology.",
        "rules": "1. Keep discussions technical\n2. Cite sources\n3. No AI-generated content without disclosure\n4. Be constructive"
    },
    {
        "name": "web_development",
        "display_name": "Web Development",
        "description": "Frontend, backend, and full-stack web development discussions.",
        "rules": "1. Share your projects\n2. Ask for help\n3. Provide code examples\n4. Be helpful"
    },
    {
        "name": "startups",
        "display_name": "Startups",
        "description": "Entrepreneurship, startup advice, and business discussions.",
        "rules": "1. No self-promotion spam\n2. Share real experiences\n3. Be supportive\n4. Follow reddiquette"
    },
    {
        "name": "python",
        "display_name": "Python",
        "description": "Python programming language discussions and tutorials.",
        "rules": "1. Python-related content only\n2. Use proper formatting\n3. Search before asking\n4. Be helpful to beginners"
    }
]

# Sample posts
FAKE_POSTS = [
    {
        "title": "What's the best way to learn React in 2024?",
        "content": "I'm a backend developer looking to transition to full-stack. What's the most effective way to learn React? Should I start with the official docs or go with a course?",
        "post_type": "text"
    },
    {
        "title": "Building an AI-powered Reddit clone with Claude API",
        "content": "I'm working on a hackathon project that uses Claude API for content moderation and AI companion features. The AI can search through posts and provide answers with citations. Anyone else working on similar projects?",
        "post_type": "text"
    },
    {
        "title": "Python vs JavaScript: Which should I learn first?",
        "content": "I'm completely new to programming and want to know which language to start with. I'm interested in both web development and data science. What are your thoughts?",
        "post_type": "text"
    },
    {
        "title": "My startup failed after 2 years - here's what I learned",
        "content": "After 2 years of building my SaaS product, I had to shut it down. The main issues were: 1) Not validating the market properly, 2) Building too many features, 3) Not focusing on customer acquisition early enough. Happy to answer questions about the experience.",
        "post_type": "text"
    },
    {
        "title": "The future of AI in software development",
        "content": "With tools like GitHub Copilot and ChatGPT, how do you think AI will change software development? Will it replace developers or make us more productive?",
        "post_type": "text"
    },
    {
        "title": "FastAPI vs Django: Which framework for a new project?",
        "content": "I'm starting a new API project and can't decide between FastAPI and Django REST Framework. FastAPI seems faster and more modern, but Django has more built-in features. What would you choose?",
        "post_type": "text"
    },
    {
        "title": "How to handle authentication in a React + FastAPI app",
        "content": "I'm building a full-stack app with React frontend and FastAPI backend. What's the best way to handle JWT authentication? Should I store tokens in localStorage or cookies?",
        "post_type": "text"
    },
    {
        "title": "Data science career path: PhD vs Industry experience",
        "content": "I'm a recent CS graduate interested in data science. Should I pursue a PhD or jump straight into industry? I'm particularly interested in machine learning and AI applications.",
        "post_type": "text"
    }
]

# Sample comments
FAKE_COMMENTS = [
    "Great question! I'd recommend starting with the official React docs and building small projects.",
    "I've been using React for 3 years and still learn something new every day. The ecosystem is constantly evolving.",
    "Check out the React tutorial on their website - it's really well structured for beginners.",
    "I started with a Udemy course and then moved to the official docs. Both approaches work well.",
    "This is exactly what I needed! Thanks for sharing your experience.",
    "I'm working on something similar but using OpenAI's API. How's the Claude integration working for you?",
    "The citation feature sounds really interesting. How do you handle the vector search?",
    "I'd love to see a demo of this when it's ready!",
    "Python is great for data science, JavaScript for web development. Why not learn both?",
    "I started with Python and found it easier to understand programming concepts.",
    "JavaScript has more immediate visual feedback which can be motivating for beginners.",
    "It really depends on what you want to build. Python for data/ML, JavaScript for web apps.",
    "Thanks for sharing your experience. What would you do differently if you started again?",
    "The market validation point is so important. I made the same mistake with my first startup.",
    "How did you handle the emotional side of shutting down? That must have been really tough.",
    "This is really valuable advice. Thanks for being so open about your failures.",
    "I think AI will augment developers rather than replace them. It's a powerful tool.",
    "The key is learning to work with AI tools effectively. They're not going away.",
    "I'm worried about junior developers relying too heavily on AI without understanding the fundamentals.",
    "FastAPI is great for APIs, Django for full web applications. Choose based on your needs.",
    "I love FastAPI's automatic documentation and type hints. Much more modern than Django.",
    "Django has better admin interface and ORM out of the box. FastAPI is more minimal.",
    "I'd go with FastAPI for new projects. It's faster and more flexible.",
    "Use httpOnly cookies for security. localStorage is vulnerable to XSS attacks.",
    "I prefer JWT in localStorage with proper token refresh logic. It's simpler to implement.",
    "Consider using a library like react-query for state management and caching.",
    "PhD gives you deeper theoretical knowledge, industry gives you practical experience.",
    "I did a PhD and it opened doors to research positions, but industry experience is more valuable for most roles.",
    "It depends on your goals. Research positions often require PhD, but most industry jobs don't.",
    "I'd recommend getting some industry experience first, then decide if you need a PhD for your specific goals."
]

def get_random_user():
    return random.choice(FAKE_USERS)

def get_random_subreddit():
    return random.choice(FAKE_SUBREDDITS)

def get_random_post():
    return random.choice(FAKE_POSTS)

def get_random_comment():
    return random.choice(FAKE_COMMENTS)

def get_random_date(days_ago=30):
    """Get a random date within the last N days"""
    return datetime.now() - timedelta(days=random.randint(0, days_ago))

def generate_fake_posts(count=50):
    """Generate additional fake posts using Faker"""
    posts = []
    for _ in range(count):
        posts.append({
            "title": fake.sentence(nb_words=6),
            "content": fake.paragraph(nb_sentences=3),
            "post_type": random.choice(["text", "link", "image"])
        })
    return posts

def generate_fake_comments(count=100):
    """Generate additional fake comments using Faker"""
    comments = []
    for _ in range(count):
        comments.append(fake.sentence(nb_words=random.randint(5, 20)))
    return comments
