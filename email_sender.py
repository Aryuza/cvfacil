import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def send_cvs_email(to_email: str, attachment_paths: list[str], candidate_name: str, gmail_user: str, gmail_password: str):
    """
    Sends an email with the CV PDFs attached via Gmail.
    """
    msg = MIMEMultipart()
    msg['Subject'] = f"Tu Nuevo CV Optimizado - {candidate_name}"
    msg['From'] = gmail_user
    msg['To'] = to_email

    body_html = f"""
    <html>
      <body>
        <p>hola <b>{candidate_name}</b>,</p>
        <p>👆 Aquí tenés el enlace para descargar tu currículum en formato PDF. Podés enviarlo por WhatsApp, correo electrónico o imprimirlo. (Si el link no funciona, copiá y pegalo en tu navegador).</p>
        
        <p>⚠ <b>Importante:</b> Revisá que toda la información esté correcta. Si necesitás realizar alguna modificación o detectás algún error, contactanos únicamente por WhatsApp. Las modificaciones son sin cargo durante las primeras 12 h; después de ese plazo tendrán un costo adicional.</p>
        
        <p>Para solicitar un cambio, por favor enviá un mensaje por WhatsApp con el siguiente formato:</p>
        <p>ERROR: [texto actual que querés cambiar]<br>
        QUIERO CAMBIAR POR: [nuevo texto o información correcta]</p>
        
        <p>💡 Así podremos identificar el cambio rápidamente y actualizar tu CV sin demoras.</p>
        
        <p><b>Material adicional incluido:</b><br>
        📋 Lista de contactos de empresas<br>
        📘 Guías “35 Trucos para Triunfar en una Entrevista Laboral” y “Cómo elaborar tu LinkedIn”</p>
        
        <p><a href="https://drive.google.com/drive/folders/1kJSVLca9BqsFc4nWAZPBQYra7wo1Y8vn?usp=sharing">https://drive.google.com/drive/folders/1kJSVLca9BqsFc4nWAZPBQYra7wo1Y8vn?usp=sharing</a></p>
        
        <p><b>Cursos de regalo:</b><br>
        🎓 Excel + Word + PowerPoint</p>
        
        <p><a href="https://drive.google.com/drive/folders/1WdilyL788ULQl1QRKXG1PPe4PXSUJnY5?usp=sharing">https://drive.google.com/drive/folders/1WdilyL788ULQl1QRKXG1PPe4PXSUJnY5?usp=sharing</a></p>
        
        <p><b>Pasos para enviar tu currículum:</b></p>
        <ol>
          <li><b>Email personalizado:</b> enviá al correo correcto, mencionando el nombre del destinatario y el puesto.</li>
          <li><b>Mensaje breve:</b> explicá quién sos y por qué sos un buen candidato.</li>
          <li><b>Adjuntos:</b> incluí tu currículum y, si es posible, una carta de presentación.</li>
          <li><b>Revisá y enviá:</b> asegurate de que no haya errores antes de enviar.</li>
        </ol>
        
        <p>¡Gracias por confiar en nosotros!<br>
        💼 Éxitos en tu búsqueda laboral 🚀</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(body_html, 'html'))

    for file_path in attachment_paths:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            msg.attach(part)
        else:
            print(f"Warning: Attachment not found: {file_path}")

    try:
        print(f"Connecting to Gmail SMTP to send to {to_email}...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(gmail_user, gmail_password)
            smtp.send_message(msg)
        print("Finalizing: Email sent successfully.")
        return True
    except Exception as e:
        print(f"Error: Error sending email: {e}")
        return False
