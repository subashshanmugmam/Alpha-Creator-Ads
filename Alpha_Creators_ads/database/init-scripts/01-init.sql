-- Alpha Creators Ads Database Initialization Script
-- This script sets up the basic database structure and initial data

\echo 'Starting Alpha Creators Ads database initialization...'

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS monitoring;

\echo 'Extensions and schemas created successfully'

-- Create basic indexes for performance
\echo 'Creating performance indexes...'

-- User table indexes (will be created when SQLAlchemy runs)
-- These are example indexes that can be created manually if needed

-- Create a function for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

\echo 'Trigger function created successfully'

-- Create monitoring table for database health
CREATE TABLE IF NOT EXISTS monitoring.db_health_checks (
    id SERIAL PRIMARY KEY,
    check_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial health check
INSERT INTO monitoring.db_health_checks (check_name, status, response_time_ms) 
VALUES ('initial_setup', 'success', 0);

\echo 'Database health monitoring table created'

-- Create analytics schema tables
CREATE TABLE IF NOT EXISTS analytics.daily_metrics (
    id SERIAL PRIMARY KEY,
    metric_date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(metric_date, metric_name)
);

\echo 'Analytics tables created'

-- Grant permissions
GRANT USAGE ON SCHEMA analytics TO alphaads_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO alphaads_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO alphaads_user;

GRANT USAGE ON SCHEMA monitoring TO alphaads_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO alphaads_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA monitoring TO alphaads_user;

\echo 'Permissions granted successfully'

-- Insert initial configuration data
CREATE TABLE IF NOT EXISTS system_config (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add trigger for updated_at
CREATE TRIGGER update_system_config_updated_at 
    BEFORE UPDATE ON system_config 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default configuration
INSERT INTO system_config (key, value, description) VALUES
('app_version', '1.0.0', 'Application version'),
('maintenance_mode', 'false', 'Maintenance mode flag'),
('max_daily_posts', '100000', 'Maximum posts processed per day'),
('api_rate_limit', '1000', 'API requests per minute limit')
ON CONFLICT (key) DO NOTHING;

\echo 'System configuration initialized'

-- Create performance monitoring views
CREATE OR REPLACE VIEW monitoring.table_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as bytes
FROM pg_tables 
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

CREATE OR REPLACE VIEW monitoring.database_stats AS
SELECT 
    pg_database_size(current_database()) as database_size_bytes,
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
    (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections;

\echo 'Monitoring views created'

-- Log completion
INSERT INTO monitoring.db_health_checks (check_name, status, response_time_ms) 
VALUES ('initialization_complete', 'success', 0);

\echo 'Alpha Creators Ads database initialization completed successfully!'
\echo 'Database is ready for the application backend to create its tables.'
