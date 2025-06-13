# Absolut - Agentic Banking Solution

A comprehensive banking solution that includes payment processing and database management capabilities.

## Components

### Generic Database Service
Located in `genericdbservice/`, this component provides a secure and efficient way to interact with any database table through AWS Lambda. It implements a generic Data Access Object (DAO) pattern that supports all CRUD operations.

Key features:
- Generic database operations for any table
- Secure database connection handling
- JSON serialization for all data types (including Decimal and DateTime)
- Input validation and SQL injection prevention
- Comprehensive error handling and logging

#### Files in `genericdbservice/`:
- `lambda_function.py`: Main Lambda handler that processes requests
- `generic_dao.py`: Generic Data Access Object implementation
- `db_config.py`: Database configuration (use AWS Secrets Manager in production)
- `requirements.txt`: Required Python packages

#### Example Usage:
```json
// Create a record
{
    "action": "create",
    "table_name": "accounts",
    "data": {
        "account_number": "1234567890",
        "account_holder": "John Doe",
        "balance": 1000.00
    }
}

// Read records
{
    "action": "read",
    "table_name": "accounts",
    "conditions": {
        "account_holder": "John Doe"
    }
}

// Update records
{
    "action": "update",
    "table_name": "accounts",
    "data": {
        "balance": 1500.00
    },
    "conditions": {
        "account_number": "1234567890"
    }
}

// Delete records
{
    "action": "delete",
    "table_name": "accounts",
    "conditions": {
        "account_number": "1234567890"
    }
}
```

### Payment Processing
The repository includes payment processing components:
- `payment-master.zip`: Core payment processing functionality
- `payment-jpintegrated.zip`: Payment processing with additional integrations

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/chenavg/absolut.git
cd absolut
```

2. Set up the Generic Database Service:
```bash
cd genericdbservice
pip install -r requirements.txt
```

3. Deploy the Lambda function to AWS:
- Create a new Lambda function in AWS Console
- Upload the deployment package (see deployment instructions below)
- Configure VPC and security settings
- Set up database credentials in AWS Secrets Manager

## Security

This repository contains sensitive banking components. Please ensure:
- All credentials are managed through AWS Secrets Manager
- Database access is properly secured
- VPC and security groups are correctly configured
- Regular security audits are performed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

## Support

For support, please create an issue in the repository or contact the development team.
