import resend
from django.conf import settings


class ServicioCorreoResend:
    def enviar_codigo_cambio(self, destinatario, codigo):
        if not settings.RESEND_API_KEY:
            raise RuntimeError("RESEND_API_KEY no está configurada.")
        if not settings.RESEND_FROM_EMAIL:
            raise RuntimeError("RESEND_FROM_EMAIL no está configurado.")

        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(
            {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [destinatario],
                "subject": "Código para cambiar tu contraseña",
                "html": (
                    "<h2>Cambio de contraseña</h2>"
                    "<p>Usa este código para continuar:</p>"
                    f"<p style=\"font-size: 24px; font-weight: bold;\">{codigo}</p>"
                    "<p>Si no solicitaste este cambio, ignora este correo.</p>"
                ),
            }
        )
