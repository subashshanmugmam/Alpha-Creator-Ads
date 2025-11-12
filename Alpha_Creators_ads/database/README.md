# Alpha Creators Ads - Database Setup

This directory contains all database-related configurations and setup files for the Alpha Creators Ads platform.

## 🗄️ Database Architecture

The system uses a multi-database architecture to optimize for different data types and use cases:

### **PostgreSQL** - Primary Relational Database
- **Purpose**: Users, campaigns, analytics, structured data
- **Port**: 5432
- **Database**: `alphaads`
- **User**: `alphaads_user`

### **Redis** - Caching & Session Storage
- **Purpose**: Session management, caching, real-time data
- **Port**: 6379
- **Configuration**: `redis.conf`

### **MongoDB** - Document Database
- **Purpose**: Social media content, unstructured data
- **Port**: 27017
- **Database**: `alphaads`

### **Neo4j** - Graph Database
- **Purpose**: Customer relationships, graph analytics
- **Ports**: 7474 (HTTP), 7687 (Bolt)
- **Browser**: http://localhost:7474

### **InfluxDB** - Time Series Database
- **Purpose**: Metrics, performance data, analytics
- **Port**: 8086
- **Organization**: `alphaads`
- **Bucket**: `metrics`

### **Apache Kafka** - Message Streaming
- **Purpose**: Real-time data streaming, event processing
- **Port**: 9092
- **Zookeeper**: 2181

## 🚀 Quick Start

### 1. Start All Databases
```bash
# Start all database services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Access Database Admin Tools

#### PostgreSQL Admin (pgAdmin)
- **URL**: http://localhost:5050
- **Email**: admin@alphaads.com
- **Password**: your_secure_password

#### MongoDB Admin (Mongo Express)
- **URL**: http://localhost:8081
- **Username**: admin
- **Password**: your_secure_password

#### Neo4j Browser
- **URL**: http://localhost:7474
- **Username**: neo4j
- **Password**: your_secure_password

#### Redis Insight
- **URL**: http://localhost:8001

#### InfluxDB UI
- **URL**: http://localhost:8086
- **Username**: admin
- **Password**: your_secure_password

## 📋 Database Initialization

### PostgreSQL Tables
The following tables will be created automatically when the backend starts:
- `users` - User accounts and authentication
- `customer_profiles` - Customer behavior and preferences
- `campaigns` - Advertising campaigns
- `ad_creatives` - Generated ad content
- `social_media_posts` - Collected social media data
- `platform_deliveries` - Multi-platform ad delivery tracking
- `reinforcement_learning_models` - ML model states
- `system_metrics` - Performance monitoring

### MongoDB Collections
- `social_media_data` - Raw social media content
- `nlp_analysis` - NLP processing results
- `user_interactions` - User behavior tracking

### Neo4j Graph Schema
- `Customer` nodes with relationship mappings
- `Product` nodes and preferences
- `Campaign` effectiveness relationships

### InfluxDB Measurements
- `system_performance` - CPU, memory, disk metrics
- `api_metrics` - Request/response times
- `campaign_performance` - Real-time campaign data

## 🔧 Configuration Files

### Environment Variables
Create a `.env` file in this directory:
```env
# PostgreSQL
POSTGRES_DB=alphaads
POSTGRES_USER=alphaads_user
POSTGRES_PASSWORD=your_secure_password

# MongoDB
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=your_secure_password

# Neo4j
NEO4J_AUTH=neo4j/your_secure_password

# InfluxDB
INFLUXDB_ADMIN_PASSWORD=your_secure_password
INFLUXDB_TOKEN=your-super-secret-auth-token

# Redis
REDIS_PASSWORD=your_secure_password
```

### Redis Configuration
Custom Redis configuration is available in `redis.conf`

### Database Initialization Scripts
- `init-scripts/` - PostgreSQL initialization SQL
- `mongo-init/` - MongoDB initialization scripts

## 🛠️ Maintenance

### Backup & Restore

#### PostgreSQL Backup
```bash
# Backup
docker exec alphaads_postgres pg_dump -U alphaads_user alphaads > backup.sql

# Restore
docker exec -i alphaads_postgres psql -U alphaads_user alphaads < backup.sql
```

#### MongoDB Backup
```bash
# Backup
docker exec alphaads_mongodb mongodump --out /backup

# Restore
docker exec alphaads_mongodb mongorestore /backup
```

### Monitoring

#### Check Database Health
```bash
# All services health
docker-compose ps

# Individual health checks
docker-compose exec postgres pg_isready -U alphaads_user -d alphaads
docker-compose exec redis redis-cli ping
docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
```

#### View Resource Usage
```bash
# Resource usage
docker stats

# Disk usage
docker system df
```

### Scaling

#### Scale Kafka
```bash
# Add more Kafka brokers
docker-compose up -d --scale kafka=3
```

#### Scale Redis
```bash
# Redis cluster setup (requires additional configuration)
# See redis-cluster.yml for cluster setup
```

## 🔒 Security

### Default Passwords
**⚠️ IMPORTANT**: Change all default passwords before production deployment!

### Network Security
- All databases are isolated in `alphaads_network`
- Only necessary ports are exposed to host
- Use environment variables for credentials

### Data Encryption
- Enable SSL/TLS for production deployments
- Use encrypted volumes for sensitive data
- Implement database-level encryption

## 📊 Performance Tuning

### PostgreSQL Optimization
```sql
-- Connection limits
max_connections = 100

-- Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB

-- Logging
log_statement = 'all'
log_duration = on
```

### MongoDB Optimization
```javascript
// Indexing strategy
db.social_media_data.createIndex({"timestamp": 1})
db.social_media_data.createIndex({"user_id": 1, "platform": 1})
```

### Redis Optimization
```conf
# Memory management
maxmemory 256mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check port usage
sudo lsof -i :5432
sudo lsof -i :6379
sudo lsof -i :27017

# Stop conflicting services
sudo systemctl stop postgresql
sudo systemctl stop redis-server
sudo systemctl stop mongod
```

#### Permission Issues
```bash
# Fix volume permissions
sudo chown -R 999:999 ./postgres_data
sudo chown -R 1001:1001 ./redis_data
sudo chown -R 999:999 ./mongodb_data
```

#### Memory Issues
```bash
# Increase Docker memory limits
docker-compose down
# Edit Docker Desktop settings to increase memory
docker-compose up -d
```

### Log Analysis
```bash
# View all logs
docker-compose logs

# Follow specific service logs
docker-compose logs -f postgres
docker-compose logs -f mongodb
docker-compose logs -f kafka
```

## 📈 Monitoring & Alerts

### Health Checks
All services include health checks that can be monitored:
```bash
# Check health status
docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Health}}"
```

### Metrics Collection
- InfluxDB stores performance metrics
- Grafana dashboards available for visualization
- Prometheus metrics endpoint on databases

### Alerting
Configure alerts for:
- Database connectivity issues
- High memory/CPU usage
- Disk space warnings
- Replication lag
- Connection pool exhaustion

---

## 📞 Support

For database-related issues:
1. Check the troubleshooting section above
2. Review service logs: `docker-compose logs [service-name]`
3. Verify environment configuration
4. Check resource availability (memory, disk, network)

**Database Stack Version**: Latest stable versions as of September 2025
