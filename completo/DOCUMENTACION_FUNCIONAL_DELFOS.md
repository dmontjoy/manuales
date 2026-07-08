# Documentación Funcional del Sistema Delfos

> **Propósito.** Este documento describe toda la funcionalidad del backend de Delfos tal como la exponen los controladores (endpoints de la API). Está pensado como base para redactar el manual de usuario/administrador.
>
> **Fuente.** Generado a partir del mapa de rutas real (`php artisan route:list`) cruzado con los 82 controladores del proyecto.
> **Alcance.** 82 controladores · 545 endpoints.
> **Backend.** Laravel 11 (`delfos-backend-laravel`). **Frontend.** Angular (`delfos-frontend`).
> **Fecha.** 07/07/2026.

---

## 1. Cómo leer este documento

Cada módulo se documenta con una tabla de endpoints:

| Columna | Significado |
|---|---|
| **Método** | Verbo HTTP: `GET` (consultar), `POST` (crear/editar/acciones), `DELETE` (eliminar). |
| **Ruta** | Path relativo a la base de la API. Los `{parámetro}` son valores en la URL (p. ej. `{idsh}` = id del stakeholder). |
| **Acción** | Método del controlador que atiende la ruta. |
| **Descripción** | Qué hace de cara al usuario. |

### 1.1 Convenciones de nombres (patrones que se repiten en todo el sistema)

Entender estos sufijos permite leer cualquier módulo sin explicación adicional:

| Patrón | Qué hace |
|---|---|
| `.../listar` | Lista **paginada y filtrable** de registros. |
| `.../listar-init` | Datos iniciales para la pantalla de listado (catálogos, filtros, opciones de dropdown). |
| `.../listar-mapa` | Igual que `listar`, pero preparado para la vista de **mapa** (incluye geometría/coordenadas). |
| `.../ver/{id}` | **Detalle** completo de un registro. |
| `.../crear` | **Crea** un registro nuevo. |
| `.../crear-init` | Datos iniciales para el **formulario de creación** (catálogos, valores por defecto). |
| `.../editar` | **Actualiza** un registro existente. |
| `.../eliminar/{id}` | **Elimina** (baja lógica, `activo = 0`) un registro. |
| `.../reordenar` | Cambia el **orden** de los ítems de un catálogo (drag & drop). |
| `.../exportar` | Exporta a archivo (Excel/PDF) de forma **síncrona**. |
| `.../exportar/iniciar` + `.../exportar/{exportId}/status` + `.../exportar/{exportId}/download` | Exportación **asíncrona** (para volúmenes grandes): se inicia un trabajo, se consulta su estado y se descarga al terminar. |
| `.../archivo-exportar` | Exporta los **archivos adjuntos** del módulo. |
| `.../proceso/{id}` | **Línea de tiempo / historial** de un registro (trazabilidad de estados). |
| `.../informe` | Genera un **informe** imprimible/consolidado. |
| `.../qc` | Marca de **control de calidad** (Quality Check) sobre un registro. |
| `.../ficha/{id}` | **Ficha** (hoja de resumen 360°) de una entidad. |
| `dropdown/...` | Devuelve listas ligeras para **selectores** de formularios. |

### 1.2 Seguridad y contexto (transversal a todos los módulos)

- **Autenticación.** Salvo el bloque de acceso (login, recuperación, URL de OAuth), **todos los endpoints exigen JWT** (cookie HttpOnly `token_delfos`). Cadena de middlewares: `jwt` → `profile-permit` (permiso del rol sobre el endpoint) → `accion-log` (registro de auditoría de la acción).
- **Multi-tenant.** Cada proyecto/comunidad es una **base de datos independiente**; la conexión se resuelve a partir del proyecto contenido en el JWT. Un usuario sólo ve/toca datos de su propio proyecto.
- **Autorización por registro.** En interacciones, reclamos, solicitudes y compromisos, un usuario con rol básico sólo puede editar/eliminar lo que él creó (o donde es relacionista asignado); administradores y supervisores no tienen esa restricción. En **stakeholders** el CRUD es compartido (admin/usuario/supervisor).
- **Rate limiting.** `login`, `oauth`, `recover` y `recover/password` tienen límites de peticiones. Login además con reCAPTCHA y bloqueo temporal por intentos fallidos.

---

## 2. Mapa de módulos

| # | Área funcional | Módulos incluidos |
|---|---|---|
| 3 | **Acceso y cuenta** | Autenticación, Recuperación de contraseña, OAuth, Perfil, Notificaciones, Sesiones |
| 4 | **Boletín** | Avisos/novedades |
| 5 | **Stakeholders** | Ficha 360°, evaluación, importación, duplicados |
| 6 | **Predios** | Predios, códigos, vínculo con stakeholders |
| 7 | **Interacciones** | Interacciones y comentarios |
| 8 | **Reclamos** | Reclamo y su ciclo (propuesta, respuesta, cerrado, evaluación, apelación) |
| 9 | **Solicitudes (Monitoreo)** | Solicitud y su ciclo (propuesta, revisión, aprobado, cerrado, evaluación) |
| 10 | **Compromisos** | Compromiso y entregables (cumplimiento, ajuste, cancelado, implementación) |
| 11 | **Compromisos externos (Compromisox)** | Compromisox y su ciclo |
| 12 | **Mapa (GIS)** | Mapa base, capas, dibujo |
| 13 | **Delfos IA** | Chat asistido por IA y preguntas frecuentes |
| 14 | **Reportes y Dashboards** | Tableros por módulo + Power BI |
| 15 | **Generador de archivos / Exportaciones** | Exportaciones asíncronas |
| 16 | **Generales y selectores** | Datos comunes y dropdowns |
| 17 | **Configuración (Setup)** | Catálogos, usuarios, tags, ubigeo, mapa, IA, evaluación |
| 18 | **Soporte (Bug)** | Reporte de incidencias |

---

## 3. Acceso y cuenta

### 3.1 Autenticación — `AuthController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/auth/init` | `init` | Datos iniciales de la pantalla de login (proyecto, textos, flags de configuración). Público. |
| POST | `/auth/login` | `login` | Inicia sesión con usuario/contraseña. Valida reCAPTCHA, aplica bloqueo por intentos, emite el JWT en cookie HttpOnly. |
| POST | `/auth/oauth` | `oauth` | Inicia sesión mediante proveedor externo (OAuth). |
| GET | `/auth/me` | `me` | Devuelve los datos del usuario autenticado (restaura sesión desde la cookie). |

### 3.2 Recuperación de contraseña — `RecoverController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| POST | `/recover` | `solicitar` | Solicita recuperación: envía por correo un token de un solo uso (expira en 15 min). Protegido con reCAPTCHA. |
| POST | `/recover/validar` | `validar` | Verifica que un token de recuperación sea válido antes de mostrar el formulario de cambio. |
| POST | `/recover/password` | `passwordCambiar` | Cambia la contraseña usando el token válido. |

### 3.3 Conexiones OAuth (calendario/correo) — `OauthController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/oauth/url` | `servicioUrl` | Devuelve la URL de autorización del proveedor (Google/Outlook). |
| POST | `/oauth/conectar` | `servicioConectar` | Vincula la cuenta externa al usuario (guarda tokens). |
| DELETE | `/oauth/desconectar/{idconexion}` | `servicioDesconectar` | Elimina una conexión OAuth existente. |

### 3.4 Perfil — `PerfilController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/perfil` | `init` | Datos del perfil del usuario actual. |
| GET | `/perfil/formulario-init` | `formularioInit` | Datos iniciales para editar el perfil. |
| POST | `/perfil/actualizar` | `actualizar` | Actualiza datos personales del perfil. |
| POST | `/perfil/password-editar` | `passwordEditar` | Cambia la contraseña del usuario autenticado. |
| POST | `/perfil/logout` | `logout` | Cierra la sesión actual (invalida el token). |
| POST | `/perfil/logout-all` | `logoutTodos` | Cierra todas las sesiones del usuario en todos los dispositivos. |

### 3.5 Notificaciones del perfil — `PerfilNotificacionController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/perfil/notificaciones/init` | `init` | Preferencias de notificación del usuario. |
| POST | `/perfil/notificaciones/editar` | `editar` | Actualiza las preferencias de notificación. |

### 3.6 Sesiones activas — `PerfilSesionController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/perfil/sesion/listar` | `sesionListar` | Lista las sesiones activas del usuario (dispositivos/últimos accesos). |

---

## 4. Boletín — `BoletinController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/boletin/init` | `boletinInit` | Obtiene el boletín/aviso vigente para mostrar al usuario. |
| POST | `/boletin/visto` | `boletinVisto` | Marca el boletín como visto por el usuario. |

---

## 5. Stakeholders

Entidad central del sistema: personas naturales y organizaciones con las que la empresa se relaciona.

### 5.1 Gestión de stakeholders — `StakeholderController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/stakeholder/listar` | `stakeholderListar` | Lista paginada y filtrable de stakeholders. |
| GET | `/stakeholder/listar-init` | `stakeholderListarInit` | Catálogos y filtros para el listado. |
| GET | `/stakeholder/listar-mapa` | `stakeholderListar` | Listado con geolocalización para vista de mapa. |
| GET | `/stakeholder/crear-init` | `stakeholderCrearInit` | Datos iniciales del formulario de alta (tipos, ubigeo, evaluación). |
| POST | `/stakeholder/crear` | `stakeholderCrear` | Crea un stakeholder (persona u organización). |
| POST | `/stakeholder/editar` | `stakeholderEditar` | Edita un stakeholder existente. |
| POST | `/stakeholder/editar-tags` | `stakeholderEditarTags` | Asigna/actualiza las etiquetas (tags) de un stakeholder. |
| DELETE | `/stakeholder/eliminar/{idsh}` | `stakeholderEliminar` | Elimina un stakeholder (baja lógica; valida que no tenga registros asociados). |
| GET | `/stakeholder/ver/{idsh}` | `stakeholderVer` | Detalle de un stakeholder. |
| GET | `/stakeholder/ficha/{idsh}` | `stakeholderFicha` | Ficha 360° (datos, historial, interacciones, evaluaciones). |
| GET | `/stakeholder/ficha-mapa/{idsh}` | `stakeholderFichaMapa` | Ficha con la ubicación geográfica del stakeholder. |
| POST | `/stakeholder/documentos-adjuntos` | `stakeholderAdjuntos` | Gestiona documentos adjuntos del stakeholder. |
| POST | `/stakeholder/merge` | `stakeholderMerge` | Fusiona dos stakeholders duplicados en uno. |
| GET | `/stakeholder/informe` | `stakeholderInforme` | Informe consolidado de stakeholders. |
| GET | `/stakeholder/exportar` | `stakeholderExportar` | Exporta el listado (síncrono). |
| POST | `/stakeholder/exportar/iniciar` | `stakeholderExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/stakeholder/exportar/{exportId}/status` | `stakeholderExportarStatus` | Consulta el estado de la exportación. |
| GET | `/stakeholder/exportar/{exportId}/download` | `stakeholderExportarDownload` | Descarga el archivo exportado. |
| GET | `/dropdown/stakeholder` | `stakeholderDropdown` | Selector de stakeholders (búsqueda). |
| GET | `/dropdown/stakeholder-natural` | `stakeholderNaturalDropdown` | Selector sólo de personas naturales. |
| GET | `/dropdown/stakeholder-organizacion` | `stakeholderOrganizacionDropdown` | Selector sólo de organizaciones. |

### 5.2 Evaluación de stakeholders — `StakeholderEvaluacionController`

Evaluación por dimensiones/categorías (p. ej. poder, interés, posición).

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/stakeholder/evaluacion` | `init` | Datos iniciales del módulo de evaluación. |
| GET | `/stakeholder/evaluacion/listar` | `evaluacionListar` | Lista de evaluaciones. |
| POST | `/stakeholder/evaluacion/crear` | `evaluacionCrear` | Registra una evaluación. |
| POST | `/stakeholder/evaluacion/editar` | `evaluacionEditar` | Edita una evaluación. |
| DELETE | `/stakeholder/evaluacion/eliminar/{idsh_dimension}` | `evaluacionEliminar` | Elimina una evaluación por dimensión. |
| GET | `/stakeholder/evaluacion/exportar` | `evaluacionExportar` | Exporta evaluaciones (síncrono). |
| POST | `/stakeholder/evaluacion/exportar/iniciar` | `evaluacionExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/stakeholder/evaluacion/exportar/{exportId}/status` | `evaluacionExportarStatus` | Estado de la exportación. |
| GET | `/stakeholder/evaluacion/exportar/{exportId}/download` | `evaluacionExportarDownload` | Descarga el archivo. |

### 5.3 Importación de stakeholders — `ImportacionShController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/importacion/stakeholder/guia` | `guia` | Guía/instrucciones de importación. |
| GET | `/importacion/stakeholder/formato` | `formato` | Descarga la plantilla (formato) de importación. |
| POST | `/importacion/stakeholder/verificar` | `verificar` | Valida el archivo cargado y previsualiza errores antes de importar. |
| POST | `/importacion/stakeholder/ejecutar` | `ejecutar` | Ejecuta la importación masiva de stakeholders. |

### 5.4 Relacionistas — `RelacionistaController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/dropdown/relacionista` | `relacionistaDropdown` | Selector de relacionistas (usuarios que gestionan la relación con el stakeholder). |

---

## 6. Predios

Parcelas/terrenos y su vínculo con stakeholders.

### 6.1 Predios — `PredioController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/predio/listar` | `predioListar` | Lista paginada y filtrable de predios. |
| GET | `/predio/listar-init` | `predioListarInit` | Catálogos y filtros del listado. |
| GET | `/predio/listar-mapa` | `predioListar` | Listado con geometría para el mapa. |
| GET | `/predio/crear-init` | `predioCrearInit` | Datos iniciales del formulario de alta. |
| POST | `/predio/crear` | `predioCrear` | Crea un predio. |
| POST | `/predio/editar` | `predioEditar` | Edita un predio. |
| DELETE | `/predio/eliminar/{idpredio}` | `predioEliminar` | Elimina un predio. |
| GET | `/predio/ver/{idpredio}` | `predioVer` | Detalle de un predio. |
| GET | `/predio/ver-codigo/{codigo}` | `predioVerCodigo` | Detalle de un predio por su código. |
| GET | `/predio/ficha/{idpredio}` | `predioFicha` | Ficha del predio. |
| GET | `/predio/stakeholders` | `predioStakeholders` | Stakeholders vinculados a predios. |
| GET | `/predio/exportar` | `predioExportar` | Exporta el listado de predios. |
| GET | `/dropdown/predio` | `predioDropdown` | Selector de predios. |

### 6.2 Códigos de predio — `PredioCodigoController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/predio/codigo/listar` | `predioCodigoListar` | Lista los códigos asociados a un predio. |
| POST | `/predio/codigo/crear` | `predioCodigoCrear` | Agrega un código a un predio. |
| DELETE | `/predio/codigo/eliminar/{idcodigo}` | `predioCodigoEliminar` | Elimina un código de predio. |

### 6.3 Stakeholders del predio — `PredioStakeholderController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| POST | `/predio/stakeholder/crear` | `shPredioCrear` | Vincula un stakeholder a un predio (con parentesco/condición). |
| POST | `/predio/stakeholder/editar` | `shPredioEditar` | Edita el vínculo stakeholder–predio. |
| DELETE | `/predio/stakeholder/eliminar/{idpersona_predio}` | `shPredioEliminar` | Elimina el vínculo stakeholder–predio. |

---

## 7. Interacciones

Registro de contactos/reuniones/comunicaciones con stakeholders.

### 7.1 Interacciones — `InteraccionController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/interaccion/listar` | `interaccionListar` | Lista paginada y filtrable de interacciones. |
| GET | `/interaccion/listar-init` | `interaccionListarInit` | Catálogos y filtros del listado. |
| GET | `/interaccion/listar-mapa` | `interaccionListar` | Listado para vista de mapa. |
| GET | `/interaccion/crear-init` | `interaccionCrearInit` | Datos iniciales del formulario de alta. |
| POST | `/interaccion/crear` | `interaccionCrear` | Crea una interacción. |
| POST | `/interaccion/editar` | `interaccionEditar` | Edita una interacción. |
| DELETE | `/interaccion/eliminar/{idinteraccion}` | `interaccionEliminar` | Elimina una interacción. |
| GET | `/interaccion/ver/{idinteraccion}` | `interaccionVer` | Detalle de una interacción. |
| POST | `/interaccion/generar-crear-ia` | `interaccionGenerarCrearIa` | Genera/crea una interacción asistida por IA (a partir de texto/insumos). |
| POST | `/interaccion/qc` | `interaccionQc` | Marca de control de calidad. |
| GET | `/interaccion/archivo-exportar` | `interaccionArchivoExportar` | Exporta los adjuntos. |
| GET | `/interaccion/exportar` | `interaccionExportar` | Exporta el listado (síncrono). |
| POST | `/interaccion/exportar/iniciar` | `interaccionExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/interaccion/exportar/{exportId}/status` | `interaccionExportarStatus` | Estado de la exportación. |
| GET | `/interaccion/exportar/{exportId}/download` | `interaccionExportarDownload` | Descarga el archivo. |

### 7.2 Comentarios de interacción — `InteraccionComentarioController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/interaccion/comentario/listar` | `comentarioListar` | Lista comentarios de una interacción. |
| POST | `/interaccion/comentario/crear` | `comentarioCrear` | Agrega un comentario. |
| POST | `/interaccion/comentario/editar` | `comentarioEditar` | Edita un comentario. |
| DELETE | `/interaccion/comentario/eliminar/{idinteraccion_comentario}` | `comentarioEliminar` | Elimina un comentario. |
| GET | `/interaccion/comentario/ver/{idinteraccion_comentario}` | `comentarioVer` | Detalle de un comentario. |

---

## 8. Reclamos

Gestión de reclamos/quejas de stakeholders y su ciclo de vida completo.

### 8.1 Reclamo — `ReclamoController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/reclamo/listar` | `reclamoListar` | Lista paginada y filtrable de reclamos. |
| GET | `/reclamo/listar-init` | `reclamoListarInit` | Catálogos y filtros del listado. |
| GET | `/reclamo/listar-mapa` | `reclamoListar` | Listado para vista de mapa. |
| GET | `/reclamo/crear-init` | `reclamoCrearInit` | Datos iniciales del formulario de alta. |
| POST | `/reclamo/crear` | `reclamoCrear` | Crea un reclamo. |
| POST | `/reclamo/editar` | `reclamoEditar` | Edita un reclamo. |
| DELETE | `/reclamo/eliminar/{idreclamo}` | `reclamoEliminar` | Elimina un reclamo. |
| GET | `/reclamo/ver/{idreclamo}` | `reclamoVer` | Detalle de un reclamo. |
| GET | `/reclamo/proceso/{idreclamo}` | `reclamoProceso` | Línea de tiempo del reclamo (cambios de estado). |
| GET | `/reclamo/informe` | `reclamoInforme` | Informe del reclamo. |
| POST | `/reclamo/qc` | `reclamoQc` | Marca de control de calidad. |
| GET | `/reclamo/archivo-exportar` | `reclamoArchivoExportar` | Exporta los adjuntos. |
| GET | `/reclamo/exportar` | `reclamoExportar` | Exporta el listado (síncrono). |
| POST | `/reclamo/exportar/iniciar` | `reclamoExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/reclamo/exportar/{exportId}/status` | `reclamoExportarStatus` | Estado de la exportación. |
| GET | `/reclamo/exportar/{exportId}/download` | `reclamoExportarDownload` | Descarga el archivo. |

### 8.2 Ciclo del reclamo (sub-módulos)

Cada sub-módulo representa una etapa del reclamo y comparte el patrón CRUD (`crear`, `editar`, `eliminar/{id}`, `ver/{id}`; algunos con `crear-init`).

**Propuesta** — `ReclamoPropuestaController` (`/reclamo/propuesta/...`): propuesta de solución al reclamo.
**Respuesta** — `ReclamoRespuestaController` (`/reclamo/respuesta/...`): respuesta formal al reclamante (incluye `crear-init`).
**Cerrado** — `ReclamoCerradoController` (`/reclamo/cerrado/...`): cierre del reclamo (incluye `crear-init`).
**Evaluación** — `ReclamoEvaluacionController` (`/reclamo/evaluacion/...`): evaluación del reclamo resuelto.
**Apelación** — `ReclamoApelacionController` (`/reclamo/apelacion/...`): apelación cuando el reclamante no acepta la respuesta.

| Sub-módulo | crear | editar | eliminar | ver | crear-init |
|---|:-:|:-:|:-:|:-:|:-:|
| Propuesta (`/reclamo/propuesta`) | ✔ | ✔ | ✔ `/{idpropuesta}` | ✔ | — |
| Respuesta (`/reclamo/respuesta`) | ✔ | ✔ | ✔ `/{idrespuesta}` | ✔ | ✔ |
| Cerrado (`/reclamo/cerrado`) | ✔ | ✔ | ✔ `/{idcerrado}` | ✔ | ✔ |
| Evaluación (`/reclamo/evaluacion`) | ✔ | ✔ | ✔ `/{idevaluacion}` | ✔ | — |
| Apelación (`/reclamo/apelacion`) | ✔ | ✔ | ✔ `/{idapelacion}` | ✔ | — |

---

## 9. Solicitudes (Monitoreo)

Gestión de solicitudes/requerimientos (internamente "monitoreo") y su ciclo de vida.

### 9.1 Solicitud — `SolicitudController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/solicitud/listar` | `solicitudListar` | Lista paginada y filtrable de solicitudes. |
| GET | `/solicitud/listar-init` | `solicitudListarInit` | Catálogos y filtros del listado. |
| GET | `/solicitud/listar-mapa` | `solicitudListar` | Listado para vista de mapa. |
| GET | `/solicitud/crear-init` | `SolicitudCrearInit` | Datos iniciales del formulario de alta. |
| POST | `/solicitud/crear` | `solicitudCrear` | Crea una solicitud. |
| POST | `/solicitud/editar` | `solicitudEditar` | Edita una solicitud. |
| DELETE | `/solicitud/eliminar/{idmonitoreo}` | `solicitudEliminar` | Elimina una solicitud. |
| GET | `/solicitud/ver/{idmonitoreo}` | `solicitudVer` | Detalle de una solicitud. |
| GET | `/solicitud/proceso/{idmonitoreo}` | `solicitudProceso` | Línea de tiempo de la solicitud. |
| GET | `/solicitud/informe` | `solicitudInforme` | Informe de la solicitud. |
| POST | `/solicitud/qc` | `solicitudQc` | Marca de control de calidad. |
| GET | `/solicitud/archivo-exportar` | `solicitudArchivoExportar` | Exporta los adjuntos. |
| GET | `/solicitud/exportar` | `solicitudExportar` | Exporta el listado (síncrono). |
| POST | `/solicitud/exportar/iniciar` | `solicitudExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/solicitud/exportar/{exportId}/status` | `solicitudExportarStatus` | Estado de la exportación. |
| GET | `/solicitud/exportar/{exportId}/download` | `solicitudExportarDownload` | Descarga el archivo. |

### 9.2 Ciclo de la solicitud (sub-módulos)

Mismo patrón CRUD por etapa:

**Propuesta** — `SolicitudPropuestaController` (`/solicitud/propuesta/...`).
**Revisión** — `SolicitudRevisionController` (`/solicitud/revision/...`).
**Aprobado** — `SolicitudAprobadoController` (`/solicitud/aprobado/...`, incluye `crear-init`).
**Cerrado** — `SolicitudCerradoController` (`/solicitud/cerrado/...`, incluye `crear-init`).
**Evaluación** — `SolicitudEvaluacionController` (`/solicitud/evaluacion/...`).

| Sub-módulo | crear | editar | eliminar | ver | crear-init |
|---|:-:|:-:|:-:|:-:|:-:|
| Propuesta (`/solicitud/propuesta`) | ✔ | ✔ | ✔ `/{idpropuesta}` | ✔ | — |
| Revisión (`/solicitud/revision`) | ✔ | ✔ | ✔ `/{idrevision}` | ✔ | — |
| Aprobado (`/solicitud/aprobado`) | ✔ | ✔ | ✔ `/{idaprobado}` | ✔ | ✔ |
| Cerrado (`/solicitud/cerrado`) | ✔ | ✔ | ✔ `/{idcerrado}` | ✔ | ✔ |
| Evaluación (`/solicitud/evaluacion`) | ✔ | ✔ | ✔ `/{idevaluacion}` | ✔ | — |

---

## 10. Compromisos

Compromisos adquiridos con stakeholders y sus entregables.

### 10.1 Compromiso — `CompromisoController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/compromiso/listar` | `compromisoListar` | Lista paginada y filtrable de compromisos. |
| GET | `/compromiso/listar-init` | `compromisoListarInit` | Catálogos y filtros del listado. |
| GET | `/compromiso/listar-mapa` | `compromisoListar` | Listado para vista de mapa. |
| GET | `/compromiso/crear-init` | `compromisoCrearInit` | Datos iniciales del formulario de alta. |
| POST | `/compromiso/crear` | `compromisoCrear` | Crea un compromiso. |
| POST | `/compromiso/editar` | `compromisoEditar` | Edita un compromiso. |
| DELETE | `/compromiso/eliminar/{idcompromiso}` | `compromisoEliminar` | Elimina un compromiso. |
| GET | `/compromiso/ver/{idcompromiso}` | `compromisoVer` | Detalle de un compromiso. |
| POST | `/compromiso/qc` | `compromisoQc` | Marca de control de calidad. |
| GET | `/compromiso/archivo-exportar` | `compromisoArchivoExportar` | Exporta los adjuntos. |
| GET | `/compromiso/exportar` | `compromisoExportar` | Exporta el listado (síncrono). |
| POST | `/compromiso/exportar/iniciar` | `compromisoExportarIniciar` | Inicia exportación asíncrona. |
| GET | `/compromiso/exportar/{exportId}/status` | `compromisoExportarStatus` | Estado de la exportación. |
| GET | `/compromiso/exportar/{exportId}/download` | `compromisoExportarDownload` | Descarga el archivo. |

### 10.2 Entregables del compromiso — `EntregableController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/compromiso/entregable` | `entregableCompromiso` | Entregables de un compromiso. |
| GET | `/compromiso/entregable/listar` | `entregableListar` | Lista de entregables. |
| GET | `/compromiso/entregable/crear-init` | `entregableCrearInit` | Datos iniciales del formulario. |
| POST | `/compromiso/entregable/crear` | `entregableCrear` | Crea un entregable. |
| POST | `/compromiso/entregable/editar` | `entregableEditar` | Edita un entregable. |
| DELETE | `/compromiso/entregable/eliminar/{identregable}` | `entregableEliminar` | Elimina un entregable. |
| GET | `/compromiso/entregable/ver/{identregable}` | `entregableVer` | Detalle de un entregable. |
| GET | `/compromiso/entregable/proceso/{identregable}` | `entregableProceso` | Línea de tiempo del entregable. |
| GET | `/compromiso/entregable/exportar` | `entregableExportar` | Exporta entregables. |

### 10.3 Etapas del entregable (sub-módulos)

Mismo patrón CRUD por etapa del entregable:

**Cumplimiento** — `EntregableCumplimientoController` (`/compromiso/cumplimiento/...`, incluye `crear-init`): registro de cumplimiento.
**Ajuste** — `EntregableAjusteController` (`/compromiso/ajuste/...`): ajustes al entregable.
**Cancelado** — `EntregableCanceladoController` (`/compromiso/cancelado/...`): cancelación.
**Implementación** — `EntregableImplementacionController` (`/compromiso/implementacion/...`): implementación.

| Etapa | crear | editar | eliminar | ver | crear-init |
|---|:-:|:-:|:-:|:-:|:-:|
| Cumplimiento (`/compromiso/cumplimiento`) | ✔ | ✔ | ✔ `/{idcumplimiento}` | ✔ | ✔ |
| Ajuste (`/compromiso/ajuste`) | ✔ | ✔ | ✔ `/{idajuste}` | ✔ | — |
| Cancelado (`/compromiso/cancelado`) | ✔ | ✔ | ✔ `/{idcancelado}` | ✔ | — |
| Implementación (`/compromiso/implementacion`) | ✔ | ✔ | ✔ `/{idimplementacion}` | ✔ | — |

---

## 11. Compromisos externos (Compromisox)

Variante de compromisos (compromisos "x") con su propio ciclo.

### 11.1 Compromisox — `CompromisoxController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/compromisox/listar` | `compromisoListar` | Lista paginada y filtrable. |
| GET | `/compromisox/listar-init` | `compromisoListarInit` | Catálogos y filtros. |
| GET | `/compromisox/listar-mapa` | `compromisoListar` | Listado para vista de mapa. |
| GET | `/compromisox/crear-init` | `compromisoCrearInit` | Datos iniciales del formulario. |
| POST | `/compromisox/crear` | `compromisoCrear` | Crea un compromisox. |
| POST | `/compromisox/editar` | `compromisoEditar` | Edita un compromisox. |
| DELETE | `/compromisox/eliminar/{idcompromisox}` | `compromisoEliminar` | Elimina un compromisox. |
| GET | `/compromisox/ver/{idcompromisox}` | `compromisoVer` | Detalle. |
| GET | `/compromisox/proceso/{idcompromisox}` | `compromisoProceso` | Línea de tiempo. |
| GET | `/compromisox/informe` | `compromisoInforme` | Informe. |
| POST | `/compromisox/qc` | `compromisoQc` | Control de calidad. |
| GET | `/compromisox/archivo-exportar` | `compromisoArchivoExportar` | Exporta adjuntos. |
| GET | `/compromisox/exportar` | `compromisoExportar` | Exporta el listado. |

### 11.2 Etapas del compromisox (sub-módulos)

**Implementar** — `CompromisoxImplementarController` (`/compromisox/implementar/...`, incluye `crear-init`).
**Completo** — `CompromisoxCompletoController` (`/compromisox/completo/...`, incluye `crear-init`).
**Redefinir** — `CompromisoxRedefinirController` (`/compromisox/redefinir/...`, incluye `crear-init`).
**Cancelar** — `CompromisoxCancelarController` (`/compromisox/cancelar/...`, incluye `crear-init`).

| Etapa | crear | editar | eliminar | ver | crear-init |
|---|:-:|:-:|:-:|:-:|:-:|
| Implementar (`/compromisox/implementar`) | ✔ | ✔ | ✔ `/{idimplementar}` | ✔ | ✔ |
| Completo (`/compromisox/completo`) | ✔ | ✔ | ✔ `/{idcompleto}` | ✔ | ✔ |
| Redefinir (`/compromisox/redefinir`) | ✔ | ✔ | ✔ `/{idredefinir}` | ✔ | ✔ |
| Cancelar (`/compromisox/cancelar`) | ✔ | ✔ | ✔ `/{idcancelar}` | ✔ | ✔ |

---

## 12. Mapa (GIS)

### 12.1 Mapa base — `MapaController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/mapa/init` | `mapaInit` | Inicializa el mapa (capas, zoom, configuración del proyecto). |
| GET | `/mapa/capa` | `mapaInit` | Carga las capas del mapa. |
| GET | `/mapa/buscar-direccion` | `mapaBuscarDireccion` | Geocodificación: busca coordenadas por dirección. |
| GET | `/mapa/buscar-coord` | `mapaBuscarCoord` | Geocodificación inversa: busca por coordenadas. |
| GET | `/mapa/exportar-geo` | `mapaExportarGeo` | Exporta información geográfica. |

### 12.2 Dibujo en el mapa — `MapaDibujoController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/mapa/dibujo/ver` | `dibujoVer` | Obtiene los dibujos/polígonos guardados. |
| GET | `/mapa/dibujo/crear-init` | `dibujoCrearInit` | Datos iniciales para dibujar. |
| POST | `/mapa/dibujo/crear` | `dibujoCrear` | Guarda un dibujo/polígono. |
| POST | `/mapa/dibujo/editar` | `dibujoEditar` | Edita un dibujo. |
| DELETE | `/mapa/dibujo/eliminar/{idsh_shapefile_polygons}` | `dibujoEliminar` | Elimina un polígono. |

---

## 13. Delfos IA — `IaChatController`

Asistente conversacional y preguntas frecuentes.

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/ia-chat/pregunta` | `preguntaIaChat` | Envía una pregunta al asistente IA y obtiene respuesta. |
| POST | `/ia-chat/crear-conversacion` | `crearConversacion` | Crea una conversación nueva. |
| GET | `/ia-chat/conversacion-listar` | `conversacionListar` | Lista las conversaciones del usuario. |
| GET | `/ia-chat/conversacion/detalle/{idia_conversacion?}` | `conversacionDetalle` | Detalle/mensajes de una conversación. |
| POST | `/ia-chat/editar-conversacion-nombre` | `editarConversacionNombre` | Renombra una conversación. |
| DELETE | `/ia-chat/eliminar-conversacion/{idia_conversacion}` | `eliminarConversacion` | Elimina una conversación. |
| GET | `/ia-chat/preguntas-frecuentes` | `preguntasFrecuentes` | Lista preguntas frecuentes. |
| POST | `/ia-chat/crear-pregunta-frecuente` | `crearPreguntaFrecuente` | Crea una pregunta frecuente. |
| POST | `/ia-chat/editar-pregunta-frecuente` | `editarPreguntaFrecuente` | Edita una pregunta frecuente. |
| DELETE | `/ia-chat/eliminar-pregunta-frecuente/{idia_pregunta_frecuente}` | `eliminarPreguntaFrecuente` | Elimina una pregunta frecuente. |

---

## 14. Reportes y Dashboards

Tableros analíticos por módulo. Cada dashboard sigue el patrón: `init-dashboard` (carga inicial), `total` (KPIs), varios `graficoXxx` (gráficos), y sus `exportar-Xxx` (exportar cada gráfico). Muchos incluyen `ubigeo` (distribución geográfica).

### 14.1 Inicio — `DashboardInicioController`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/reportes/inicio/init-dashboard` | Tablero de inicio (resumen general). |

### 14.2 Dashboard de Interacciones — `DashboardInteraccionController` (18 endpoints)
`init-dashboard`, `total`, y gráficos: `evolucion`, `canal-evolucion`, `prioridad`, `tema`, `relacionista`, `organizacion-tipo`, `ubigeo`, `stakeholder-tipo`, `stakeholder-genero`, `stakeholder-categoria`, `stakeholder-evaluado` — cada uno con su `exportar-...` correspondiente. Base: `/reportes/interaccion/...`.

### 14.3 Dashboard de Reclamos — `DashboardReclamoController` (11)
`init-dashboard`, `total`, gráficos `evolucion`, `categoria-vigencia`, `responsable-vigencia`, `stakeholder-categoria`, `stakeholder-evaluado`, `ubigeo` + exportaciones. Base: `/reportes/reclamo/...`.

### 14.4 Dashboard de Solicitudes — `DashboardSolicitudController` (11)
Igual estructura que reclamos. Base: `/reportes/solicitud/...`.

### 14.5 Dashboard de Compromisos — `DashboardCompromisoController` (10)
`init-dashboard`, gráficos `avance`, `categoria-avance`, `fuente-avance`, `evolucion`, `ubigeo` + exportaciones. Base: `/reportes/compromiso/...`.

### 14.6 Dashboard de Entregables de Compromiso — `DashboardCompromisoEntregableController` (12)
`init-dashboard`, gráficos `avance`, `categoria-vigencia`, `fuente-vigencia`, `responsable-vigencia`, `evolucion`, `ubigeo` + exportaciones. Base: `/reportes/compromiso/entregable/...`.

### 14.7 Dashboard de Compromisox — `DashboardCompromisoxController` (6)
`init-dashboard`, `dashboard`, `performance`, y gráficos `nuevo`, `abierto`, `cerrado`. Base: `/reportes/compromisox/...`.

### 14.8 Dashboard de Stakeholders — `DashboardStakeholderController` (12)
`init-dashboard`, `total`, gráficos `identificado`, `organizacion`, `sexo`, `tag`, `evaluado`, `ubigeo` + exportaciones. Base: `/reportes/stakeholder/...`.

### 14.9 Dashboard de Descripción de Stakeholders — `DashboardStakeholderDescripcionController` (7)
`init-dashboard`, `total`, gráficos `poder-interes`, `importancia`, `etiqueta`, `relacionista`, `ubigeo`. Base: `/reportes/stakeholder/descripcion/...`.

### 14.10 Dashboard de Evaluación de Stakeholders — `DashboardStakeholderEvaluacionController` (9)
`init-dashboard`, gráficos `posicion`, `posicion-categoria`, `posicion-evolucion`, `matriz-dimensiones` + exportaciones. Base: `/reportes/stakeholder/evaluacion/...`.

### 14.11 Reportes / Power BI — `ReporteController`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/reportes/init` | Inicializa el módulo de reportes. |
| GET | `/reportes/power-bi` | Obtiene la URL/token del reporte Power BI embebido (origen restringido a `app.powerbi.com`). |

---

## 15. Generador de archivos / Exportaciones — `GeneradorArchivosController`

Servicio central de exportaciones asíncronas usado por varios módulos.

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| POST | `/generador-archivos/crear` | `solicitudCrear` | Crea una solicitud de generación de archivo (encola el trabajo). |
| GET | `/generador-archivos/descargar` | `solicitudDescargar` | Descarga el archivo generado (protegido por JWT). |

---

## 16. Generales y selectores

### 16.1 General — `GeneralController`
| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/proyecto` | `nombreProyecto` | Nombre/datos del proyecto actual. |
| GET | `/dropdown/general` | `busquedaGeneralDropdown` | Búsqueda general (multi-entidad) para selectores. |
| GET | `/dropdown/moneda` | `monedaDropdown` | Selector de monedas. |

---

## 17. Configuración (Setup)

Módulo de administración: catálogos maestros, usuarios, permisos, ubigeo, mapa, IA y evaluación. Requiere rol con permisos de configuración.

### 17.1 Configuración general del proyecto — `Setup\General\GeneralController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/general/init` | `init` | Datos iniciales de configuración. |
| GET | `/setup/general/configuracion` | `configuracionListar` | Lista parámetros de configuración. |
| POST | `/setup/general/configuracion/editar` | `configuracionEditar` | Edita parámetros de configuración. |
| GET | `/setup/general/archivo-configuracion` | `configuracionArchivoVer` | Ve la configuración de archivos. |
| POST | `/setup/general/archivo-configuracion/editar` | `configuracionArchivoEditar` | Edita la configuración de archivos. |
| POST | `/setup/general/nombre-proyecto-editar` | `nombreProyectoEditar` | Cambia el nombre del proyecto. |
| POST | `/setup/general/logo-proyecto-editar` | `logoProyectoEditar` | Cambia el logo del proyecto. |
| POST | `/setup/general/rango-predeterminado-editar` | `rangoPredeterminadoEditar` | Configura el rango de fechas por defecto. |
| GET | `/setup/general/feriado/listar` | `feriadoListar` | Lista feriados (para cálculo de plazos). |
| POST | `/setup/general/feriado/crear` | `feriadoCrear` | Crea un feriado. |
| POST | `/setup/general/feriado/editar` | `feriadoEditar` | Edita un feriado. |
| DELETE | `/setup/general/feriado/eliminar/{idferiado}` | `feriadoEliminar` | Elimina un feriado. |

### 17.2 Usuarios y permisos — `Setup\UsuarioController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/usuario/listar` | `usuarioListar` | Lista los usuarios del proyecto. |
| POST | `/setup/usuario/crear` | `usuarioCrear` | Crea un usuario. |
| POST | `/setup/usuario/editar` | `usuarioEditar` | Edita un usuario. |
| DELETE | `/setup/usuario/eliminar/{idusuario}` | `usuarioEliminar` | Elimina un usuario. |
| GET | `/setup/usuario/ver/{idusuario}` | `usuarioVer` | Detalle de un usuario. |
| POST | `/setup/usuario/password-editar` | `passwordEditar` | Restablece la contraseña de un usuario. |
| POST | `/setup/usuario/rol-editar` | `usuariosRolEditar` | Cambia el rol/permisos de usuarios. |

### 17.3 Etiquetas (Tags) — `Setup\TagController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/tag/listar` | `tagListar` | Lista tags. |
| POST | `/setup/tag/crear` | `tagCrear` | Crea un tag. |
| POST | `/setup/tag/editar` | `tagEditar` | Edita un tag. |
| DELETE | `/setup/tag/eliminar/{idtag}` | `tagEliminar` | Elimina un tag. |
| GET | `/setup/tag/ver/{idtag}` | `tagVer` | Detalle de un tag. |
| POST | `/setup/tag/merge` | `tagMerge` | Fusiona dos tags. |
| GET | `/setup/tag/exportar` | `tagExportar` | Exporta los tags. |
| GET | `/dropdown/tag` | `tagDropdown` | Selector de tags. |

### 17.4 Ubigeo (división geográfica) — `Setup\UbigeoController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/ubigeo/init` | `init` | Datos iniciales del módulo ubigeo. |
| GET | `/setup/ubigeo/listar` | `ubigeoListar` | Lista los ubigeos (departamento/provincia/distrito…). |
| POST | `/setup/ubigeo/crear` | `ubigeoCrear` | Crea un ubigeo. |
| POST | `/setup/ubigeo/editar` | `ubigeoEditar` | Edita un ubigeo. |
| DELETE | `/setup/ubigeo/eliminar/{idubigeo}` | `ubigeoEliminar` | Elimina un ubigeo. |
| GET | `/setup/ubigeo/ver/{idubigeo}` | `ubigeoVer` | Detalle de un ubigeo. |
| GET | `/dropdown/ubigeo-general` | `ubigeoGeneralDropdown` | Selector general de ubigeo. |
| GET | `/dropdown/ubigeo-padres` | `ubigeoPadresDropdown` | Ubigeos padre (niveles superiores). |
| GET | `/dropdown/ubigeo-hijos` | `ubigeoHijosDropdown` | Ubigeos hijo (niveles inferiores). |
| GET | `/dropdown/ubigeo-retrospectivo` | `ubigeoRetrospectivoDropdown` | Cadena ascendente de ubigeo. |

### 17.5 Configuración del mapa — `Setup\General\Mapa\MapaController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/general/mapa/capa/listar` | `capaListar` | Lista las capas configuradas. |
| POST | `/setup/general/mapa/capa/crear` | `capaCrear` | Crea una capa (shapefile/metadata). |
| POST | `/setup/general/mapa/capa/editar` | `capaEditar` | Edita una capa. |
| DELETE | `/setup/general/mapa/capa/eliminar/{idshapefile_metadata}` | `capaEliminar` | Elimina una capa. |
| POST | `/setup/general/mapa/capa/reordenar` | `capaReordenar` | Reordena las capas. |
| POST | `/setup/general/mapa/capa/toggle` | `capaToggle` | Activa/desactiva una capa. |
| POST | `/setup/general/mapa/buscador-editar` | `mapaBuscadorEditar` | Configura el buscador del mapa. |
| POST | `/setup/general/mapa/coordenada-editar` | `mapaCoordenadaEditar` | Configura la coordenada central. |
| POST | `/setup/general/mapa/zoom-init` | `mapaZoomInitEditar` | Configura el zoom inicial. |
| POST | `/setup/general/mapa/zoom-snap` | `mapaZoomSnapEditar` | Configura el zoom-snap. |
| GET | `/dropdown/mapa-capa` | `capaDropdown` | Selector de capas. |

### 17.6 Módulos — `Setup\General\ModuloController`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/setup/general/modulo/listar` | Lista los módulos y su estado (activo/inactivo). |
| POST | `/setup/general/modulo/editar` | Activa/desactiva o configura módulos. |

### 17.7 Delfos IA (prompts) — `Setup\General\PromptDelfosIa\PromptDelfosIaController`

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/general/delfos-ia/listar` | `promptListar` | Lista los prompts de IA (cabeceras). |
| GET | `/setup/general/delfos-ia/ver/{idprompt}` | `promptVersionVer` | Ve un prompt y sus versiones. |
| POST | `/setup/general/delfos-ia/crear` | `promptVersionCrear` | Crea un prompt (con primera versión). |
| POST | `/setup/general/delfos-ia/editar` | `promptVersionEditar` | Edita/crea una nueva versión del prompt. |
| POST | `/setup/general/delfos-ia/activar/{idprompt_detalle}` | `activarVersion` | Activa una versión concreta del prompt. |
| DELETE | `/setup/general/delfos-ia/eliminar/{idprompt}` | `promptVersionEliminar` | Elimina un prompt. |
| GET | `/setup/general/delfos-ia/modulos` | `obtenerModulos` | Módulos disponibles para asociar prompts. |

### 17.8 Configuración de la evaluación de stakeholders — `Setup\General\Stakeholder\SetupEvaluacionController`

Define el modelo de evaluación: categorías, variables y su categorización/matriz.

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/setup/general/stakeholder/evaluacion/init` | `setupInit` | Datos iniciales del setup de evaluación. |
| GET | `.../categoria/listar` | `categoriaListar` | Lista categorías de evaluación. |
| GET | `.../categoria/crear-init` | `categoriaCrearInit` | Datos del formulario de categoría. |
| POST | `.../categoria/crear` | `categoriaCrear` | Crea una categoría. |
| POST | `.../categoria/editar` | `categoriaEditar` | Edita una categoría. |
| DELETE | `.../categoria/eliminar/{id}` | `categoriaEliminar` | Elimina una categoría. |
| GET | `.../categoria/ver/{id}` | `categoriaVer` | Detalle de categoría. |
| POST | `.../categoria/reordenar` | `categoriaReordenar` | Reordena categorías. |
| GET | `.../variable/listar` | `variableListar` | Lista variables de evaluación. |
| GET | `.../variable/crear-init` | `variableCrearInit` | Datos del formulario de variable. |
| POST | `.../variable/crear` | `variableCrear` | Crea una variable. |
| POST | `.../variable/editar` | `variableEditar` | Edita una variable. |
| DELETE | `.../variable/eliminar/{id}` | `variableEliminar` | Elimina una variable. |
| GET | `.../variable/ver/{id}` | `variableVer` | Detalle de variable. |
| GET | `.../categorizacion/editar-init` | `categorizacionEditarInit` | Datos para editar la categorización. |
| POST | `.../categorizacion/editar` | `categorizacionEditar` | Edita la categorización. |
| GET | `.../categorizacion/matriz` | `categorizacionVariables` | Matriz de categorización. |
| POST | `.../categorizacion/variables` | `categorizacionVariables` | Define las variables de la categorización. |

> Base común: `/setup/general/stakeholder/evaluacion/...`

### 17.9 Duplicados de stakeholders — `Setup\General\Stakeholder\StakeholderDuplicadosController`
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/setup/general/stakeholder/duplicados` | Lista posibles stakeholders duplicados. |
| POST | `/setup/general/stakeholder/duplicados/excluir` | Marca un par como "no duplicado" (excluir). |

### 17.10 Catálogos maestros por módulo (patrón CRUD estándar)

Estos catálogos alimentan los selectores de los módulos operativos. **Todos** comparten el patrón: `listar`, `crear`, `editar`, `eliminar/{id}`, `reordenar` y (la mayoría) `ver/{id}`.

| Catálogo | Controlador | Ruta base |
|---|---|---|
| Tipo de stakeholder | `TipoStakeholderController` | `/setup/general/stakeholder/tipo-sh` (editar/listar/ver/reordenar) |
| Tipo de organización | `TipoOrganizacionController` | `/setup/general/stakeholder/tipo-organizacion` |
| Nivel de ubigeo | `UbigeoNivelController` | `/setup/general/stakeholder/ubigeo-nivel` (editar/listar/ver) |
| Tipo de interacción | `TipoInteraccionController` | `/setup/general/interaccion/tipo-interaccion` |
| Prioridad de interacción | `PrioridadController` | `/setup/general/interaccion/prioridad` |
| Duración de interacción | `DuracionController` | `/setup/general/interaccion/duracion` |
| Tipo de reclamo | `TipoReclamoController` | `/setup/general/reclamo/tipo-reclamo` |
| Canal de reclamo | `ReclamoCanalController` | `/setup/general/reclamo/canal` |
| Tipo de solicitud | `TipoSolicitudController` | `/setup/general/solicitud/tipo-solicitud` |
| Canal de solicitud (monitoreo) | `MonitoreoCanalController` | `/setup/general/solicitud/canal` |
| Categoría de compromiso | `Compromiso\CategoriaCompromisoController` | `/setup/general/compromiso/categoria-compromiso` |
| Fuente de compromiso | `Compromiso\FuenteController` | `/setup/general/compromiso/fuente` |
| Categoría de entregable | `CompromisoEntregable\CategoriaCompromisoController` | `/setup/general/compromiso-entregable/categoria-compromiso` |
| Fuente de entregable | `CompromisoEntregable\FuenteController` | `/setup/general/compromiso-entregable/fuente` |
| Condición de propiedad (predio) | `CondicionPropiedadController` | `/setup/general/predio/condicion-propiedad` |
| Parentesco (predio) | `ParentescoController` | `/setup/general/predio/parentesco` |
| Uso de predio | `UsoPredioController` | `/setup/general/predio/uso-predio` |

> Ejemplo de operaciones para cualquiera de la tabla (tomando "tipo de reclamo"):
> `GET .../listar` · `POST .../crear` · `POST .../editar` · `DELETE .../eliminar/{id}` · `GET .../ver/{id}` · `POST .../reordenar`.

---

## 18. Soporte — `BugController`

Reporte y seguimiento de incidencias del sistema.

| Método | Ruta | Acción | Descripción |
|---|---|---|---|
| GET | `/bug/listar` | `bugListar` | Lista los bugs reportados. |
| GET | `/bug/listar-init` | `bugListarInit` | Catálogos y filtros del listado. |
| GET | `/bug/crear-init` | `bugCrearInit` | Datos iniciales del formulario (módulos, tipos). |
| POST | `/bug/crear` | `bugCrear` | Reporta un bug (con adjuntos validados). |
| POST | `/bug/editar` | `bugEditar` | Edita un bug. |
| DELETE | `/bug/eliminar/{idbug}` | `bugEliminar` | Elimina un bug. |
| GET | `/bug/ver/{idbug}` | `bugVer` | Detalle de un bug. |
| GET | `/bug/archivo-exportar` | `bugArchivoExportar` | Exporta los adjuntos de un bug. |

---

## Apéndice A. Resumen por controlador

| Área | Controladores | Endpoints aprox. |
|---|---|---|
| Acceso y cuenta | Auth, Recover, Oauth, Perfil, PerfilNotificacion, PerfilSesion | 19 |
| Boletín | Boletin | 2 |
| Stakeholders | Stakeholder, StakeholderEvaluacion, ImportacionSh, Relacionista | 38 |
| Predios | Predio, PredioCodigo, PredioStakeholder | 19 |
| Interacciones | Interaccion, InteraccionComentario | 20 |
| Reclamos | Reclamo + 5 sub-módulos | 38 |
| Solicitudes | Solicitud + 5 sub-módulos | 38 |
| Compromisos | Compromiso, Entregable + 4 etapas | 41 |
| Compromisox | Compromisox + 4 etapas | 33 |
| Mapa | Mapa, MapaDibujo | 10 |
| Delfos IA | IaChat | 10 |
| Reportes | 10 dashboards + Reporte | 99 |
| Exportaciones | GeneradorArchivos | 2 |
| Generales | General | 3 |
| Configuración (Setup) | ~30 controladores | 160+ |
| Soporte | Bug | 8 |
| **Total** | **82 controladores** | **545 endpoints** |

## Apéndice B. Notas para el manual

- **Pantallas "init".** Cada módulo tiene endpoints `...-init` que el frontend consume al abrir la pantalla; en el manual conviene documentarlos como "la pantalla carga sus catálogos/filtros" en lugar de como acciones del usuario.
- **Exportaciones grandes.** Donde exista el trío `exportar/iniciar` + `status` + `download`, el manual debe explicar el flujo asíncrono: el usuario inicia, ve una barra de progreso y descarga al finalizar.
- **Vista de mapa.** Los endpoints `listar-mapa` son la misma información que el listado pero para el modo mapa; conviene documentarlos juntos.
- **Roles.** Documentar qué roles ven el módulo de **Configuración (Setup)** y las acciones de **Usuarios** (alta/rol), que son de administrador.
- **Control de calidad (`qc`).** Explicar quién puede marcar QC y qué efecto tiene en los listados/reportes.
