import random
import smtplib
import email.message


codigo_aleatorio = ''.join(random.choices('0123456789', k=4))
print(f'Código Gerado: {codigo_aleatorio}')

# Função para enviar e-mail
def enviar_email():
    corpo_email = f"""
    <p>Olá,</p>
    <p>Seu código de verificação é: <strong>{codigo_aleatorio}</strong></p>
    <p>Use este código para continuar com seu processo.</p>
    <p>Atenciosamente,</p>
    <p><strong>CarFix</strong></p>
    """

    msg = email.message.Message()
    msg['Subject'] = "Teste"
    msg['From'] = 'carfixofc@gmail.com' 
    msg['To'] = 'dbia4549@gmail.com'  
    password = 'vuts ggqs uudv wrpz' 
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(msg['From'], password)  
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
        s.quit()
        print('Email enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar o email: {e}')


enviar_email()
