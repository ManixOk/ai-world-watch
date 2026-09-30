# AI World Watch

Reloj público que muestra cuánto control humano tenemos sobre la inteligencia artificial.
Se alimenta solo de fuentes oficiales, y cada señal la aprueba una persona antes de publicarse.

## Cómo funciona

1. **Todos los días a las 7:00 (hora de Ciudad de México)** una IA busca noticias, pero solo en sitios oficiales (laboratorios, gobiernos, investigadores). La lista está en `scripts/config.py`.
2. Cada hallazgo se convierte en un **candidato**: una ficha en la pestaña *Issues* de GitHub. Nada se publica todavía.
3. **Una persona revisa**: abre la fuente, confirma que dice eso y le pone la etiqueta `aprobado` (o `rechazado`).
4. Al aprobar, el reloj se actualiza solo en uno o dos minutos.

**Regla de la zona:** es el nivel más alto entre las señales aprobadas que suman riesgo en los últimos 90 días. Si pasan 90 días sin señales graves, la aguja baja.

**Filtros contra errores:** se descartan automáticamente las noticias de sitios no oficiales, las repetidas y los enlaces que la IA no haya visto realmente en su búsqueda.

## Puesta en marcha (una sola vez, unos 20 minutos)

1. Creá una cuenta en github.com si no tenés.
2. Creá un repositorio nuevo **público** llamado `ai-world-watch`.
3. Subí todos estos archivos (botón *Add file > Upload files*). La carpeta `.github` es importante: si tu computadora la oculta, subila desde la terminal o pedí ayuda.
4. Conseguí una clave de API en console.anthropic.com (*API Keys*). Se paga por uso.
5. En el repositorio: *Settings > Secrets and variables > Actions > New repository secret*. Nombre: `ANTHROPIC_API_KEY`, valor: tu clave.
6. En *Settings > Actions > General*, en *Workflow permissions*, elegí **Read and write permissions** y guardá.
7. En *Settings > Pages*, en *Source* elegí **Deploy from a branch**, rama `main`, carpeta `/ (root)`. Guardá.
8. En la pestaña *Actions*, abrí **Actualizar reloj** y tocá **Run workflow** para la primera búsqueda.

Tu reloj queda en `https://TU-USUARIO.github.io/ai-world-watch/`.

## Revisar señales desde el teléfono

Instalá la app de GitHub, entrá al repositorio y abrí *Issues*. Cada candidato trae el enlace a la fuente y los pasos para revisarlo. Podés corregir el título o el nivel editando el bloque de datos antes de aprobar.

## Ajustes

- **Modelo de Claude:** por defecto `claude-sonnet-5-5`. Para cambiarlo, creá una variable `MODELO` en *Settings > Secrets and variables > Actions > Variables*.
- **Fuentes permitidas y ventana de 90 días:** en `scripts/config.py`.
- **Costo:** depende de cuántas búsquedas haga por día (máximo 8 por corrida). Revisá los precios vigentes en la consola de Anthropic.
