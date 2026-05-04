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
        "pablo.borges@groove.tech",
        "daniel.cochoni@groove.tech",
        "eliandro@groove.tech",
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

        msg = MIMEMultipart("alternative")
        msg["From"] = email_remetente
        msg["To"] = email_remetente          # remetente no To (campo visível)
        msg["Bcc"] = ", ".join(destinatarios)  # destinatários em BCC (invisível entre si)
        msg["Subject"] = assunto
        msg.attach(MIMEText(html_final, "html"))

        todos = [email_remetente] + destinatarios
        server.sendmail(email_remetente, todos, msg.as_string())
        print(f"Email enviado para {len(destinatarios)} destinatarios via BCC.")

        server.quit()
        print("Todos os e-mails enviados com sucesso.")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        raise


if __name__ == "__main__":
    enviar_relatorio()
