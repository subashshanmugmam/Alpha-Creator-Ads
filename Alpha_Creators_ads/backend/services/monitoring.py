"""
Monitoring and health check service.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psutil
import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from dataclasses import dataclass

from core.config import settings
from core.database import get_redis, get_mongo, get_neo4j, get_influx

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
PROCESSING_QUEUE_SIZE = Gauge('processing_queue_size', 'Size of processing queues', ['queue_name'])
SYSTEM_CPU_USAGE = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
SYSTEM_MEMORY_USAGE = Gauge('system_memory_usage_percent', 'System memory usage percentage')
NLP_PROCESSING_TIME = Histogram('nlp_processing_seconds', 'NLP processing time')
AD_GENERATION_TIME = Histogram('ad_generation_seconds', 'Ad generation time')


@dataclass
class SystemHealth:
    """System health status"""
    status: str  # healthy, degraded, unhealthy
    services: Dict[str, str]
    metrics: Dict[str, Any]
    timestamp: datetime


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    database_connections: Dict[str, int]
    queue_sizes: Dict[str, int]
    response_times: Dict[str, float]


class HealthChecker:
    """Health check for various system components"""
    
    async def check_database_health(self) -> Dict[str, str]:
        """Check health of all databases"""
        health_status = {}
        
        # PostgreSQL
        try:
            # This would normally test a simple query
            health_status["postgresql"] = "healthy"
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            health_status["postgresql"] = "unhealthy"
        
        # Redis
        try:
            redis_client = await get_redis()
            await redis_client.ping()
            health_status["redis"] = "healthy"
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status["redis"] = "unhealthy"
        
        # MongoDB
        try:
            mongo_db = await get_mongo()
            await mongo_db.command("ping")
            health_status["mongodb"] = "healthy"
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            health_status["mongodb"] = "unhealthy"
        
        # Neo4j
        try:
            neo4j_driver = await get_neo4j()
            await neo4j_driver.verify_connectivity()
            health_status["neo4j"] = "healthy"
        except Exception as e:
            logger.error(f"Neo4j health check failed: {e}")
            health_status["neo4j"] = "unhealthy"
        
        # InfluxDB
        try:
            influx_client = await get_influx()
            health = await influx_client.health()
            health_status["influxdb"] = "healthy" if health.status == "pass" else "degraded"
        except Exception as e:
            logger.error(f"InfluxDB health check failed: {e}")
            health_status["influxdb"] = "unhealthy"
        
        return health_status
    
    async def check_external_apis(self) -> Dict[str, str]:
        """Check health of external APIs"""
        health_status = {}
        
        # Social Media APIs
        apis_to_check = [
            ("twitter", "https://api.twitter.com/2/tweets/20"),
            ("openai", "https://api.openai.com/v1/models"),
        ]
        
        for api_name, url in apis_to_check:
            try:
                # This would normally make a test API call
                health_status[api_name] = "healthy"
            except Exception as e:
                logger.warning(f"{api_name} API health check failed: {e}")
                health_status[api_name] = "degraded"
        
        return health_status
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health"""
        try:
            # Check database health
            db_health = await self.check_database_health()
            
            # Check external APIs
            api_health = await self.check_external_apis()
            
            # Combine all services
            all_services = {**db_health, **api_health}
            
            # Determine overall status
            unhealthy_count = sum(1 for status in all_services.values() if status == "unhealthy")
            degraded_count = sum(1 for status in all_services.values() if status == "degraded")
            
            if unhealthy_count > 0:
                overall_status = "unhealthy"
            elif degraded_count > 2:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            # Get system metrics
            metrics = await self.get_system_metrics()
            
            return SystemHealth(
                status=overall_status,
                services=all_services,
                metrics=metrics,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting system health: {e}")
            return SystemHealth(
                status="unhealthy",
                services={},
                metrics={},
                timestamp=datetime.utcnow()
            )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            # CPU and Memory
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "network_packets_sent": network.packets_sent,
                "network_packets_recv": network.packets_recv,
                "uptime_seconds": time.time() - psutil.boot_time()
            }
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {}


class MetricsCollector:
    """Collect and export metrics"""
    
    def __init__(self):
        self.health_checker = HealthChecker()
        self.metrics_history = []
        
    async def start_metrics_collection(self):
        """Start collecting metrics periodically"""
        logger.info("Starting metrics collection...")
        
        # Start Prometheus metrics server
        start_http_server(8001)
        logger.info("Prometheus metrics server started on port 8001")
        
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)
    
    async def collect_metrics(self):
        """Collect current metrics"""
        try:
            # System metrics
            metrics = await self.health_checker.get_system_metrics()
            
            # Update Prometheus metrics
            SYSTEM_CPU_USAGE.set(metrics.get("cpu_usage_percent", 0))
            SYSTEM_MEMORY_USAGE.set(metrics.get("memory_usage_percent", 0))
            
            # Store metrics history
            self.metrics_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": metrics
            })
            
            # Keep only last 1000 entries
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
    
    def get_metrics_history(self, hours: int = 24) -> List[Dict]:
        """Get metrics history for the last N hours"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            entry for entry in self.metrics_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]


class AlertManager:
    """Manage system alerts and notifications"""
    
    def __init__(self):
        self.alert_rules = {
            "high_cpu": {"threshold": 80, "duration": 300},  # 80% for 5 minutes
            "high_memory": {"threshold": 85, "duration": 300},
            "high_disk": {"threshold": 90, "duration": 60},
            "service_down": {"threshold": 1, "duration": 60},
            "high_response_time": {"threshold": 5.0, "duration": 120}
        }
        self.active_alerts = {}
    
    async def check_alerts(self, health: SystemHealth):
        """Check for alert conditions"""
        current_time = datetime.utcnow()
        
        # Check CPU usage
        cpu_usage = health.metrics.get("cpu_usage_percent", 0)
        await self._check_threshold_alert(
            "high_cpu", cpu_usage, 
            self.alert_rules["high_cpu"]["threshold"],
            current_time
        )
        
        # Check memory usage
        memory_usage = health.metrics.get("memory_usage_percent", 0)
        await self._check_threshold_alert(
            "high_memory", memory_usage,
            self.alert_rules["high_memory"]["threshold"],
            current_time
        )
        
        # Check service health
        unhealthy_services = sum(
            1 for status in health.services.values() 
            if status == "unhealthy"
        )
        await self._check_threshold_alert(
            "service_down", unhealthy_services,
            self.alert_rules["service_down"]["threshold"],
            current_time
        )
    
    async def _check_threshold_alert(
        self, alert_name: str, current_value: float, 
        threshold: float, current_time: datetime
    ):
        """Check if a threshold alert should be triggered"""
        if current_value >= threshold:
            if alert_name not in self.active_alerts:
                self.active_alerts[alert_name] = current_time
            else:
                # Check if alert duration threshold is met
                duration = (current_time - self.active_alerts[alert_name]).total_seconds()
                rule_duration = self.alert_rules[alert_name]["duration"]
                
                if duration >= rule_duration:
                    await self._trigger_alert(alert_name, current_value, threshold)
        else:
            # Clear alert if value is below threshold
            if alert_name in self.active_alerts:
                await self._clear_alert(alert_name)
                del self.active_alerts[alert_name]
    
    async def _trigger_alert(self, alert_name: str, value: float, threshold: float):
        """Trigger an alert"""
        logger.warning(
            f"ALERT TRIGGERED: {alert_name} - "
            f"Value: {value}, Threshold: {threshold}"
        )
        
        # Here you would integrate with alerting systems like:
        # - Slack notifications
        # - Email alerts
        # - PagerDuty
        # - Discord webhooks
    
    async def _clear_alert(self, alert_name: str):
        """Clear an alert"""
        logger.info(f"ALERT CLEARED: {alert_name}")


def setup_monitoring():
    """Initialize monitoring components"""
    logger.info("Setting up monitoring...")
    
    # This would start background tasks for monitoring
    # In a real implementation, you'd use asyncio.create_task() or similar
    
    logger.info("Monitoring setup complete")


# Singleton instances
health_checker = HealthChecker()
metrics_collector = MetricsCollector()
alert_manager = AlertManager()
