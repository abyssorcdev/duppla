# Duppla - Full Stack Application

Aplicación full-stack con FastAPI, React, PostgreSQL y Redis, todo orquestado con Docker Compose.

## 🚀 Tecnologías

### Backend
- **FastAPI** - Framework web moderno para Python
- **SQLAlchemy** - ORM para PostgreSQL
- **Redis** - Caché en memoria
- **Uvicorn** - Servidor ASGI

### Frontend
- **React 18** - Biblioteca de UI
- **Vite** - Build tool
- **Tailwind CSS** - Framework CSS
- **Axios** - Cliente HTTP

### Base de Datos
- **PostgreSQL 15** - Base de datos relacional
- **Redis 7** - Almacenamiento en caché

## 📋 Requisitos Previos

- Docker (versión 20.10 o superior)
- Docker Compose (versión 2.0 o superior)

## 🛠️ Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <tu-repositorio>
cd duppla
```

### 2. Configurar Variables de Entorno

#### Backend
```bash
cp backend/.env.example backend/.env
```

#### Frontend
```bash
cp frontend/.env.example frontend/.env
```

## 🐳 Uso con Docker Compose

### Modo Desarrollo

Para iniciar todos los servicios en modo desarrollo:

```bash
docker-compose up -d
```

Esto iniciará:
- **Backend** en `http://localhost:8000`
- **Frontend** en `http://localhost:5173`
- **PostgreSQL** en `localhost:5432`
- **Redis** en `localhost:6379`

### Ver Logs

```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Detener los Servicios

```bash
docker-compose down
```

### Limpiar Volúmenes (Borrar Base de Datos)

```bash
docker-compose down -v
```

### Modo Producción

Para producción, usa el archivo `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Este modo incluye:
- Frontend servido por Nginx
- Backend con múltiples workers
- Red aislada para los servicios

## 📡 Endpoints de la API

### Endpoints Principales

- `GET /` - Mensaje de bienvenida
- `GET /health` - Estado de salud de la API
- `GET /api/v1/test-db` - Verificar conexión a PostgreSQL
- `GET /api/v1/test-redis` - Verificar conexión a Redis
- `GET /docs` - Documentación interactiva de la API (Swagger UI)
- `GET /redoc` - Documentación alternativa (ReDoc)

## 🏗️ Estructura del Proyecto

```
duppla/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py          # Endpoints de la API
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py          # Configuración
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Conexión PostgreSQL
│   │   │   └── redis_client.py    # Cliente Redis
│   │   ├── __init__.py
│   │   └── main.py                # Punto de entrada
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx                # Componente principal
│   │   ├── index.css              # Estilos globales
│   │   └── main.jsx               # Punto de entrada
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── index.html
│   ├── nginx.conf
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── docker-compose.yml             # Desarrollo
├── docker-compose.prod.yml        # Producción
└── README.md
```

## 🔧 Desarrollo

### Ejecutar Backend Localmente (sin Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Ejecutar Frontend Localmente (sin Docker)

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Verificar la Instalación

1. Abre tu navegador en `http://localhost:5173`
2. Deberías ver una página con el estado de los servicios
3. Todos los servicios deben mostrar "✓ Conectado"

## 📝 Comandos Útiles

### Docker Compose

```bash
# Construir imágenes sin cache
docker-compose build --no-cache

# Reiniciar un servicio específico
docker-compose restart backend

# Ver contenedores en ejecución
docker-compose ps

# Ejecutar comando en un contenedor
docker-compose exec backend bash
docker-compose exec frontend sh

# Ver uso de recursos
docker stats
```

### Backend

```bash
# Acceder al shell de Python en el contenedor
docker-compose exec backend python

# Ejecutar migraciones (cuando estén configuradas)
docker-compose exec backend alembic upgrade head
```

### Base de Datos

```bash
# Acceder a PostgreSQL
docker-compose exec db psql -U postgres -d duppla

# Backup de la base de datos
docker-compose exec db pg_dump -U postgres duppla > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres duppla < backup.sql
```

### Redis

```bash
# Acceder a Redis CLI
docker-compose exec redis redis-cli

# Ver todas las claves
docker-compose exec redis redis-cli KEYS "*"

# Limpiar caché
docker-compose exec redis redis-cli FLUSHALL
```

## 🐛 Solución de Problemas

### Error: Puerto ya en uso

```bash
# Verificar qué está usando el puerto
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Matar el proceso
kill -9 <PID>
```

### Error: Contenedores no inician

```bash
# Ver logs detallados
docker-compose logs

# Limpiar todo y reiniciar
docker-compose down -v
docker-compose up --build
```

### Error: Base de datos no conecta

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Ver logs de PostgreSQL
docker-compose logs db

# Reiniciar PostgreSQL
docker-compose restart db
```

## 📚 Próximos Pasos

1. **Configurar Migraciones de Base de Datos**
   - Usar Alembic para gestionar el esquema de la base de datos

2. **Agregar Autenticación**
   - Implementar JWT para autenticación de usuarios

3. **Agregar Tests**
   - Configurar pytest para backend
   - Configurar Vitest para frontend

4. **CI/CD**
   - Configurar GitHub Actions o GitLab CI

5. **Monitoreo**
   - Agregar logging estructurado
   - Implementar métricas con Prometheus

## 📄 Licencia

[Tu Licencia Aquí]

## 🤝 Contribuir

[Instrucciones para contribuir]

## 📧 Contacto

[Tu información de contacto]
