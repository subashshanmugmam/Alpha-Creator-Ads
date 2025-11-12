# GitHub Copilot Backend Development Prompt
## Next-Gen Target Marketing: Real-Time Emotion-Aware Ad Creation System

### Project Overview
Build a comprehensive backend system for real-time emotion-aware advertising that processes social media data, analyzes sentiment, generates personalized ads using AI, and delivers them across multiple platforms. The system should handle high-volume data streaming, advanced NLP processing, and real-time ad generation.

### Core Architecture Requirements

#### 1. Data Pipeline & Streaming Architecture
```
Please help me build a real-time data streaming architecture that:
- Ingests data from multiple social media APIs (Twitter, Facebook, Instagram, LinkedIn)
- Uses Apache Kafka/Redis for message queuing and real-time data processing
- Implements data validation, cleaning, and preprocessing pipelines
- Handles rate limiting and API quota management
- Stores raw and processed data in appropriate databases
- Includes error handling and retry mechanisms for failed API calls
- Implements data privacy compliance (GDPR, CCPA) with anonymization
```

#### 2. Advanced NLP & Sentiment Analysis Engine
```
Create a comprehensive NLP processing system that:
- Performs multi-level sentiment analysis (basic sentiment + emotion detection + aspect-based analysis + intent classification)
- Uses pre-trained models like BERT, RoBERTa, or similar for emotion detection
- Implements custom models for aspect-based sentiment analysis
- Classifies user intent (research, purchase-ready, complaint, etc.)
- Extracts entities, topics, and contextual information from social media posts
- Handles multiple languages and social media slang/abbreviations
- Processes emojis and multimedia content descriptions
- Creates confidence scores for each analysis result
- Implements caching for frequently analyzed content patterns
```

#### 3. Dynamic Customer Profiling System
```
Build a customer profiling system that:
- Creates and maintains dynamic user profiles from social media data
- Implements Multi-Response State Representation (MRSR) for customer behavior modeling
- Tracks emotional journey and behavioral patterns over time
- Segments users based on psychological profiles, interests, and current emotional state
- Updates profiles in real-time as new data arrives
- Implements privacy-preserving techniques (differential privacy, k-anonymity)
- Creates audience segments and buyer personas automatically
- Stores profile data in both relational and graph databases for different access patterns
```

#### 4. AI-Powered Ad Creative Generation Engine
```
Develop a generative AI system that:
- Integrates with LLM APIs (OpenAI GPT-4, Anthropic Claude, or local models)
- Generates personalized ad copy based on user emotional state and preferences
- Creates multiple ad variations for A/B testing automatically
- Generates visual content descriptions and integrates with image generation APIs
- Implements template-based generation with dynamic content insertion
- Ensures brand consistency and compliance with advertising guidelines
- Handles content moderation and inappropriate content filtering
- Implements prompt engineering for different emotional contexts and product categories
- Caches generated content to avoid redundant API calls
- Tracks generation costs and implements budget controls
```

#### 5. Reinforcement Learning Optimization Module
```
Create a reinforcement learning system that:
- Implements Deep Q-Networks (DQN) for sequential ad delivery optimization
- Uses Multi-Response State Representation for customer lifetime value optimization
- Optimizes ad sequencing, timing, and platform selection
- Implements reward functions based on engagement, conversion, and long-term customer value
- Handles exploration vs exploitation tradeoffs in ad delivery
- Implements offline RL training on historical data
- Creates policy networks for different customer segments
- Includes A/B testing framework for policy evaluation
- Implements safe deployment with gradual rollout mechanisms
```

#### 6. Multi-Platform Ad Delivery System
```
Build an ad delivery system that:
- Integrates with major advertising platforms (Google Ads, Facebook Ads, LinkedIn Ads, etc.)
- Manages campaign creation, budget allocation, and bid optimization
- Implements real-time ad placement and delivery
- Handles different ad formats (text, image, video, carousel)
- Manages frequency capping and budget pacing
- Implements impression and click tracking
- Handles platform-specific requirements and constraints
- Includes failover mechanisms for platform outages
- Implements cost optimization across platforms
```

#### 7. Real-Time Analytics & Performance Monitoring
```
Create a comprehensive analytics system that:
- Tracks real-time performance metrics (CTR, conversion rates, engagement)
- Implements custom dashboards for different stakeholders
- Creates automated alerts for performance anomalies
- Tracks customer journey from social media post to conversion
- Implements attribution modeling for multi-touch campaigns
- Generates automated reports and insights
- Includes A/B testing statistical significance calculations
- Monitors system health, API usage, and processing latencies
- Implements data visualization and reporting APIs
```

#### 8. API Gateway & Authentication System
```
Develop a secure API gateway that:
- Implements JWT-based authentication and authorization
- Manages API rate limiting and quota enforcement
- Includes request/response logging and monitoring
- Implements API versioning and backward compatibility
- Handles CORS for web applications
- Includes comprehensive API documentation with OpenAPI/Swagger
- Implements caching strategies for frequently accessed endpoints
- Includes input validation and sanitization
- Handles different user roles and permissions
```

### Technical Stack Specifications

#### Backend Framework & Language
```
Use the following technology stack:
- Python 3.9+ with FastAPI for high-performance API development
- Alternatively, Node.js with Express.js for JavaScript-based development
- Implement asynchronous processing throughout
- Use type hints/TypeScript for better code maintainability
- Include comprehensive error handling and logging
```

#### Database Architecture
```
Implement a multi-database architecture:
- PostgreSQL for relational data (user profiles, campaigns, transactions)
- Redis for caching, session storage, and real-time data
- MongoDB for storing unstructured social media data and content
- InfluxDB or similar for time-series analytics data
- Neo4j for graph-based customer relationship modeling
- Implement database connection pooling and transaction management
- Include backup and disaster recovery strategies
```

#### Message Queue & Streaming
```
Set up real-time data processing:
- Apache Kafka for high-throughput message streaming
- Redis Streams for lightweight real-time processing
- Celery for background task processing
- Implement dead letter queues for failed messages
- Include monitoring and alerting for queue health
```

#### Cloud Infrastructure
```
Deploy on cloud infrastructure with:
- Containerization using Docker and Docker Compose
- Kubernetes for orchestration and scaling
- AWS/GCP/Azure services integration
- Auto-scaling based on load and processing requirements
- Load balancing and service discovery
- Implement CI/CD pipelines for automated deployment
```

### Security & Compliance Requirements

#### Data Privacy & Security
```
Implement comprehensive security measures:
- Data encryption at rest and in transit
- PII anonymization and pseudonymization
- GDPR compliance with right to deletion and data portability
- Implement audit logging for all data access
- Regular security vulnerability scanning
- Rate limiting and DDoS protection
- Secure API key and credential management
- Data retention policies and automated cleanup
```

#### Monitoring & Observability
```
Implement comprehensive monitoring:
- Application performance monitoring (APM)
- Structured logging with correlation IDs
- Health checks and service discovery
- Metrics collection and alerting
- Distributed tracing for complex workflows
- Error tracking and reporting
- Performance profiling and optimization
```

### Development Guidelines

#### Code Quality Standards
```
Follow these development practices:
- Write comprehensive unit tests with >80% coverage
- Implement integration tests for API endpoints
- Use linting tools (pylint, black, mypy for Python)
- Include type hints for all functions and classes
- Write clear docstrings and API documentation
- Implement design patterns appropriate for each component
- Follow SOLID principles and clean architecture
- Include performance benchmarks for critical paths
```

#### Error Handling & Resilience
```
Implement robust error handling:
- Custom exception classes for different error types
- Circuit breaker patterns for external service calls
- Exponential backoff for retry mechanisms
- Graceful degradation when services are unavailable
- Comprehensive logging of errors with context
- Health check endpoints for all services
- Automated recovery procedures where possible
```

### Specific Implementation Requests

When generating code, please:
1. Start with the core data pipeline and social media API integration
2. Implement the NLP processing engine with modular components
3. Create the customer profiling system with real-time updates
4. Build the AI content generation module with proper API integration
5. Develop the reinforcement learning optimization system
6. Implement the multi-platform ad delivery mechanisms
7. Create comprehensive analytics and monitoring systems
8. Set up proper testing, documentation, and deployment configurations

### Performance Requirements
- Handle 100,000+ social media posts per hour
- Process sentiment analysis within 30 seconds of data ingestion
- Generate personalized ads within 5 minutes of sentiment detection
- Support 10,000+ concurrent users
- Maintain 99.9% uptime with proper failover mechanisms
- Scale horizontally based on load

### Additional Context
This system should be production-ready with proper error handling, logging, monitoring, and security measures. Include comprehensive documentation, unit tests, and deployment configurations. The code should be modular, maintainable, and follow industry best practices for large-scale systems.