"""Verificación de persistencia real y ausencia de escrituras indebidas (Guía Semana 14).

Llama al API por HTTP (como lo haría el frontend) y comprueba cada resultado con una
CONEXIÓN INDEPENDIENTE a la base de datos (no la del API):

  P1  RF-01 válido:     POST /predict -> 201; el registro se recupera igual desde otra conexión.
  P2  RF-01 rechazo:    archivo .txt -> 400; mismo número de registros antes y después.
  P3  RF-01 rechazo:    imagen corrupta -> 400; sin registro huérfano.
  P4  RF-01 rechazo:    petición sin archivo -> 400; sin registro huérfano.
  P5  RF-01 rechazo:    imagen > 5 MB -> 413; sin registro huérfano.
  P6  RF-01 rechazo:    sin token -> 401; sin registro huérfano.
  P7  RF-02 válido:     GET /predict/{id} -> 200 con los mismos datos; el registro no cambia.
  P8  RF-02 ausencia:   GET /predict/999999999 -> 404; la tabla no cambia.
  P9  RF-02 entrada:    GET /predict/0 -> 400; la tabla no cambia.
  P10 RF-02 válido:     GET /history -> 200; la tabla no cambia.
  P11 RF-02 rechazo:    PATCH /verify con categoría inválida -> 400; categoria_confirmada no cambia.
  P12 RF-03 válido:     GET /stats -> 200; total_consultas coincide con la BD; la tabla no cambia.

Requisitos: el backend corriendo y estas variables (en backend/.env o en la terminal):
  DATABASE_URL  la misma base de datos que usa el backend
  API_TOKEN     access_token de Supabase de un usuario asociado a una empresa
  API_URL       opcional, por defecto http://localhost:8000

Uso (desde backend/):
  python scripts/verificar_persistencia.py
  python scripts/verificar_persistencia.py --imagen ruta/a/residuo.jpg
  python scripts/verificar_persistencia.py --limpiar     # borra el registro creado al final
  python scripts/verificar_persistencia.py --salida ../DOCS/evidencia_persistencia.md

Nota: P1 crea UN registro real en prediction_logs. Use --limpiar para borrarlo al terminar.
"""

import argparse
import io
import os
import sys
from datetime import datetime
from decimal import Decimal

import httpx
import jwt
from dotenv import load_dotenv
from PIL import Image
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv()

COLUMNAS = (
    "id, fecha, clase_predicha, confianza, tiempo_inferencia, "
    "advertencia_activada, company_id, user_id, categoria_confirmada"
)


# ─── Conexión independiente a la BD (no usa la sesión del API) ───
class BD:
    def __init__(self, url: str):
        self.engine = create_engine(
            make_url(url.strip().strip('"').strip()), pool_pre_ping=True
        )

    def _uno(self, sql: str, **params):
        with self.engine.connect() as conn:  # conexión nueva en cada lectura
            return conn.execute(text(sql), params).mappings().first()

    def company_id(self, user_id: str):
        fila = self._uno(
            "SELECT company_id FROM company_members WHERE user_id = :u", u=user_id
        )
        return fila["company_id"] if fila else None

    def contar(self, company_id: int) -> int:
        return self._uno(
            "SELECT COUNT(*) AS n FROM prediction_logs WHERE company_id = :c",
            c=company_id,
        )["n"]

    def registro(self, prediction_id: int):
        fila = self._uno(
            f"SELECT {COLUMNAS} FROM prediction_logs WHERE id = :i", i=prediction_id
        )
        if not fila:
            return None
        return {
            k: float(v) if isinstance(v, Decimal) else v for k, v in dict(fila).items()
        }

    def borrar(self, prediction_id: int) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text("DELETE FROM prediction_logs WHERE id = :i"), {"i": prediction_id}
            )


# ─── Utilidades ───
def imagen_prueba(ruta):
    if ruta:
        with open(ruta, "rb") as f:
            datos = f.read()
        tipo = (
            "image/png"
            if ruta.lower().endswith(".png")
            else ("image/webp" if ruta.lower().endswith(".webp") else "image/jpeg")
        )
        return os.path.basename(ruta), datos, tipo
    buf = io.BytesIO()
    Image.new("RGB", (224, 224), color=(150, 110, 70)).save(buf, format="JPEG")
    return "residuo_prueba.jpg", buf.getvalue(), "image/jpeg"


def normalizar(valor):
    """Unifica fechas (datetime o texto, con 'T' o espacio) para compararlas."""
    if isinstance(valor, datetime):
        valor = valor.isoformat()
    return valor.replace("T", " ") if isinstance(valor, str) else valor


class Reporte:
    def __init__(self):
        self.filas = []

    def agregar(self, codigo, escenario, esperado, obtenido, ok):
        self.filas.append((codigo, escenario, esperado, obtenido, ok))
        print(
            f"[{'CUMPLE' if ok else 'FALLA '}] {codigo:4} {escenario}\n"
            f"         esperado: {esperado}\n         obtenido: {obtenido}"
        )

    @property
    def todo_ok(self):
        return all(f[4] for f in self.filas)

    def markdown(self, contexto: dict) -> str:
        lineas = [
            "# Evidencia: persistencia real y ausencia de escrituras indebidas",
            "",
        ]
        lineas += [f"- **{k}:** {v}" for k, v in contexto.items()]
        lineas += [
            "",
            "| Prueba | Escenario | Esperado | Obtenido | Resultado |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for c, e, esp, obt, ok in self.filas:
            lineas.append(
                f"| {c} | {e} | {esp} | {obt} | {'✅ Cumple' if ok else '❌ No cumple'} |"
            )
        total = sum(1 for f in self.filas if f[4])
        lineas += ["", f"**Resultado:** {total}/{len(self.filas)} pruebas cumplen.", ""]
        return "\n".join(lineas)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--imagen", help="Imagen real de un residuo (por defecto se genera una)."
    )
    parser.add_argument(
        "--limpiar",
        action="store_true",
        help="Borrar al final el registro creado en P1.",
    )
    parser.add_argument("--salida", help="Guardar el reporte en un archivo Markdown.")
    args = parser.parse_args()

    api_url = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
    token = (os.getenv("API_TOKEN") or "").strip()
    db_url = os.getenv("DATABASE_URL")
    if not token or not db_url:
        sys.exit(
            "Faltan variables: defina API_TOKEN y DATABASE_URL (ver la ayuda con --help)."
        )

    # El user_id (sub) se lee del token solo para ubicar la empresa en la BD.
    user_id = jwt.decode(token, options={"verify_signature": False}).get("sub")
    bd = BD(db_url)
    company_id = bd.company_id(user_id)
    if company_id is None:
        sys.exit(
            "El usuario del token no está asociado a ninguna empresa: asócielo antes de probar."
        )

    auth = {"Authorization": f"Bearer {token}"}
    cliente = httpx.Client(base_url=api_url, timeout=60)
    rep = Reporte()
    nombre, datos_img, tipo_img = imagen_prueba(args.imagen)
    inicio = datetime.now()
    total_inicial = bd.contar(company_id)
    print(
        f"API: {api_url} | empresa: {company_id} | registros iniciales de la empresa: {total_inicial}\n"
    )

    # ── P1 RF-01 válido: 201 + recuperación desde otra conexión ──
    antes = bd.contar(company_id)
    r = cliente.post(
        "/predict", headers=auth, files={"file": (nombre, datos_img, tipo_img)}
    )
    despues = bd.contar(company_id)
    pid, reg = None, None
    if r.status_code == 201:
        cuerpo = r.json()
        pid = cuerpo.get("id_prediccion")
        reg = bd.registro(pid) if pid else None
    ok = (
        r.status_code == 201
        and reg is not None
        and despues == antes + 1
        and reg["clase_predicha"] == cuerpo["clase"]
        and abs(reg["confianza"] - cuerpo["confianza"]) < 1e-6
        and reg["tiempo_inferencia"] == cuerpo["tiempo_inferencia_ms"]
        and reg["advertencia_activada"] == cuerpo["advertencia"]
        and reg["company_id"] == company_id
        and reg["user_id"] == user_id
    )
    obtenido = (
        f"{r.status_code}; id={pid}; registros {antes}->{despues}; "
        f"BD: clase={reg['clase_predicha']}, confianza={reg['confianza']}"
        if reg
        else f"{r.status_code} {r.text[:120]}"
    )
    rep.agregar(
        "P1",
        "RF-01 válido: POST /predict con imagen",
        "201, ID real, +1 registro y mismos datos leídos desde otra conexión",
        obtenido,
        ok,
    )
    if pid is None:
        print("\nNo se pudo crear el registro de prueba; se detiene la verificación.")
        sys.exit(1)

    # ── P2-P6 RF-01 rechazos: sin registro huérfano ──
    def rechazo(codigo, escenario, esperado_http, **kwargs):
        n0 = bd.contar(company_id)
        resp = cliente.post("/predict", **kwargs)
        n1 = bd.contar(company_id)
        rep.agregar(
            codigo,
            escenario,
            f"{esperado_http}; registros sin cambio",
            f"{resp.status_code} {resp.json().get('detail', '')!r}; registros {n0}->{n1}",
            resp.status_code == esperado_http and n0 == n1,
        )

    rechazo(
        "P2",
        "RF-01 rechazo: archivo .txt",
        400,
        headers=auth,
        files={"file": ("nota.txt", b"no soy una imagen", "text/plain")},
    )
    rechazo(
        "P3",
        "RF-01 rechazo: imagen corrupta",
        400,
        headers=auth,
        files={"file": ("rota.jpg", b"esto no es un jpg", "image/jpeg")},
    )
    rechazo("P4", "RF-01 rechazo: petición sin archivo", 400, headers=auth)
    rechazo(
        "P5",
        "RF-01 rechazo: imagen de 6 MB",
        413,
        headers=auth,
        files={"file": ("grande.jpg", b"0" * (6 * 1024 * 1024), "image/jpeg")},
    )
    rechazo(
        "P6",
        "RF-01 rechazo: sin token",
        401,
        files={"file": (nombre, datos_img, tipo_img)},
    )

    # ── P7-P10 RF-02 consultas: no modifican datos ──
    def consulta(codigo, escenario, ruta, esperado_http, extra=None):
        n0, snap0 = bd.contar(company_id), bd.registro(pid)
        resp = cliente.get(ruta, headers=auth)
        n1, snap1 = bd.contar(company_id), bd.registro(pid)
        ok_extra, txt_extra = extra(resp) if extra else (True, "")
        rep.agregar(
            codigo,
            escenario,
            f"{esperado_http}; tabla y registro sin cambios",
            f"{resp.status_code}{txt_extra}; registros {n0}->{n1}; "
            f"registro {'sin cambios' if snap0 == snap1 else 'MODIFICADO'}",
            resp.status_code == esperado_http
            and n0 == n1
            and snap0 == snap1
            and ok_extra,
        )

    def coincide_con_bd(resp):
        if resp.status_code != 200:
            return False, ""
        api = {k: normalizar(v) for k, v in resp.json().items()}
        bdd = {k: normalizar(v) for k, v in bd.registro(pid).items()}
        iguales = (
            all(
                str(api.get(k))[:19] == str(bdd[k])[:19]
                for k in ("id", "clase_predicha", "fecha")
            )
            and abs(api["confianza"] - bdd["confianza"]) < 1e-6
        )
        return (
            iguales,
            f" (datos {'coinciden' if iguales else 'NO coinciden'} con la BD)",
        )

    consulta(
        "P7",
        f"RF-02 válido: GET /predict/{pid}",
        f"/predict/{pid}",
        200,
        coincide_con_bd,
    )
    consulta("P8", "RF-02 ausencia: GET /predict/999999999", "/predict/999999999", 404)
    consulta("P9", "RF-02 entrada inválida: GET /predict/0", "/predict/0", 400)
    consulta("P10", "RF-02 válido: GET /history", "/history?skip=0&limit=10", 200)

    # ── P11 RF-02 verificación con categoría inválida: no escribe ──
    cat0 = bd.registro(pid)["categoria_confirmada"]
    resp = cliente.patch(
        f"/predict/{pid}/verify", headers=auth, json={"categoria_correcta": "vidrio"}
    )
    cat1 = bd.registro(pid)["categoria_confirmada"]
    rep.agregar(
        "P11",
        "RF-02 rechazo: PATCH /verify con categoría 'vidrio'",
        "400; categoria_confirmada sin cambio",
        f"{resp.status_code}; categoria_confirmada {cat0!r}->{cat1!r}",
        resp.status_code == 400 and cat0 == cat1,
    )

    # ── P12 RF-03: estadísticas coinciden con la BD y no escriben ──
    def total_coincide(resp):
        if resp.status_code != 200:
            return False, ""
        api_total, bd_total = resp.json()["total_consultas"], bd.contar(company_id)
        return api_total == bd_total, f" (total API={api_total}, BD={bd_total})"

    consulta("P12", "RF-03 válido: GET /stats", "/stats", 200, total_coincide)

    # ── Cierre ──
    total_final = bd.contar(company_id)
    if args.limpiar:
        bd.borrar(pid)
        print(f"\nRegistro de prueba {pid} eliminado (--limpiar).")
    resumen = sum(1 for f in rep.filas if f[4])
    print(
        f"\nResultado: {resumen}/{len(rep.filas)} pruebas cumplen. "
        f"Registros de la empresa: {total_inicial} -> {total_final} (solo P1 debía escribir)."
    )

    if args.salida:
        contexto = {
            "Fecha de ejecución": inicio.strftime("%Y-%m-%d %H:%M:%S"),
            "API": api_url,
            "Base de datos": f"{make_url(db_url.strip().strip(chr(34))).get_backend_name()} "
            f"({make_url(db_url.strip().strip(chr(34))).host})",
            "Empresa (company_id)": company_id,
            "Imagen usada": nombre,
            "Registros de la empresa": f"{total_inicial} -> {total_final} (solo P1 escribe)",
            "Registro creado": f"id={pid}"
            + (" (eliminado con --limpiar)" if args.limpiar else ""),
        }
        with open(args.salida, "w", encoding="utf-8") as f:
            f.write(rep.markdown(contexto))
        print(f"Reporte guardado en {args.salida}")

    sys.exit(0 if rep.todo_ok else 1)


if __name__ == "__main__":
    main()
