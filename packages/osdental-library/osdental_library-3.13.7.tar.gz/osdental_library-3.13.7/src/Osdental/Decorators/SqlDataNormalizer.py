from functools import wraps
from sqlalchemy.engine.row import RowMapping, Row
from sqlalchemy.engine import Result
from typing import Any, Callable, Awaitable


def dictify_sql_result(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorador que convierte automáticamente los resultados devueltos por funciones asíncronas
    que usan SQLAlchemy (ORM o Core), transformando RowMapping o Row en dicts puros.
    
    Maneja correctamente:
    - None
    - Escalares (int, str, etc.)
    - RowMapping / Row únicos o listas
    - Result devuelto sin procesar
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)

        # --- Caso 1: None o vacío ---
        if result is None:
            return None

        # --- Caso 2: SQLAlchemy Result ---
        # Si alguien devolvió el objeto Result directamente (sin .mappings() ni .fetchall())
        if isinstance(result, Result):
            try:
                # Intentar convertir el contenido del Result en dicts
                rows = result.mappings().all()
                return [dict(r) for r in rows]
            except Exception:
                # Si no son mappings, intentar convertir Row normales
                rows = result.all()
                return [dict(r._mapping) for r in rows]

        # --- Caso 3: Lista de RowMapping o Row ---
        if isinstance(result, list) and result:
            first_item = result[0]
            if isinstance(first_item, RowMapping):
                return [dict(r) for r in result]
            if isinstance(first_item, Row):
                return [dict(r._mapping) for r in result]
            return result  # lista de escalares o ya dicts

        # --- Caso 4: RowMapping o Row único ---
        if isinstance(result, RowMapping):
            return dict(result)
        if isinstance(result, Row):
            return dict(result._mapping)

        # --- Caso 5: Escalar (str, int, etc.) o dict ya procesado ---
        return result

    return wrapper
