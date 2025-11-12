# Alpha Creators Ads - Backend System

A comprehensive real-time emotion-aware advertising system that processes social media data, analyzes sentiment, and generates personalized advertisements using AI.

## 🏗️ Architecture Overview

This system implements a microservices architecture with the following core components:

- **Data Pipeline**: Real-time social media data ingestion from multiple platforms
- **NLP Engine**: Advanced sentiment analysis and emotion detection
- **Customer Profiling**: Dynamic user behavior and emotional pattern analysis
- **AI Ad Generation**: Personalized ad creative generation using LLMs
- **Reinforcement Learning**: Ad delivery optimization using RL algorithms
- **Multi-Platform Delivery**: Integration with major advertising platforms
- **Real-time Analytics**: Performance monitoring and insights

## 🛠️ Technology Stack

### Backend Framework
- **Python 3.11+** with FastAPI for high-performance APIs
- **Async/await** throughout for concurrent processing
- **Type hints** for better code maintainability

### Databases
- **PostgreSQL**: Relational data (users, campaigns, transactions)
- **Redis**: Caching, session storage, and real-time data
- **MongoDB**: Unstructured social media data and content
- **Neo4j**: Graph-based customer relationship modeling
- **InfluxDB**: Time-series analytics data

### Message Streaming
- **Apache Kafka**: High-throughput message streaming
- **Redis Streams**: Lightweight real-time processing
- **Celery**: Background task processing

### Machine Learning/AI
- **Transformers**: BERT, RoBERTa for sentiment analysis
- **spaCy**: Named entity recognition and NLP
- **OpenAI/Anthropic APIs**: Ad content generation
- **TensorFlow/PyTorch**: Custom ML models
- **scikit-learn**: Traditional ML algorithms

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Structured logging**: With correlation IDs
- **Health checks**: For all services

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Alpha_Creators_ads/backend
```

### 2. Environment Setup

Create a `.env` file in the backend directory:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys and configurations
nano .env
```

Required environment variables:
```env
# Database URLs
DATABASE_URL=postgresql://alphaads:password@localhost:5432/alphaads
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/alphaads

# Social Media API Keys
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# AI/ML API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
HUGGINGFACE_API_TOKEN=your_huggingface_token

# Advertising Platform APIs
GOOGLE_ADS_DEVELOPER_TOKEN=your_google_ads_token
FACEBOOK_ADS_ACCESS_TOKEN=your_facebook_ads_token
```

### 3. Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Check service status
docker-compose ps
```

### 4. Development Setup (Alternative)

For local development without Docker:

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

# Create directories
mkdir -p logs data models

# Start databases (requires separate setup)
# Then start the API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Services and Ports

| Service | Port | Description |
|---------|------|-------------|
| API | 8000 | Main FastAPI application |
| Prometheus Metrics | 8001 | Metrics endpoint |
| PostgreSQL | 5432 | Primary database |
| Redis | 6379 | Cache and session store |
| MongoDB | 27017 | Document database |
| Neo4j | 7474/7687 | Graph database |
| InfluxDB | 8086 | Time-series database |
| Kafka | 9092 | Message broker |
| Prometheus | 9090 | Metrics server |
| Grafana | 3000 | Monitoring dashboard |

## 🔧 API Endpoints

### Health Checks
- `GET /` - Basic API status
- `GET /health` - Simple health check
- `GET /api/v1/health/detailed` - Detailed system health
- `GET /api/v1/health/metrics` - Current system metrics

### Documentation
- `GET /api/docs` - Swagger UI
- `GET /api/redoc` - ReDoc documentation

### Core APIs (Coming Soon)
- `/api/v1/users` - User management
- `/api/v1/campaigns` - Campaign management
- `/api/v1/analytics` - Performance analytics
- `/api/v1/nlp` - NLP processing endpoints

## 🧠 Core Components

### 1. Social Media Ingestion Service
```python
# services/social_media_ingestion.py
- Collects data from Twitter, Facebook, Instagram, LinkedIn
- Handles rate limiting and API quotas
- Sends data to Kafka for processing
```

### 2. NLP Processing Engine
```python
# services/nlp_engine.py
- Multi-level sentiment analysis (VADER + BERT)
- Emotion detection using DistilRoBERTa
- Named entity recognition with spaCy
- Intent classification
```

### 3. Customer Profiling System
```python
# services/customer_profiling.py
- Dynamic user profile creation
- Emotional journey tracking
- Behavioral pattern analysis
- Privacy-preserving techniques
```

### 4. AI Ad Generation Engine
```python
# services/ad_generation.py
- Integration with OpenAI/Anthropic APIs
- Template-based generation
- Content moderation
- A/B testing support
```

### 5. Monitoring & Analytics
```python
# services/monitoring.py
- Real-time performance metrics
- Health checks for all components
- Alerting and notifications
- Prometheus metrics export
```

## 📈 Performance Targets

- **Throughput**: Handle 100,000+ social media posts per hour
- **Latency**: Process sentiment analysis within 30 seconds
- **Ad Generation**: Generate personalized ads within 5 minutes
- **Concurrency**: Support 10,000+ concurrent users
- **Uptime**: Maintain 99.9% availability
- **Scalability**: Horizontal scaling based on load

## 🔒 Security & Compliance

### Data Privacy
- GDPR compliance with right to deletion
- Data anonymization and pseudonymization
- PII encryption at rest and in transit
- Audit logging for all data access

### Security Measures
- JWT-based authentication
- API rate limiting
- Input validation and sanitization
- Regular security vulnerability scanning
- Secure credential management

## 🧪 Testing

```bash
# Run unit tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run integration tests
pytest tests/integration/ -v

# Run load tests
locust -f tests/load/locustfile.py
```

## 📊 Monitoring & Observability

### Prometheus Metrics
Access metrics at: `http://localhost:8001/metrics`

Key metrics tracked:
- Request count and duration
- Database connection pools
- Queue sizes and processing times
- System resource usage
- NLP processing performance

### Grafana Dashboards
Access dashboards at: `http://localhost:3000` (admin/admin)

Pre-configured dashboards:
- System Overview
- API Performance
- Database Health
- NLP Processing Metrics
- Business KPIs

### Logs
Structured JSON logs with correlation IDs:
```bash
# View API logs
docker-compose logs -f api

# View all logs
docker-compose logs -f
```

## 🚀 Deployment

### Production Deployment

1. **Environment Configuration**
   ```bash
   # Set production environment variables
   export ENVIRONMENT=production
   export DEBUG=false
   export SECRET_KEY=your-production-secret-key
   ```

2. **Database Migration**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

3. **Start Services**
   ```bash
   # Start with production configuration
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment
Kubernetes manifests are available in the `k8s/` directory:

```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

## 🛠️ Development

### Adding New Features

1. **Create a new service**
   ```python
   # services/your_service.py
   class YourService:
       async def process_data(self, data):
           # Implementation
           pass
   ```

2. **Add API endpoints**
   ```python
   # api/v1/endpoints/your_endpoint.py
   from fastapi import APIRouter
   
   router = APIRouter()
   
   @router.post("/your-endpoint")
   async def your_endpoint():
       # Implementation
       pass
   ```

3. **Include in router**
   ```python
   # api/v1/router.py
   from api.v1.endpoints import your_endpoint
   
   api_router.include_router(
       your_endpoint.router, 
       prefix="/your-endpoint", 
       tags=["your-endpoint"]
   )
   ```

### Code Quality

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .

# Pre-commit hooks
pre-commit install
```

## 📚 Documentation

- **API Documentation**: Available at `/api/docs` when running
- **Architecture Docs**: See `docs/architecture.md`
- **Deployment Guide**: See `docs/deployment.md`
- **Contributing**: See `docs/contributing.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the logs for error details

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Core API framework
- [x] Database setup
- [x] Basic monitoring
- [ ] Social media ingestion
- [ ] NLP processing engine

### Phase 2
- [ ] Customer profiling system
- [ ] AI ad generation
- [ ] Basic reinforcement learning

### Phase 3
- [ ] Advanced RL optimization
- [ ] Multi-platform ad delivery
- [ ] Advanced analytics
- [ ] Production hardening

---

Built with ❤️ by the Alpha Creators Ads Team
