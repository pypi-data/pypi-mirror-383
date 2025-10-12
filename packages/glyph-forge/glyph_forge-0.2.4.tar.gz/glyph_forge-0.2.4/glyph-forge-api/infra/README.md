# Glyph Forge Infrastructure

This directory contains the AWS CDK infrastructure code for Glyph Forge, organized by resource type for better maintainability and scalability.

## Structure

```
infra/
├── __init__.py              # Main package exports
├── app.py                   # CDK app entry point
├── requirements.txt         # Python dependencies
├── common/                  # Shared utilities
│   ├── __init__.py
│   ├── iam.py              # IAM utilities
│   ├── networking.py       # VPC/networking utilities
│   └── tags.py             # Tagging utilities
├── ecr/                    # ECR repositories
│   ├── __init__.py
│   └── glyph_ecr_stack.py
├── lambda/                 # Lambda functions
│   ├── __init__.py
│   ├── glyph_lambda_stack.py
│   └── LAMBDA_DEPLOYMENT.md
├── pipeline/               # CI/CD pipelines
│   ├── __init__.py
│   └── glyph_pipeline_stack.py
├── s3/                    # S3 buckets
│   ├── __init__.py
│   └── glyph_s3_stack.py
└── api_gateway/           # API Gateway resources (future)
    └── __init__.py
```

## Usage

### Deploying Infrastructure

```bash
# Deploy ECR repositories
cdk deploy GlyphECRDev GlyphECRQA GlyphECRProd

# Deploy CI/CD pipelines
cdk deploy GlyphPipelineDev GlyphPipelineQA GlyphPipelineProd

# Deploy Lambda functions
cdk deploy GlyphLambdaDev GlyphLambdaQA GlyphLambdaProd

# Deploy S3 buckets
cdk deploy GlyphS3Dev GlyphS3QA GlyphS3Prod
```

### Using Common Utilities

The `common/` package provides reusable utilities:

```python
from infra.common import get_common_tags, create_basic_execution_role

# Apply consistent tags
tags = get_common_tags("dev")
for key, value in tags.items():
    Tags.of(self).add(key, value)

# Create standard execution role
role = create_basic_execution_role(self, "MyRole")
```

## Adding New Resources

1. Create a new folder under `infra/` (e.g., `rds/`, `s3/`)
2. Add `__init__.py` with exports
3. Create stack classes following the naming pattern
4. Update `infra/__init__.py` to export new stacks
5. Add imports to `app.py`

## Environment Variables

Required environment variables:
- `GLYPH_DEV_ACCOUNT` - AWS account ID for dev environment
- `GLYPH_QA_ACCOUNT` - AWS account ID for QA environment  
- `GLYPH_PROD_ACCOUNT` - AWS account ID for prod environment
- `GLYPH_REGION` - AWS region (default: us-east-1)
- `GLYPH_FORGE_REPO` - GitHub repository for CI/CD (default: Devpro-LLC/glyph-forge-api)