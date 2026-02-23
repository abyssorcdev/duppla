# Duppla - API de Documentos Financieros

Sistema full-stack para la gestión de documentos financieros con procesamiento batch asíncrono, autenticación OAuth2 con Google y control de acceso basado en roles (RBAC).

> **Beta desplegada en Render**: El proyecto cuenta con una versión beta funcional desplegada en [Render](https://render.com) mediante blueprint (`render.yaml`), incluyendo backend, frontend, Celery worker, PostgreSQL y Redis. Disponible en [Duppla Finance](https://duppla-frontend.onrender.com/).

## Arquitectura

El backend sigue **Clean Architecture** con cuatro capas concéntricas donde las dependencias siempre apuntan hacia el centro (Domain):

```
Presentation (routes, middleware) → Application (services, DTOs) → Domain (entities, state machine)
                                                                    ↑
                              Infrastructure (repos, cache, notifications) ── implementa contratos de Domain
```

El frontend usa el patrón **Container/Presentational** con React Context para estado global y custom hooks para lógica reutilizable.

## Stack Tecnológico

### Backend
| Tecnología | Propósito |
|-----------|-----------|
| **FastAPI** + Uvicorn | Framework web y servidor ASGI |
| **SQLAlchemy 2.0** + Alembic | ORM y migraciones de base de datos |
| **Celery** | Procesamiento batch asíncrono |
| **Redis 7** | Cache, rate limiting (sliding window) y broker de mensajes |
| **PostgreSQL 15** | Persistencia (schema `finance`) |
| **python-jose** | Emisión y validación de JWT (HS256) |
| **Pydantic v2** | Validación de DTOs y configuración |
| **uv** | Gestión de dependencias (`requirements.txt`) |

### Frontend
| Tecnología | Propósito |
|-----------|-----------|
| **React 18** | UI declarativa con componentes funcionales |
| **React Router v6** | Routing SPA con rutas protegidas y anidadas |
| **Tailwind CSS 3.4** | Utility-first CSS con dark mode (clase) |
| **Axios 1.6** | Cliente HTTP con interceptors para JWT |
| **Vite 5** | Build tool y dev server con HMR |

### Testing
| Tecnología | Propósito |
|-----------|-----------|
| **pytest** + pytest-cov | Tests unitarios e integración backend (100% coverage) |
| **Vitest** + Testing Library | Tests unitarios frontend (~100% coverage) |
| **Faker** | Generación dinámica de datos de prueba |

## Estructura del Proyecto

```
duppla/
├── backend/
│   ├── alembic/versions/
│   ├── app/
│   │   ├── api/
│   │   │   ├── dependencies/
│   │   │   ├── middleware/
│   │   │   └── routes/
│   │   ├── application/
│   │   │   ├── dtos/
│   │   │   └── services/
│   │   ├── core/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── exceptions.py
│   │   │   └── state_machine.py
│   │   └── infrastructure/
│   │       ├── cache/
│   │       ├── database/
│   │       ├── notifications/
│   │       └── repositories/
│   ├── tests/
│   │   ├── common/
│   │   ├── unit/
│   │   └── integration/
│   ├── setup.cfg
│   └── worker.py
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   ├── batch/
│   │   │   ├── common/
│   │   │   ├── documents/
│   │   │   └── layout/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── test/
│   │   └── utils/
│   └── vite.config.js
├── .github/workflows/ci.yml
├── docker-compose.yml
├── render.yaml
└── README.md
```

## Funcionalidades Principales

### Gestión de Documentos
- CRUD completo con validación de negocio (monto > 0, metadata requerida)
- Máquina de estados: `DRAFT → PENDING → APPROVED` / `REJECTED → DRAFT`
- Búsqueda con filtros (tipo, estado, rango de monto) y paginación
- Auditoría automática de cada operación

### Procesamiento Batch Asíncrono
- Envío de lotes de documentos a procesamiento vía Celery
- Auto-evaluación: monto, metadata, reglas de negocio
- Polling de estado del job desde el frontend
- Notificación webhook al completar

### Autenticación y Autorización
- Login con Google OAuth2 (flujo authorization code)
- JWT con auto-expiración y logout automático
- RBAC con 3 roles: `admin`, `loader`, `approver`
- Flujo de aprobación: usuarios nuevos quedan en `PENDING` hasta que un admin les asigna rol

### Panel de Administración
- Gestión de usuarios (aprobar, deshabilitar, cambiar rol)
- Logs de auditoría con filtros y paginación
- Dashboard con estadísticas agregadas

## Requisitos Previos

- Docker (>= 20.10) y Docker Compose (>= 2.0)
- O bien: Python 3.11+, Node.js 18+, PostgreSQL 15, Redis 7

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/abyssorcdev/duppla.git
cd duppla
```

### 2. Configurar Variables de Entorno

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Variables requeridas en el backend:
- `DATABASE_URL` / credenciales PostgreSQL
- `REDIS_URL` / `REDIS_HOST` / `REDIS_PORT`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXPIRE_MINUTES`
- `WEBHOOK_URL` (opcional, para notificaciones)

## Uso con Docker Compose

### Modo Desarrollo

```bash
docker-compose up -d
```

Esto inicia 7 servicios:
- **Backend** en `http://localhost:8000` (API + Swagger en `/api/v1/docs`)
- **Frontend** en `http://localhost:5173`
- **Celery Worker** para procesamiento batch
- **Flower** en `http://localhost:5555` (monitoreo de tareas)
- **PostgreSQL** en `localhost:5432`
- **Redis** en `localhost:6379`

### Comandos Comunes

```bash
docker-compose logs -f backend        # Logs del backend
docker-compose exec backend alembic upgrade head  # Ejecutar migraciones
docker-compose down                   # Detener servicios
docker-compose down -v                # Detener y borrar volúmenes
```

## Desarrollo Local (sin Docker)

### Backend

```bash
cd backend
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend (pytest)

```bash
cd backend
pytest tests --cov=app --cov-config=setup.cfg --cov-report=term-missing --verbose
```

Los tests de integración requieren una base de datos PostgreSQL real (configurada automáticamente en CI vía GitHub Actions services).

### Frontend (Vitest)

```bash
cd frontend
npm test -- --coverage
```

## CI/CD

El proyecto usa **GitHub Actions** con el siguiente pipeline:

1. **Lint Backend** - Ruff (linting + formatting)
2. **Lint Frontend** - ESLint
3. **Test Backend** - pytest con PostgreSQL y Redis como servicios, reporte de coverage
4. **Test Frontend** - Vitest con reporte de coverage
5. **Deploy** - Despliegue automático a Render (en rama `main`)

## Despliegue en Render

El archivo `render.yaml` define el blueprint con los siguientes servicios:

| Servicio | Tipo | Plan |
|----------|------|------|
| `duppla-backend` | Web Service (Docker) | Starter |
| `duppla-worker` | Worker (Celery) | Starter |
| `duppla-frontend` | Static Site | Free |
| `duppla-db` | PostgreSQL 15 | Free |
| `duppla-redis` | Redis | Free |

Los secretos se gestionan mediante **Render Environment Groups** (`duppla-secrets`).

## Endpoints de la API

| Método | Endpoint | Rol Requerido | Descripción |
|--------|----------|---------------|-------------|
| `GET` | `/auth/google` | Público | Iniciar flujo OAuth2 |
| `GET` | `/api/v1/documents` | Cualquier rol activo | Listar/buscar documentos |
| `GET` | `/api/v1/documents/{id}` | Cualquier rol activo | Detalle de documento |
| `POST` | `/api/v1/documents` | Admin, Loader | Crear documento |
| `PUT` | `/api/v1/documents/{id}` | Admin, Loader | Actualizar documento (solo DRAFT) |
| `PATCH` | `/api/v1/documents/{id}/status` | Admin, Approver | Cambiar estado |
| `POST` | `/api/v1/documents/batch/process` | Admin, Loader | Procesar lote |
| `GET` | `/api/v1/jobs` | Cualquier rol activo | Listar jobs |
| `GET` | `/api/v1/jobs/{job_id}` | Cualquier rol activo | Estado del job |
| `GET` | `/api/v1/admin/users` | Admin | Listar usuarios |
| `PATCH` | `/api/v1/admin/users/{id}/approve` | Admin | Aprobar usuario |
| `PATCH` | `/api/v1/admin/users/{id}/disable` | Admin | Deshabilitar usuario |
| `GET` | `/api/v1/admin/logs` | Admin | Logs de auditoría |
| `GET` | `/health` | Público | Estado de salud |
| `GET` | `/api/v1/docs` | Público | Swagger UI |

## Patrones de Diseño

| Patrón | Aplicación |
|--------|-----------|
| **Clean Architecture** | Estructura general del backend (4 capas) |
| **Repository** | Abstracción de acceso a datos con conversión ORM ↔ entidad |
| **Use Case** | Un servicio = una responsabilidad, método `execute()` |
| **State Machine** | Tabla declarativa de transiciones válidas de documentos |
| **Strategy + Factory** | Sistema de notificaciones con canales intercambiables |
| **Dependency Injection** | FastAPI `Depends` para servicios y middleware |
| **Container/Presentational** | Pages (lógica) vs Components (UI) en frontend |
| **Guard Pattern** | `ProtectedRoute` con verificación de auth + rol |
| **Interceptor** | Axios interceptors para JWT y manejo global de 401 |
