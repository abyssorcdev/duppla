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

## Swagger UI

La documentación interactiva de la API está disponible en:

- **Local**: http://localhost:8000/api/v1/docs
- **Beta (Render)**: https://duppla-backend.onrender.com/api/v1/docs

Para probar endpoints autenticados desde Swagger, haz clic en **"Authorize"** (candado verde) y pega el token generado con el script `generate_token.py`.

## Ejemplos de API (cURL / Postman)

> Reemplaza `{{BASE_URL}}` por `http://localhost:8000` (local) o `https://duppla-backend.onrender.com` (beta).
> Reemplaza `{{TOKEN}}` por el JWT obtenido tras autenticarse con Google o generado con el script local.

### Generar token para testing local (sin Google OAuth)

```bash
# Listar usuarios disponibles
docker compose exec backend python scripts/generate_token.py --list

# Generar token con el primer admin activo (default)
docker compose exec backend python scripts/generate_token.py

# Generar token para un usuario específico
docker compose exec backend python scripts/generate_token.py --email user@example.com

# Generar token con duración personalizada (8 horas)
docker compose exec backend python scripts/generate_token.py --hours 8

# Guardar el token en una variable
export TOKEN="$(docker compose exec backend python scripts/generate_token.py 2>/dev/null | grep '^eyJ')"
```

### Health Check

```bash
curl {{BASE_URL}}/health
```

### Autenticación

```bash
# Iniciar flujo OAuth2 con Google (abrir en navegador)
curl -L {{BASE_URL}}/auth/google
```

### Documentos

```bash
# Crear documento
curl -X POST {{BASE_URL}}/api/v1/documents \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "invoice",
    "amount": 50000.00,
    "metadata": {
      "client": "Acme Corp",
      "email": "billing@acme.com",
      "reference": "INV-2026-001"
    },
    "created_by": "user@example.com"
  }'

# Listar documentos con filtros y paginación
curl -X GET "{{BASE_URL}}/api/v1/documents?type=invoice&status=draft&amount_min=1000&page=1&page_size=10" \
  -H "Authorization: Bearer {{TOKEN}}"

# Obtener documento por ID
curl -X GET {{BASE_URL}}/api/v1/documents/1 \
  -H "Authorization: Bearer {{TOKEN}}"

# Actualizar documento (solo en estado DRAFT)
curl -X PUT {{BASE_URL}}/api/v1/documents/1 \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "receipt",
    "amount": 75000.50,
    "metadata": {
      "client": "Acme Corp",
      "email": "billing@acme.com"
    },
    "user_id": "user@example.com"
  }'

# Cambiar estado de documento
curl -X PATCH {{BASE_URL}}/api/v1/documents/1/status \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "pending",
    "comment": "Listo para revisión"
  }'
```

### Procesamiento Batch

```bash
# Procesar lote de documentos
curl -X POST {{BASE_URL}}/api/v1/documents/batch/process \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "document_ids": [1, 2, 3, 4, 5]
  }'
```

### Jobs

```bash
# Listar jobs con filtros
curl -X GET "{{BASE_URL}}/api/v1/jobs?status=completed&page=1&page_size=10" \
  -H "Authorization: Bearer {{TOKEN}}"

# Obtener estado de un job
curl -X GET {{BASE_URL}}/api/v1/jobs/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer {{TOKEN}}"
```

### Administración (solo admin)

```bash
# Listar usuarios
curl -X GET "{{BASE_URL}}/api/v1/admin/users?status=pending" \
  -H "Authorization: Bearer {{TOKEN}}"

# Aprobar usuario y asignar rol
curl -X PATCH {{BASE_URL}}/api/v1/admin/users/550e8400-e29b-41d4-a716-446655440000/approve \
  -H "Authorization: Bearer {{TOKEN}}" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "loader"
  }'

# Deshabilitar usuario
curl -X PATCH {{BASE_URL}}/api/v1/admin/users/550e8400-e29b-41d4-a716-446655440000/disable \
  -H "Authorization: Bearer {{TOKEN}}"

# Consultar logs de auditoría
curl -X GET "{{BASE_URL}}/api/v1/admin/logs?table_name=documents&action=state_change&limit=20" \
  -H "Authorization: Bearer {{TOKEN}}"
```

### Probar el Flujo Completo (end-to-end)

```bash
# 1. Generar token de admin
export TOKEN="$(docker compose exec backend python scripts/generate_token.py 2>/dev/null | grep '^eyJ')"

# 2. Crear un documento en estado DRAFT
curl -s -X POST {{BASE_URL}}/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "invoice",
    "amount": 50000.00,
    "metadata": {"client": "Acme Corp", "email": "billing@acme.com"},
    "created_by": "admin@duppla.co"
  }'
# → Respuesta: documento con id=1, status="draft"

# 3. Enviar a procesamiento batch (cambia DRAFT → PENDING si pasa las reglas)
curl -s -X POST {{BASE_URL}}/api/v1/documents/batch/process \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"document_ids": [1]}'
# → Respuesta: job_id="...", status="pending" (HTTP 202)

# 4. Hacer polling del job hasta que complete (repetir cada 3-5 segundos)
curl -s {{BASE_URL}}/api/v1/jobs/{{JOB_ID}} \
  -H "Authorization: Bearer $TOKEN"
# → Cuando status="completed", el result muestra el detalle por documento

# 5. Verificar que el documento cambió de estado
curl -s {{BASE_URL}}/api/v1/documents/1 \
  -H "Authorization: Bearer $TOKEN"
# → status="pending" (monto < 10M y tiene client + email en metadata)

# 6. Aprobar manualmente (PENDING → APPROVED)
curl -s -X PATCH {{BASE_URL}}/api/v1/documents/1/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"new_status": "approved"}'
# → status="approved" (estado final, inmutable)

# 7. El webhook se disparó automáticamente al completar el job (paso 4)
#    Verificar en https://webhook.site el payload recibido
```

**Reglas de auto-procesamiento del batch:**
- Monto > 10,000,000 → `REJECTED` (razón: `amount_exceeds_limit`)
- Falta `client` o `email` en metadata → `REJECTED` (razón: `missing_required_fields`)
- Pasa ambas validaciones → `PENDING`
- Documentos en `REJECTED` se resetean a `DRAFT` para corrección
- Documentos en `PENDING` o `APPROVED` se omiten

### Tipos de Documento Válidos

`invoice`, `receipt`, `voucher`, `credit_note`, `debit_note`

### Estados de Documento

`draft`, `pending`, `approved`, `rejected`

### Roles de Usuario

`admin`, `loader`, `approver`

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

## Decisiones de Arquitectura

### ¿Por qué FastAPI?

FastAPI ofrece una curva de aprendizaje favorable para prototipar rápido, pero además aporta ventajas técnicas que el proyecto aprovecha directamente: generación automática de documentación OpenAPI/Swagger (disponible en `/api/v1/docs`), validación nativa con Pydantic v2 en todos los DTOs, y soporte async nativo que facilita la integración con Celery.

### ¿Por qué PostgreSQL en vez de SQLite?

Además de experiencia previa con PostgreSQL, el diseño del proyecto requiere funcionalidades que SQLite no soporta bien: schemas (`finance`) para aislar las tablas del dominio, triggers para auditoría automática a nivel de base de datos, check constraints (`amount > 0`), y soporte JSON nativo para el campo `metadata`. Es también la base de datos que se usaría en producción real.

### ¿Por qué Celery en vez de BackgroundTasks?

`BackgroundTasks` de FastAPI es más simple, pero las tareas se pierden si el servidor se reinicia. Celery con Redis como broker ofrece persistencia de tareas, escalabilidad y monitoreo visual con Flower — funcionalidades críticas para procesamiento batch en un entorno de producción.

### ¿Por qué Clean Architecture (4 capas)?

Separar Domain, Application, Infrastructure y Presentation hace que cada capa tenga su propia responsabilidad y pueda modificarse sin afectar significativamente a las demás. En la práctica, esto se traduce en **testabilidad**: los tests unitarios del dominio (state machine, validaciones de monto) se ejecutan sin necesitar base de datos ni Redis, acelerando el ciclo de desarrollo.

### ¿Por qué Redis?

Redis cumple tres roles en el proyecto: broker de mensajes para Celery, cache de API keys validadas (TTL de 5 minutos), y almacén de contadores para rate limiting con algoritmo de ventana deslizante. Usar un solo servicio para estos tres propósitos simplifica la infraestructura.

## Mejoras de Performance y Seguridad

| Categoría | Implementación | Detalle |
|-----------|---------------|---------|
| **Rate Limiting** | Sliding window en Redis | 100 req/min por usuario, headers `X-RateLimit-*`, fallback graceful si Redis no está disponible |
| **Autenticación JWT** | Google OAuth2 + JWT | Tokens HS256 con expiración configurable (7 días default), validación de estado de cuenta en cada request |
| **RBAC** | 3 roles + estados de cuenta | `admin`, `loader`, `approver` con verificación de estado (`PENDING`/`ACTIVE`/`DISABLED`) en cada request |
| **Validación de entrada** | Pydantic v2 + DB constraints | Monto máx 999,999,999.99, metadata máx 20 keys, check constraint `amount > 0` en PostgreSQL |
| **Auditoría** | Triggers + application-level | Logs automáticos de cambios en BD y registro explícito de transiciones de estado con `user_id` |
| **Retry con backoff** | Webhooks HTTP | 3 reintentos con backoff exponencial (2s, 4s, 8s) y timeout de 10s por request |
| **Connection pooling** | SQLAlchemy `pool_pre_ping` | Validación de conexiones antes de uso para evitar errores por conexiones stale |
| **Paginación con límites** | Offset-based | Default 10, máximo 100 resultados por página para prevenir queries masivas |
| **CORS** | Whitelist de orígenes | Solo orígenes permitidos explícitamente (configurable vía `ALLOWED_ORIGINS`) |

## Trade-offs y Limitaciones

### ¿Qué faltó por tiempo?

- **Endpoint DELETE** para documentos (el CRUD no incluye eliminación)
- **Refresh tokens**: actualmente solo access tokens con expiración de 7 días; en producción se usaría rotación de refresh tokens con TTL corto del access token
- **Login con credenciales propias**: actualmente solo se puede iniciar sesión con Google OAuth2; faltó implementar registro e inicio de sesión con email y contraseña como alternativa

### ¿Qué harías diferente en producción?

- **Gestión de secretos** con AWS Secrets Manager o HashiCorp Vault en vez de variables de entorno
- **Refresh token rotation** con access tokens de vida corta (15-30 min)
- **Dead-letter queue** para tareas de Celery que fallan repetidamente
- **Notificaciones a admins** cuando un usuario nuevo se registra y queda pendiente de aprobación (email, Slack, etc.)
- **Notificaciones al usuario** cuando un job de procesamiento batch finaliza (actualmente solo se dispara el webhook, pero el usuario no recibe aviso directo)
- **Observabilidad** con logging estructurado (JSON), métricas y rastreo distribuido para debuggear problemas entre servicios
- **Soft delete** para documentos y usuarios, preservando trazabilidad de datos financieros
- **Almacenamiento de archivos** en S3 o similar para los documentos reales (PDFs de facturas, comprobantes), no solo metadata
- **Rate limiting diferenciado** por endpoint (ej: batch processing más restrictivo que consultas de lectura)
- **Request ID único** que se propague por todo el flujo (API → Celery → webhook) para trazabilidad completa
