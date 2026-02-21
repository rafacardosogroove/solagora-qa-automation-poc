import smtplib
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')
    
    # LISTA LIMPA E SEM ERROS DE SINTAXE
    destinatarios = [
        "rcardoso1904@gmail.com",
        "edson.oliveira@groove.tech",
        "pedro.vinicius@groove.tech",
        "agata.oliveira@groove.tech",
        "andre.nunes@groove.tech",
        "andre.martins@groove.tech"
    ]
    
    try:
        # Tenta ler o arquivo que o Job anterior gerou
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

        # CONEXÃO COM O SERVIDOR
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)

        # DISPARO INDIVIDUAL (Evita bloqueio de spam e garante que apareça nos 'Enviados')
        for destino in destinatarios:
            msg = MIMEMultipart()
            msg['From'] = email_remetente
            msg['To'] = destino
            msg['Subject'] = f"📊 Relatório de Qualidade SolAgora - {datetime.now().strftime('%d/%m')}"
            msg.attach(MIMEText(html_final, 'html'))
            
            server.send_message(msg)
            print(f"✅ Enviado para: {destino}")

        server.quit()
        print("🚀 Todos os e-mails foram processados!")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {e}")

if __name__ == '__main__':
    enviar_relatorio()