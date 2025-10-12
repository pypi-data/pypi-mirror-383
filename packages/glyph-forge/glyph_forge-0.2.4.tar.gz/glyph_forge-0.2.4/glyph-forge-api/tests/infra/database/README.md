# Database Infrastructure Tests

This directory contains comprehensive unit and integration tests for the Glyph Forge database infrastructure components.

## Test Structure

```
tests/infra/database/
├── __init__.py                     # Package initialization
├── conftest.py                     # Test fixtures and configuration
├── test_runner.py                  # Test runner script
├── test_glyph_rds_stack.py        # RDS stack unit tests
├── test_glyph_secrets_stack.py    # Secrets Manager stack unit tests
├── test_glyph_db_maintenance_stack.py  # Maintenance Lambda stack unit tests
├── test_cron_scheduler.py         # Cron scheduler logic unit tests
├── test_migrate.py                # Database migration script unit tests
├── test_integration.py            # Cross-stack integration tests
└── README.md                      # This file
```

## Components Tested

### 1. RDS Stack (`test_glyph_rds_stack.py`)
- VPC creation with public, private, and isolated subnets
- Security groups for database and Lambda access
- RDS PostgreSQL instance configuration
- Parameter groups with environment-specific settings
- Backup, monitoring, and maintenance windows
- Environment-specific resource sizing (dev vs prod)

### 2. Secrets Manager Stack (`test_glyph_secrets_stack.py`)
- Database credentials with auto-generated passwords
- Stripe API keys placeholder structure
- Notification configuration secrets
- Environment-specific naming conventions
- Proper removal policies for different environments

### 3. Database Maintenance Stack (`test_glyph_db_maintenance_stack.py`)
- Lambda function for maintenance operations
- Lambda layer with database dependencies
- EventBridge schedules (daily, hourly, health checks)
- IAM permissions for cross-service access
- VPC configuration for Lambda functions

### 4. Cron Scheduler (`test_cron_scheduler.py`)
- Database maintenance operations
- Health check monitoring
- Webhook processing and retry logic
- Slack and email alerting
- Lambda handler functions
- Error handling and logging

### 5. Migration Script (`test_migrate.py`)
- Database initialization and schema creation
- Migration tracking and status
- Schema verification
- CLI command handling
- Error handling and rollback

### 6. Integration Tests (`test_integration.py`)
- Cross-stack resource references
- Security group connectivity
- IAM permission chains
- Environment consistency
- Deployment dependency order

## Running Tests

### Run All Tests
```bash
cd tests/infra/database
python test_runner.py
```

### Run Specific Test Types
```bash
# Unit tests only
python test_runner.py --test-type unit

# Integration tests only
python test_runner.py --test-type integration

# Specific test file
python test_runner.py --specific glyph_rds_stack
```

### Run with Pytest Directly
```bash
# All database tests
pytest tests/infra/database/ -v

# Specific test file
pytest tests/infra/database/test_glyph_rds_stack.py -v

# With coverage
pytest tests/infra/database/ --cov=infra.database --cov-report=html
```

## Test Configuration

### Fixtures (`conftest.py`)
- Mock AWS services (CDK, Secrets Manager, RDS)
- Mock database connections (psycopg2)
- Sample test data for various scenarios
- Test utilities and helpers

### Mocked Dependencies
- `psycopg2` - PostgreSQL database adapter
- `boto3` - AWS SDK
- `requests` - HTTP library for webhooks
- `schedule` - Job scheduling library

## Test Coverage Areas

### Infrastructure as Code
- ✅ CDK stack synthesis and resource creation
- ✅ Resource properties and configuration
- ✅ Cross-stack references and dependencies
- ✅ Environment-specific configurations
- ✅ IAM permissions and security groups

### Database Operations
- ✅ Connection handling and error recovery
- ✅ Query execution and result processing
- ✅ Transaction management
- ✅ Migration and schema operations

### Maintenance and Monitoring
- ✅ Scheduled maintenance tasks
- ✅ Health check operations
- ✅ Alert generation and notification
- ✅ Error handling and retry logic

### Lambda Functions
- ✅ Event handling and routing
- ✅ Environment variable configuration
- ✅ VPC and security group setup
- ✅ Layer dependencies and packaging

## Best Practices

### Test Organization
- Each infrastructure component has its own test file
- Integration tests verify cross-component interactions
- Fixtures provide reusable test data and mocks
- Test utilities reduce code duplication

### Mocking Strategy
- Mock external dependencies (AWS services, databases)
- Use realistic test data that matches production schemas
- Mock at the appropriate abstraction level
- Preserve error conditions for negative testing

### Assertions
- Test both success and failure scenarios
- Verify resource properties and configurations
- Check cross-references and dependencies
- Validate environment-specific differences

## Adding New Tests

### For New Infrastructure Components
1. Create `test_new_component.py`
2. Add fixtures for the component in `conftest.py`
3. Test resource creation, configuration, and integration
4. Add integration tests if the component interacts with others

### For New Database Operations
1. Add tests to `test_cron_scheduler.py` or `test_migrate.py`
2. Mock database responses appropriately
3. Test both success and error scenarios
4. Verify logging and alerting behavior

### For New Lambda Functions
1. Test event handling and routing
2. Mock AWS service interactions
3. Verify environment configuration
4. Test error handling and timeouts

## Troubleshooting

### Common Issues
- **Import errors**: Ensure all dependencies are mocked in `conftest.py`
- **CDK synthesis errors**: Check resource properties and references
- **Mock configuration**: Verify mock return values match expected formats
- **Test isolation**: Ensure tests don't depend on external state

### Debug Tips
- Use `-v` flag for verbose test output
- Add `--tb=long` for detailed tracebacks
- Use `--pdb` to drop into debugger on failures
- Check mock call history with `mock.call_args_list`

## Continuous Integration

These tests are designed to run in CI/CD pipelines without external dependencies:
- All AWS services are mocked
- No actual database connections required
- Fast execution suitable for PR checks
- Comprehensive coverage for infrastructure validation