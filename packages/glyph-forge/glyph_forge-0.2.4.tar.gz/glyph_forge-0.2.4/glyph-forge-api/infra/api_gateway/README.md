# Glyph Forge API Gateway Implementation

This module implements the global API delivery system for Glyph Forge using AWS API Gateway and CloudFront.

## Architecture

### Components

1. **HTTP API Gateway** (`GlyphApiStack`)
   - Lambda proxy integration
   - CORS enabled
   - Global edge acceleration via CloudFront
   - Cost-optimized for high-volume traffic

2. **REST API Gateway** (`GlyphApiSecurityStack`)
   - Usage plans and API keys
   - Subscription tier enforcement
   - Throttling and quotas
   - Access logging

### Subscription Tiers

| Plan | Rate Limit | Burst Limit | Monthly Quota |
|------|------------|-------------|---------------|
| Starter | 10 req/sec | 20 req/sec | 1,000 requests |
| Pro | 50 req/sec | 100 req/sec | 10,000 requests |
| Enterprise | 200 req/sec | 500 req/sec | Unlimited |

## Deployment

### Prerequisites

1. Lambda function deployed
2. Environment variables configured in `.env`

### Deploy API Gateway

```bash
# Development environment
./scripts/deploy-api-dev.sh

# Manual deployment
cd infra
cdk deploy GlyphApiDev GlyphApiSecurityDev
```

### Outputs

After deployment, you'll get:

- **API URL**: Direct API Gateway endpoint
- **CloudFront URL**: Global edge-accelerated endpoint
- **API Keys**: For testing subscription tiers

## Usage

### Health Check

```bash
curl https://your-cloudfront-url/health
curl https://your-cloudfront-url/v1/health
```

### With API Key (REST API)

```bash
curl -H "x-api-key: YOUR_API_KEY" https://your-rest-api-url/v1/glyphs
```

## Security Features

- **HTTPS Only**: All traffic redirected to HTTPS
- **CORS**: Configured for browser access
- **Rate Limiting**: Per-tier throttling
- **Access Logs**: CloudWatch integration
- **X-Ray Tracing**: End-to-end visibility (optional)

## Cost Optimization

- HTTP API used for primary traffic (cheaper than REST)
- CloudFront reduces API Gateway data transfer costs
- Usage plans prevent runaway costs
- Caching disabled for dynamic content

## Monitoring

- CloudWatch metrics for API Gateway
- Access logs for request analysis
- Usage plan metrics for billing
- Lambda integration metrics

## Custom Domain Setup

To use a custom domain (e.g., `api.glyphforge.com`):

1. Create ACM certificate in `us-east-1`
2. Update stack with domain name and certificate ARN
3. Configure Route 53 CNAME to CloudFront distribution

## Global Performance

CloudFront edge locations provide:
- Reduced latency worldwide
- DDoS protection
- SSL termination at edge
- Compression for API responses