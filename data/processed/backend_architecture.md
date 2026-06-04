# GTD System & Backend Architecture

This document contains two diagrams:
1. **System Integration Diagram**: Shows how the Frontend, Backend, ML Service, and Database interact.
2. **Backend N-Tier Architecture**: Dives deep into the Java Spring Boot source code structure.

---

## 1. System Integration Diagram

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    classDef spring fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef python fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff
    classDef db fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff

    %% Components
    Client["💻 React Frontend Dashboard"]:::frontend
    
    subgraph Backend [Java Spring Boot Core API]
        Controller["🛣️ Controllers (REST API)"]:::spring
        Service["⚙️ Services (Business Logic)"]:::spring
        Repository["🗄️ Repositories (Spring Data JPA)"]:::spring
        RestTemplate["🌐 REST Client (HTTP)"]:::spring
    end
    
    subgraph ML_Service [Python ML Prediction Service]
        FastAPI["🚀 FastAPI Server (Port 8000)"]:::python
        Model["🧠 Trained ML Model (Scikit-Learn/XGBoost)"]:::python
    end
    
    subgraph Database [PostgreSQL Data Warehouse]
        PG[("🐘 PostgreSQL (gtd_db)")]:::db
        Cube["🧊 iceberg_cube (BUC Data Cube)"]:::db
        StarSchema["⭐ Star Schema (Fact & Dims)"]:::db
    end

    %% Flow/Connections
    Client -->|"1. GET /api/v1/cube-stats<br/>(Fetch Dashboard Data)"| Controller
    Client -->|"2. POST /api/v1/predictions<br/>(Predict Risk)"| Controller
    
    Controller --> Service
    
    %% DB Flow
    Service -->|"Queries Data"| Repository
    Repository -->|"JDBC / JPA"| PG
    PG --- Cube
    PG --- StarSchema
    
    %% ML Flow
    Service -.->|"Proxy Prediction Request"| RestTemplate
    RestTemplate -->|"POST /predict"| FastAPI
    FastAPI -->|"Load & Run Inference"| Model
    Model -->|"Return Risk Probability"| FastAPI
    FastAPI -->|"Return JSON"| RestTemplate
```

---

## 2. Java Spring Boot N-Tier Architecture (Core API)

```mermaid
graph TD
    %% Define Styles
    classDef client fill:#1e293b,stroke:#0f172a,stroke-width:2px,color:#fff
    classDef config fill:#ec4899,stroke:#be185d,stroke-width:2px,color:#fff
    classDef filter fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff
    classDef controller fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    classDef service fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef repo fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff
    classDef model fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff
    classDef external fill:#475569,stroke:#334155,stroke-width:2px,color:#fff

    Client((Client HTTP Requests)):::client

    subgraph SpringBootApp [Spring Boot Application Context]
        
        %% Config & Filter Layer
        Config["⚙️ config<br/>(CorsConfig, AppConfig)"]:::config
        Filter["🛡️ filter<br/>(LoggingFilter)"]:::filter
        
        %% Presentation Layer
        Controller["🛣️ controller<br/>(CubeStatController, PredictionController)"]:::controller
        
        %% Business Layer
        Service["⚙️ service<br/>(CubeStatService, PredictionService)"]:::service
        
        %% Data Access Layer
        Repository["🗄️ repository<br/>(CubeStatRepository)"]:::repo
        
        %% Models
        subgraph DataModels [Data Models]
            DTO["📦 dto<br/>(ApiResponse, Prediction DTOs)"]:::model
            Entity["📜 entity<br/>(CubeStat)"]:::model
        end

    end

    %% External Systems
    DB[(PostgreSQL Database)]:::external
    ML[(Python FastAPI)]:::external

    %% Relationships and Flow
    Config -.->|"Configures"| Controller
    Config -.->|"Configures"| Service
    
    Client -->|"1. Request"| Filter
    Filter -->|"2. Forward"| Controller
    
    Controller -->|"3. DTO Exchange"| DTO
    Controller -->|"4. Invoke Logic"| Service
    
    Service -->|"5. Convert to DTO"| DTO
    Service -->|"6. Query DB"| Repository
    Service -.->|"HTTP Proxy"| ML
    
    Repository -->|"7. Map ResultSet"| Entity
    Repository <-->|"JDBC / JPA"| DB
```

## Architecture Layers Explained

1. **`config` (Configuration Layer)**: Contains Spring configuration classes such as CORS setup, WebMvc config, and Bean definitions (like `RestTemplate` for calling the ML service).
2. **`filter` (Security & Middleware Layer)**: Intercepts incoming HTTP requests before they reach the controllers. Used for request logging (`LoggingFilter`), authentication, and input sanitization.
3. **`controller` (Presentation Layer)**: Exposes RESTful API endpoints. Responsible for validating incoming HTTP requests, mapping them to DTOs, and routing them to the appropriate Service.
4. **`service` (Business Logic Layer)**: Contains the core business rules. It orchestrates data flow, applies transformations, interacts with external ML APIs, and handles transactions.
5. **`repository` (Data Access Layer)**: Interfaces with the PostgreSQL database using Spring Data JPA. Abstracts away raw SQL queries into method names and handles object-relational mapping.
6. **`dto` & `entity` (Data Models)**: 
   - **Entity**: Java classes directly mapped to database tables (e.g., `iceberg_cube`).
   - **DTO (Data Transfer Object)**: Safe objects used to transfer data over the network to the client (e.g., `ApiResponse`), ensuring database structures aren't directly exposed.
