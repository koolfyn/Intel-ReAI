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
    },
    {
        "title": "Why I switched from MongoDB to PostgreSQL for my startup",
        "content": "After 6 months of using MongoDB, I migrated to PostgreSQL. The main reasons: 1) Complex queries were getting messy, 2) ACID compliance was crucial for financial data, 3) Better tooling and ecosystem. The migration took 2 weeks but was worth it.",
        "post_type": "text"
    },
    {
        "title": "Building a real-time chat app with WebSockets and Redis",
        "content": "I built a chat application using FastAPI, WebSockets, and Redis for pub/sub. The architecture handles 10k+ concurrent users. Key learnings: Redis pub/sub is amazing, WebSocket connection management is tricky, and proper error handling is crucial.",
        "post_type": "text"
    },
    {
        "title": "Machine Learning model deployment: Docker vs Serverless",
        "content": "I've deployed ML models using both Docker containers and AWS Lambda. Docker gives you more control but Lambda is easier to scale. For production, I'd recommend Docker with Kubernetes for complex models, Lambda for simple inference.",
        "post_type": "text"
    },
    {
        "title": "The complete guide to building a REST API with FastAPI",
        "content": "FastAPI has become my go-to framework for APIs. Here's why: automatic OpenAPI docs, type hints, async support, and great performance. I'll share my project structure and best practices that I've learned over 2 years.",
        "post_type": "text"
    },
    {
        "title": "How I reduced my React bundle size by 60%",
        "content": "My React app was 2.5MB initially. After code splitting, lazy loading, tree shaking, and optimizing images, it's now 1MB. The key was identifying the heaviest dependencies and finding lighter alternatives.",
        "post_type": "text"
    },
    {
        "title": "Database design patterns for microservices",
        "content": "When building microservices, database design is crucial. I've used database-per-service, shared database, and CQRS patterns. Each has trade-offs. Database-per-service is ideal for true independence but requires careful data consistency planning.",
        "post_type": "text"
    },
    {
        "title": "Building a recommendation engine from scratch",
        "content": "I built a content recommendation system using collaborative filtering and content-based filtering. The hybrid approach works best. Key challenges: cold start problem, scalability, and maintaining recommendation quality as the dataset grows.",
        "post_type": "text"
    },
    {
        "title": "Why I chose TypeScript over JavaScript for my next project",
        "content": "After 3 years of JavaScript, I switched to TypeScript. The benefits: better IDE support, fewer runtime errors, easier refactoring, and better team collaboration. The learning curve is worth it for larger projects.",
        "post_type": "text"
    },
    {
        "title": "The hidden costs of using third-party APIs",
        "content": "I integrated 5 different APIs in my last project. The hidden costs: rate limiting, data inconsistency, API changes breaking your code, and vendor lock-in. Always have fallback plans and consider building your own solutions for critical features.",
        "post_type": "text"
    },
    {
        "title": "How to scale a web application from 1k to 1M users",
        "content": "I've scaled multiple applications. The journey: 1) Optimize database queries, 2) Add caching (Redis), 3) Use CDN for static assets, 4) Implement horizontal scaling, 5) Add monitoring and alerting. Each step requires careful planning.",
        "post_type": "text"
    },
    {
        "title": "Building a real-time dashboard with WebSockets and D3.js",
        "content": "I created a real-time analytics dashboard showing live user activity, sales data, and system metrics. WebSockets provide real-time updates, D3.js handles the visualizations. The challenge was managing state and ensuring smooth animations.",
        "post_type": "text"
    },
    {
        "title": "The pros and cons of serverless architecture",
        "content": "I've built both traditional and serverless applications. Serverless pros: no server management, auto-scaling, pay-per-use. Cons: cold starts, vendor lock-in, limited execution time. Choose based on your use case and team expertise.",
        "post_type": "text"
    },
    {
        "title": "How to implement proper error handling in your API",
        "content": "Error handling is often overlooked but crucial for production APIs. I use structured error responses, proper HTTP status codes, logging, and monitoring. The key is being consistent and providing helpful error messages to API consumers.",
        "post_type": "text"
    },
    {
        "title": "Building a CI/CD pipeline with GitHub Actions",
        "content": "I set up automated testing, building, and deployment using GitHub Actions. The pipeline includes: linting, unit tests, integration tests, security scanning, Docker builds, and deployment to staging/production. It saves hours of manual work.",
        "post_type": "text"
    },
    {
        "title": "The evolution of frontend state management",
        "content": "I've used Redux, MobX, Zustand, and React Query. Each has its place. Redux for complex state, Zustand for simplicity, React Query for server state. The key is choosing the right tool for your specific needs and team size.",
        "post_type": "text"
    },
    {
        "title": "How to build a search engine with Elasticsearch",
        "content": "I built a full-text search feature using Elasticsearch. The setup includes: indexing, querying, faceted search, autocomplete, and relevance scoring. Elasticsearch is powerful but requires understanding of analyzers and mapping.",
        "post_type": "text"
    },
    {
        "title": "The art of writing maintainable code",
        "content": "After 5 years of coding, I've learned that maintainable code is more important than clever code. Key principles: clear naming, small functions, consistent formatting, good documentation, and regular refactoring. Your future self will thank you.",
        "post_type": "text"
    },
    {
        "title": "Building a notification system with Redis and WebSockets",
        "content": "I implemented real-time notifications using Redis pub/sub and WebSockets. The system handles email, push, and in-app notifications. The challenge was ensuring delivery and handling offline users. Redis streams help with message persistence.",
        "post_type": "text"
    },
    {
        "title": "Why I switched from REST to GraphQL",
        "content": "After using REST for years, I tried GraphQL. The benefits: single endpoint, client-specified queries, strong typing, and better developer experience. The trade-offs: complexity, caching challenges, and learning curve. Worth it for complex APIs.",
        "post_type": "text"
    },
    {
        "title": "The complete guide to API security best practices",
        "content": "API security is critical. Essential practices: authentication (JWT/OAuth), authorization, input validation, rate limiting, HTTPS, CORS configuration, and security headers. I also use API gateways for additional protection and monitoring.",
        "post_type": "text"
    },
    {
        "title": "Building a multi-tenant SaaS application",
        "content": "I built a SaaS app serving 100+ companies. Key considerations: data isolation, tenant-specific configurations, billing, and scalability. I used database-per-tenant for strict isolation and shared database with tenant_id for cost efficiency.",
        "post_type": "text"
    },
    {
        "title": "How to optimize database performance",
        "content": "Database performance is crucial for user experience. Key optimizations: proper indexing, query optimization, connection pooling, read replicas, and caching. I also use database monitoring tools to identify slow queries and bottlenecks.",
        "post_type": "text"
    },
    {
        "title": "The future of web development: WebAssembly and beyond",
        "content": "WebAssembly is changing how we think about web performance. I've experimented with running C++ code in the browser, and the results are impressive. The future might see more native-like performance in web applications.",
        "post_type": "text"
    },
    {
        "title": "Building a real-time collaborative editor",
        "content": "I built a collaborative text editor using operational transformation and WebSockets. The challenges: conflict resolution, cursor synchronization, and handling network issues. The result is a Google Docs-like experience with real-time collaboration.",
        "post_type": "text"
    },
    {
        "title": "The psychology of code reviews",
        "content": "Code reviews are about more than finding bugs. They're about knowledge sharing, maintaining code quality, and team building. I've learned that constructive feedback, clear communication, and focusing on the code (not the person) leads to better outcomes.",
        "post_type": "text"
    },
    {
        "title": "How to build a recommendation system for e-commerce",
        "content": "I built a product recommendation engine using collaborative filtering and content-based filtering. The system analyzes user behavior, purchase history, and product attributes. The key is balancing accuracy with performance and handling the cold start problem.",
        "post_type": "text"
    },
    {
        "title": "The complete guide to Docker and containerization",
        "content": "Docker has revolutionized deployment. I containerize all my applications now. Key benefits: consistency, portability, and easy scaling. I also use Docker Compose for local development and Kubernetes for production orchestration.",
        "post_type": "text"
    },
    {
        "title": "Building a real-time analytics platform",
        "content": "I created an analytics platform that processes millions of events in real-time. The stack: Apache Kafka for streaming, Apache Spark for processing, and ClickHouse for storage. The challenge was handling data volume and ensuring low latency.",
        "post_type": "text"
    },
    {
        "title": "Why I love functional programming concepts",
        "content": "After learning functional programming concepts, I apply them in JavaScript and Python. Immutability, pure functions, and higher-order functions make code more predictable and testable. It's not about being purely functional, but adopting the good parts.",
        "post_type": "text"
    },
    {
        "title": "The complete guide to testing strategies",
        "content": "Testing is crucial for reliable software. I use unit tests, integration tests, and end-to-end tests. The testing pyramid: many unit tests, some integration tests, few E2E tests. I also practice TDD for critical features and use mocking for external dependencies.",
        "post_type": "text"
    },
    {
        "title": "Building a real-time chat application with message persistence",
        "content": "I built a chat app with message history, file sharing, and emoji reactions. The architecture: WebSockets for real-time, PostgreSQL for persistence, Redis for caching, and S3 for file storage. The challenge was handling message ordering and delivery guarantees.",
        "post_type": "text"
    },
    {
        "title": "The evolution of JavaScript frameworks",
        "content": "I've used jQuery, Angular, React, and Vue. Each framework has its strengths. React for component reusability, Vue for simplicity, Angular for enterprise apps. The key is understanding the underlying concepts rather than just learning syntax.",
        "post_type": "text"
    },
    {
        "title": "How to build a scalable microservices architecture",
        "content": "I've built microservices using Docker, Kubernetes, and service mesh. Key principles: single responsibility, loose coupling, high cohesion, and proper communication patterns. The challenge is managing distributed systems complexity and ensuring data consistency.",
        "post_type": "text"
    },
    {
        "title": "The art of API design",
        "content": "Good API design is crucial for developer experience. Key principles: consistency, predictability, versioning, and good documentation. I follow RESTful conventions, use proper HTTP methods, and provide clear error messages. API design is an art, not just a science.",
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
    "I'd recommend getting some industry experience first, then decide if you need a PhD for your specific goals.",
    "PostgreSQL is definitely the better choice for most applications. The ACID compliance is crucial.",
    "I made the same switch from MongoDB to PostgreSQL. The query performance improvement was significant.",
    "MongoDB is great for prototyping but PostgreSQL scales better for production workloads.",
    "The migration process can be tricky. Did you use any specific tools for the data migration?",
    "WebSockets + Redis is a solid combination for real-time features. What's your Redis setup?",
    "I've been using Socket.IO for WebSocket management. How do you handle reconnection logic?",
    "10k concurrent users is impressive! What's your server infrastructure like?",
    "Docker is definitely the way to go for ML model deployment. Kubernetes makes it even better.",
    "I've had issues with cold starts in Lambda for ML models. Docker containers solve that problem.",
    "What's your model serving latency with Docker vs Lambda? I'm curious about the performance difference.",
    "FastAPI's automatic OpenAPI docs are a game changer. Saves so much time on documentation.",
    "The type hints in FastAPI make the code so much more maintainable. Love it!",
    "I'm still learning FastAPI but already prefer it over Flask. The async support is great.",
    "Bundle size optimization is crucial for user experience. What tools did you use for analysis?",
    "Code splitting with React.lazy() made a huge difference in my app's initial load time.",
    "Tree shaking is often overlooked but can save significant bundle size. Good point!",
    "Database-per-service is ideal but can be complex to implement. How do you handle cross-service queries?",
    "CQRS is powerful but adds complexity. When do you think it's worth the overhead?",
    "I've been considering microservices for my next project. Any advice on getting started?",
    "Recommendation systems are fascinating. How do you handle the cold start problem for new users?",
    "Collaborative filtering vs content-based filtering - which performs better in your experience?",
    "The hybrid approach makes sense. How do you weight the different recommendation strategies?",
    "TypeScript has saved me from so many runtime errors. The learning curve is worth it.",
    "I'm still on the fence about TypeScript. The setup and configuration can be overwhelming.",
    "The IDE support with TypeScript is amazing. IntelliSense works so much better.",
    "Third-party API dependencies are a real risk. I always try to have fallback plans.",
    "Rate limiting can kill your app if not handled properly. How do you manage it?",
    "API versioning is crucial when dealing with external services. What's your strategy?",
    "Scaling from 1k to 1M users is a journey. Caching is definitely the first step.",
    "CDN for static assets made a huge difference in our global performance.",
    "Monitoring and alerting are often overlooked but essential for production systems.",
    "D3.js is powerful but has a steep learning curve. How did you get started with it?",
    "Real-time dashboards are challenging. How do you handle data updates and state management?",
    "WebSockets for real-time data is great, but handling connection drops can be tricky.",
    "Serverless is great for certain use cases but not a silver bullet. Good analysis.",
    "Cold starts are the biggest downside of serverless. Docker containers solve that.",
    "Vendor lock-in is a real concern with serverless. How do you mitigate that risk?",
    "Error handling is often an afterthought but so important for user experience.",
    "Structured error responses make debugging so much easier for API consumers.",
    "Logging and monitoring are essential for understanding what's happening in production.",
    "GitHub Actions has been a game changer for our CI/CD pipeline. So much easier than Jenkins.",
    "Automated testing in CI/CD saves so much time and catches issues early.",
    "Security scanning in the pipeline is crucial. What tools do you use?",
    "State management in React has evolved so much. Redux is still my go-to for complex apps.",
    "React Query is amazing for server state management. Much better than useEffect for API calls.",
    "Zustand is so much simpler than Redux for smaller applications. Love the minimal API.",
    "Elasticsearch is powerful but can be complex to set up and maintain.",
    "Full-text search with faceted filtering is a great user experience. How do you handle relevance scoring?",
    "Analyzers in Elasticsearch are crucial for good search results. What's your approach?",
    "Maintainable code is more important than clever code. Great principle!",
    "Code reviews are essential for maintaining code quality and sharing knowledge.",
    "Documentation is often overlooked but so important for team collaboration.",
    "Redis pub/sub is perfect for real-time notifications. How do you handle message persistence?",
    "WebSocket connection management can be tricky. How do you handle reconnection and heartbeat?",
    "Offline user handling is a challenge. Do you queue messages for when they come back online?",
    "GraphQL is great for complex APIs but adds overhead for simple use cases.",
    "The single endpoint approach in GraphQL is nice but caching becomes more complex.",
    "Client-specified queries in GraphQL are powerful but can lead to performance issues.",
    "API security is critical. JWT tokens with proper expiration are essential.",
    "Rate limiting and input validation are the first line of defense against attacks.",
    "CORS configuration can be tricky. What's your approach for different environments?",
    "Multi-tenant SaaS is complex. Data isolation is crucial for security and compliance.",
    "Tenant-specific configurations can get messy. How do you manage them?",
    "Database performance optimization is an ongoing process. What monitoring tools do you use?",
    "Query optimization and proper indexing are the foundation of good performance.",
    "Connection pooling is often overlooked but crucial for handling concurrent requests.",
    "WebAssembly is exciting but still has limitations. What use cases have you found for it?",
    "Running C++ in the browser is impressive. What's the performance like compared to JavaScript?",
    "The future of web development is definitely interesting. WebAssembly opens up new possibilities.",
    "Operational transformation is complex but necessary for real-time collaboration.",
    "Conflict resolution in collaborative editing is challenging. How do you handle it?",
    "Cursor synchronization and handling network issues are the hardest parts.",
    "Code reviews are about more than finding bugs. They're about knowledge sharing and team building.",
    "Constructive feedback is key to good code reviews. Focus on the code, not the person.",
    "Clear communication in code reviews helps everyone learn and improve.",
    "Recommendation systems are fascinating. How do you balance accuracy with performance?",
    "The cold start problem is tricky. How do you handle new users with no history?",
    "Collaborative filtering vs content-based filtering - which works better for your use case?",
    "Docker has revolutionized how we think about deployment and scaling.",
    "Containerization makes development and production environments so much more consistent.",
    "Kubernetes for orchestration is powerful but has a learning curve. Worth it for larger systems.",
    "Real-time analytics with high volume is challenging. Kafka is great for streaming data.",
    "ClickHouse is amazing for analytical queries. Much faster than traditional databases.",
    "Handling millions of events requires careful architecture. What's your data pipeline like?",
    "Functional programming concepts make code more predictable and testable.",
    "Immutability and pure functions are great principles to apply in any language.",
    "Higher-order functions are powerful. I use them more and more in my JavaScript code.",
    "Testing is crucial for reliable software. TDD helps catch issues early.",
    "The testing pyramid is a good guideline. More unit tests, fewer integration tests, even fewer E2E tests.",
    "Mocking external dependencies is essential for reliable unit tests.",
    "Real-time chat with message persistence is complex. How do you handle message ordering?",
    "WebSockets for real-time, PostgreSQL for persistence, Redis for caching - solid architecture.",
    "File sharing in chat apps adds complexity. How do you handle large file uploads?",
    "JavaScript frameworks each have their strengths. Understanding the concepts is more important than syntax.",
    "React's component model is great for reusability and maintainability.",
    "Vue's simplicity makes it great for smaller projects and teams.",
    "Angular's opinionated approach is good for large enterprise applications.",
    "Microservices require careful planning. Service boundaries are crucial for success.",
    "Docker and Kubernetes make microservices much more manageable.",
    "Service mesh adds another layer but can be worth it for complex systems.",
    "API design is indeed an art. Consistency and predictability are key.",
    "Good documentation makes APIs so much more usable. OpenAPI/Swagger helps a lot.",
    "Versioning strategies are important for API evolution. Semantic versioning works well."
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
