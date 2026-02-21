import smtplib
import os
import markdown  # <--- Nova biblioteca
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')
    email_destinatario = "rcardoso1904@gmail.com,edson.oliveira@groove.tech"
    
    try:
        with open('email_dashboard.md', 'r', encoding='utf-8') as f:
            conteudo_md = f.read()

        # CONVERSÃO: Transforma o texto do GitHub em HTML para o e-mail
        corpo_html = markdown.markdown(conteudo_md, extensions=['tables'])

        # Estilização extra para o e-mail não ficar com fonte feia
        html_final = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    {corpo_html}
                </div>
            </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = email_remetente
        msg['To'] = email_destinatario
        msg['Subject'] = f"📊 Relatório de Qualidade SolAgora - {datetime.now().strftime('%d/%m')}"

        # Enviamos como HTML em vez de plain text
        msg.attach(MIMEText(html_final, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)
        server.send_message(msg)
        server.quit()
        print("✅ E-mail HTML enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    enviar_relatorio()