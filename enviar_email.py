import smtplib
import os
import markdown
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def enviar_relatorio():
    email_remetente = os.environ.get('EMAIL_USER')
    senha_remetente = os.environ.get('EMAIL_PASS')
    
    # LISTA DE DESTINATÁRIOS (Formatada como lista real de Python)
    destinatarios = [
        "rcardoso1904@gmail.com",
        "edson.oliveira@groove.tech",
        "pedro.vinicius@groove.tech",
        "agata.oliveira@groove.tech",
        "andre.nunes@groove.tech",
        "andre.martins@groove.tech"
    ]
    
    try:
        # 1. Tenta ler o dashboard gerado pelo Job anterior
        with open('email_dashboard.md', 'r', encoding='utf-8') as f:
            conteudo_md = f.read()

        # 2. Converte Markdown para HTML
        corpo_html = markdown.markdown(conteudo_md, extensions=['tables'])

        # 3. Estilização para garantir que as tabelas apareçam bonitas
        html_final = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 800px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
                    {corpo_html}
                </div>
            </body>
        </html>
        """

        # 4. Conecta ao Servidor do Google
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_remetente, senha_remetente)

        # 5. DISPARO INDIVIDUAL (O segredo para não ser bloqueado)
        for destino in destinatarios:
            msg = MIMEMultipart()
            msg['From'] = email_remetente
            msg['To'] = destino
            msg['Subject'] = f"📊 Relatório de Qualidade SolAgora - {datetime.now().strftime('%d/%m')}"
            msg.attach(MIMEText(html_final, 'html'))
            
            server.send_message(msg)
            print(f"✅ Enviado com sucesso para: {destino}")

        server.quit()
        print("🚀 Todos os relatórios foram despachados!")

    except Exception as e:
        print(f"❌ ERRO NO PROCESSO: {e}")

if __name__ == '__main__':
    enviar_relatorio()