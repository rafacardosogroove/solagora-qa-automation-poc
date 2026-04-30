import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


def enviar_relatorio():
    email_remetente = os.environ.get("EMAIL_USER")
    senha_remetente = os.environ.get("EMAIL_PASS")

    destinatarios = [
        "rcardoso1904@gmail.com",
        "edson.oliveira@groove.tech",
        "pedro.vinicius@groove.tech",
        "agata.oliveira@groove.tech",
        "andre.nunes@groove.tech",
        "andre.martins@groove.tech",
    ]

    # Lê o HTML gerado pelo gerar_dashboard.py
    arquivo_html = "email_dashboard.html"
    if not os.path.exists(arquivo_html):
        print(f"❌ Arquivo {arquivo_html} não encontrado. Execute gerar_dashboard.py antes.")
        return

    with open(arquivo_html, "r", encoding="utf-8") as f:
        html_final = f.read()

    assunto = f"📊 Dashboard QA SolAgora — {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)

        for destino in destinatarios:
            msg = MIMEMultipart("alternative")
            msg["From"] = email_remetente
            msg["To"] = destino
            msg["Subject"] = assunto
            msg.attach(MIMEText(html_final, "html"))
            server.sendmail(email_remetente, destino, msg.as_string())
            print(f"✅ E-mail enviado para: {destino}")

        server.quit()
        print("✅ Todos os e-mails enviados com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        raise


if __name__ == "__main__":
    enviar_relatorio()
