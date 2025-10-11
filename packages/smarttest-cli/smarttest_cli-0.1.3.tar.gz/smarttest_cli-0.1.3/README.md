# Smart-Test

Smart-Test is an automated API testing platform that allows you to define, execute, and validate test scenarios efficiently. Specifically designed to validate API responses with custom criteria, this tool is ideal for development teams that need to ensure the quality and consistency of their services.

## Features

- **Endpoint Definition**: Define API endpoints with their parameters, methods, and expected schemas.
- **Test Scenarios**: Create test scenarios with specific input data and custom validations.
- **Advanced Validations**: Validate API responses using:
  - HTTP status codes
  - JSON schema validation
  - Specific field validations using operators (==, !=, >, <, exists, etc.)
  - JMESPath expressions for advanced queries in JSON responses
- **Authentication**: Support for scenarios that require authentication, with token and header management.
- **User Authentication**: Secure user authentication using Clerk, with system access control for customers.
- **Customer Management**: Register and manage customers with Clerk integration, storing additional user information in the database.
- **Flexible Execution**: Run individual scenarios or all scenarios for an endpoint.
- **Detailed Reports**: Get detailed success and failure reports with specific information about validations.

## Requirements

- Python 3.8+
- FastAPI
- SQLite
- Uvicorn
- Pydantic
- SQLAlchemy
- JMESPath
- Requests
- Clerk SDK for Python

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/smart-test.git
   cd smart-test
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for Clerk:
   ```bash
   export CLERK_API_KEY=your_clerk_api_key
   export CLERK_JWT_KEY=your_clerk_jwt_verification_key
   ```

5. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

## Project Structure

```
smart-test/
├── database/
│   ├── model.py         # SQLAlchemy models
│   └── schemas.py       # Pydantic schemas
├── middleware/
│   └── auth_middleware.py    # Authentication middleware
├── routes/
│   ├── endpoint_routes.py    # Routes for managing endpoints
│   ├── scenario_routes.py    # Routes for managing scenarios
│   ├── auth_routes.py        # Routes for auth configuration
│   └── customer_routes.py    # Routes for customer management
├── service/
│   ├── EndpointService.py    # Services for endpoints
│   ├── ScenarioService.py    # Services for scenarios
│   ├── AuthConfigService.py  # Services for auth configuration
│   ├── ClerkAuthService.py   # Services for Clerk authentication
│   └── ...
├── scenarioExecution.py      # Scenario execution logic
├── HttpRequestService.py     # Service for making HTTP requests
├── main.py                   # Application entry point
├── test.db                   # SQLite database
└── README.md                 # This file
```

## Usage

### Define an Endpoint

```bash
curl -X POST "http://localhost:8000/endpoint" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "/api/v1/resource",
    "method": "GET",
    "raw_definition": {
      "parameters": [...],
      "responses": [...]
    }
  }'
```

### Create a Scenario

```bash
curl -X POST "http://localhost:8000/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint_id": 1,
    "name": "Test scenario",
    "expected_http_status": 200,
    "body": {...},
    "headers": {...},
    "requires_auth": true
  }'
```

### Add Field Validations

```bash
curl -X POST "http://localhost:8000/scenario/1/field-value-validations" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint_id": 1,
    "user_input": "devices[0].name == \"Eugenio Dimmer Dev 11\""
  }'
```

### Execute a Scenario

```bash
curl -X POST "http://localhost:8000/endpoint/1/execute-scenario/1"
```

### Execute All Scenarios for an Endpoint

```bash
curl -X POST "http://localhost:8000/endpoint/1/execute-scenarios"
```

## Custom Validations

Smart-Test supports custom validations using JMESPath expressions and various operators:

- `==`: Equality
- `!=`: Inequality
- `>`, `>=`, `<`, `<=`: Numeric comparisons
- `exists`: Verifies that a field exists and is not null or an empty list

Examples:

- `devices[0].name == "Eugenio Dimmer Dev 11"` - Verifies that the name of the first device is exactly "Eugenio Dimmer Dev 11"
- `devices[?traits[?trait == 'LIGHT_SCHEDULES']]` - Verifies that there is at least one device with a trait called "LIGHT_SCHEDULES"
- `count(devices) > 1` - Verifies that there is more than one device in the response

## Authentication

### API Authentication

For scenarios that require authentication, set `requires_auth: true` when creating the scenario. The system will automatically:

1. Look for the authentication configuration for the system associated with the endpoint
2. Obtain an authentication token
3. Include the necessary authentication headers in the request

If authentication fails, the system will continue with the execution but will log the error.

### User Authentication with Clerk

The application uses Clerk for secure user authentication. To use this feature:

1. Set up a Clerk account and obtain your API key and JWT verification key
2. Set the environment variables `CLERK_API_KEY` and `CLERK_JWT_KEY`
3. Include the JWT token in the Authorization header of your requests as a Bearer token

#### Customer Registration

Users can register through the application which creates accounts in both Clerk and the local database:

```bash
curl -X POST "http://localhost:8000/customers/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "name": "John Doe",
    "password": "securepassword123"
  }'
```

To get the current customer's information:

```bash
curl -X GET "http://localhost:8000/customers/me" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"
```

#### Managing Customer Access

Customers can be granted access to specific systems:

```bash
curl -X POST "http://localhost:8000/customers/system-access" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN" \
  -d '{
    "customer_id": "clerk_user_id",
    "system_id": 1
  }'
```

To list systems a customer has access to:

```bash
curl -X GET "http://localhost:8000/customers/system-access" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"
```

To revoke access:

```bash
curl -X DELETE "http://localhost:8000/customers/system-access/1" \
  -H "Authorization: Bearer YOUR_CLERK_JWT_TOKEN"
```

## API Error Handling

The API uses consistent error handling with appropriate HTTP status codes:

- **404 Not Found**: When a requested resource doesn't exist
- **400 Bad Request**: For validation errors or invalid input
- **403 Forbidden**: When a user doesn't have access to a resource
- **401 Unauthorized**: When authentication fails

All errors follow a consistent format:

```json
{
  "detail": "Error message or object with additional information"
}
```

## Debugging

The system includes detailed logs to facilitate debugging:

- Information about loaded endpoints and scenarios
- Details of executed validations and their results
- Information about HTTP requests made and responses received
- Authentication and authorization checks

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
