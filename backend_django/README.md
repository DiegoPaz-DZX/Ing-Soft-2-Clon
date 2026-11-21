# Backend Django de Kyzen

El backend se levanta en el puerto 8000 y usa Django con SQLite como base de datos
persistente (`db.sqlite3`).

```powershell
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Rutas implementadas hasta ahora:

- `GET /api/balance` (HU6)
- `GET /api/tips` (HU12)
- `GET /api/categorias` (HU2)
- `POST /api/registro` (HU7)
- `GET /api/movimientos?desde=AAAA-MM-DD&hasta=AAAA-MM-DD` (HU4)
- `POST /api/login` con `{"correo": "...", "clave": "..."}` (HU8)
- `GET /api/reportes/financiero?desde=AAAA-MM-DD&hasta=AAAA-MM-DD` (HU22). Con `formato=csv` o `formato=json` descarga el reporte
- `GET /api/preferencias/moneda?cuenta=ID` y `PUT /api/preferencias/moneda` con `{"cuenta": ID, "divisa": "PEN" | "USD"}` (HU24)
- `GET /api/admin/usuarios` y `PUT /api/admin/usuarios/ID/rol` usando el token de administrador (HU27)
- `POST /api/movimientos/importar` con un archivo CSV, XLS o XLSX y token de sesión (HU20)

## Importar movimientos (HU20)

El archivo se envía como `multipart/form-data` en el campo `archivo`. Debe incluir las columnas
`tipo`, `monto` y `fecha`; también acepta `descripcion`, `categoria` y `moneda`. Primero se validan
todas las filas y recién después se guardan en la cuenta de la sesión, para no dejar una importación
a medias cuando hay un error.

## Seguridad (HU27)

Luego de ejecutar las migraciones se puede preparar una cuenta administradora así:

```powershell
python manage.py crear_administrador admin@kyzen.local Kyzen2026
```

Las descripciones de movimientos se cifran con Fernet antes de guardarse en SQLite. Los permisos
de administración se controlan en la aplicación mediante el rol de la cuenta.

El tipo de cambio del dólar se consulta una vez al día en `TIPO_CAMBIO_URL` (ver `settings.py`) y se
guarda en la tabla `TipoCambioDiario`. Si la consulta falla se usa el último valor guardado y, si no
hay ninguno, `TIPO_CAMBIO_SOLES_POR_DOLAR`.

La creación de servicios está centralizada en `FabricaServicios`. Cada servicio depende de una
interfaz de repositorio para que la parte de negocio no quede amarrada directamente a Django.

Para correr las pruebas:

```powershell
python manage.py test
```
