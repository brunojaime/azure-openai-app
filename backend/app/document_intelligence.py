from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import os
import base64

# ⚠️ Usa variables de entorno en producción
endpoint = os.getenv("DOC_INTELLIGENCE_ENDPOINT")
key = os.getenv("DOC_INTELLIGENCE_API")

client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))


def analizar_documento_azure(local_path: str) -> dict:
    with open(local_path, "rb") as f:
        contenido = f.read()
    poller = client.begin_analyze_document(
        "prebuilt-idDocument",
        contenido,
        content_type="application/octet-stream"
    )

    result = poller.result()

    doc = result.documents[0]

    def safe_get(field, expected_type="string"):
        f = doc.fields.get(field)
        if not f:
            return None
        if expected_type == "date":
            return f.value_date if hasattr(f, "value_date") else f.content
        return f.value_string if hasattr(f, "value_string") else f.content
    print(doc)
    nacimiento_val = safe_get("DateOfBirth", expected_type="date")
    if nacimiento_val and hasattr(nacimiento_val, "isoformat"):
        nacimiento_val = nacimiento_val.isoformat()

    resultado = {
        "nombre": safe_get("FirstName"),
        "apellido": safe_get("LastName"),
        "dni": safe_get("DocumentNumber"),
        "nacimiento": nacimiento_val,
        "nro_dni": safe_get("DocumentNumber")
    }
    return resultado