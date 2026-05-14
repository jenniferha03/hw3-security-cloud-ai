# Homework 3.1 — Spring Security & JWT

Spring Boot application (Homework 1 movie API) extended with **Spring Security**, **JWT authentication**, **H2** persistence for users, and **`@PreAuthorize`** on protected endpoints. Login is exposed only as **`POST /auth/login`** (no Spring Security form login).

## Requirements implemented

| Item                                 | Implementation                                                                 |
| ------------------------------------ | ------------------------------------------------------------------------------ |
| Spring Security                      | `spring-boot-starter-security`, dual `SecurityFilterChain` (H2 console vs API) |
| Users in H2                          | JPA entity `AppUser`, table `users`, BCrypt passwords                          |
| `UserDetails` / `UserDetailsService` | `AppUserDetails`, `AppUserDetailsService`                                      |
| JWT filter                           | `JwtAuthenticationFilter` validates Bearer tokens and sets `SecurityContext`   |
| `@PreAuthorize`                      | `MovieController` — `hasRole('USER')`                                          |
| Custom login                         | `AuthController` — `POST /auth/login` (JSON body)                              |

## Prerequisites

- **Java 17+** (project uses Java 17 in `pom.xml`; CI or local may run newer)
- **Maven** (or use the included `./mvnw` wrapper)

## Run the application

```bash
cd homework-3.1
./mvnw spring-boot:run
```

Default URL: **http://localhost:8080** (change with `server.port` in `application.properties` if needed).

## Default user (seeded on startup)

| Field    | Value      |
| -------- | ---------- |
| Username | `user`     |
| Password | `password` |
| Role     | `USER`     |

## Endpoints summary

Base URL: `http://localhost:8080` (unless you change `server.port`).

| Method | Path                           | Auth                     | Description                                                                                             |
| ------ | ------------------------------ | ------------------------ | ------------------------------------------------------------------------------------------------------- |
| `POST` | `/auth/login`                  | None                     | JSON body: `username`, `password`. Returns `{ "token": "<JWT>" }` (or error body / **401** on failure). |
| `GET`  | `/api/v1/movies`               | Bearer JWT (`ROLE_USER`) | **No query params:** list all movies. **With `Title`:** search — optional `Year`, `page` (default `1`). |
| `GET`  | `/h2-console`, `/h2-console/*` | None (dev only)          | H2 web console UI.                                                                                      |

All `/api/v1/movies` routes are protected by `@PreAuthorize("hasRole('USER')")` in addition to a valid JWT for that user.

## API quick reference

### 1. Login (no JWT required)

```http
POST /auth/login
Content-Type: application/json

{"username":"user","password":"password"}
```

**Response:** JSON with a `token` field (JWT).

### 2. Protected movie endpoints

Send the JWT as a Bearer token:

```http
GET /api/v1/movies
Authorization: Bearer <token>
```

Example with `curl` (install [jq](https://jqlang.github.io/jq/) or paste the token manually):

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"password"}' | jq -r '.token')

curl -s http://localhost:8080/api/v1/movies \
  -H "Authorization: Bearer ${TOKEN}"
```

Search example:

```http
GET /api/v1/movies?Title=batman&page=1
Authorization: Bearer <token>
```

Requests **without** a valid JWT receive **401 Unauthorized**.

## H2 console (development)

Enabled when `spring.h2.console.enabled=true`.

1. Open **http://localhost:8080/h2-console** (trailing slash is fine).
2. **JDBC URL:** `jdbc:h2:mem:moviesdb`
3. **User name:** `sa`
4. **Password:** _(leave empty)_

Example query: `SELECT * FROM USERS;`

> **Note:** On Spring Boot **3.4.x**, the H2 console is auto-registered; security uses `PathRequest.toH2Console()` on a dedicated filter chain.

## Configuration (`application.properties`)

| Property              | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| `spring.datasource.*` | H2 in-memory datasource                                 |
| `spring.h2.console.*` | H2 console path and settings                            |
| `jwt.secret`          | HS256 signing key — **must be at least 32 UTF-8 bytes** |
| `jwt.expiration-ms`   | JWT lifetime (default 24 hours)                         |

For production, replace `jwt.secret` with a strong random value and **disable** the H2 console.

## Build & tests

```bash
./mvnw clean test
./mvnw clean package
```

Runnable JAR:

```bash
java -jar target/homework-3-1-1.0.0.jar
```

## Project layout

Base package: **`antra.homework31`**.

```
homework-3.1/
├── pom.xml
├── README.md
├── mvnw, mvnw.cmd, .mvn/
└── src/
    ├── main/java/antra/homework31/
    │   ├── Homework31Application.java
    │   ├── config/
    │   │   ├── DataInitializer.java          # seeds default user
    │   │   └── RestTemplateConfig.java
    │   ├── controller/
    │   │   ├── AuthController.java
    │   │   └── MovieController.java
    │   ├── dto/
    │   │   ├── LoginRequest.java
    │   │   └── LoginResponse.java
    │   ├── movie/
    │   │   ├── MovieData.java
    │   │   └── MovieResponse.java
    │   ├── service/
    │   │   ├── MovieService.java
    │   │   └── impl/MovieServiceImpl.java
    │   ├── security/
    │   │   ├── SecurityConfig.java
    │   │   ├── JwtService.java
    │   │   └── JwtAuthenticationFilter.java
    │   └── user/
    │       ├── AppUser.java
    │       ├── AppUserRepository.java
    │       ├── AppUserDetails.java
    │       └── AppUserDetailsService.java
    ├── main/resources/application.properties
    └── test/java/antra/homework31/
        └── Homework31ApplicationTests.java
```

### Common HTTP statuses (endpoints)

| Code              | Typical cause                                                         |
| ----------------- | --------------------------------------------------------------------- |
| **200**           | Success.                                                              |
| **400**           | Login: missing `username`/`password`, or malformed JSON body.         |
| **401**           | Login: wrong credentials. Movies: missing/invalid/expired JWT.        |
| **403**           | Authenticated but missing `ROLE_USER` (unusual with the seeded user). |
| **404** / **405** | Wrong path or HTTP method.                                            |
| **500**           | Server error (e.g. upstream movie API failure).                       |

## Tech stack

- Spring Boot **3.4.6** (release train; project artifact version **1.0.0**, not `SNAPSHOT`)
- Spring Security **6** / JWT (jjwt **0.12.x**)
- Spring Data JPA + **H2**
