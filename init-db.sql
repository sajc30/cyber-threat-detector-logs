-- PostgreSQL initialization script for Cyber Threat Detector
-- This script creates the necessary tables for storing alerts and feedback

-- Create the alerts table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    host VARCHAR(255) NOT NULL,
    process VARCHAR(255),
    user_name VARCHAR(255),
    event_type VARCHAR(100),
    anomaly_score DECIMAL(5,4) NOT NULL,
    sequence_window TEXT,
    raw_log_ids TEXT[], -- Array of Elasticsearch document IDs
    is_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the feedback table for user corrections
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(alert_id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL CHECK (feedback_type IN ('true_positive', 'false_positive')),
    comments TEXT,
    submitted_by VARCHAR(255),
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the model_metrics table to track model performance over time
CREATE TABLE IF NOT EXISTS model_metrics (
    metric_id SERIAL PRIMARY KEY,
    model_version VARCHAR(50) NOT NULL,
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    roc_auc_score DECIMAL(5,4),
    threshold_value DECIMAL(5,4),
    evaluation_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dataset_size INTEGER,
    notes TEXT
);

-- Create the log_sources table to track different data sources
CREATE TABLE IF NOT EXISTS log_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(255) NOT NULL UNIQUE,
    source_type VARCHAR(100) NOT NULL, -- 'syslog', 'hadoop', 'windows', 'generic'
    is_active BOOLEAN DEFAULT TRUE,
    last_ingested TIMESTAMPTZ,
    total_logs_processed BIGINT DEFAULT 0,
    total_anomalies_detected BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_host ON alerts(host);
CREATE INDEX IF NOT EXISTS idx_alerts_anomaly_score ON alerts(anomaly_score);
CREATE INDEX IF NOT EXISTS idx_alerts_acknowledged ON alerts(is_acknowledged);
CREATE INDEX IF NOT EXISTS idx_feedback_alert_id ON feedback(alert_id);
CREATE INDEX IF NOT EXISTS idx_feedback_type ON feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_model_metrics_version ON model_metrics(model_version);
CREATE INDEX IF NOT EXISTS idx_log_sources_name ON log_sources(source_name);

-- Insert default log sources
INSERT INTO log_sources (source_name, source_type) VALUES 
    ('loghub_linux', 'syslog'),
    ('loghub_hadoop', 'hadoop'),
    ('landauer_dataset', 'syslog'),
    ('kaggle_dataset', 'generic'),
    ('synthetic_logs', 'generic')
ON CONFLICT (source_name) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at column
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_log_sources_updated_at BEFORE UPDATE ON log_sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create a view for alert statistics
CREATE OR REPLACE VIEW alert_statistics AS
SELECT 
    DATE_TRUNC('hour', timestamp) as hour_bucket,
    host,
    COUNT(*) as alert_count,
    AVG(anomaly_score) as avg_anomaly_score,
    MAX(anomaly_score) as max_anomaly_score,
    COUNT(CASE WHEN is_acknowledged THEN 1 END) as acknowledged_count
FROM alerts
GROUP BY DATE_TRUNC('hour', timestamp), host
ORDER BY hour_bucket DESC, alert_count DESC;

-- Create a view for feedback summary
CREATE OR REPLACE VIEW feedback_summary AS
SELECT 
    feedback_type,
    COUNT(*) as feedback_count,
    COUNT(DISTINCT alert_id) as unique_alerts,
    DATE_TRUNC('day', submitted_at) as feedback_date
FROM feedback
GROUP BY feedback_type, DATE_TRUNC('day', submitted_at)
ORDER BY feedback_date DESC;

-- Grant permissions (adjust as needed for your security requirements)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ctd_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ctd_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO ctd_user;

-- Insert some sample data for testing (optional)
-- Uncomment the following lines to add sample data

/*
INSERT INTO alerts (host, process, user_name, event_type, anomaly_score, sequence_window) VALUES
    ('web01', 'sshd', 'admin', 'login_attempt', 0.95, '[1,2,3,4,5]'),
    ('db01', 'postgres', 'postgres', 'query', 0.75, '[10,11,12,13,14]'),
    ('app01', 'nginx', 'www-data', 'request', 0.85, '[20,21,22,23,24]');

INSERT INTO feedback (alert_id, feedback_type, comments, submitted_by) VALUES
    (1, 'false_positive', 'This was a legitimate admin login', 'security_analyst'),
    (2, 'true_positive', 'Confirmed suspicious database activity', 'dba'),
    (3, 'false_positive', 'Normal traffic spike during deployment', 'devops_engineer');

INSERT INTO model_metrics (model_version, precision_score, recall_score, f1_score, roc_auc_score, threshold_value, dataset_size) VALUES
    ('v1.0.0', 0.85, 0.90, 0.875, 0.92, 0.75, 10000),
    ('v1.1.0', 0.87, 0.91, 0.89, 0.93, 0.73, 12000);
*/

-- Print success message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Created tables: alerts, feedback, model_metrics, log_sources';
    RAISE NOTICE 'Created views: alert_statistics, feedback_summary';
    RAISE NOTICE 'Created indexes and triggers for performance optimization';
END $$; 