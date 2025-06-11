# Payment Integration Service

This project is a Spring Boot application for handling online and global payment transactions, integrating with JPMorgan Chase (JPMC) APIs. It provides a modular structure for payment requests, transaction status, and authentication.

## Table of Contents
- [Key Components](#key-components)
- [Configuration](#configuration)
- [Build & Run](#build--run)
- [API Workflow](#api-workflow)
- [Extending the Project](#extending-the-project)
- [Testing](#testing)

---


## Key Components

- **PaymentApplication.java**: Main Spring Boot entry point.
- **dto/**: Data Transfer Objects for requests and responses.
- **jpmc/client/**: Handles communication with JPMC APIs, including authentication and payment operations.
- **service/**: Business logic for validation and payment processing.
- **resources/**: Configuration files and OpenAPI specifications.

---

## Configuration

- `application.properties`: Set API base URLs, credentials, and other environment-specific properties.
- `pom.xml`: Maven configuration, dependencies (Spring Boot, Spring Web, etc.).

---

## Build & Run

1. **Build the project:**
   ```
   ./mvnw clean install
   ```

2. **Run the application:**
   ```
   ./mvnw spring-boot:run
   ```

3. **Configuration:**
   - Set environment variables or update `src/main/resources/application.properties` for:
     - API base URLs
     - Merchant credentials
     - Other integration settings

---

## API Workflow

1. **Authentication:**
   - `AuthService` fetches and manages access tokens for API calls.

2. **Payment Requests:**
   - `OnlinePaymentService` and `GlobalPaymentService` handle business logic for online and global payments.
   - DTOs like `OnlinePaymentRequest` and `PaymentRequest` encapsulate request data.

3. **External API Calls:**
   - `OnlinePaymentClient` and `GlobalPaymentClient` use `RestTemplate` to interact with JPMC endpoints.
   - Headers (including bearer tokens and merchant IDs) are set for each request.

4. **Validation:**
   - `ValidationService` and `ValidationClient` ensure requests are well-formed and meet business rules.

5. **Response Handling:**
   - Responses are mapped to DTOs and returned to the caller.

---

## Extending the Project

- Add new payment types by creating new DTOs and service/client classes.
- Update OpenAPI YAML files in `src/main/resources` for API documentation.
- Add new configuration properties as needed in `application.properties`.

---

## Testing

- Unit and integration tests can be added under `src/test/java/com/rohan/payment/`.
- Use Spring Boot’s testing support for mocking and context loading.

---

## OpenAPI Specifications

- `Online Payments API 2.7.0.yaml` and `Global Payments 1.1.29.yaml` provide API documentation and contract details.

---

## License

This project is for demonstration and integration purposes.

