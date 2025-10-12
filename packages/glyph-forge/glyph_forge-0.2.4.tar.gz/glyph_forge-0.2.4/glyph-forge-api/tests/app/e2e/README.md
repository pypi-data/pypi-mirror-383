# End-to-End Tests for Stripe & Customer Database

This directory contains comprehensive end-to-end tests for Stripe integration and customer database operations in the Glyph Forge application.

## Overview

These tests provide full coverage of:
- **Stripe Checkout**: Complete checkout flows including session creation, payment processing, and subscription activation
- **Customer Database Operations**: User lifecycle, subscription management, API key operations, usage tracking
- **Webhook Integration**: Stripe webhook event processing and database synchronization
- **Payment Processing**: Invoice payments, failures, retries, and refunds

## Test Organization

### `test_stripe_checkout_e2e.py`
End-to-end tests for Stripe checkout workflows:
- ✅ New customer checkout flow
- ✅ Checkout with trial periods
- ✅ Checkout idempotency (duplicate event handling)
- ✅ User validation and error handling
- ✅ Multiple subscription tiers
- ✅ Metadata handling
- ✅ Stripe API failure scenarios
- ✅ Database transaction rollback
- ✅ Webhook signature verification
- ✅ One-time payment handling
- ✅ Existing subscription updates

**Key Test Classes:**
- `TestStripeCheckoutEndToEnd`: Complete checkout workflow tests

### `test_customer_database_e2e.py`
Comprehensive database operation tests:
- ✅ User CRUD operations and lifecycle
- ✅ Default subscription creation
- ✅ Soft delete cascading
- ✅ Subscription upgrades/downgrades
- ✅ Subscription cancellation
- ✅ Trial-to-active transitions
- ✅ API key lifecycle (creation, rotation, revocation)
- ✅ API usage tracking and aggregation
- ✅ Rate limiting
- ✅ Payment history tracking
- ✅ Audit logging
- ✅ Database constraints and triggers

**Key Test Classes:**
- `TestUserDatabaseOperations`: User CRUD and lifecycle
- `TestSubscriptionDatabaseOperations`: Subscription management
- `TestAPIKeyDatabaseOperations`: API key lifecycle
- `TestAPIUsageDatabaseOperations`: Usage tracking and metrics
- `TestPaymentDatabaseOperations`: Payment history
- `TestAuditLogDatabaseOperations`: Audit trail
- `TestDatabaseConstraintsAndTriggers`: Data integrity

### `test_stripe_webhook_integration_e2e.py`
Integration tests for webhook processing:
- ✅ Webhook event deduplication
- ✅ Event logging and status tracking
- ✅ Subscription creation workflow
- ✅ Subscription update/upgrade workflow
- ✅ Subscription cancellation workflow
- ✅ Trial ending notifications
- ✅ Payment success processing
- ✅ Payment failure handling
- ✅ One-time vs subscription payments
- ✅ Error handling and recovery
- ✅ Database transaction rollback
- ✅ Stripe API timeouts
- ✅ Webhook security validation
- ✅ Complete lifecycle workflows (creation → payment → upgrade → cancellation)
- ✅ Payment retry workflows

**Key Test Classes:**
- `TestWebhookEventLifecycle`: Event processing lifecycle
- `TestSubscriptionLifecycleIntegration`: Subscription events
- `TestPaymentProcessingIntegration`: Payment workflows
- `TestWebhookErrorHandlingIntegration`: Error scenarios
- `TestWebhookSecurityIntegration`: Security validation
- `TestCompleteWorkflowIntegration`: Multi-event workflows

### `conftest.py`
Shared fixtures and test utilities:
- **Environment Setup**: Test environment configuration
- **Database Fixtures**: Mock connections, pools, transactions
- **User Fixtures**: Test users, authentication tokens
- **Subscription Fixtures**: All subscription tiers and configurations
- **API Key Fixtures**: Test API keys and credentials
- **Stripe Fixtures**: Mock customers, prices, subscriptions, checkout sessions, invoices
- **Payment Fixtures**: Payment history data
- **Usage Fixtures**: API usage and metrics data
- **Audit Fixtures**: Audit log entries
- **Helper Functions**: Test utilities, factories, assertions

## Running Tests

### Run All E2E Tests
```bash
pytest tests/app/e2e/
```

### Run Specific Test File
```bash
pytest tests/app/e2e/test_stripe_checkout_e2e.py
pytest tests/app/e2e/test_customer_database_e2e.py
pytest tests/app/e2e/test_stripe_webhook_integration_e2e.py
```

### Run Specific Test Class
```bash
pytest tests/app/e2e/test_stripe_checkout_e2e.py::TestStripeCheckoutEndToEnd
pytest tests/app/e2e/test_customer_database_e2e.py::TestUserDatabaseOperations
```

### Run Specific Test
```bash
pytest tests/app/e2e/test_stripe_checkout_e2e.py::TestStripeCheckoutEndToEnd::test_complete_checkout_flow_new_customer
```

### Run with Coverage
```bash
pytest tests/app/e2e/ --cov=app --cov-report=html
```

### Run with Verbose Output
```bash
pytest tests/app/e2e/ -v
```

### Run Only Failed Tests
```bash
pytest tests/app/e2e/ --lf
```

## Test Coverage

### Stripe Checkout Coverage
- [x] New customer onboarding
- [x] Returning customer checkout
- [x] Trial subscription setup
- [x] Multiple subscription tiers (free, starter, professional, enterprise)
- [x] Checkout metadata handling
- [x] Idempotency and duplicate detection
- [x] Error handling (user not found, API failures, database errors)
- [x] Transaction integrity
- [x] Webhook signature verification

### Database Operations Coverage
- [x] User lifecycle (create, read, update, soft delete)
- [x] Email uniqueness constraints
- [x] Stripe customer ID association
- [x] Last login tracking
- [x] Subscription creation (all tiers)
- [x] Subscription upgrades/downgrades
- [x] Subscription cancellation with reasons
- [x] Billing period resets
- [x] Trial-to-active transitions
- [x] One active subscription per user constraint
- [x] API key creation with subscription validation
- [x] API key usage tracking
- [x] API key rotation
- [x] API key revocation with audit trail
- [x] API key expiration checks
- [x] API usage partitioning by date
- [x] Monthly usage aggregation
- [x] Rate limiting per time window
- [x] Payment history tracking
- [x] Payment refund status
- [x] Audit logging for sensitive operations
- [x] Database constraints (email format, period dates, positive amounts)
- [x] Automatic triggers (updated_at, usage aggregation, audit logging)

### Webhook Integration Coverage
- [x] Event deduplication
- [x] Event status tracking (processing, completed, failed)
- [x] `checkout.session.completed` handling
- [x] `customer.subscription.created` handling
- [x] `customer.subscription.updated` handling
- [x] `customer.subscription.deleted` handling
- [x] `customer.subscription.trial_will_end` handling
- [x] `invoice.payment_succeeded` handling
- [x] `invoice.payment_failed` handling
- [x] User not found error handling
- [x] Database transaction rollback on errors
- [x] Stripe API timeout handling
- [x] Invalid webhook signature rejection
- [x] Malformed payload rejection
- [x] Complete lifecycle workflows
- [x] Payment retry workflows

## Test Architecture

### Mocking Strategy
Tests use comprehensive mocking to avoid external dependencies:
- **Stripe API**: Mocked using `unittest.mock.patch`
- **Database**: Mocked using `AsyncMock` for asyncpg connections
- **AWS Services**: Mocked Secrets Manager and Cognito
- **Time**: Fixtures for time-based testing

### Async Testing
All tests use `@pytest.mark.asyncio` for proper async/await support with FastAPI and asyncpg.

### Fixtures
Reusable fixtures in `conftest.py` provide:
- Consistent test data across all tests
- Easy setup for complex scenarios
- Reduced test code duplication
- Clear test dependencies

### Assertions
Tests verify:
- Database method calls (`execute`, `fetchrow`, `fetch`)
- Query content (INSERT, UPDATE, SELECT statements)
- Transaction boundaries
- Error conditions and exception types
- Return values and status codes

## Key Testing Patterns

### 1. Database Call Verification
```python
execute_calls = [str(call) for call in mock_db_connection.execute.call_args_list]
subscription_insert = [call for call in execute_calls if 'INSERT INTO subscriptions' in call]
assert len(subscription_insert) > 0
```

### 2. Error Scenario Testing
```python
mock_db_connection.execute = AsyncMock(
    side_effect=asyncpg.PostgresError("Database error")
)
with pytest.raises(asyncpg.PostgresError):
    await function_under_test()
```

### 3. Workflow Testing
```python
# 1. Create subscription
await handle_subscription_created(conn, subscription_data)

# 2. Process payment
await handle_payment_succeeded(conn, invoice_data)

# 3. Verify state
assert conn.execute.call_count >= 2
```

## Relationship to Infrastructure Tests

These E2E tests complement but **do not overlap** with `tests/infra/database/`:

| Infrastructure Tests | E2E Tests |
|---------------------|-----------|
| CDK stack creation | Application logic |
| AWS resource configuration | Stripe webhook handlers |
| IAM policies | Database operations |
| VPC and networking | API key management |
| Lambda functions | User workflows |
| EventBridge rules | Payment processing |
| CloudWatch monitoring | Usage tracking |

**Infrastructure tests** verify that AWS resources are correctly provisioned.
**E2E tests** verify that the application correctly uses those resources.

## Environment Variables

Required for running tests (set in `conftest.py`):
```bash
ENVIRONMENT=test
DATABASE_URL=postgresql://test:test@localhost:5432/test_db
STRIPE_SECRET_KEY=sk_test_123
STRIPE_WEBHOOK_SECRET=whsec_test_123
JWT_SECRET=test_jwt_secret_key_for_testing
```

## Dependencies

Required Python packages:
```
pytest
pytest-asyncio
pytest-cov
asyncpg
stripe
fastapi
boto3
```

## Future Enhancements

Potential areas for additional coverage:
- [ ] Concurrent webhook processing
- [ ] Webhook retry mechanisms
- [ ] Rate limit enforcement integration
- [ ] Usage quota enforcement
- [ ] Email notification testing
- [ ] Webhook event replay
- [ ] Subscription proration handling
- [ ] Multi-currency support
- [ ] Tax calculation integration
- [ ] Coupon and discount handling

## Troubleshooting

### Tests Fail with Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Async Test Warnings
Ensure `pytest-asyncio` is installed and tests use `@pytest.mark.asyncio`.

### Mock Not Working
Verify patch paths match the actual import locations in the source code.

### Database Connection Errors
Tests should not connect to real databases - check that mocks are properly configured in fixtures.

## Contributing

When adding new tests:
1. Use existing fixtures from `conftest.py` when possible
2. Follow the established naming conventions (`test_*`)
3. Add comprehensive docstrings explaining what is tested
4. Use descriptive assertion messages
5. Test both success and failure scenarios
6. Update this README with new coverage areas

## Contact

For questions about these tests, contact the development team or refer to:
- [Main Project README](../../../README.md)
- [Infrastructure Tests](../../infra/database/README.md)
- [Stripe Integration Documentation](../../../docs/stripe_integration.md)
