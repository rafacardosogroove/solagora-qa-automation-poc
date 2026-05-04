from datetime import datetime
_run_id = datetime.now().strftime("%m%d%H%M%S")
_email_counter = 0

CUSTOMER = {
    "cpf": "831.102.825-77",
    "nome": "Aurore Teste Thiel",
}

VALID_DATA = {
    "celular": "(11) 9 9999-1111",
    "celular_alt": "(11) 9 9999-2222",
}

INVALID_DATA = {
    "email_sem_dominio": "usuario.sem.dominio",
    "celular_incompleto": "(11) 9 999",
    "vazio": "",
}

# Email único por passo — evita conflito de unicidade entre testes
def next_email() -> str:
    global _email_counter
    _email_counter += 1
    return f"qa.auto.{_run_id}.{_email_counter:03d}@solagora.com.br"

# CPFs já reivindicados nesta execução — cada teste deve receber um cliente único
_USED_CPFS: set = set()

INVALID_DATA = {
    "email_sem_dominio": "usuario.sem.dominio",
    "celular_incompleto": "(11) 9 999",
    "vazio": "",
}
