"""
Actividad 2 - API CRUD de Productos con FastAPI
================================================
Este archivo implementa una API RESTful completa para el recurso Productos,
con persistencia en SQLite y documentación automática en Swagger UI.

Swagger UI: http://127.0.0.1:8000/docs
ReDoc:      http://127.0.0.1:8000/redoc
"""

from pathlib import Path
import sqlite3
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Path as Ruta, status
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# Configuración general y base de datos
# -----------------------------------------------------------------------------
ruta_base = Path(__file__).parent
ruta_bd = ruta_base / "productos.db"


app = FastAPI(
    title="API CRUD de Productos",
    description=(
        "API RESTful para crear, listar, actualizar y eliminar productos. "
        "Incluye validaciones de negocio y persistencia en SQLite."
    ),
    version="1.0.0",
)


def obtener_conexion_bd():
    """Crea conexión SQLite con filas tipo diccionario."""
    conexion = sqlite3.connect(ruta_bd)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    """Crea la tabla productos si no existe."""
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            categoria TEXT
        )
        """
    )
    conexion.commit()
    conexion.close()


@app.on_event("startup")
def al_arrancar_api():
    inicializar_bd()


# -----------------------------------------------------------------------------
# Esquemas (se ven en Swagger)
# -----------------------------------------------------------------------------
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre del producto")
    precio: float = Field(..., gt=0, description="Precio del producto (debe ser > 0)")
    stock: int = Field(..., ge=0, description="Cantidad disponible (entero >= 0)")
    categoria: Optional[str] = Field(default=None, description="Categoría del producto")


class ProductoCrear(ProductoBase):
    pass


class ProductoActualizar(ProductoBase):
    pass


class ProductoParcheStock(BaseModel):
    stock: int = Field(..., ge=0, description="Nuevo stock (entero >= 0)")


class ProductoRespuesta(ProductoBase):
    id: int = Field(..., description="ID autogenerado")


class RespuestaError(BaseModel):
    error: str
    detalles: Optional[List[str]] = None


# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
def fila_a_diccionario(fila):
    return {
        "id": fila["id"],
        "nombre": fila["nombre"],
        "precio": fila["precio"],
        "stock": fila["stock"],
        "categoria": fila["categoria"],
    }


def buscar_producto_por_id(id_producto: int):
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    fila = cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,)).fetchone()
    conexion.close()
    return fila


# -----------------------------------------------------------------------------
# Endpoints CRUD
# -----------------------------------------------------------------------------
@app.get(
    "/api/productos",
    response_model=List[ProductoRespuesta],
    summary="Obtener todos los productos",
)
def obtener_todos_los_productos():
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    filas = cursor.execute("SELECT * FROM productos ORDER BY id ASC").fetchall()
    conexion.close()
    return [fila_a_diccionario(fila) for fila in filas]


@app.get(
    "/api/productos/{id_producto}",
    response_model=ProductoRespuesta,
    responses={404: {"model": RespuestaError, "description": "Producto no encontrado"}},
    summary="Obtener un producto por ID",
)
def obtener_producto_por_id(
    id_producto: int = Ruta(..., ge=1, description="ID del producto a buscar"),
):
    fila = buscar_producto_por_id(id_producto)
    if not fila:
        raise HTTPException(status_code=404, detail={"error": "Producto no encontrado."})
    return fila_a_diccionario(fila)


@app.post(
    "/api/productos",
    response_model=ProductoRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo producto",
)
def crear_producto(datos_nuevo_producto: ProductoCrear):
    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, precio, stock, categoria) VALUES (?, ?, ?, ?)",
        (
            datos_nuevo_producto.nombre.strip(),
            float(datos_nuevo_producto.precio),
            int(datos_nuevo_producto.stock),
            datos_nuevo_producto.categoria,
        ),
    )
    conexion.commit()
    id_creado = cursor.lastrowid
    fila = cursor.execute("SELECT * FROM productos WHERE id = ?", (id_creado,)).fetchone()
    conexion.close()
    return fila_a_diccionario(fila)


@app.put(
    "/api/productos/{id_producto}",
    response_model=ProductoRespuesta,
    responses={404: {"model": RespuestaError, "description": "Producto no encontrado"}},
    summary="Actualizar producto completo",
)
def actualizar_producto_completo(
    datos_actualizados: ProductoActualizar,
    id_producto: int = Ruta(..., ge=1, description="ID del producto a actualizar"),
):
    if not buscar_producto_por_id(id_producto):
        raise HTTPException(status_code=404, detail={"error": "Producto no encontrado."})

    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    cursor.execute(
        """
        UPDATE productos
        SET nombre = ?, precio = ?, stock = ?, categoria = ?
        WHERE id = ?
        """,
        (
            datos_actualizados.nombre.strip(),
            float(datos_actualizados.precio),
            int(datos_actualizados.stock),
            datos_actualizados.categoria,
            id_producto,
        ),
    )
    conexion.commit()
    fila = cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,)).fetchone()
    conexion.close()
    return fila_a_diccionario(fila)


@app.patch(
    "/api/productos/{id_producto}",
    response_model=ProductoRespuesta,
    responses={404: {"model": RespuestaError, "description": "Producto no encontrado"}},
    summary="Actualizar stock parcialmente",
)
def actualizar_stock_parcial(
    datos_parche: ProductoParcheStock,
    id_producto: int = Ruta(..., ge=1, description="ID del producto a actualizar stock"),
):
    if not buscar_producto_por_id(id_producto):
        raise HTTPException(status_code=404, detail={"error": "Producto no encontrado."})

    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    cursor.execute("UPDATE productos SET stock = ? WHERE id = ?", (int(datos_parche.stock), id_producto))
    conexion.commit()
    fila = cursor.execute("SELECT * FROM productos WHERE id = ?", (id_producto,)).fetchone()
    conexion.close()
    return fila_a_diccionario(fila)


@app.delete(
    "/api/productos/{id_producto}",
    summary="Eliminar producto",
    responses={
        200: {"description": "Producto eliminado"},
        404: {"model": RespuestaError, "description": "Producto no encontrado"},
    },
)
def eliminar_producto(
    id_producto: int = Ruta(..., ge=1, description="ID del producto a eliminar"),
):
    if not buscar_producto_por_id(id_producto):
        raise HTTPException(status_code=404, detail={"error": "Producto no encontrado."})

    conexion = obtener_conexion_bd()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
    conexion.commit()
    conexion.close()
    return {"mensaje": "Producto eliminado correctamente."}
