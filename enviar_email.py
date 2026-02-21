import smtplib
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')
    
    # Criamos uma lista real, que é o que o Python e o Google amam
    destinatarios = [
        "rcardoso1904@gmail.com",
        "edson.oliveira@groove.tech",
        "pedro.vinicius@groove.tech",
        "agata.oliveira@groove.tech",
        "andre.nunes@groove.tech",
        "andre.martins@groove.tech"
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

        msg = MIMEMultipart()
        msg['From'] = email_remetente
        msg['To'] = ", ".join(destinatarios) # Formato visual para o e-mail
        msg['Subject'] = f"📊 Relatório de Qualidade SolAgora - {datetime.now().strftime('%d/%m')}"

        msg.attach(MIMEText(html_final, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)
        
        # AQUI ESTÁ A MUDANÇA: Enviamos para a LISTA de e-mails
        server.sendmail(email_remetente, destinatarios, msg.as_string())
        server.quit()
        print(f"✅ E-mail enviado com sucesso para {len(destinatarios)} pessoas!")
        
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")

if __name__ == '__main__':
    enviar_relatorio()