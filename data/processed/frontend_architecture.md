# GTD React Frontend Architecture

This document outlines the architecture of the React + Vite frontend application. It follows a modular structure separating UI components from business logic and API communication.

```mermaid
graph TD
    %% Define Styles
    classDef comp fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    classDef service fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    classDef api fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff
    classDef ext fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff
    classDef vendor fill:#ec4899,stroke:#be185d,stroke-width:2px,color:#fff

    User((User Interaction)):::ext
    
    subgraph FrontendApp [React Application - Vite and TailwindCSS]
        
        %% Components
        subgraph Components [UI Components]
            Dashboard["📊 Dashboard.jsx<br/>(Charts, Maps, Interconnected Filters)"]:::comp
            Simulator["🔮 RiskSimulator.jsx<br/>(Prediction Form & Results)"]:::comp
        end
        
        %% Services
        subgraph Services [Service Layer]
            DashService["⚙️ dashboardService.js<br/>(Fetches BUC Cube Data)"]:::service
            PredService["⚙️ predictionService.js<br/>(Fetches ML Predictions)"]:::service
        end
        
        %% API / Axios
        subgraph APIClient [API Client]
            Axios["🌐 axiosInstance.js<br/>(Base URL, Interceptors)"]:::api
        end
        
        %% UI Libraries
        subgraph ThirdParty [Third-Party Libraries]
            Recharts["📈 Recharts (Graphs)"]:::vendor
            SimpleMaps["🗺️ react-simple-maps"]:::vendor
        end
        
    end

    Backend[("Java Spring Boot API<br/>(localhost:8080)")]:::ext

    %% Interactions
    User -->|"Interacts with UI"| Dashboard
    User -->|"Inputs features"| Simulator
    
    Dashboard -->|"Renders UI"| Recharts
    Dashboard -->|"Renders UI"| SimpleMaps
    
    Dashboard -->|"1. Request Data"| DashService
    Simulator -->|"1. Request Prediction"| PredService
    
    DashService -->|"2. Call API"| Axios
    PredService -->|"2. Call API"| Axios
    
    Axios <-->|"3. HTTP GET/POST"| Backend
```

## Architecture Layers Explained

1. **`components` (Presentation Layer)**:
   - Contains React functional components (`Dashboard.jsx`, `RiskSimulator.jsx`).
   - Manages local state (e.g., filter values, loading indicators, interconnected dropdowns).
   - Uses TailwindCSS for styling and external libraries (Recharts, react-simple-maps) to visualize data.
2. **`services` (Business/Logic Layer)**:
   - Acts as a bridge between UI components and the API.
   - Decouples API calling logic from the React components. For example, `dashboardService.js` handles all endpoints related to Data Cube statistics.
3. **`api` (HTTP Client Layer)**:
   - A centralized Axios instance configured with the Base URL (e.g., `VITE_API_BASE_URL`).
   - Essential for handling CORS, Authorization headers (if added later), and global error handling/interceptors.
4. **Third-Party Integrations**:
   - **TailwindCSS**: Provides utility-first styling for the entire application.
   - **Recharts**: Used for rendering dynamic, responsive SVGs like Trend lines and Bar charts.
   - **React-Simple-Maps**: Used for rendering the global choropleth map.
