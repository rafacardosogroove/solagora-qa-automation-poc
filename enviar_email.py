import smtplib
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')

    destinatarios = [
        "rcardoso1904@gmail.com",
        # "edson.oliveira@groove.tech",
        # "pedro.vinicius@groove.tech",
        # "agata.oliveira@groove.tech",
        # "andre.nunes@groove.tech",
        # "andre.martins@groove.tech"
    ]

    try:
        with open('email_dashboard.md', 'r', encoding='utf-8') as f:
            conteudo_md = f.read()

        corpo_html = markdown.markdown(conteudo_md, extensions=['tables'])

        html_final = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    {corpo_html}
                </div>
            </body>
        </html>
        """

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)

        for destino in destinatarios:
            msg = MIMEMultipart()
            msg['From'] = email_remetente
            msg['To'] = destino
            msg['Subject'] = f"🚀 Status Automação SolAgora - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

            msg.attach(MIMEText(html_final, 'html'))
            server.sendmail(email_remetente, destino, msg.as_string())
            print(f"✅ E-mail enviado para: {destino}")

        server.quit()
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")


if __name__ == '__main__':
    enviar_relatorio()