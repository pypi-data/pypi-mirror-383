# Glyph Forge Database Schema & Maintenance

Comprehensive database schema for Stripe integration with automated maintenance, monitoring, and fire-and-forget operations.

## 📋 Overview

This database schema provides:
- **User Management**: AWS Cognito + Stripe customer integration
- **Subscription Billing**: Multi-tier subscription management
- **API Key System**: Secure API authentication and tracking
- **Usage Tracking**: Time-series API usage with automatic partitioning
- **Auto-Healing**: Triggers for data integrity and default values
- **Monitoring**: Health checks and anomaly detection
- **Automated Maintenance**: Cleanup, partitioning, and sync jobs

## 🗂️ File Structure

```
infra/database/
├── schema.sql                    # Core database schema with tables, indexes, triggers
├── maintenance_functions.sql     # Cleanup and maintenance functions
├── monitoring_views.sql          # Health check and reporting views
├── migrate.py                    # Database migration script
├── cron_scheduler.py            # Python scheduler for maintenance jobs
├── cron_setup.sh                # Shell script to setup cron jobs
├── aws_lambda_deploy.yaml       # CloudFormation template for AWS Lambda
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Initialize Database

```bash
# Set database connection
export DATABASE_URL="postgresql://user:password@localhost:5432/glyph_forge"

# Install dependencies
pip install -r requirements.txt

# Test connection
python migrate.py test

# Initialize schema
python migrate.py init

# Verify installation
python migrate.py verify
```

### 2. Setup Automated Maintenance

**Option A: Using Cron (Linux/Unix)**

```bash
# Setup cron jobs (requires sudo)
sudo ./cron_setup.sh

# Edit configuration
nano .env

# Verify cron jobs
crontab -l
```

**Option B: Using Systemd Service**

```bash
# Enable service
sudo systemctl enable glyph-forge-maintenance.service
sudo systemctl start glyph-forge-maintenance.service

# Check status
sudo systemctl status glyph-forge-maintenance.service

# View logs
sudo journalctl -u glyph-forge-maintenance.service -f
```

**Option C: AWS Lambda (Production)**

```bash
# Package Lambda function
./package_lambda.sh

# Deploy CloudFormation stack
aws cloudformation deploy \
  --template-file aws_lambda_deploy.yaml \
  --stack-name glyph-forge-db-maintenance \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    DatabaseURL="postgresql://..." \
    SlackWebhookURL="https://hooks.slack.com/..." \
    VpcSecurityGroupIds="sg-xxxxx" \
    VpcSubnetIds="subnet-xxxxx,subnet-yyyyy"
```

## 📊 Database Schema

### Core Tables

#### `users`
- Linked to AWS Cognito and Stripe
- Stores email, name, account status
- Auto-creates default free subscription on insert

#### `subscriptions`
- Manages subscription tiers (free, starter, professional, enterprise)
- Tracks billing periods and usage limits
- Unique constraint: one active subscription per user

#### `api_keys`
- Stores hashed API keys with prefixes
- Environment-specific (development, staging, production)
- Tracks usage count and last used timestamp

#### `api_usage` (Partitioned)
- Time-series request logs partitioned by month
- Automatic partition creation for future months
- Old partitions dropped after retention period (90 days)

#### `monthly_usage_summary`
- Pre-aggregated usage statistics
- Updated automatically via trigger on `api_usage` inserts

#### `payment_history`
- Complete record of Stripe payments
- Links to invoices and receipts

#### `stripe_webhook_events`
- Audit log of all Stripe webhook events
- Idempotency tracking to prevent duplicate processing

#### `rate_limits`
- Time-windowed rate limiting state
- Automatic cleanup of expired windows

#### `audit_log`
- Comprehensive audit trail
- Tracks all sensitive operations

### Auto-Healing Triggers

1. **Default Subscription**: Creates free tier subscription for new users
2. **Updated At**: Automatically updates `updated_at` timestamp
3. **Monthly Usage**: Aggregates API usage statistics in real-time
4. **API Key Usage**: Updates last used timestamp and counter
5. **Audit Logging**: Tracks changes to subscriptions and API keys

## 🔧 Maintenance Functions

### Daily Tasks

```sql
-- Run all daily maintenance
SELECT * FROM run_daily_maintenance();

-- Individual tasks
SELECT cleanup_old_api_usage(90);        -- Drop partitions > 90 days
SELECT cleanup_webhook_events(30);        -- Delete processed webhooks > 30 days
SELECT create_api_usage_partitions(3);   -- Create 3 months of partitions
SELECT fix_orphaned_stripe_customers();  -- Fix missing subscriptions
```

### Hourly Tasks

```sql
-- Sync usage counts
SELECT sync_subscription_usage();

-- Check for stale data
SELECT * FROM find_stale_subscriptions();
```

### Webhook Processing

```sql
-- Check if webhook can be processed (idempotency)
SELECT start_webhook_processing('evt_xxxxx');

-- Mark webhook as completed
SELECT complete_webhook_processing('evt_xxxxx', NULL);  -- Success
SELECT complete_webhook_processing('evt_xxxxx', 'Error message');  -- Failure
```

## 📈 Monitoring Views

### Health Checks

```sql
-- Overall system health
SELECT * FROM v_system_health;

-- Specific issues
SELECT * FROM v_orphaned_stripe_customers;
SELECT * FROM v_stale_subscriptions;
SELECT * FROM v_failed_webhook_events;
SELECT * FROM v_paid_users_without_keys;
```

### Usage Anomalies

```sql
-- High volume users (potential abuse)
SELECT * FROM v_high_volume_users;

-- Users near their limit
SELECT * FROM v_users_near_limit;

-- Repeated failures (potential issues)
SELECT * FROM v_repeated_failures;

-- Slow endpoints
SELECT * FROM v_slow_endpoints;
```

### Business Metrics

```sql
-- Subscription breakdown
SELECT * FROM v_subscription_breakdown;

-- Revenue metrics
SELECT * FROM v_revenue_metrics;

-- User growth
SELECT * FROM v_user_growth;

-- API usage trends
SELECT * FROM v_api_usage_trends;
```

### Operational Metrics

```sql
-- Database size
SELECT * FROM v_database_size;

-- Connection pool status
SELECT * FROM v_database_connections;

-- Long running queries
SELECT * FROM v_long_running_queries;

-- API key usage
SELECT * FROM v_api_key_usage_summary;
```

### Critical Alerts

```sql
-- Get all critical alerts
SELECT * FROM v_critical_alerts;
```

## ⏰ Maintenance Schedule

### Cron Jobs

| Frequency | Time | Job | Description |
|-----------|------|-----|-------------|
| Daily | 1:00 AM | Create Partitions | Create future month partitions |
| Daily | 2:00 AM | Daily Maintenance | Full maintenance run |
| Daily | 8:00 AM | Daily Report | Send summary report |
| Hourly | :05 | Sync Usage | Update subscription counters |
| Hourly | :10 | Fix Orphans | Create missing subscriptions |
| Every 15 min | | Health Check | Check system health |
| Weekly | Sun 3:00 AM | Deep Cleanup | Cleanup audit logs, etc. |

### Lambda Functions

| Function | Trigger | Timeout | Memory |
|----------|---------|---------|--------|
| Daily Maintenance | 2:00 AM UTC | 15 min | 512 MB |
| Health Check | Every 15 min | 5 min | 256 MB |
| Hourly Sync | Every hour :05 | 5 min | 256 MB |

## 🔐 Security Considerations

### API Keys
- ✅ Keys are hashed using bcrypt before storage
- ✅ Only prefix shown in database (e.g., `glyph_sk_live_1234...`)
- ✅ Full key only displayed once during generation
- ✅ Keys can be revoked with reason tracking

### Webhooks
- ✅ Stripe signature verification required
- ✅ Idempotency prevents duplicate processing
- ✅ Complete audit trail of all events

### Database
- ✅ Prepared statements prevent SQL injection
- ✅ Advisory locks prevent race conditions
- ✅ Audit log tracks all sensitive operations
- ✅ Connection limits prevent exhaustion

## 📊 Performance Optimizations

### Partitioning
- `api_usage` partitioned by month
- Automatic partition creation
- Automatic partition dropping (>90 days)

### Indexes
- Covering indexes on common query patterns
- Partial indexes for active records only
- GIN indexes on JSONB columns

### Aggregation
- `monthly_usage_summary` pre-aggregated via trigger
- Reduces query load on `api_usage` table

### Cleanup
- Automatic vacuum and analyze
- Expired data cleanup
- Dead row monitoring

## 🚨 Alerting

### Critical Alerts (Immediate Action)
- Stale subscriptions (>3 days expired but still active)
- Failed webhooks (>3 retries)
- High error rate (>50 errors/hour per user)
- Database connections >80%

### Warning Alerts (Review Soon)
- Orphaned Stripe customers (>10)
- Failed webhooks (1-3 retries)
- Users approaching limit (>80%)
- Database connections >60%

### Info Alerts (Awareness)
- Paid users without API keys
- Daily maintenance summary
- Usage reports

## 🧪 Testing

### Test Database Connection

```bash
python migrate.py test
```

### Run Specific Maintenance Job

```bash
python cron_scheduler.py --job health
python cron_scheduler.py --job daily
python cron_scheduler.py --job sync
```

### Verify Schema

```bash
python migrate.py verify
```

### Check Status

```bash
python migrate.py status
```

## 📝 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://user:password@host:5432/database

# Optional (Alerting)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
ALERT_EMAIL=alerts@yourdomain.com

# Optional (AWS Lambda)
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

## 🔄 Backup Strategy

### Automated Backups (AWS RDS)
- Daily snapshots (7-day retention)
- Point-in-time recovery enabled
- Backup window: 3:00-4:00 AM UTC

### Manual Backup

```bash
# Full backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Schema only
pg_dump --schema-only $DATABASE_URL > schema_backup.sql

# Data only
pg_dump --data-only $DATABASE_URL > data_backup.sql
```

### Restore

```bash
# Restore full backup
psql $DATABASE_URL < backup_20250930.sql
```

## 🐛 Troubleshooting

### Issue: Stale Subscriptions

```sql
-- Check for stale subscriptions
SELECT * FROM v_stale_subscriptions;

-- Manually fix (after verifying with Stripe)
UPDATE subscriptions
SET status = 'canceled', canceled_at = NOW()
WHERE id = 'subscription_id';
```

### Issue: Failed Webhooks

```sql
-- Check failed webhooks
SELECT * FROM v_failed_webhook_events;

-- Retry webhook processing
SELECT * FROM retry_failed_webhooks(3);
```

### Issue: Orphaned Customers

```sql
-- Check orphaned customers
SELECT * FROM v_orphaned_stripe_customers;

-- Auto-fix
SELECT * FROM fix_orphaned_stripe_customers();
```

### Issue: High Database Size

```sql
-- Check table sizes
SELECT * FROM v_database_size;

-- Cleanup old data
SELECT cleanup_old_api_usage(90);

-- Vacuum tables
VACUUM ANALYZE;
```

## 📖 Additional Resources

- [Stripe Integration Plan](../../docs/stripe_integration.md)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)

## 📧 Support

For issues or questions:
- Check logs: `/var/log/glyph-forge/`
- View CloudWatch Logs (Lambda)
- Contact: dev@glyphapi.ai

---

**Last Updated**: 2025-09-30
**Version**: 1.0.0
**Status**: Production Ready
