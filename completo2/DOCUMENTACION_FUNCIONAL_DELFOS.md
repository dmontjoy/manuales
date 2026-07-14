# Documentación Funcional del Sistema Delfos

> **Qué es esto.** La documentación funcional completa del backend de Delfos: **las 544 rutas de la API, una por una**, cada una cruzada con el controlador que la atiende (`app/Http/Controllers/`), el servicio que implementa su lógica (`app/Services/`), el servicio Angular del frontend que la consume y la **pantalla real** donde el usuario la dispara.
>
> **Cómo se construyó.** Tres fuentes cruzadas:
> 1. `php artisan route:list` → las 544 rutas reales (no las suposiciones del código).
> 2. Análisis estático del frontend (`delfos-frontend`): se extrajeron las llamadas HTTP de los 95 servicios Angular y se mapearon a los 380 componentes y sus plantillas HTML.
> 3. **Recorrido en vivo de la aplicación** con navegador automatizado, registrando para cada pantalla las peticiones de red que realmente emite. Ese registro es la evidencia del cruce ruta ↔ vista.
>
> **Alcance.** 82 controladores · 544 endpoints · 168 servicios backend · 95 servicios Angular · 380 componentes.
> **Stack.** Laravel 11 / PHP 8.2 · Angular 19 · MySQL multi-tenant · S3 · Power BI.
> **Entorno de captura.** Proyecto "Línea 2 del Metro de Lima y Callao" (`metro2`), usuario `admin`, rol Administrador.
> **Fecha.** 14/07/2026.

---

## 1. Cómo leer este documento

- La **§2** explica las convenciones de rutas y la seguridad transversal (aplican a todos los módulos).
- La **§3** documenta cada módulo funcional con sus pantallas reales y los endpoints que cada una dispara.
- La **§4** recoge los **hallazgos** del recorrido: código muerto, endpoints huérfanos, un 403 con rol Administrador y el módulo de IA inaccesible.
- El **Anexo A** lista **las 544 rutas una por una**, con controlador, acción, servicio Angular y vista.

### 1.1 Convenciones de nombres

Los sufijos se repiten en todo el sistema; conocerlos permite leer cualquier módulo sin explicación adicional.

| Patrón | Qué hace |
|---|---|
| `.../listar` | Lista paginada y filtrable. |
| `.../listar-init` | Catálogos y filtros que necesita la pantalla de listado. |
| `.../listar-mapa` | Igual que `listar`, pero devolviendo geometría para la vista de mapa. |
| `.../ver/{id}` | Detalle de un registro. |
| `.../crear` · `.../crear-init` | Alta, y los catálogos que necesita su formulario. |
| `.../editar` · `.../eliminar/{id}` | Modificación y baja. |
| `.../reordenar` | Cambia el orden de un catálogo (drag & drop). |
| `.../exportar` | Exportación **síncrona** a Excel/PDF. |
| `.../exportar/iniciar` + `/{id}/status` + `/{id}/download` | Exportación **asíncrona** para volúmenes grandes. |
| `.../archivo-exportar` | Exporta las **evidencias** (adjuntos) del módulo. |
| `.../proceso/{id}` | Línea de tiempo del registro (trazabilidad de estados). |
| `.../informe` | Informe PDF consolidado. |
| `.../qc` | Marca de control de calidad (Quality Check). |
| `.../ficha/{id}` | Ficha 360° de una entidad. |
| `dropdown/...` | Listas ligeras para los selectores de los formularios. |

### 1.2 Seguridad y contexto (transversal)

- **Autenticación.** Salvo el bloque de acceso (`/auth/init`, `/auth/login`, `/auth/oauth`, `/recover*`, `/oauth/url`), **todos los endpoints exigen JWT** en cookie HttpOnly `token_delfos`. Cadena por petición: `jwt` → `profile-permit` (permiso del rol sobre el endpoint) → `accion-log` (auditoría). Globales: `SecureHeaders` (CSP), `MaintenanceMiddleware`, `VerifyCsrfOrigin`.
- **Multi-tenant.** Cada proyecto es una base de datos independiente; la conexión se resuelve desde el proyecto contenido en el JWT.
- **Autorización por registro.** En interacción, reclamo, solicitud y compromiso, el rol básico sólo edita/elimina lo que creó (o donde es relacionista asignado). La lectura dentro del proyecto es abierta: *"ver todo el proyecto, editar sólo lo propio"*. En stakeholders el CRUD es compartido.
- **Protección del acceso.** Rate limiting en `login`, `oauth`, `recover` y `recover/password`; reCAPTCHA y bloqueo temporal con backoff tras intentos fallidos.
- **Módulos activables.** Configuración → Módulos enciende y apaga módulos por proyecto. Verificado en vivo en `metro2`: Interacciones, Reclamos, Compromisos, Solicitud e IA activos; **Predios desactivado**.

---

## 2. Las pantallas y los endpoints que disparan

Cada pantalla se documenta con la captura real y **las peticiones que emite**, registradas en vivo durante el recorrido.

### 2.1 Acceso — Login

![Login](manual-assets/01-login.png)

Ingreso con usuario y contraseña, acceso con Outlook/Google y enlace de recuperación. Protegida por reCAPTCHA.

| Al abrir / actuar | Endpoint |
|---|---|
| Cargar la pantalla | `GET /auth/init` |
| Pulsar *Iniciar Sesión* | `POST /auth/login` |
| Botones Outlook / Google | `GET /oauth/url` → `POST /auth/oauth` |
| Recargar con sesión viva | `GET /auth/me` |

### 2.2 Inicio

![Inicio](manual-assets/v02-inicio.png)

KPIs por módulo, actividades pendientes y relacionistas más activos.

| Al abrir | Endpoint |
|---|---|
| Perfil del usuario | `GET /perfil` |
| Aviso pendiente | `GET /boletin/init` |
| KPIs y pendientes | `GET /reportes/inicio/init-dashboard` |
| Gráfico de relacionistas | `GET /reportes/interaccion/relacionista` |
| Buscador de la barra superior | `GET /dropdown/general` |

### 2.3 Stakeholders — listado

![Stakeholders](manual-assets/v03-stakeholder-listar.png)

Directorio con filtros por fecha, stakeholder, relacionista y etiquetas; paginación y botones de buscar, filtro avanzado y descarga.

| Al abrir / actuar | Endpoint |
|---|---|
| Catálogos y filtros | `GET /stakeholder/listar-init` |
| Resultados | `GET /stakeholder/listar` |
| Vista de mapa | `GET /stakeholder/listar-mapa` |
| Botón de descarga | `POST /generador-archivos/crear` |

### 2.4 Stakeholders — alta

![Nuevo stakeholder](manual-assets/v04-stakeholder-crear.png)

Formulario con conmutador **Natural / Organización**, contacto, ubicación, etiquetas y organización.

| Al abrir / actuar | Endpoint |
|---|---|
| Catálogos del formulario | `GET /stakeholder/crear-init` |
| Guardar | `POST /stakeholder/crear` |
| Adjuntar documentos | `POST /stakeholder/documentos-adjuntos` |

### 2.5 Ficha del stakeholder (360°)

La ficha reúne toda la historia del stakeholder en pestañas. Cada pestaña carga su módulo filtrado por ese stakeholder.

![Ficha — Editar](manual-assets/v05-ficha-tab-editar.png)

*Pestaña **Editar** (la que abre por defecto): datos del stakeholder y su evaluación (Posición, Poder, Interés) en la cabecera.*

![Ficha — Interacción](manual-assets/v06-ficha-tab-interaccion.png)

*Pestaña **Interacción**: el histórico de contactos (2036 en este caso).*

![Ficha — Reclamos](manual-assets/v07-ficha-tab-reclamo.png)
![Ficha — Compromiso](manual-assets/v08-ficha-tab-compromiso.png)
![Ficha — Solicitudes](manual-assets/v09-ficha-tab-solicitud.png)

![Ficha — Combinar](manual-assets/v11-ficha-tab-combinar.png)

*Pestaña **Combinar**: detecta duplicados y fusiona dos fichas. La advertencia lo dice claro: la acción no se puede deshacer.*

| Pestaña | Endpoint que dispara |
|---|---|
| (cabecera, siempre) | `GET /stakeholder/ficha/{idsh}` |
| Editar | `GET /stakeholder/ver/{idsh}` · `GET /stakeholder/crear-init` · `POST /stakeholder/editar` |
| Interacción | `GET /interaccion/listar?ficha={idsh}` |
| Reclamos | `GET /reclamo/listar?ficha={idsh}` |
| Compromiso | `GET /compromiso/listar?ficha={idsh}` |
| Solicitudes | `GET /solicitud/listar?ficha={idsh}` |
| Combinar | `GET /setup/general/stakeholder/duplicados` · `POST /stakeholder/merge` |
| Evaluación (cabecera) | `GET /stakeholder/evaluacion` · `POST /stakeholder/evaluacion/crear` |

### 2.6 Interacciones

![Interacciones](manual-assets/v12-interaccion-listar.png)

Cada tarjeta muestra fecha, stakeholder, relacionistas, etiquetas, descripción y evidencias (PDF).

El alta tiene **dos modos**, y esto es una particularidad del sistema:

![Nueva interacción — Con IA](manual-assets/v13-interaccion-crear.png)

*Modo **Con IA**: se pegan las notas en bruto y el sistema redacta la interacción (`POST /interaccion/generar-crear-ia`).*

![Nueva interacción — Manual](manual-assets/v14-interaccion-crear-manual.png)

*Modo **Manual**: descripción, fecha, tipo, prioridad, stakeholder, relacionista, etiquetas, evidencias y el check de **Control de calidad** (`POST /interaccion/qc`).*

| Al abrir / actuar | Endpoint |
|---|---|
| Catálogos y filtros | `GET /interaccion/listar-init` |
| Resultados | `GET /interaccion/listar` |
| Abrir *Nueva* | `GET /interaccion/crear-init` |
| Generar con IA | `POST /interaccion/generar-crear-ia` |
| Guardar | `POST /interaccion/crear` |
| Comentarios de seguimiento | `GET /interaccion/comentario/listar` · `POST /interaccion/comentario/crear` |

### 2.7 Reclamos

![Reclamos](manual-assets/v15-reclamo-listar.png)

Cada reclamo lleva código (`C-XXXX`), categoría, estado, fecha de registro y **vencimiento**.

![Menú de acciones del reclamo](manual-assets/v16-reclamo-menu-acciones.png)

*El menú **⋮** de cada tarjeta es donde vive el ciclo del reclamo:*

| Opción del menú | Endpoint |
|---|---|
| Editar | `POST /reclamo/editar` |
| **Gestionar** (abre el ciclo) | `GET /reclamo/proceso/{idreclamo}` |
| Control de calidad | `POST /reclamo/qc` |
| Crear Informe | `GET /reclamo/informe` |
| Añadir evaluación | `POST /reclamo/evaluacion/crear` |
| Eliminar | `DELETE /reclamo/eliminar/{idreclamo}` |

**Ciclo:** Recepción → Evaluación → Propuesta → Respuesta → (Apelación) → Cierre. Cada etapa es un sub-controlador con el mismo patrón CRUD (`crear` / `editar` / `ver/{id}` / `eliminar/{id}`).

### 2.8 Solicitudes

![Solicitudes](manual-assets/v18-solicitud-listar.png)

Internamente la entidad se llama *monitoreo* — de ahí que los parámetros de ruta sean `{idmonitoreo}`.

**Ciclo:** Recepción → Evaluación → Propuesta → Revisión → Aprobación → Cierre.

### 2.9 Compromisos y entregables

![Compromisos](manual-assets/v19-compromiso-listar.png)

Cada compromiso muestra código, **contador de entregables** (p. ej. `1 / 1`), categoría, fuente, estado (Hecho / Pendiente / En proceso) y vencimiento.

![Entregables](manual-assets/v20-compromiso-entregables.png)

> **Incidencia detectada.** Al expandir un compromiso para ver sus entregables, `GET /compromiso/entregable?idcompromiso=143` devuelve **403 Forbidden** incluso con rol **Administrador**, y los entregables no llegan a mostrarse. Ver §4.

**Ciclo del entregable:** Implementación → Cumplimiento, con Ajuste y Cancelación como desvíos.

### 2.10 Compromisos externos (Compromisox)

![Compromisos externos](manual-assets/v21-compromisox-listar.png)

> **Ojo con las rutas del frontend:** `/pages/gestion/**commitment**` muestra *Compromisos* (con entregables) y `/pages/gestion/**compromiso**` muestra *Compromisos externos*. Están cruzadas respecto a lo que uno esperaría.

**Ciclo:** Implementar → Completar, con Redefinir y Cancelar como desvíos.

### 2.11 Exportaciones — el modal de descarga

![Modal de descarga](manual-assets/v22-modal-descarga.png)

Presente en **todos** los listados. **Datos** exporta el Excel de los registros filtrados; **Evidencias** exporta sus archivos adjuntos. Encola el trabajo (`POST /generador-archivos/crear`), se genera en segundo plano y se descarga al terminar.

### 2.12 Reportes

Cada reporte tiene **dos pestañas**, y sirven cosas distintas:

![Reporte de Interacciones](manual-assets/v23-reporte-interaccion.png)

*Pestaña **Reporte**: la construye el backend de Delfos. Al abrirla sólo pide `GET /reportes/interaccion/init-dashboard`, que devuelve el bloque completo de datos.*

![Dashboard Power BI](manual-assets/v24-reporte-interaccion-dashboard.png)

*Pestaña **Dashboard**: es un **informe de Microsoft Power BI embebido** (`GET /reportes/power-bi`), no los endpoints `grafico*` del backend.*

Los otros reportes siguen el mismo patrón:

![Reclamos](manual-assets/11-reporte-reclamo.png)
![Solicitudes](manual-assets/12-reporte-solicitud.png)
![Compromisos](manual-assets/13-reporte-compromiso.png)
![Stakeholders](manual-assets/14-reporte-stakeholder.png)
![Descripción de stakeholders](manual-assets/15-reporte-stakeholder-descripcion.png)

### 2.13 Configuración

![Configuración General](manual-assets/v25-setup-general.png)

Un acordeón con 11 secciones: Personalización, Stakeholder, Interacciones, Reclamos, Solicitudes, Compromisos, Mapas, Módulos, Importar Stakeholder, Fechas y Feriados y Delfos IA. Al abrir pide `GET /setup/general/init`.

![Catálogos de interacción](manual-assets/v26-setup-catalogos-interaccion.png)

*Dentro de cada sección viven los catálogos maestros (aquí: canales de atención, niveles de prioridad y alternativas de duración), todos con el mismo patrón `listar`/`crear`/`editar`/`reordenar`/`eliminar`.*

![Módulos](manual-assets/v27-setup-modulos.png)

*La sección **Módulos** enciende y apaga módulos por proyecto. Aquí se ve por qué **Predios** no aparece en el menú de `metro2`: está desmarcado.*

![Usuarios](manual-assets/17-setup-usuario.png)
![Etiquetas](manual-assets/18-setup-tag.png)
![Locaciones / Ubigeo](manual-assets/19-setup-ubigeo.png)

### 2.14 Perfil y sesión

![Menú de usuario](manual-assets/v29-perfil-menu.png)
![Configurar usuario](manual-assets/v30-perfil-configurar.png)

| Al abrir / actuar | Endpoint |
|---|---|
| Datos del perfil | `GET /perfil` · `GET /perfil/formulario-init` |
| Guardar cambios | `POST /perfil/actualizar` |
| Cambiar contraseña | `POST /perfil/password-editar` |
| Notificaciones | `GET/POST /perfil/notificaciones/*` |
| Sesiones activas | `GET /perfil/sesion/listar` |
| Conexiones Google/Outlook | `POST /oauth/conectar` · `DELETE /oauth/desconectar/{id}` |
| Cerrar sesión | `POST /perfil/logout` · `POST /perfil/logout-all` |

### 2.15 Soporte

![Soporte](manual-assets/v28-soporte-bug.png)

Registro y seguimiento de incidencias, con adjuntos y estado (Pendiente / Cerrado). Los adjuntos se validan (extensión, MIME y tamaño) antes de subirse a S3.

---

## 3. Módulos sin pantalla capturable

| Módulo | Endpoints | Por qué no hay captura |
|---|---|---|
| **Predios** (`PredioController`, `PredioCodigoController`, `PredioStakeholderController`) | 19 | Módulo **desactivado** en `metro2` (verificado en Configuración → Módulos). La ruta del frontend redirige a Inicio. |
| **Delfos IA** (`IaChatController`) | 10 | El módulo figura **activo**, pero la ruta `/pages/delfos-ia` redirige a Inicio: el guard la rechaza. Ver §4. |
| **Mapa** (`MapaController`, `MapaDibujoController`) | 10 | Es una vista alternativa de los listados (`listar-mapa`), no una pantalla propia del menú. |

---

## 4. Hallazgos del recorrido

Cinco cosas que salieron al cruzar el código con la aplicación en vivo. Las tres primeras son problemas reales; las dos últimas, trampas de lectura del código.

### 4.1 `GET /compromiso/entregable` devuelve 403 con rol Administrador

Al expandir un compromiso en `/pages/gestion/commitment`, la petición `GET /compromiso/entregable?idcompromiso=143` responde **403 Forbidden** y los entregables **no se muestran**. El usuario es `admin`, rol Administrador, y el módulo Compromisos está activo. El 403 lo emite `profile-permit`, lo que apunta a que ese endpoint no está dado de alta en la tabla de permisos del rol (el resto de rutas del módulo, `listar` y `listar-init`, sí responden 200). Es la incidencia más visible del recorrido: **el módulo de entregables es inaccesible desde la interfaz**. Requiere revisar los permisos del rol para esa ruta.

### 4.2 Delfos IA está activo pero su ruta es inaccesible

En Configuración → Módulos, **IA aparece marcado**, y el ítem "Delfos IA" se muestra en el menú lateral. Sin embargo, al abrirlo (se abre en pestaña nueva) el guard redirige a `/pages/inicio`. Los 10 endpoints de `IaChatController` existen y están cableados en el frontend, pero la pantalla no es alcanzable con esta sesión. La pista está en el propio aviso de la pantalla de Módulos: *"Las modificaciones se verán reflejadas la próxima vez que los usuarios inicien sesión"* — el permiso viaja dentro del JWT (`modulos_permitidos`), así que conviene comprobar si el token emitido incluye el módulo de IA.

### 4.3 49 endpoints no los invoca ningún servicio del frontend

De las 544 rutas, **495 tienen un consumidor identificado** en Angular y **49 no**. Las causas, verificadas una a una:

| Grupo | Endpoints | Explicación |
|---|---|---|
| Exportación asíncrona | 18 (`*/exportar/iniciar`, `/{id}/status`, `/{id}/download`) | **Falso positivo**: se construyen dinámicamente en `exportacion-asincrona.adapter.ts` (`${config.basePath}/${exportId}/status`), por eso no aparecen como literales. Sí se usan. |
| Gráficos de dashboards | ~20 (`/reportes/*/grafico*`, `descripcion/*`, `compromisox/*`) | La pestaña *Dashboard* la sirve **Power BI**, no estos endpoints. Los servicios Angular sólo llaman a `init-dashboard`. **Son endpoints huérfanos de hecho.** |
| Catálogos y varios | ~11 (`/dropdown/moneda`, `/setup/general/modulo/listar`, `.../evaluacion/variable/listar`, `/predio/ver-codigo/{codigo}`…) | Sin consumidor. Algunos pertenecen a Predios (módulo apagado); otros son candidatos reales a limpieza. |

### 4.4 Tres controladores sin ninguna ruta (código muerto)

`Compromiso\EntregableProcesoController` y `Compromisox\CompromisoxProcesoController` existen en disco pero **ninguna ruta los apunta**: la línea de tiempo la sirven `EntregableController@entregableProceso` y `CompromisoxController@compromisoProceso`. (El tercero, `Controller`, es la clase base de Laravel.) Son candidatos a borrarse.

### 4.5 Dos trampas al leer las rutas

- **`listar` y `listar-mapa` comparten método.** En los siete módulos de gestión ambas rutas apuntan al *mismo* método del controlador; es la ruta, no el código, la que decide si se devuelve la geometría.
- **`/reportes/reclamo/descargar` no es del dashboard de reclamos.** Pese al prefijo, lo atiende `GeneradorArchivosController@solicitudDescargar`: es la descarga del generador de archivos.

---
# Anexo A — Las 544 rutas, una por una

Cada ruta con su **controlador**, **acción**, **servicio backend**, **servicio Angular** que la consume y la **vista** (pantalla) donde aparece. Las rutas marcadas *(sin consumo)* no son invocadas por ningún servicio del frontend.


### `Auth\AuthController` — 4 endpoints

**Servicios backend:** `AuthService`, `MailerService`, `GoogleOauthService`, `OauthService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/auth/init` | `init` | `LoginService` | Login |
| GET | `/auth/me` | `me` | `AuthSessionService` | Cualquiera (restaura sesion) |
| POST | `/auth/login` | `login` | `LoginService` | Login |
| POST | `/auth/oauth` | `oauth` | `OauthService` | Login |

### `Auth\RecoverController` — 2 endpoints

**Servicios backend:** `RecoverService`, `MailerService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| POST | `/recover` | `solicitar` | `RecoverService` | Recuperar contrasena |
| POST | `/recover/password` | `passwordCambiar` | `RecoverService` | Recuperar contrasena |

### `Boletin\BoletinController` — 2 endpoints

**Servicios backend:** `BoletinService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/boletin/init` | `boletinInit` | `BoletinService` | Boletin (al ingresar) |
| POST | `/boletin/visto` | `boletinVisto` | `BoletinService` | Boletin (al ingresar) |

### `Bug\BugController` — 8 endpoints

**Servicios backend:** `BugListarService`, `BugService`, `MailerService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/bug/archivo-exportar` | `bugArchivoExportar` | `BugSugerenciaService` | Soporte |
| GET | `/bug/crear-init` | `bugCrearInit` | `BugSugerenciaService` | Soporte |
| GET | `/bug/listar` | `bugListar` | `BugSugerenciaService` | Soporte |
| GET | `/bug/listar-init` | `bugListarInit` | `BugSugerenciaService` | Soporte |
| GET | `/bug/ver/{idbug}` | `bugVer` | `BugSugerenciaService` | Soporte |
| POST | `/bug/crear` | `bugCrear` | `BugSugerenciaService` | Soporte |
| POST | `/bug/editar` | `bugEditar` | `BugSugerenciaService` | Soporte |
| DELETE | `/bug/eliminar/{idbug}` | `bugEliminar` | `BugSugerenciaService` | Soporte |

### `Compromiso\CompromisoController` — 14 endpoints

**Servicios backend:** `CompromisoExportacionService`, `CompromisoListarService`, `CompromisoService`, `EntregableService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/archivo-exportar` | `compromisoArchivoExportar` | `CompromisoService` | Compromisos > Descarga |
| GET | `/compromiso/crear-init` | `compromisoCrearInit` | `CompromisoService` | Compromisos (listado) |
| GET | `/compromiso/exportar` | `compromisoExportar` | `CompromisoService` | Compromisos > Descarga |
| GET | `/compromiso/exportar/{exportId}/download` | `compromisoExportarDownload` | _(sin consumo)_ | Compromisos > Descarga |
| GET | `/compromiso/exportar/{exportId}/status` | `compromisoExportarStatus` | _(sin consumo)_ | Compromisos > Descarga |
| GET | `/compromiso/listar` | `compromisoListar` | `CompromisoService` | Compromisos (listado) |
| GET | `/compromiso/listar-init` | `compromisoListarInit` | `CompromisoService` | Compromisos (listado) |
| GET | `/compromiso/listar-mapa` | `compromisoListar` | `CompromisoService` | Compromisos (listado) |
| GET | `/compromiso/ver/{idcompromiso}` | `compromisoVer` | `CompromisoService` | Compromisos (listado) |
| POST | `/compromiso/crear` | `compromisoCrear` | `CompromisoService` | Compromisos (listado) |
| POST | `/compromiso/editar` | `compromisoEditar` | `CompromisoService` | Compromisos (listado) |
| POST | `/compromiso/exportar/iniciar` | `compromisoExportarIniciar` | _(sin consumo)_ | Compromisos > Descarga |
| POST | `/compromiso/qc` | `compromisoQc` | `CompromisoService` | Compromisos (listado) |
| DELETE | `/compromiso/eliminar/{idcompromiso}` | `compromisoEliminar` | `CompromisoService` | Compromisos (listado) |

### `Compromiso\EntregableAjusteController` — 4 endpoints

**Servicios backend:** `EntregableAjusteService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/ajuste/ver/{idajuste}` | `ajusteVer` | `EntregableAjusteService` | Entregable > Etapas |
| POST | `/compromiso/ajuste/crear` | `ajusteCrear` | `EntregableAjusteService` | Entregable > Etapas |
| POST | `/compromiso/ajuste/editar` | `ajusteEditar` | `EntregableAjusteService` | Entregable > Etapas |
| DELETE | `/compromiso/ajuste/eliminar/{idajuste}` | `ajusteEliminar` | `EntregableAjusteService` | Entregable > Etapas |

### `Compromiso\EntregableCanceladoController` — 4 endpoints

**Servicios backend:** `EntregableCanceladoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/cancelado/ver/{idcancelado}` | `canceladoVer` | `EntregableCanceladoService` | Entregable > Etapas |
| POST | `/compromiso/cancelado/crear` | `canceladoCrear` | `EntregableCanceladoService` | Entregable > Etapas |
| POST | `/compromiso/cancelado/editar` | `canceladoEditar` | `EntregableCanceladoService` | Entregable > Etapas |
| DELETE | `/compromiso/cancelado/eliminar/{idcancelado}` | `canceladoEliminar` | `EntregableCanceladoService` | Entregable > Etapas |

### `Compromiso\EntregableController` — 9 endpoints

**Servicios backend:** `CompromisoExportacionService`, `EntregableListarService`, `EntregableService`, `GeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/entregable` | `entregableCompromiso` | `CompromisoEntregableService` | Compromiso > Entregables |
| GET | `/compromiso/entregable/crear-init` | `entregableCrearInit` | `CompromisoEntregableService` | Compromiso > Entregables |
| GET | `/compromiso/entregable/exportar` | `entregableExportar` | `CompromisoEntregableService` | Compromiso > Entregables |
| GET | `/compromiso/entregable/listar` | `entregableListar` | `CompromisoEntregableService` | Compromiso > Entregables |
| GET | `/compromiso/entregable/proceso/{identregable}` | `entregableProceso` | `CompromisoEntregableService` | Compromiso > Entregables |
| GET | `/compromiso/entregable/ver/{identregable}` | `entregableVer` | `CompromisoEntregableService` | Compromiso > Entregables |
| POST | `/compromiso/entregable/crear` | `entregableCrear` | `CompromisoEntregableService` | Compromiso > Entregables |
| POST | `/compromiso/entregable/editar` | `entregableEditar` | `CompromisoEntregableService` | Compromiso > Entregables |
| DELETE | `/compromiso/entregable/eliminar/{identregable}` | `entregableEliminar` | `CompromisoEntregableService` | Compromiso > Entregables |

### `Compromiso\EntregableCumplimientoController` — 5 endpoints

**Servicios backend:** `EntregableCumplimientoService`, `GeneralService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/cumplimiento/crear-init` | `cumplimientoCrearInit` | `EntregableCumplimientoService` | Entregable > Etapas |
| GET | `/compromiso/cumplimiento/ver/{idcumplimiento}` | `cumplimientoVer` | `EntregableCumplimientoService` | Entregable > Etapas |
| POST | `/compromiso/cumplimiento/crear` | `cumplimientoCrear` | `EntregableCumplimientoService` | Entregable > Etapas |
| POST | `/compromiso/cumplimiento/editar` | `cumplimientoEditar` | `EntregableCumplimientoService` | Entregable > Etapas |
| DELETE | `/compromiso/cumplimiento/eliminar/{idcumplimiento}` | `cumplimientoEliminar` | `EntregableCumplimientoService` | Entregable > Etapas |

### `Compromiso\EntregableImplementacionController` — 4 endpoints

**Servicios backend:** `EntregableImplementacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromiso/implementacion/ver/{idimplementacion}` | `implementacionVer` | `EntregableImplementacionService` | Entregable > Etapas |
| POST | `/compromiso/implementacion/crear` | `implementacionCrear` | `EntregableImplementacionService` | Entregable > Etapas |
| POST | `/compromiso/implementacion/editar` | `implementacionEditar` | `EntregableImplementacionService` | Entregable > Etapas |
| DELETE | `/compromiso/implementacion/eliminar/{idimplementacion}` | `implementacionEliminar` | `EntregableImplementacionService` | Entregable > Etapas |

### `Compromisox\CompromisoxCancelarController` — 5 endpoints

**Servicios backend:** `CompromisoxCancelarService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromisox/cancelar/crear-init` | `cancelarCrearInit` | `CompromisoxCancelarService` | Compromisos (listado) |
| GET | `/compromisox/cancelar/ver/{idcancelar}` | `cancelarVer` | `CompromisoxCancelarService` | Compromisos (listado) |
| POST | `/compromisox/cancelar/crear` | `cancelarCrear` | `CompromisoxCancelarService` | Compromisos (listado) |
| POST | `/compromisox/cancelar/editar` | `cancelarEditar` | `CompromisoxCancelarService` | Compromisos (listado) |
| DELETE | `/compromisox/cancelar/eliminar/{idcancelar}` | `cancelarEliminar` | `CompromisoxCancelarService` | Compromisos (listado) |

### `Compromisox\CompromisoxCompletoController` — 5 endpoints

**Servicios backend:** `CompromisoxCompletoService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromisox/completo/crear-init` | `completoCrearInit` | `CompromisoxCompletoService` | Compromisos (listado) |
| GET | `/compromisox/completo/ver/{idcompleto}` | `completoVer` | `CompromisoxCompletoService` | Compromisos (listado) |
| POST | `/compromisox/completo/crear` | `completoCrear` | `CompromisoxCompletoService` | Compromisos (listado) |
| POST | `/compromisox/completo/editar` | `completoEditar` | `CompromisoxCompletoService` | Compromisos (listado) |
| DELETE | `/compromisox/completo/eliminar/{idcompleto}` | `completoEliminar` | `CompromisoxCompletoService` | Compromisos (listado) |

### `Compromisox\CompromisoxController` — 13 endpoints

**Servicios backend:** `CompromisoxExportacionService`, `CompromisoxListarService`, `CompromisoxService`, `MailerService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromisox/archivo-exportar` | `compromisoArchivoExportar` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/crear-init` | `compromisoCrearInit` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/exportar` | `compromisoExportar` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/informe` | `compromisoInforme` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/listar` | `compromisoListar` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/listar-init` | `compromisoListarInit` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/listar-mapa` | `compromisoListar` | _(sin consumo)_ | Compromisos (listado) |
| GET | `/compromisox/proceso/{idcompromisox}` | `compromisoProceso` | `CompromisoxService` | Compromisos (listado) |
| GET | `/compromisox/ver/{idcompromisox}` | `compromisoVer` | `CompromisoxService` | Compromisos (listado) |
| POST | `/compromisox/crear` | `compromisoCrear` | `CompromisoxService` | Compromisos (listado) |
| POST | `/compromisox/editar` | `compromisoEditar` | `CompromisoxService` | Compromisos (listado) |
| POST | `/compromisox/qc` | `compromisoQc` | `CompromisoxService` | Compromisos (listado) |
| DELETE | `/compromisox/eliminar/{idcompromisox}` | `compromisoEliminar` | `CompromisoxService` | Compromisos (listado) |

### `Compromisox\CompromisoxImplementarController` — 5 endpoints

**Servicios backend:** `CompromisoxImplementarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromisox/implementar/crear-init` | `implementarCrearInit` | `CompromisoxImplementarService` | Compromisos (listado) |
| GET | `/compromisox/implementar/ver/{idimplementar}` | `implementarVer` | `CompromisoxImplementarService` | Compromisos (listado) |
| POST | `/compromisox/implementar/crear` | `implementarCrear` | `CompromisoxImplementarService` | Compromisos (listado) |
| POST | `/compromisox/implementar/editar` | `implementarEditar` | `CompromisoxImplementarService` | Compromisos (listado) |
| DELETE | `/compromisox/implementar/eliminar/{idimplementar}` | `implementarEliminar` | `CompromisoxImplementarService` | Compromisos (listado) |

### `Compromisox\CompromisoxRedefinirController` — 5 endpoints

**Servicios backend:** `CompromisoxRedefinirService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/compromisox/redefinir/crear-init` | `redefinirCrearInit` | `CompromisoxRedefinirService` | Compromisos (listado) |
| GET | `/compromisox/redefinir/ver/{idredefinir}` | `redefinirVer` | `CompromisoxRedefinirService` | Compromisos (listado) |
| POST | `/compromisox/redefinir/crear` | `redefinirCrear` | `CompromisoxRedefinirService` | Compromisos (listado) |
| POST | `/compromisox/redefinir/editar` | `redefinirEditar` | `CompromisoxRedefinirService` | Compromisos (listado) |
| DELETE | `/compromisox/redefinir/eliminar/{idredefinir}` | `redefinirEliminar` | `CompromisoxRedefinirService` | Compromisos (listado) |

### `GeneradorArchivos\GeneradorArchivosController` — 2 endpoints

**Servicios backend:** `GeneradorArchivosService`, `GeneradorProcesadorService`, `MailerService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/reclamo/descargar` | `solicitudDescargar` | _(sin consumo)_ | Descarga generador de archivos |
| POST | `/generador-archivos/crear` | `solicitudCrear` | `GeneradorService` | Modal Opciones de Descarga |

### `General\GeneralController` — 3 endpoints

**Servicios backend:** `GeneralService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/general` | `busquedaGeneralDropdown` | `DropdownService` | Buscador global (barra superior) |
| GET | `/dropdown/moneda` | `monedaDropdown` | _(sin consumo)_ | Selector de moneda |
| GET | `/proyecto` | `nombreProyecto` | `SharedService` | Cabecera del proyecto |

### `IaChat\IaChatController` — 10 endpoints

**Servicios backend:** `IaChatService`, `InteraccionListarService`, `ReclamoListarService`, `PromptDelfosIaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/ia-chat/conversacion-listar` | `conversacionListar` | `AiService` | Delfos IA (no accesible) |
| GET | `/ia-chat/conversacion/detalle/{idia_conversacion?}` | `conversacionDetalle` | _(sin consumo)_ | Delfos IA (no accesible) |
| GET | `/ia-chat/pregunta` | `preguntaIaChat` | `AiService` | Delfos IA (no accesible) |
| GET | `/ia-chat/preguntas-frecuentes` | `preguntasFrecuentes` | `AiService` | Delfos IA (no accesible) |
| POST | `/ia-chat/crear-conversacion` | `crearConversacion` | `AiService` | Delfos IA (no accesible) |
| POST | `/ia-chat/crear-pregunta-frecuente` | `crearPreguntaFrecuente` | `AiService` | Delfos IA (no accesible) |
| POST | `/ia-chat/editar-conversacion-nombre` | `editarConversacionNombre` | `AiService` | Delfos IA (no accesible) |
| POST | `/ia-chat/editar-pregunta-frecuente` | `editarPreguntaFrecuente` | `AiService` | Delfos IA (no accesible) |
| DELETE | `/ia-chat/eliminar-conversacion/{idia_conversacion}` | `eliminarConversacion` | `AiService` | Delfos IA (no accesible) |
| DELETE | `/ia-chat/eliminar-pregunta-frecuente/{idia_pregunta_frecuente}` | `eliminarPreguntaFrecuente` | `AiService` | Delfos IA (no accesible) |

### `Importacion\ImportacionShController` — 4 endpoints

**Servicios backend:** `ImportacionService`, `ImportacionShService`, `TipoStakeholderService`, `UbigeoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/importacion/stakeholder/formato` | `formato` | `SetupImportarStakeholderService` | Config. > Importar Stakeholder |
| GET | `/importacion/stakeholder/guia` | `guia` | `SetupImportarStakeholderService` | Config. > Importar Stakeholder |
| POST | `/importacion/stakeholder/ejecutar` | `ejecutar` | `SetupImportarStakeholderService` | Config. > Importar Stakeholder |
| POST | `/importacion/stakeholder/verificar` | `verificar` | `SetupImportarStakeholderService` | Config. > Importar Stakeholder |

### `Interaccion\InteraccionComentarioController` — 5 endpoints

**Servicios backend:** `InteraccionComentarioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/interaccion/comentario/listar` | `comentarioListar` | `InteraccionComentarioService` | Interaccion > Comentarios |
| GET | `/interaccion/comentario/ver/{idinteraccion_comentario}` | `comentarioVer` | `InteraccionComentarioService` | Interaccion > Comentarios |
| POST | `/interaccion/comentario/crear` | `comentarioCrear` | `InteraccionComentarioService` | Interaccion > Comentarios |
| POST | `/interaccion/comentario/editar` | `comentarioEditar` | `InteraccionComentarioService` | Interaccion > Comentarios |
| DELETE | `/interaccion/comentario/eliminar/{idinteraccion_comentario}` | `comentarioEliminar` | `InteraccionComentarioService` | Interaccion > Comentarios |

### `Interaccion\InteraccionController` — 15 endpoints

**Servicios backend:** `AsyncExport`, `MailerService`, `InteraccionExportacionService`, `InteraccionListarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/interaccion/archivo-exportar` | `interaccionArchivoExportar` | `InteraccionService` | Interacciones > Descarga |
| GET | `/interaccion/crear-init` | `interaccionCrearInit` | `InteraccionService` | Interacciones > Nueva |
| GET | `/interaccion/exportar` | `interaccionExportar` | `InteraccionService` | Interacciones > Descarga |
| GET | `/interaccion/exportar/{exportId}/download` | `interaccionExportarDownload` | _(sin consumo)_ | Interacciones > Descarga |
| GET | `/interaccion/exportar/{exportId}/status` | `interaccionExportarStatus` | _(sin consumo)_ | Interacciones > Descarga |
| GET | `/interaccion/listar` | `interaccionListar` | `InteraccionService` | Interacciones (listado) |
| GET | `/interaccion/listar-init` | `interaccionListarInit` | `InteraccionService` | Interacciones (listado) |
| GET | `/interaccion/listar-mapa` | `interaccionListar` | `InteraccionService` | Interacciones (listado) |
| GET | `/interaccion/ver/{idinteraccion}` | `interaccionVer` | `InteraccionService` | Interacciones (listado) |
| POST | `/interaccion/crear` | `interaccionCrear` | `InteraccionService` | Interacciones > Nueva |
| POST | `/interaccion/editar` | `interaccionEditar` | `InteraccionService` | Interacciones (listado) |
| POST | `/interaccion/exportar/iniciar` | `interaccionExportarIniciar` | _(sin consumo)_ | Interacciones > Descarga |
| POST | `/interaccion/generar-crear-ia` | `interaccionGenerarCrearIa` | `InteraccionService` | Interacciones > Nueva |
| POST | `/interaccion/qc` | `interaccionQc` | `InteraccionService` | Interacciones (listado) |
| DELETE | `/interaccion/eliminar/{idinteraccion}` | `interaccionEliminar` | `InteraccionService` | Interacciones (listado) |

### `Mapa\MapaController` — 5 endpoints

**Servicios backend:** `InteraccionListarService`, `MapaConfigService`, `MapaFileService`, `MapaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/mapa/buscar-coord` | `mapaBuscarCoord` | `MapaService` | Vista de mapa (listados) |
| GET | `/mapa/buscar-direccion` | `mapaBuscarDireccion` | `MapaService` | Vista de mapa (listados) |
| GET | `/mapa/capa` | `mapaInit` | `MapaService` | Vista de mapa (listados) |
| GET | `/mapa/exportar-geo` | `mapaExportarGeo` | `MapaService` | Vista de mapa (listados) |
| GET | `/mapa/init` | `mapaInit` | `MapaService` | Vista de mapa (listados) |

### `Mapa\MapaDibujoController` — 5 endpoints

**Servicios backend:** `MapaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/mapa/dibujo/crear-init` | `dibujoCrearInit` | `MapaService` | Vista de mapa (listados) |
| GET | `/mapa/dibujo/ver` | `dibujoVer` | `MapaService` | Vista de mapa (listados) |
| POST | `/mapa/dibujo/crear` | `dibujoCrear` | `MapaService` | Vista de mapa (listados) |
| POST | `/mapa/dibujo/editar` | `dibujoEditar` | `MapaService` | Vista de mapa (listados) |
| DELETE | `/mapa/dibujo/eliminar/{idsh_shapefile_polygons}` | `dibujoEliminar` | `MapaService` | Vista de mapa (listados) |

### `Oauth\OauthController` — 3 endpoints

**Servicios backend:** `GoogleOauthService`, `OauthService`, `OauthUsuarioService`, `OutlookOauthService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/oauth/url` | `servicioUrl` | `OauthService` | Perfil > Conexiones |
| POST | `/oauth/conectar` | `servicioConectar` | `OauthService` | Perfil > Conexiones |
| DELETE | `/oauth/desconectar/{idconexion}` | `servicioDesconectar` | `OauthService` | Perfil > Conexiones |

### `Perfil\PerfilController` — 6 endpoints

**Servicios backend:** `OauthUsuarioService`, `PerfilService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/perfil` | `init` | `PerfilUsuarioService` | Perfil de usuario |
| GET | `/perfil/formulario-init` | `formularioInit` | `PerfilUsuarioService` | Perfil de usuario |
| POST | `/perfil/actualizar` | `actualizar` | `PerfilUsuarioService` | Perfil de usuario |
| POST | `/perfil/logout` | `logout` | `PerfilUsuarioService` | Perfil de usuario |
| POST | `/perfil/logout-all` | `logoutTodos` | `PerfilUsuarioService` | Perfil de usuario |
| POST | `/perfil/password-editar` | `passwordEditar` | `PerfilUsuarioService` | Perfil de usuario |

### `Perfil\PerfilNotificacionController` — 2 endpoints

**Servicios backend:** `PerfilNotificacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/perfil/notificaciones/init` | `init` | `PerfilNotificacionService` | Perfil > Notificaciones |
| POST | `/perfil/notificaciones/editar` | `editar` | `PerfilNotificacionService` | Perfil > Notificaciones |

### `Perfil\PerfilSesionController` — 1 endpoints

**Servicios backend:** `PerfilSesionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/perfil/sesion/listar` | `sesionListar` | `PerfilSesionService` | Perfil > Sesiones |

### `Predio\PredioCodigoController` — 3 endpoints

**Servicios backend:** `PredioCodigoService`, `PredioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/predio/codigo/listar` | `predioCodigoListar` | `PredioCodigoService` | Predios (modulo DESACTIVADO) |
| POST | `/predio/codigo/crear` | `predioCodigoCrear` | `PredioCodigoService` | Predios (modulo DESACTIVADO) |
| DELETE | `/predio/codigo/eliminar/{idcodigo}` | `predioCodigoEliminar` | `PredioCodigoService` | Predios (modulo DESACTIVADO) |

### `Predio\PredioController` — 13 endpoints

**Servicios backend:** `PerfilService`, `PredioExportacionService`, `PredioListarService`, `PredioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/predio` | `predioDropdown` | `DropdownService` | Selector de predio (modulo off) |
| GET | `/predio/crear-init` | `predioCrearInit` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/exportar` | `predioExportar` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/ficha/{idpredio}` | `predioFicha` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/listar` | `predioListar` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/listar-init` | `predioListarInit` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/listar-mapa` | `predioListar` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/stakeholders` | `predioStakeholders` | `PredioService` | Predios (modulo DESACTIVADO) |
| GET | `/predio/ver-codigo/{codigo}` | `predioVerCodigo` | _(sin consumo)_ | Predios (modulo DESACTIVADO) |
| GET | `/predio/ver/{idpredio}` | `predioVer` | `PredioService` | Predios (modulo DESACTIVADO) |
| POST | `/predio/crear` | `predioCrear` | `PredioService` | Predios (modulo DESACTIVADO) |
| POST | `/predio/editar` | `predioEditar` | `PredioService` | Predios (modulo DESACTIVADO) |
| DELETE | `/predio/eliminar/{idpredio}` | `predioEliminar` | `PredioService` | Predios (modulo DESACTIVADO) |

### `Predio\PredioStakeholderController` — 3 endpoints

**Servicios backend:** `StakeholderPredioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| POST | `/predio/stakeholder/crear` | `shPredioCrear` | `PredioStakeholderService` | Predios (modulo DESACTIVADO) |
| POST | `/predio/stakeholder/editar` | `shPredioEditar` | `PredioStakeholderService` | Predios (modulo DESACTIVADO) |
| DELETE | `/predio/stakeholder/eliminar/{idpersona_predio}` | `shPredioEliminar` | `PredioStakeholderService` | Predios (modulo DESACTIVADO) |

### `Reclamo\ReclamoApelacionController` — 4 endpoints

**Servicios backend:** `ReclamoApelacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/apelacion/ver/{idapelacion}` | `apelacionVer` | `ReclamoApelacionService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/apelacion/crear` | `apelacionCrear` | `ReclamoApelacionService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/apelacion/editar` | `apelacionEditar` | `ReclamoApelacionService` | Reclamo > Gestionar (ciclo) |
| DELETE | `/reclamo/apelacion/eliminar/{idapelacion}` | `apelacionEliminar` | `ReclamoApelacionService` | Reclamo > Gestionar (ciclo) |

### `Reclamo\ReclamoCerradoController` — 5 endpoints

**Servicios backend:** `ReclamoCerradoService`, `TipoReclamoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/cerrado/crear-init` | `cerradoCrearInit` | `ReclamoCerradoService` | Reclamo > Gestionar (ciclo) |
| GET | `/reclamo/cerrado/ver/{idcerrado}` | `cerradoVer` | `ReclamoCerradoService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/cerrado/crear` | `cerradoCrear` | `ReclamoCerradoService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/cerrado/editar` | `cerradoEditar` | `ReclamoCerradoService` | Reclamo > Gestionar (ciclo) |
| DELETE | `/reclamo/cerrado/eliminar/{idcerrado}` | `cerradoEliminar` | `ReclamoCerradoService`, `ReclamoService` | Reclamo > Gestionar (ciclo) |

### `Reclamo\ReclamoController` — 16 endpoints

**Servicios backend:** `AsyncExport`, `GeneralService`, `MailerService`, `PerfilService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/archivo-exportar` | `reclamoArchivoExportar` | `ReclamoService` | Reclamos > Descarga |
| GET | `/reclamo/crear-init` | `reclamoCrearInit` | `ReclamoService` | Reclamos (listado) |
| GET | `/reclamo/exportar` | `reclamoExportar` | `ReclamoService` | Reclamos > Descarga |
| GET | `/reclamo/exportar/{exportId}/download` | `reclamoExportarDownload` | _(sin consumo)_ | Reclamos > Descarga |
| GET | `/reclamo/exportar/{exportId}/status` | `reclamoExportarStatus` | _(sin consumo)_ | Reclamos > Descarga |
| GET | `/reclamo/informe` | `reclamoInforme` | `ReclamoService` | Reclamos > Descarga |
| GET | `/reclamo/listar` | `reclamoListar` | `ReclamoService` | Reclamos (listado) |
| GET | `/reclamo/listar-init` | `reclamoListarInit` | `ReclamoService` | Reclamos (listado) |
| GET | `/reclamo/listar-mapa` | `reclamoListar` | `ReclamoService` | Reclamos (listado) |
| GET | `/reclamo/proceso/{idreclamo}` | `reclamoProceso` | `ReclamoService` | Reclamos (listado) |
| GET | `/reclamo/ver/{idreclamo}` | `reclamoVer` | `ReclamoService` | Reclamos (listado) |
| POST | `/reclamo/crear` | `reclamoCrear` | `ReclamoService` | Reclamos (listado) |
| POST | `/reclamo/editar` | `reclamoEditar` | `ReclamoService` | Reclamos (listado) |
| POST | `/reclamo/exportar/iniciar` | `reclamoExportarIniciar` | _(sin consumo)_ | Reclamos > Descarga |
| POST | `/reclamo/qc` | `reclamoQc` | `ReclamoService` | Reclamos (listado) |
| DELETE | `/reclamo/eliminar/{idreclamo}` | `reclamoEliminar` | `ReclamoService` | Reclamos (listado) |

### `Reclamo\ReclamoEvaluacionController` — 4 endpoints

**Servicios backend:** `ReclamoEvaluacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/evaluacion/ver/{idevaluacion}` | `evaluacionVer` | `ReclamoEvaluacionService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/evaluacion/crear` | `evaluacionCrear` | `ReclamoEvaluacionService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/evaluacion/editar` | `evaluacionEditar` | `ReclamoEvaluacionService` | Reclamo > Gestionar (ciclo) |
| DELETE | `/reclamo/evaluacion/eliminar/{idevaluacion}` | `evaluacionEliminar` | `ReclamoEvaluacionService` | Reclamo > Gestionar (ciclo) |

### `Reclamo\ReclamoPropuestaController` — 4 endpoints

**Servicios backend:** `ReclamoPropuestaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/propuesta/ver/{idpropuesta}` | `propuestaVer` | `ReclamoPropuestaService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/propuesta/crear` | `propuestaCrear` | `ReclamoPropuestaService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/propuesta/editar` | `propuestaEditar` | `ReclamoPropuestaService` | Reclamo > Gestionar (ciclo) |
| DELETE | `/reclamo/propuesta/eliminar/{idpropuesta}` | `propuestaEliminar` | `ReclamoPropuestaService` | Reclamo > Gestionar (ciclo) |

### `Reclamo\ReclamoRespuestaController` — 5 endpoints

**Servicios backend:** `GeneralService`, `ReclamoService`, `ReclamoRespuestaService`, `SetupGeneralService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reclamo/respuesta/crear-init` | `respuestaCrearInit` | `ReclamoRespuestaService` | Reclamo > Gestionar (ciclo) |
| GET | `/reclamo/respuesta/ver/{idrespuesta}` | `respuestaVer` | `ReclamoRespuestaService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/respuesta/crear` | `respuestaCrear` | `ReclamoRespuestaService` | Reclamo > Gestionar (ciclo) |
| POST | `/reclamo/respuesta/editar` | `respuestaEditar` | `ReclamoRespuestaService` | Reclamo > Gestionar (ciclo) |
| DELETE | `/reclamo/respuesta/eliminar/{idrespuesta}` | `respuestaEliminar` | `ReclamoRespuestaService` | Reclamo > Gestionar (ciclo) |

### `Relacionista\RelacionistaController` — 1 endpoints

**Servicios backend:** `RelacionistaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/relacionista` | `relacionistaDropdown` | `DropdownService` | Selector de relacionista |

### `Reportes\DashboardCompromisoController` — 10 endpoints

**Servicios backend:** `CompromisoListarService`, `DashboardCompromisoService`, `TipoStakeholderService`, `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/compromiso/avance` | `graficoAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/categoria-avance` | `graficoCategoriaAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/evolucion` | `graficoEvolucion` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/exportar-avance` | `exportarAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/exportar-categoria-avance` | `exportarCategoriaAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/exportar-evolucion` | `exportarEvolucion` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/exportar-fuente-avance` | `exportarFuenteAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/fuente-avance` | `graficoFuenteAvance` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/init-dashboard` | `dashboardInit` | `DashboardCompromisoService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/ubigeo` | `graficoUbigeo` | `DashboardCompromisoService` | Reporte de Compromisos |

### `Reportes\DashboardCompromisoEntregableController` — 12 endpoints

**Servicios backend:** `EntregableListarService`, `DashboardCompromisoEntregableService`, `TipoStakeholderService`, `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/compromiso/entregable/avance` | `graficoAvance` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/categoria-vigencia` | `graficoCategoriaVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/evolucion` | `graficoEvolucion` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/exportar-avance` | `exportarAvance` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/exportar-categoria-vigencia` | `exportarCategoriaVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/exportar-evolucion` | `exportarEvolucion` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/exportar-fuente-vigencia` | `exportarFuenteVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/exportar-responsable-vigencia` | `exportarResponsableVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/fuente-vigencia` | `graficoFuenteVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/init-dashboard` | `dashboardInit` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/responsable-vigencia` | `graficoResponsableVigencia` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |
| GET | `/reportes/compromiso/entregable/ubigeo` | `graficoUbigeo` | `DashboardCompromisoEntregableService` | Reporte de Compromisos |

### `Reportes\DashboardCompromisoxController` — 6 endpoints

**Servicios backend:** `DashboardCompromisoxService`, `ReporteService`, `CategoriaCompromisoService`, `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/compromisox/abierto` | `graficoAbiertos` | _(sin consumo)_ | Reporte Compromisos externos |
| GET | `/reportes/compromisox/cerrado` | `graficoCerrados` | _(sin consumo)_ | Reporte Compromisos externos |
| GET | `/reportes/compromisox/dashboard` | `dashboard` | `DashboardCompromisoxService` | Reporte Compromisos externos |
| GET | `/reportes/compromisox/init-dashboard` | `dashboardInit` | `DashboardCompromisoxService` | Reporte Compromisos externos |
| GET | `/reportes/compromisox/nuevo` | `graficoNuevos` | _(sin consumo)_ | Reporte Compromisos externos |
| GET | `/reportes/compromisox/performance` | `dashboardPerformance` | _(sin consumo)_ | Reporte Compromisos externos |

### `Reportes\DashboardInicioController` — 1 endpoints

**Servicios backend:** `DashboardInicioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/inicio/init-dashboard` | `dashboardInit` | `InicioService` | Inicio |

### `Reportes\DashboardInteraccionController` — 18 endpoints

**Servicios backend:** `InteraccionListarService`, `DashboardInteraccionService`, `TipoStakeholderService`, `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/interaccion/canal-evolucion` | `graficoCanalEvolucion` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/evolucion` | `graficoEvolucion` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/exportar-canal-evolucion` | `exportarCanalEvolucion` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/exportar-evolucion` | `exportarEvolucion` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/exportar-prioridad` | `exportarPrioridad` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/exportar-relacionista` | `exportarRelacionistasActivos` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/exportar-tema` | `exportarTemas` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/init-dashboard` | `dashboardInit` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/organizacion-tipo` | `graficoOrganizacionTipo` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/prioridad` | `graficoPrioridad` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/relacionista` | `graficoRelacionistasActivos` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/stakeholder-categoria` | `dashboardStakeholderCategorias` | _(sin consumo)_ | Reporte de Interacciones |
| GET | `/reportes/interaccion/stakeholder-evaluado` | `graficoStakeholderEvaluado` | _(sin consumo)_ | Reporte de Interacciones |
| GET | `/reportes/interaccion/stakeholder-genero` | `graficoStakeholderGenero` | _(sin consumo)_ | Reporte de Interacciones |
| GET | `/reportes/interaccion/stakeholder-tipo` | `graficoStakeholderTipo` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/tema` | `graficoTemas` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/total` | `dashboardTotales` | `DashboardInteraccionService` | Reporte de Interacciones |
| GET | `/reportes/interaccion/ubigeo` | `graficoUbigeo` | `DashboardInteraccionService` | Reporte de Interacciones |

### `Reportes\DashboardReclamoController` — 11 endpoints

**Servicios backend:** `ReclamoListarService`, `DashboardReclamoService`, `TipoStakeholderService`, `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/reclamo/categoria-vigencia` | `graficoCategoriaVigencia` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/evolucion` | `graficoEvolucion` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/exportar-categoria-vigencia` | `exportarCategoriaVigencia` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/exportar-evolucion` | `exportarEvolucion` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/exportar-responsable-vigencia` | `exportarResponsableVigencia` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/init-dashboard` | `dashboardInit` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/responsable-vigencia` | `graficoResponsableVigencia` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/stakeholder-categoria` | `dashboardStakeholderCategorias` | _(sin consumo)_ | Reporte de Reclamos |
| GET | `/reportes/reclamo/stakeholder-evaluado` | `graficoStakeholderEvaluado` | _(sin consumo)_ | Reporte de Reclamos |
| GET | `/reportes/reclamo/total` | `dashboardTotales` | `DashboardReclamoService` | Reporte de Reclamos |
| GET | `/reportes/reclamo/ubigeo` | `graficoUbigeo` | `DashboardReclamoService` | Reporte de Reclamos |

### `Reportes\DashboardSolicitudController` — 11 endpoints

**Servicios backend:** `DashboardSolicitudService`, `TipoStakeholderService`, `UbigeoNivelService`, `SolicitudListarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/solicitud/categoria-vigencia` | `graficoCategoriaVigencia` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/evolucion` | `graficoEvolucion` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/exportar-categoria-vigencia` | `exportarCategoriaVigencia` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/exportar-evolucion` | `exportarEvolucion` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/exportar-responsable-vigencia` | `exportarResponsableVigencia` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/init-dashboard` | `dashboardInit` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/responsable-vigencia` | `graficoResponsableVigencia` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/stakeholder-categoria` | `dashboardStakeholderCategoria` | _(sin consumo)_ | Reporte de Solicitudes |
| GET | `/reportes/solicitud/stakeholder-evaluado` | `graficoStakeholderEvaluado` | _(sin consumo)_ | Reporte de Solicitudes |
| GET | `/reportes/solicitud/total` | `dashboardTotales` | `DashboardSolicitudService` | Reporte de Solicitudes |
| GET | `/reportes/solicitud/ubigeo` | `graficoUbigeo` | `DashboardSolicitudService` | Reporte de Solicitudes |

### `Reportes\DashboardStakeholderController` — 12 endpoints

**Servicios backend:** `DashboardStakeholderFiltradoService`, `DashboardStakeholderService`, `UbigeoNivelService`, `StakeholderListarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/stakeholder/evaluado` | `dashboardEvaluados` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/exportar-identificado` | `exportarIdentificados` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/exportar-organizacion` | `exportarOrganizacion` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/exportar-sexo` | `exportarSexo` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/exportar-tag` | `exportarTag` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/identificado` | `graficoIdentificados` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/init-dashboard` | `dashboardInit` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/organizacion` | `graficoOrganizacion` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/sexo` | `graficoSexo` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/tag` | `graficoTag` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/total` | `dashboardTotales` | `DashboardStakeholderService` | Reporte de Stakeholders |
| GET | `/reportes/stakeholder/ubigeo` | `graficoUbigeo` | `DashboardStakeholderService` | Reporte de Stakeholders |

### `Reportes\DashboardStakeholderDescripcionController` — 7 endpoints

**Servicios backend:** `DashboardStakeholderDescripcionService`, `UbigeoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/stakeholder/descripcion/etiqueta` | `dashboardEtiquetas` | _(sin consumo)_ | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/importancia` | `graficoPosicionImportancia` | _(sin consumo)_ | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/init-dashboard` | `descripcionDashboardInit` | `ReporteStakeholderDescripcionService` | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/poder-interes` | `graficoPoderInteres` | _(sin consumo)_ | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/relacionista` | `dashboardRelacionistas` | _(sin consumo)_ | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/total` | `dashboardTotales` | _(sin consumo)_ | Reporte Descripcion de SH |
| GET | `/reportes/stakeholder/descripcion/ubigeo` | `dashboardUbigeo` | _(sin consumo)_ | Reporte Descripcion de SH |

### `Reportes\DashboardStakeholderEvaluacionController` — 9 endpoints

**Servicios backend:** `DashboardStakeholderEvaluacionService`, `StakeholderListarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/stakeholder/evaluacion/exportar-matriz-dimensiones` | `exportarMatrizDimensiones` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/exportar-posicion` | `exportarPosicion` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/exportar-posicion-categoria` | `exportarPosicionCategoria` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/exportar-posicion-evolucion` | `exportarEvolucionPosicion` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/init-dashboard` | `dashboardInit` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/matriz-dimensiones` | `graficoMatrizDimensiones` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/posicion` | `graficoPosicion` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/posicion-categoria` | `graficoPosicionCategoria` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |
| GET | `/reportes/stakeholder/evaluacion/posicion-evolucion` | `graficoEvolucionPosicion` | `DashboardStakeholderEvaluacionService` | Reporte Stakeholders > Evaluaciones |

### `Reportes\ReporteController` — 2 endpoints

**Servicios backend:** `ReporteService`, `UbigeoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/reportes/init` | `init` | `ReporteGeneralService` | Reportes > pestana Dashboard (Power BI) |
| GET | `/reportes/power-bi` | `powerBiObtener` | `ReporteGeneralService` | Reportes > pestana Dashboard (Power BI) |

### `Setup\General\CompromisoEntregable\CategoriaCompromisoController` — 6 endpoints

**Servicios backend:** `CategoriaCompromisoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/compromiso-entregable/categoria-compromiso/listar` | `categoriaCompromisoListar` | `SetupCompromisoTipoService` | Config. > Compromisos |
| GET | `/setup/general/compromiso-entregable/categoria-compromiso/ver/{idcompromiso_categoria}` | `categoriaCompromisoVer` | `SetupCompromisoTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/categoria-compromiso/crear` | `categoriaCompromisoCrear` | `SetupCompromisoTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/categoria-compromiso/editar` | `categoriaCompromisoEditar` | `SetupCompromisoTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/categoria-compromiso/reordenar` | `categoriaCompromisoReordenar` | `SetupCompromisoTipoService` | Config. > Compromisos |
| DELETE | `/setup/general/compromiso-entregable/categoria-compromiso/eliminar/{idcompromiso_categoria}` | `categoriaCompromisoEliminar` | `SetupCompromisoTipoService` | Config. > Compromisos |

### `Setup\General\CompromisoEntregable\FuenteController` — 6 endpoints

**Servicios backend:** `FuenteService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/compromiso-entregable/fuente/listar` | `fuenteListar` | `SetupCompromisoFuenteService` | Config. > Compromisos |
| GET | `/setup/general/compromiso-entregable/fuente/ver/{idcompromiso_fuente}` | `fuenteVer` | `SetupCompromisoFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/fuente/crear` | `fuenteCrear` | `SetupCompromisoFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/fuente/editar` | `fuenteEditar` | `SetupCompromisoFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso-entregable/fuente/reordenar` | `fuenteReordenar` | `SetupCompromisoFuenteService` | Config. > Compromisos |
| DELETE | `/setup/general/compromiso-entregable/fuente/eliminar/{idcompromiso_fuente}` | `fuenteEliminar` | `SetupCompromisoFuenteService` | Config. > Compromisos |

### `Setup\General\Compromiso\CategoriaCompromisoController` — 6 endpoints

**Servicios backend:** `CategoriaCompromisoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/compromiso/categoria-compromiso/listar` | `categoriaCompromisoListar` | `SetupCompromisoxTipoService` | Config. > Compromisos |
| GET | `/setup/general/compromiso/categoria-compromiso/ver/{idcompromisox_categoriax}` | `categoriaCompromisoVer` | `SetupCompromisoxTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/categoria-compromiso/crear` | `categoriaCompromisoCrear` | `SetupCompromisoxTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/categoria-compromiso/editar` | `categoriaCompromisoEditar` | `SetupCompromisoxTipoService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/categoria-compromiso/reordenar` | `categoriaCompromisoReordenar` | `SetupCompromisoxTipoService` | Config. > Compromisos |
| DELETE | `/setup/general/compromiso/categoria-compromiso/eliminar/{idcompromisox_categoriax}` | `categoriaCompromisoEliminar` | `SetupCompromisoxTipoService` | Config. > Compromisos |

### `Setup\General\Compromiso\FuenteController` — 5 endpoints

**Servicios backend:** `FuenteService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/compromiso/fuente/listar` | `fuenteListar` | `SetupCompromisoxFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/fuente/crear` | `fuenteCrear` | `SetupCompromisoxFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/fuente/editar` | `fuenteEditar` | `SetupCompromisoxFuenteService` | Config. > Compromisos |
| POST | `/setup/general/compromiso/fuente/reordenar` | `fuenteReordenar` | `SetupCompromisoxFuenteService` | Config. > Compromisos |
| DELETE | `/setup/general/compromiso/fuente/eliminar/{idcompromisox_fuentex}` | `fuenteEliminar` | `SetupCompromisoxFuenteService` | Config. > Compromisos |

### `Setup\General\GeneralController` — 12 endpoints

**Servicios backend:** `MapaService`, `SetupGeneralArchivoCnfService`, `SetupGeneralService`, `SetupEvaluacionCategoriaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/archivo-configuracion` | `configuracionArchivoVer` | _(sin consumo)_ | Configuracion General |
| GET | `/setup/general/configuracion` | `configuracionListar` | `SharedService` | Configuracion General |
| GET | `/setup/general/feriado/listar` | `feriadoListar` | `SetupFechasService` | Config. > Fechas y Feriados |
| GET | `/setup/general/init` | `init` | `SetupGeneralService` | Configuracion General |
| POST | `/setup/general/archivo-configuracion/editar` | `configuracionArchivoEditar` | `SetupGeneralService` | Configuracion General |
| POST | `/setup/general/configuracion/editar` | `configuracionEditar` | `SetupGeneralService` | Configuracion General |
| POST | `/setup/general/feriado/crear` | `feriadoCrear` | `SetupFechasService` | Config. > Fechas y Feriados |
| POST | `/setup/general/feriado/editar` | `feriadoEditar` | `SetupFechasService` | Config. > Fechas y Feriados |
| POST | `/setup/general/logo-proyecto-editar` | `logoProyectoEditar` | `SetupGeneralService` | Configuracion General |
| POST | `/setup/general/nombre-proyecto-editar` | `nombreProyectoEditar` | `SetupGeneralService` | Configuracion General |
| POST | `/setup/general/rango-predeterminado-editar` | `rangoPredeterminadoEditar` | `SetupGeneralService` | Configuracion General |
| DELETE | `/setup/general/feriado/eliminar/{idferiado}` | `feriadoEliminar` | `SetupFechasService` | Config. > Fechas y Feriados |

### `Setup\General\Interaccion\DuracionController` — 6 endpoints

**Servicios backend:** `DuracionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/interaccion/duracion/listar` | `duracionListar` | `SetupInteraccionDuracionService` | Config. > Interacciones |
| GET | `/setup/general/interaccion/duracion/ver/{idduracion}` | `duracionVer` | `SetupInteraccionDuracionService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/duracion/crear` | `duracionCrear` | `SetupInteraccionDuracionService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/duracion/editar` | `duracionEditar` | `SetupInteraccionDuracionService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/duracion/reordenar` | `duracionReordenar` | `SetupInteraccionDuracionService` | Config. > Interacciones |
| DELETE | `/setup/general/interaccion/duracion/eliminar/{idduracion}` | `duracionEliminar` | `SetupInteraccionDuracionService` | Config. > Interacciones |

### `Setup\General\Interaccion\PrioridadController` — 6 endpoints

**Servicios backend:** `PrioridadService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/interaccion/prioridad/listar` | `prioridadListar` | `SetupInteraccionPrioridadService` | Config. > Interacciones |
| GET | `/setup/general/interaccion/prioridad/ver/{idprioridad}` | `prioridadVer` | `SetupInteraccionPrioridadService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/prioridad/crear` | `prioridadCrear` | `SetupInteraccionPrioridadService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/prioridad/editar` | `prioridadEditar` | `SetupInteraccionPrioridadService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/prioridad/reordenar` | `prioridadReordenar` | `SetupInteraccionPrioridadService` | Config. > Interacciones |
| DELETE | `/setup/general/interaccion/prioridad/eliminar/{idprioridad}` | `prioridadEliminar` | `SetupInteraccionPrioridadService` | Config. > Interacciones |

### `Setup\General\Interaccion\TipoInteraccionController` — 6 endpoints

**Servicios backend:** `TipoInteraccionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/interaccion/tipo-interaccion/listar` | `tipoInteraccionListar` | `SetupInteraccionCanalService` | Config. > Interacciones |
| GET | `/setup/general/interaccion/tipo-interaccion/ver/{idinteraccion_tipo}` | `tipoInteraccionVer` | `SetupInteraccionCanalService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/tipo-interaccion/crear` | `tipoInteraccionCrear` | `SetupInteraccionCanalService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/tipo-interaccion/editar` | `tipoInteraccionEditar` | `SetupInteraccionCanalService` | Config. > Interacciones |
| POST | `/setup/general/interaccion/tipo-interaccion/reordenar` | `tipoInteraccionReordenar` | `SetupInteraccionCanalService` | Config. > Interacciones |
| DELETE | `/setup/general/interaccion/tipo-interaccion/eliminar/{idinteraccion_tipo}` | `tipoInteraccionEliminar` | `SetupInteraccionCanalService` | Config. > Interacciones |

### `Setup\General\Mapa\MapaController` — 11 endpoints

**Servicios backend:** `MapaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/mapa-capa` | `capaDropdown` | `DropdownService` | Selector de capas del mapa |
| GET | `/setup/general/mapa/capa/listar` | `capaListar` | `SetupMapaCapaService` | Config. > Mapas |
| POST | `/setup/general/mapa/buscador-editar` | `mapaBuscadorEditar` | `SetupGeneralService` | Config. > Mapas |
| POST | `/setup/general/mapa/capa/crear` | `capaCrear` | `SetupMapaCapaService` | Config. > Mapas |
| POST | `/setup/general/mapa/capa/editar` | `capaEditar` | `SetupMapaCapaService` | Config. > Mapas |
| POST | `/setup/general/mapa/capa/reordenar` | `capaReordenar` | `SetupMapaCapaService` | Config. > Mapas |
| POST | `/setup/general/mapa/capa/toggle` | `capaToggle` | `SetupMapaCapaService` | Config. > Mapas |
| POST | `/setup/general/mapa/coordenada-editar` | `mapaCoordenadaEditar` | `SetupGeneralService` | Config. > Mapas |
| POST | `/setup/general/mapa/zoom-init` | `mapaZoomInitEditar` | `SetupGeneralService` | Config. > Mapas |
| POST | `/setup/general/mapa/zoom-snap` | `mapaZoomSnapEditar` | `SetupGeneralService` | Config. > Mapas |
| DELETE | `/setup/general/mapa/capa/eliminar/{idshapefile_metadata}` | `capaEliminar` | `SetupMapaCapaService` | Config. > Mapas |

### `Setup\General\ModuloController` — 2 endpoints

**Servicios backend:** `ModuloService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/modulo/listar` | `moduloListar` | _(sin consumo)_ | Config. > Modulos |
| POST | `/setup/general/modulo/editar` | `moduloEditar` | `SetupGeneralService` | Config. > Modulos |

### `Setup\General\Predio\CondicionPropiedadController` — 5 endpoints

**Servicios backend:** `CondicionPropiedadService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/predio/condicion-propiedad/listar` | `condicionPropiedadListar` | `SetupPredioCondicionPropiedadService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/condicion-propiedad/crear` | `condicionPropiedadCrear` | `SetupPredioCondicionPropiedadService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/condicion-propiedad/editar` | `condicionPropiedadEditar` | `SetupPredioCondicionPropiedadService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/condicion-propiedad/reordenar` | `condicionPropiedadReordenar` | `SetupPredioCondicionPropiedadService` | Config. > Predios (modulo off) |
| DELETE | `/setup/general/predio/condicion-propiedad/eliminar/{idcondicion}` | `condicionPropiedadEliminar` | `SetupPredioCondicionPropiedadService` | Config. > Predios (modulo off) |

### `Setup\General\Predio\ParentescoController` — 5 endpoints

**Servicios backend:** `ParentescoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/predio/parentesco/listar` | `parentescoListar` | `SetupPredioParentescoService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/parentesco/crear` | `parentescoCrear` | `SetupPredioParentescoService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/parentesco/editar` | `parentescoEditar` | `SetupPredioParentescoService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/parentesco/reordenar` | `parentescoReordenar` | `SetupPredioParentescoService` | Config. > Predios (modulo off) |
| DELETE | `/setup/general/predio/parentesco/eliminar/{idparentesco}` | `parentescoEliminar` | `SetupPredioParentescoService` | Config. > Predios (modulo off) |

### `Setup\General\Predio\UsoPredioController` — 5 endpoints

**Servicios backend:** `UsoPredioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/predio/uso-predio/listar` | `usoPredioListar` | `SetupPredioUsoPredioService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/uso-predio/crear` | `usoPredioCrear` | `SetupPredioUsoPredioService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/uso-predio/editar` | `usoPredioEditar` | `SetupPredioUsoPredioService` | Config. > Predios (modulo off) |
| POST | `/setup/general/predio/uso-predio/reordenar` | `usoPredioReordenar` | `SetupPredioUsoPredioService` | Config. > Predios (modulo off) |
| DELETE | `/setup/general/predio/uso-predio/eliminar/{iduso}` | `usoPredioEliminar` | `SetupPredioUsoPredioService` | Config. > Predios (modulo off) |

### `Setup\General\PromptDelfosIa\PromptDelfosIaController` — 7 endpoints

**Servicios backend:** `IaChatService`, `PromptDelfosIaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/delfos-ia/listar` | `promptListar` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |
| GET | `/setup/general/delfos-ia/modulos` | `obtenerModulos` | _(sin consumo)_ | Config. > Delfos IA (prompts) |
| GET | `/setup/general/delfos-ia/ver/{idprompt}` | `promptVersionVer` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |
| POST | `/setup/general/delfos-ia/activar/{idprompt_detalle}` | `activarVersion` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |
| POST | `/setup/general/delfos-ia/crear` | `promptVersionCrear` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |
| POST | `/setup/general/delfos-ia/editar` | `promptVersionEditar` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |
| DELETE | `/setup/general/delfos-ia/eliminar/{idprompt}` | `promptVersionEliminar` | `SetupDelfosIaService` | Config. > Delfos IA (prompts) |

### `Setup\General\Reclamo\ReclamoCanalController` — 5 endpoints

**Servicios backend:** `ReclamoCanalService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/reclamo/canal/listar` | `reclamoCanalListar` | `SetupReclamoCanalService` | Config. > Reclamos |
| POST | `/setup/general/reclamo/canal/crear` | `reclamoCanalCrear` | `SetupReclamoCanalService` | Config. > Reclamos |
| POST | `/setup/general/reclamo/canal/editar` | `reclamoCanalEditar` | `SetupReclamoCanalService` | Config. > Reclamos |
| POST | `/setup/general/reclamo/canal/reordenar` | `reclamoCanalReordenar` | `SetupReclamoCanalService` | Config. > Reclamos |
| DELETE | `/setup/general/reclamo/canal/eliminar/{idreclamo_canal}` | `reclamoCanalEliminar` | `SetupReclamoCanalService` | Config. > Reclamos |

### `Setup\General\Reclamo\TipoReclamoController` — 6 endpoints

**Servicios backend:** `TipoReclamoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/reclamo/tipo-reclamo/listar` | `tipoReclamoListar` | `SetupReclamoTipoService` | Config. > Reclamos |
| GET | `/setup/general/reclamo/tipo-reclamo/ver/{idreclamo_tipo}` | `tipoReclamoVer` | _(sin consumo)_ | Config. > Reclamos |
| POST | `/setup/general/reclamo/tipo-reclamo/crear` | `tipoReclamoCrear` | `SetupReclamoTipoService` | Config. > Reclamos |
| POST | `/setup/general/reclamo/tipo-reclamo/editar` | `tipoReclamoEditar` | `SetupReclamoTipoService` | Config. > Reclamos |
| POST | `/setup/general/reclamo/tipo-reclamo/reordenar` | `tipoReclamoReordenar` | `SetupReclamoTipoService` | Config. > Reclamos |
| DELETE | `/setup/general/reclamo/tipo-reclamo/eliminar/{idreclamo_tipo}` | `tipoReclamoEliminar` | `SetupReclamoTipoService` | Config. > Reclamos |

### `Setup\General\Solicitud\MonitoreoCanalController` — 6 endpoints

**Servicios backend:** `MonitoreoCanalService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/solicitud/canal/listar` | `monitoreoCanalListar` | `SetupSolicitudCanalService` | Config. > Solicitudes |
| GET | `/setup/general/solicitud/canal/ver/{idmonitoreo_canal}` | `monitoreoCanalVer` | _(sin consumo)_ | Config. > Solicitudes |
| POST | `/setup/general/solicitud/canal/crear` | `monitoreoCanalCrear` | `SetupSolicitudCanalService` | Config. > Solicitudes |
| POST | `/setup/general/solicitud/canal/editar` | `monitoreoCanalEditar` | `SetupSolicitudCanalService` | Config. > Solicitudes |
| POST | `/setup/general/solicitud/canal/reordenar` | `monitoreoCanalReordenar` | `SetupSolicitudCanalService` | Config. > Solicitudes |
| DELETE | `/setup/general/solicitud/canal/eliminar/{idmonitoreo_canal}` | `monitoreoCanalEliminar` | `SetupSolicitudCanalService` | Config. > Solicitudes |

### `Setup\General\Solicitud\TipoSolicitudController` — 6 endpoints

**Servicios backend:** `TipoSolicitudService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/solicitud/tipo-solicitud/listar` | `tipoSolicitudListar` | `SetupSolicitudTipoService` | Config. > Solicitudes |
| GET | `/setup/general/solicitud/tipo-solicitud/ver/{idmonitoreo_tipo}` | `tipoSolicitudVer` | `SetupSolicitudTipoService` | Config. > Solicitudes |
| POST | `/setup/general/solicitud/tipo-solicitud/crear` | `tipoSolicitudCrear` | `SetupSolicitudTipoService` | Config. > Solicitudes |
| POST | `/setup/general/solicitud/tipo-solicitud/editar` | `tipoSolicitudEditar` | `SetupSolicitudTipoService` | Config. > Solicitudes |
| POST | `/setup/general/solicitud/tipo-solicitud/reordenar` | `tipoSolicitudReordenar` | `SetupSolicitudTipoService` | Config. > Solicitudes |
| DELETE | `/setup/general/solicitud/tipo-solicitud/eliminar/{idmonitoreo_tipo}` | `tipoSolicitudEliminar` | `SetupSolicitudTipoService` | Config. > Solicitudes |

### `Setup\General\Stakeholder\SetupEvaluacionController` — 18 endpoints

**Servicios backend:** `SetupEvaluacionCategoriaService`, `SetupEvaluacionCategorizacionService`, `SetupEvaluacionVariablesService`, `StakeholderEvaluacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/stakeholder/evaluacion/categoria/crear-init` | `categoriaCrearInit` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/categoria/listar` | `categoriaListar` | _(sin consumo)_ | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/categoria/ver/{id}` | `categoriaVer` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/categorizacion/editar-init` | `categorizacionEditarInit` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/categorizacion/matriz` | `categorizacionVariables` | _(sin consumo)_ | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/init` | `setupInit` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/variable/crear-init` | `variableCrearInit` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/variable/listar` | `variableListar` | _(sin consumo)_ | Config. > Stakeholder > Evaluacion |
| GET | `/setup/general/stakeholder/evaluacion/variable/ver/{id}` | `variableVer` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/categoria/crear` | `categoriaCrear` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/categoria/editar` | `categoriaEditar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/categoria/reordenar` | `categoriaReordenar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/categorizacion/editar` | `categorizacionEditar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/categorizacion/variables` | `categorizacionVariables` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/variable/crear` | `variableCrear` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| POST | `/setup/general/stakeholder/evaluacion/variable/editar` | `variableEditar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| DELETE | `/setup/general/stakeholder/evaluacion/categoria/eliminar/{id}` | `categoriaEliminar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |
| DELETE | `/setup/general/stakeholder/evaluacion/variable/eliminar/{id}` | `variableEliminar` | `SetupStakeholderEvaluacionService` | Config. > Stakeholder > Evaluacion |

### `Setup\General\Stakeholder\StakeholderDuplicadosController` — 2 endpoints

**Servicios backend:** `StakeholderDuplicadosService`, `StakeholderListarService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/stakeholder/duplicados` | `stakeholderDuplicadosListar` | `StakeholderDuplicadosService` | Config. > Stakeholder > Duplicados |
| POST | `/setup/general/stakeholder/duplicados/excluir` | `stakeholderDuplicadosExcluir` | `StakeholderDuplicadosService` | Config. > Stakeholder > Duplicados |

### `Setup\General\Stakeholder\TipoOrganizacionController` — 6 endpoints

**Servicios backend:** `TipoOrganizacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/stakeholder/tipo-organizacion/listar` | `tipoOrganizacionListar` | `SetupTipoOrganizacionService` | Config. > Stakeholder |
| GET | `/setup/general/stakeholder/tipo-organizacion/ver/{idorganizacion_tipo}` | `tipoOrganizacionVer` | `SetupTipoOrganizacionService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/tipo-organizacion/crear` | `tipoOrganizacionCrear` | `SetupTipoOrganizacionService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/tipo-organizacion/editar` | `tipoOrganizacionEditar` | `SetupTipoOrganizacionService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/tipo-organizacion/reordenar` | `tipoOrganizacionReordenar` | `SetupTipoOrganizacionService` | Config. > Stakeholder |
| DELETE | `/setup/general/stakeholder/tipo-organizacion/eliminar/{idorganizacion_tipo}` | `tipoOrganizacionEliminar` | `SetupTipoOrganizacionService` | Config. > Stakeholder |

### `Setup\General\Stakeholder\TipoStakeholderController` — 4 endpoints

**Servicios backend:** `TipoStakeholderService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/stakeholder/tipo-sh/listar` | `tipoShListar` | `SetupTipoStakeholderService` | Config. > Stakeholder |
| GET | `/setup/general/stakeholder/tipo-sh/ver/{idpersona_tipo}` | `tipoShVer` | `SetupTipoStakeholderService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/tipo-sh/editar` | `tipoShEditar` | `SetupTipoStakeholderService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/tipo-sh/reordenar` | `tipoShReordenar` | `SetupTipoStakeholderService` | Config. > Stakeholder |

### `Setup\General\Stakeholder\UbigeoNivelController` — 3 endpoints

**Servicios backend:** `UbigeoNivelService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/general/stakeholder/ubigeo-nivel/listar` | `ubigeoNivelListar` | `SetupUbigeoNivelService` | Config. > Stakeholder |
| GET | `/setup/general/stakeholder/ubigeo-nivel/ver/{idnivel}` | `ubigeoNivelVer` | `SetupUbigeoNivelService` | Config. > Stakeholder |
| POST | `/setup/general/stakeholder/ubigeo-nivel/editar` | `ubigeoNivelEditar` | `SetupUbigeoNivelService` | Config. > Stakeholder |

### `Setup\TagController` — 8 endpoints

**Servicios backend:** `TagService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/tag` | `tagDropdown` | `DropdownService` | Selector de etiquetas (formularios) |
| GET | `/setup/tag/exportar` | `tagExportar` | `TagService` | Config. > Etiquetas |
| GET | `/setup/tag/listar` | `tagListar` | `TagService` | Config. > Etiquetas |
| GET | `/setup/tag/ver/{idtag}` | `tagVer` | `TagService` | Config. > Etiquetas |
| POST | `/setup/tag/crear` | `tagCrear` | `TagService` | Config. > Etiquetas |
| POST | `/setup/tag/editar` | `tagEditar` | `TagService` | Config. > Etiquetas |
| POST | `/setup/tag/merge` | `tagMerge` | `TagService` | Config. > Etiquetas |
| DELETE | `/setup/tag/eliminar/{idtag}` | `tagEliminar` | `TagService` | Config. > Etiquetas |

### `Setup\UbigeoController` — 10 endpoints

**Servicios backend:** `UbigeoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/ubigeo-general` | `ubigeoGeneralDropdown` | `DropdownService` | Selectores de ubigeo |
| GET | `/dropdown/ubigeo-hijos` | `ubigeoHijosDropdown` | `DropdownService` | Selectores de ubigeo |
| GET | `/dropdown/ubigeo-padres` | `ubigeoPadresDropdown` | `DropdownService` | Selectores de ubigeo |
| GET | `/dropdown/ubigeo-retrospectivo` | `ubigeoRetrospectivoDropdown` | `DropdownService` | Selectores de ubigeo |
| GET | `/setup/ubigeo/init` | `init` | `UbigeoService` | Config. > Locaciones (Ubigeo) |
| GET | `/setup/ubigeo/listar` | `ubigeoListar` | `UbigeoService` | Config. > Locaciones (Ubigeo) |
| GET | `/setup/ubigeo/ver/{idubigeo}` | `ubigeoVer` | `UbigeoService` | Config. > Locaciones (Ubigeo) |
| POST | `/setup/ubigeo/crear` | `ubigeoCrear` | `UbigeoService` | Config. > Locaciones (Ubigeo) |
| POST | `/setup/ubigeo/editar` | `ubigeoEditar` | `UbigeoService` | Config. > Locaciones (Ubigeo) |
| DELETE | `/setup/ubigeo/eliminar/{idubigeo}` | `ubigeoEliminar` | `UbigeoService` | Config. > Locaciones (Ubigeo) |

### `Setup\UsuarioController` — 7 endpoints

**Servicios backend:** `MailerService`, `SetupGeneralService`, `UsuarioService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/setup/usuario/listar` | `usuarioListar` | `UsuarioService` | Config. > Usuario |
| GET | `/setup/usuario/ver/{idusuario}` | `usuarioVer` | `UsuarioService` | Config. > Usuario |
| POST | `/setup/usuario/crear` | `usuarioCrear` | `UsuarioService` | Config. > Usuario |
| POST | `/setup/usuario/editar` | `usuarioEditar` | `UsuarioService` | Config. > Usuario |
| POST | `/setup/usuario/password-editar` | `passwordEditar` | `UsuarioService` | Config. > Usuario |
| POST | `/setup/usuario/rol-editar` | `usuariosRolEditar` | `UsuarioService` | Config. > Usuario |
| DELETE | `/setup/usuario/eliminar/{idusuario}` | `usuarioEliminar` | `UsuarioService` | Config. > Usuario |

### `Solicitud\SolicitudAprobadoController` — 5 endpoints

**Servicios backend:** `GeneralService`, `SetupGeneralService`, `SolicitudAprobadoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/aprobado/crear-init` | `aprobadoCrearInit` | `SolicitudAprobadoService` | Solicitud > Gestionar (ciclo) |
| GET | `/solicitud/aprobado/ver/{idaprobado}` | `aprobadoVer` | `SolicitudAprobadoService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/aprobado/crear` | `aprobadoCrear` | `SolicitudAprobadoService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/aprobado/editar` | `aprobadoEditar` | `SolicitudAprobadoService` | Solicitud > Gestionar (ciclo) |
| DELETE | `/solicitud/aprobado/eliminar/{idaprobado}` | `aprobadoEliminar` | `SolicitudAprobadoService` | Solicitud > Gestionar (ciclo) |

### `Solicitud\SolicitudCerradoController` — 5 endpoints

**Servicios backend:** `GeneralService`, `SetupGeneralService`, `TipoSolicitudService`, `SolicitudCerradoService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/cerrado/crear-init` | `cerradoCrearInit` | `SolicitudCerradoService` | Solicitud > Gestionar (ciclo) |
| GET | `/solicitud/cerrado/ver/{idcerrado}` | `cerradoVer` | `SolicitudCerradoService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/cerrado/crear` | `cerradoCrear` | `SolicitudCerradoService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/cerrado/editar` | `cerradoEditar` | `SolicitudCerradoService` | Solicitud > Gestionar (ciclo) |
| DELETE | `/solicitud/cerrado/eliminar/{idcerrado}` | `cerradoEliminar` | `SolicitudCerradoService` | Solicitud > Gestionar (ciclo) |

### `Solicitud\SolicitudController` — 16 endpoints

**Servicios backend:** `AsyncExport`, `GeneralService`, `MailerService`, `PerfilService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/archivo-exportar` | `solicitudArchivoExportar` | `SolicitudService` | Solicitudes > Descarga |
| GET | `/solicitud/crear-init` | `SolicitudCrearInit` | `SolicitudService` | Solicitudes (listado) |
| GET | `/solicitud/exportar` | `solicitudExportar` | `SolicitudService` | Solicitudes > Descarga |
| GET | `/solicitud/exportar/{exportId}/download` | `solicitudExportarDownload` | _(sin consumo)_ | Solicitudes > Descarga |
| GET | `/solicitud/exportar/{exportId}/status` | `solicitudExportarStatus` | _(sin consumo)_ | Solicitudes > Descarga |
| GET | `/solicitud/informe` | `solicitudInforme` | `SolicitudService` | Solicitudes > Descarga |
| GET | `/solicitud/listar` | `solicitudListar` | `SolicitudService` | Solicitudes (listado) |
| GET | `/solicitud/listar-init` | `solicitudListarInit` | `SolicitudService` | Solicitudes (listado) |
| GET | `/solicitud/listar-mapa` | `solicitudListar` | `SolicitudService` | Solicitudes (listado) |
| GET | `/solicitud/proceso/{idmonitoreo}` | `solicitudProceso` | `SolicitudService` | Solicitudes (listado) |
| GET | `/solicitud/ver/{idmonitoreo}` | `solicitudVer` | `SolicitudService` | Solicitudes (listado) |
| POST | `/solicitud/crear` | `solicitudCrear` | `SolicitudService` | Solicitudes (listado) |
| POST | `/solicitud/editar` | `solicitudEditar` | `SolicitudService` | Solicitudes (listado) |
| POST | `/solicitud/exportar/iniciar` | `solicitudExportarIniciar` | _(sin consumo)_ | Solicitudes > Descarga |
| POST | `/solicitud/qc` | `solicitudQc` | `SolicitudService` | Solicitudes (listado) |
| DELETE | `/solicitud/eliminar/{idmonitoreo}` | `solicitudEliminar` | `SolicitudService` | Solicitudes (listado) |

### `Solicitud\SolicitudEvaluacionController` — 4 endpoints

**Servicios backend:** `SolicitudEvaluacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/evaluacion/ver/{idevaluacion}` | `evaluacionVer` | `SolicitudEvaluacionService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/evaluacion/crear` | `evaluacionCrear` | `SolicitudEvaluacionService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/evaluacion/editar` | `evaluacionEditar` | `SolicitudEvaluacionService` | Solicitud > Gestionar (ciclo) |
| DELETE | `/solicitud/evaluacion/eliminar/{idevaluacion}` | `evaluacionEliminar` | `SolicitudEvaluacionService` | Solicitud > Gestionar (ciclo) |

### `Solicitud\SolicitudPropuestaController` — 4 endpoints

**Servicios backend:** `SolicitudPropuestaService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/propuesta/ver/{idpropuesta}` | `propuestaVer` | `SolicitudPropuestaService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/propuesta/crear` | `propuestaCrear` | `SolicitudPropuestaService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/propuesta/editar` | `propuestaEditar` | `SolicitudPropuestaService` | Solicitud > Gestionar (ciclo) |
| DELETE | `/solicitud/propuesta/eliminar/{idpropuesta}` | `propuestaEliminar` | `SolicitudPropuestaService` | Solicitud > Gestionar (ciclo) |

### `Solicitud\SolicitudRevisionController` — 4 endpoints

**Servicios backend:** `SolicitudRevisionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/solicitud/revision/ver/{idrevision}` | `revisionVer` | `SolicitudRevisionService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/revision/crear` | `revisionCrear` | `SolicitudRevisionService` | Solicitud > Gestionar (ciclo) |
| POST | `/solicitud/revision/editar` | `revisionEditar` | `SolicitudRevisionService` | Solicitud > Gestionar (ciclo) |
| DELETE | `/solicitud/revision/eliminar/{idrevision}` | `revisionEliminar` | `SolicitudRevisionService` | Solicitud > Gestionar (ciclo) |

### `Stakeholder\StakeholderController` — 21 endpoints

**Servicios backend:** `CompromisoListarService`, `CompromisoxListarService`, `AsyncExport`, `GeneradorProcesadorService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/dropdown/stakeholder` | `stakeholderDropdown` | `DropdownService` | Selector de stakeholder |
| GET | `/dropdown/stakeholder-natural` | `stakeholderNaturalDropdown` | _(sin consumo)_ | Selector de stakeholder |
| GET | `/dropdown/stakeholder-organizacion` | `stakeholderOrganizacionDropdown` | `DropdownService` | Selector de stakeholder |
| GET | `/stakeholder/crear-init` | `stakeholderCrearInit` | `StakeholderService` | Stakeholders > Nuevo |
| GET | `/stakeholder/exportar` | `stakeholderExportar` | `StakeholderService` | Stakeholders > Descarga |
| GET | `/stakeholder/exportar/{exportId}/download` | `stakeholderExportarDownload` | _(sin consumo)_ | Stakeholders > Descarga |
| GET | `/stakeholder/exportar/{exportId}/status` | `stakeholderExportarStatus` | _(sin consumo)_ | Stakeholders > Descarga |
| GET | `/stakeholder/ficha-mapa/{idsh}` | `stakeholderFichaMapa` | `StakeholderService` | Ficha de stakeholder |
| GET | `/stakeholder/ficha/{idsh}` | `stakeholderFicha` | `StakeholderService` | Ficha de stakeholder |
| GET | `/stakeholder/informe` | `stakeholderInforme` | `StakeholderService` | Stakeholders > Descarga |
| GET | `/stakeholder/listar` | `stakeholderListar` | `StakeholderService` | Stakeholders (listado) |
| GET | `/stakeholder/listar-init` | `stakeholderListarInit` | `StakeholderService` | Stakeholders (listado) |
| GET | `/stakeholder/listar-mapa` | `stakeholderListar` | `StakeholderService` | Stakeholders (listado) |
| GET | `/stakeholder/ver/{idsh}` | `stakeholderVer` | `StakeholderService` | Stakeholders (listado) |
| POST | `/stakeholder/crear` | `stakeholderCrear` | `StakeholderService` | Stakeholders > Nuevo |
| POST | `/stakeholder/documentos-adjuntos` | `stakeholderAdjuntos` | `StakeholderService` | Stakeholders (listado) |
| POST | `/stakeholder/editar` | `stakeholderEditar` | `StakeholderService` | Stakeholders (listado) |
| POST | `/stakeholder/editar-tags` | `stakeholderEditarTags` | `StakeholderService` | Stakeholders (listado) |
| POST | `/stakeholder/exportar/iniciar` | `stakeholderExportarIniciar` | _(sin consumo)_ | Stakeholders > Descarga |
| POST | `/stakeholder/merge` | `stakeholderMerge` | `StakeholderService` | Ficha > Combinar |
| DELETE | `/stakeholder/eliminar/{idsh}` | `stakeholderEliminar` | `StakeholderService` | Stakeholders (listado) |

### `Stakeholder\StakeholderEvaluacionController` — 9 endpoints

**Servicios backend:** `AsyncExport`, `PerfilService`, `StakeholderEvaluacionListarService`, `StakeholderEvaluacionService`

| Método | Ruta | Acción | Servicio Angular | Vista |
|---|---|---|---|---|
| GET | `/stakeholder/evaluacion` | `init` | `StakeholderEvaluacionService` | Ficha > Evaluacion |
| GET | `/stakeholder/evaluacion/exportar` | `evaluacionExportar` | `StakeholderEvaluacionService` | Ficha > Evaluacion |
| GET | `/stakeholder/evaluacion/exportar/{exportId}/download` | `evaluacionExportarDownload` | _(sin consumo)_ | Ficha > Evaluacion |
| GET | `/stakeholder/evaluacion/exportar/{exportId}/status` | `evaluacionExportarStatus` | _(sin consumo)_ | Ficha > Evaluacion |
| GET | `/stakeholder/evaluacion/listar` | `evaluacionListar` | `StakeholderEvaluacionService` | Ficha > Evaluacion |
| POST | `/stakeholder/evaluacion/crear` | `evaluacionCrear` | `StakeholderEvaluacionService` | Ficha > Evaluacion |
| POST | `/stakeholder/evaluacion/editar` | `evaluacionEditar` | `StakeholderEvaluacionService` | Ficha > Evaluacion |
| POST | `/stakeholder/evaluacion/exportar/iniciar` | `evaluacionExportarIniciar` | _(sin consumo)_ | Ficha > Evaluacion |
| DELETE | `/stakeholder/evaluacion/eliminar/{idsh_dimension}` | `evaluacionEliminar` | `StakeholderEvaluacionService` | Ficha > Evaluacion |


**Total: 544 endpoints en 82 controladores.**
