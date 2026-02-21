import smtplib
import os
import markdown  # <--- Nova biblioteca
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')
    
    # Lista de destinatários atualizada
    destinatarios = [
        "rcardoso1904@gmail.com",
        "edson.oliveira@groove.tech",
        "pedro.vinicius@groove.tech",
        "agata.oliveira@groove.tech",
        "andre.nunes@groove.tech",
        "andre.martins@groove.tech"
    ]
    
    email_destinatario = ", ".join(destinatarios)
    
    try:
        with open('email_dashboard.md', 'r', encoding='utf-8') as f:
            conteudo_md = f.read()

        # CONVERSÃO: Transforma o texto do GitHub em HTML para o e-mail
        corpo_html = markdown.markdown(conteudo_md, extensions=['tables'])

        # Estilização extra para o e-mail não ficar com fonte feia
        html_final = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">📊 Relatório de Qualidade SolAgora</h2>
                    {corpo_html}
                    <hr style="border: 0; border-top: 1px solid #eee; margin-top: 20px;">
                    <p style="font-size: 12px; color: #7f8c8d;">Este é um relatório automático gerado pelo Pipeline de QA.</p>
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
        server.sendmail(email_remetente, destinatarios, msg.as_string())
        server.quit()
        print(f"✅ E-mail HTML enviado com sucesso para {len(destinatarios)} pessoas!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == '__main__':
    enviar_relatorio()