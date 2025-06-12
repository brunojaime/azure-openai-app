from nicegui import ui
import httpx

BACKEND_URL = "http://backend:8010/consulta"

@ui.page('/')
async def main():
    ui.label("Asistente LangGraph").classes("text-2xl mb-4")

    pregunta_input = ui.input("Escribe tu pregunta aquí").classes("w-full")
    respuesta_label = ui.label("").classes("mt-4 text-lg text-blue")

    # Spinner oculto por defecto
    spinner = ui.spinner(size="lg", color="blue-500").classes("mt-4 hidden")
    mensaje_cargando = ui.label("Procesando...").classes("mt-2 text-sm text-gray-500 hidden")

    async def on_click():
        pregunta = pregunta_input.value
        if not pregunta:
            respuesta_label.set_text("Por favor ingrese una pregunta.")
            return

        # Mostrar spinner y mensaje
        spinner.classes(remove="hidden")
        mensaje_cargando.classes(remove="hidden")

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(BACKEND_URL, json={"data": pregunta})
                r.raise_for_status()
                data = r.json()
                respuesta_label.set_text(data.get("respuesta", "Sin respuesta"))
        except Exception as e:
            respuesta_label.set_text(f"Error: {str(e)}")
        finally:
            # Ocultar spinner y mensaje
            spinner.classes(add="hidden")
            mensaje_cargando.classes(add="hidden")

    ui.button("Enviar").on("click", on_click)

ui.run()
