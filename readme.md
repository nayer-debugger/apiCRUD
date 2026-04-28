# Actividad 2 - API CRUD de Productos (con Swagger)

Esta API está hecha con **FastAPI + SQLite** para que puedas revisar y probar todo desde **Swagger UI**.

##  Documentación interactiva
Cuando se levante el server se puede checar aquí:
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Recurso: Productos
Atributos:
- `id` (autogenerado)
- `nombre` (string, requerido)
- `precio` (float, mayor a 0)
- `stock` (entero, mínimo 0)
- `categoria` (string)

## Endpoints requeridos
- `GET /api/productos`
- `GET /api/productos/{id}`
- `POST /api/productos`
- `PUT /api/productos/{id}`
- `PATCH /api/productos/{id}`
- `DELETE /api/productos/{id}`

## Cómo ejecutar
1. Instala dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Levanta el servidor:
   ```bash
   uvicorn app:app --reload
   ```

## Notas
- Los datos se guardan en `productos.db`.
- Las validaciones de `precio` y `stock` se aplican automáticamente y se muestran también en Swagger.
- Errores esperados:
  - `400/422` para datos inválidos.
  - `404` cuando el producto no existe.
