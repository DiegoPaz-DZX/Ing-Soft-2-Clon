# Kyzen – Frontend

Frontend de la aplicación Kyzen. Incluye el layout, navegación, rutas, componentes UI y
las primeras historias que se van integrando durante el Sprint 1.

## Historias implementadas

- **HU2:** registro rápido de gastos con categoría, persistencia en el navegador y resumen
  de la categoría con mayor consumo del día.
- **HU7:** registro de usuario con correo y contraseña, validaciones, control de correos
  repetidos y almacenamiento del hash de la contraseña.
- **HU20:** importación de hasta 500 movimientos desde archivos CSV, XLS o XLSX.
- **HU27:** roles de aplicación y cifrado de descripciones antes de guardarlas en SQLite.

El registro, inicio de sesión y los movimientos se conectan al backend Django. El navegador
mantiene una copia local de apoyo para el flujo de registro manual.

## Decisiones de diseño

- `Gasto.crear()` concentra la creación y validación básica del objeto (POO y método fábrica).
- Los servicios contienen las reglas de cada historia y las páginas se encargan de la vista
  (responsabilidad única y alta cohesión).
- Los repositorios aíslan el almacenamiento para poder reemplazar `localStorage` por la API
  del equipo sin cambiar los componentes (bajo acoplamiento e indirección).

## Ejecutar

Requiere Node.js 20 o superior.

```bash
npm install
npm run dev
```

Para ejecutar las pruebas:

```bash
npm test
```

## Estructura

```
src/
  index.css              Design tokens (colores, fuente, radios, sombras)
  App.jsx                Rutas
  routes/paths.js        Rutas y elementos de la barra de navegación
  layouts/               MainLayout (con navbar) y AuthLayout (login/registro)
  components/layout/     Navbar, Logo
  components/transacciones/ Componentes usados por HU2
  components/ui/         Button, Card, Badge, Input, Tabs, Modal, PageContainer, Placeholder
  domain/                Entidades y categorías del dominio
  repositories/          Acceso a datos locales
  services/              Reglas y casos de uso de HU2 y HU7
  pages/                 Una página por módulo
```

## Paleta

| Token           | Color     | Uso                              |
| --------------- | --------- | -------------------------------- |
| `primary`       | `#7C5CFC` | Marca, logo, botones             |
| `accent`        | `#5B5BF5` | Final del degradado de botones   |
| `income`        | `#16A34A` | Ingresos, nav activo             |
| `mint`          | `#A7F3D0` | Banner de metas                  |
| `expense`       | `#EF4444` | Gastos, alertas                  |
| `navy`          | `#1E1B3A` | Botón oscuro                     |
| `app`           | `#F6F7FB` | Fondo de la app                  |

Uso en Tailwind: `bg-primary`, `text-income`, `bg-expense-soft`, `rounded-card`, `shadow-card`…

## Rutas

| Ruta                 | Pantalla                  |
| -------------------- | ------------------------- |
| `/login`, `/registro`| Autenticación             |
| `/`                  | Panel principal           |
| `/transacciones`     | Transacciones             |
| `/historial`         | Historial de movimientos  |
| `/reportes`          | Reportes analíticos       |
| `/reportes/exportar` | Exportar reporte          |
| `/consultoria`       | Consultoría IA            |
| `/metas`             | Objetivos de ahorro       |
| `/perfil`            | Mi perfil                 |
