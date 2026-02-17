# Testing Guide - PSET2 Banking System

Este documento explica cómo probar el sistema bancario desarrollado.

## Opciones de Prueba

### Opción 1: Usando Nix Devshell (Recomendado)

La forma más confiable de probar el sistema es usando el devshell de Nix, que ya tiene todas las dependencias correctamente configuradas.

#### 1. Iniciar la Base de Datos

```bash
# Iniciar solo la base de datos con Docker
docker compose up -d db

# Esperar a que esté lista (unos 5 segundos)
sleep 5
```

#### 2. Iniciar el API

```bash
# Configurar variables de entorno
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=pset2
export POSTGRES_PASSWORD=pset2password
export POSTGRES_DB=pset2_db

# Entrar al devshell e iniciar la API
nix develop --command bash -c "uvicorn app.application.api:app --host 0.0.0.0 --port 8000"
```

La API estará disponible en:
- **API**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Redoc**: http://localhost:8000/redoc

#### 3. Ejecutar Tests Automatizados

En otra terminal:

```bash
# Dar permisos de ejecución al script
chmod +x test_api.sh

# Ejecutar el script de pruebas
./test_api.sh
```

El script ejecutará una suite completa de pruebas que incluye:
1. Health check
2. Crear cliente
3. Crear cuenta
4. Depósito
5. Retiro
6. Transferencia entre cuentas
7. Consulta de saldo
8. Listar transacciones

### Opción 2: Usando Docker Compose (Si la Red Funciona)

```bash
# Iniciar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f api

# Probar
./test_api.sh
```

**Nota**: Actualmente hay problemas temporales de DNS en el entorno de Docker para descargar paquetes de PyPI. Por eso se recomienda usar la Opción 1.

### Opción 3: Pruebas Manuales con curl

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Crear Cliente
```bash
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Juan Pérez", "email": "juan.perez@example.com"}'
```

#### Crear Cuenta
```bash
# Reemplazar CUSTOMER_ID con el ID del cliente creado
curl -X POST http://localhost:8000/accounts \
  -H "Content-Type: application/json" \
  -d '{"customer_id": "CUSTOMER_ID", "currency": "USD"}'
```

#### Depositar
```bash
# Reemplazar ACCOUNT_ID con el ID de la cuenta creada
curl -X POST http://localhost:8000/transactions/deposit \
  -H "Content-Type: application/json" \
  -d '{"account_id": "ACCOUNT_ID", "amount": 1000.00}'
```

#### Consultar Saldo
```bash
curl http://localhost:8000/accounts/ACCOUNT_ID/balance
```

#### Retirar
```bash
curl -X POST http://localhost:8000/transactions/withdraw \
  -H "Content-Type: application/json" \
  -d '{"account_id": "ACCOUNT_ID", "amount": 200.00}'
```

#### Transferir
```bash
curl -X POST http://localhost:8000/transactions/transfer \
  -H "Content-Type: application/json" \
  -d '{"from_account_id": "FROM_ACCOUNT_ID", "to_account_id": "TO_ACCOUNT_ID", "amount": 100.00"}'
```

## Endpoints Disponibles

### Customers
- `POST /customers` - Crear cliente
- `GET /customers` - Listar clientes
- `GET /customers/{id}` - Obtener cliente por ID

### Accounts
- `POST /accounts` - Crear cuenta
- `GET /accounts/{id}` - Obtener cuenta por ID
- `GET /accounts/{id}/balance` - Obtener saldo
- `GET /accounts/{id}/transactions` - Listar transacciones
- `GET /customers/{customer_id}/accounts` - Listar cuentas de un cliente

### Transactions
- `POST /transactions/deposit` - Depositar
- `POST /transactions/withdraw` - Retirar
- `POST /transactions/transfer` - Transferir
- `GET /transactions/{id}` - Obtener transacción por ID

### Ledger
- `GET /ledger/entries` - Listar todas las entradas del ledger
- `GET /accounts/{account_id}/ledger` - Listar entradas del ledger por cuenta

## Arquitectura Implementada

El sistema implementa los siguientes patrones y componentes:

### Patrones de Diseño
1. **Repository Pattern** - Abstracción de acceso a datos
2. **Strategy Pattern** - Estrategias de comisiones y reglas de riesgo
3. **Facade Pattern** - Punto único de entrada para la lógica de negocio
4. **Factory Pattern** - Creación de transacciones
5. **Builder Pattern** - Construcción de transacciones complejas

### Capas
- **Domain** (`app/domain/`) - Modelos de dominio, reglas de negocio, excepciones
- **Repositories** (`app/repositories/`) - Acceso a datos con SQLAlchemy ORM
- **Services** (`app/services/`) - Lógica de aplicación y orquestación
- **Application** (`app/application/`) - API REST con FastAPI

### Features Implementadas
- ✅ Gestión de clientes
- ✅ Gestión de cuentas (múltiples por cliente)
- ✅ Transacciones (depósito, retiro, transferencia)
- ✅ Ledger de doble entrada (auditoría completa)
- ✅ Cálculo de comisiones (estrategias configurables)
- ✅ Validación de reglas de riesgo (monto máximo, velocidad, límite diario)
- ✅ Documentación OpenAPI/Swagger
- ✅ Validación con Pydantic
- ✅ Manejo de errores y excepciones personalizadas

## Verificación de Issues Resueltos

Este branch resuelve los siguientes issues:

- ✅ #1 - Academic Domain Model (Customer/Account/Transaction/Ledger) + Invariants
- ✅ #2 - Fee Strategies (Strategy Pattern) + Integration in Use Cases
- ✅ #3 - Simple Risk Rules (max/velocity/daily) + Integration
- ✅ #4 - Transaction Factory + Builder (Creational Patterns)
- ✅ #5 - Banking Facade + Use Cases (create/deposit/withdraw/transfer/query)
- ✅ #6 - Repositories Interfaces + SQLAlchemy ORM Models (Postgres)
- ✅ #7 - FastAPI MVP Endpoints + Pydantic DTOs + Swagger Docs

## Troubleshooting

### La API no arranca
- Verificar que PostgreSQL esté corriendo: `docker ps | grep pset2_db`
- Verificar las variables de entorno
- Ver logs: `docker compose logs db`

### Errores de conexión a la base de datos
- Verificar que el puerto 5432 no esté en uso por otra aplicación
- Verificar las credenciales en `.env`

### El script test_api.sh falla
- Verificar que la API esté corriendo en el puerto correcto
- Verificar que `python` esté disponible para `json.tool`
- Usar `python3` si es necesario: editar el script

### Docker build falla (DNS errors)
- Esto es un problema temporal de red en el entorno
- Usar la Opción 1 (Nix Devshell) que ya tiene las dependencias
- O esperar a que la red se estabilice

## Próximos Pasos

Para completar el proyecto:
1. ✅ Backend completo (este branch)
2. ⏳ Frontend con Streamlit (issues #13-17)
3. ⏳ Tests con Pytest (issue #11)
4. ⏳ Demo end-to-end (issue #12)
5. ⏳ README académico final (issue #10)
