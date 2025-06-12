from nicegui import ui
import aiofiles
import tempfile
import httpx
import json
import asyncio

BACKEND_URL = "http://backend:8010/consulta"
ANALYSIS_URL = "http://backend:8010/analizar_documento"
mensaje_task = None
mensajes = [
            "Procesando...",
            "Estamos buscando los mejores resultados ",
            "Prepárate para tu próxima carrera 🏃‍♂️",
            "Analizando eventos deportivos en tiempo real...",
        ]

async def cambiar_mensaje(label_mensaje):
    i = 0
    while True:
        label_mensaje.set_text(mensajes[i % len(mensajes)])
        i += 1
        await asyncio.sleep(3)

@ui.page('/')
async def main():
    with ui.tabs().classes('w-full') as tabs:
        pregunta_tab = ui.tab('Consulta eventos')
        analisis_tab = ui.tab('Analizar documento')

    with ui.tab_panels(tabs, value=pregunta_tab).classes('w-full'):
        with ui.tab_panel(pregunta_tab):
            await build_consulta_tab()

        with ui.tab_panel(analisis_tab):
            await build_document_analysis_tab()


async def build_consulta_tab():
    ui.label("Asistente LangGraph").classes("text-2xl mb-4")

    pregunta_input = ui.input("Escribe tu pregunta aquí").classes("w-full")
    respuesta_label = ui.label("").classes("mt-4 text-lg text-blue")

    spinner = ui.spinner(size="lg", color="blue-500").classes("mt-4 hidden")
    mensaje_cargando = ui.label("Procesando...").classes("mt-2 text-sm text-gray-500 hidden")

    eventos_container = ui.column().classes("mt-6 w-full")

    async def on_click():
        pregunta = pregunta_input.value
        if not pregunta:
            respuesta_label.set_text("Por favor ingrese una pregunta.")
            return

        spinner.classes(remove="hidden")
        mensaje_cargando.classes(remove="hidden")
        eventos_container.clear()
        respuesta_label.set_text("")

        
        global mensaje_task
        mensaje_task = asyncio.create_task(cambiar_mensaje(mensaje_cargando))

        try:
            async with httpx.AsyncClient(timeout=50.0) as client:
                r = await client.post(BACKEND_URL, json={"data": pregunta})
                r.raise_for_status()
                data = r.json()
                respuesta = data.get("respuesta", "")

                if isinstance(respuesta, str):
                    try:
                        respuesta = json.loads(respuesta)
                    except json.JSONDecodeError:
                        respuesta_label.set_text(respuesta)
                        return

                if isinstance(respuesta, dict) and respuesta.get("type") == "json":
                    eventos = respuesta.get("data", [])
                    if not eventos:
                        respuesta_label.set_text("No se encontraron eventos.")
                        return

                    for evento in eventos:
                        with ui.card().classes("w-full max-w-2xl mx-auto mb-6 shadow-md transition hover:shadow-lg cursor-pointer"
                        ).on("click", lambda e, url=evento.get("link", "#"): ui.run_javascript(f'window.open("{url}", "_blank")')):
                            ui.image(evento.get("imagen", "")).classes("w-full max-h-64 object-cover object-center rounded-t-xl")
                            ui.label(evento.get("titulo", "Sin título")).classes("text-xl font-bold mt-2")
                            ui.label(f'📅 {evento.get("fecha", "Fecha desconocida")}').classes("text-sm text-gray-500 mb-2")
                            ui.label(f'{evento.get("motivo", "")}').classes("text-sm text-gray-700 italic mb-2")
                else:
                    respuesta_label.set_text(str(respuesta))

        except Exception as e:
            respuesta_label.set_text(f"Error: {str(e)}")

        finally:
            spinner.classes(add="hidden")
            mensaje_cargando.classes(add="hidden")
            if mensaje_task:
                mensaje_task.cancel()

    ui.button("Enviar").on("click", on_click)


async def build_document_analysis_tab():
    ui.label("Análisis de documento").classes("text-2xl mb-4")
    resultado_label = ui.label("").classes("mt-2 text-green")   
    spinner = ui.spinner(size="lg", color="blue-500").classes("mt-4 hidden")
    mensaje_cargando = ui.label("Procesando...").classes("mt-2 text-sm text-gray-500 hidden")
    nombre = ui.input("Nombre").classes("w-full")
    apellido = ui.input("Apellido").classes("w-full")
    dni = ui.input("Nro dni").classes("w-full")
    nacimiento = ui.input("Fecha de nacimiento").classes("w-full")


    async def on_upload(e):
        
        spinner.classes(remove="hidden")
        mensaje_cargando.classes(remove="hidden")
        
        



        file_name = e.name
        file_spooled = e.content
        file_content = file_spooled.read()
        suffix = f".{file_name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(file_content)  # ya es binario
        try:
            # Enviar el archivo al backend como multipart/form-data
            files = {'file': (file_name, file_content, 'application/octet-stream')}
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(ANALYSIS_URL, files=files)
                response.raise_for_status()
                data = response.json()

                nombre.value = data.get("nombre", "")
                apellido.value = data.get("apellido", "")
                dni.value = data.get("nro_dni", "")
                nacimiento.value = data.get("nacimiento", "")
                resultado_label.set_text("Datos cargados correctamente.")

        except Exception as err:
            resultado_label.set_text(f"Error al procesar la imagen: {err}")
        finally:
            spinner.classes(add="hidden")
            mensaje_cargando.classes(add="hidden")
            if mensaje_task:
                mensaje_task.cancel()


    upload = ui.upload(label="Subir imagen", auto_upload=True).classes("mt-4")
    upload.on_upload(on_upload)

ui.run()