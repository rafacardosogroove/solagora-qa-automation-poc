import datetime
import random
import string


class Generators:
    @staticmethod
    def cpf():
        """Gera um CPF aleatório, válido e com tendência de aprovação (Início 0-3)."""

        def calcula_digito(digitos):
            soma = 0
            peso = len(digitos) + 1
            for d in digitos:
                soma += int(d) * peso
                peso -= 1

            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        # 1. Gera o primeiro dígito entre 0 e 3 (conforme sua regra de aprovação)
        primeiro_num = [random.randint(0, 3)]

        # 2. Gera os outros 8 dígitos aleatórios
        outros_oito = [random.randint(0, 9) for _ in range(8)]

        # Une para formar os 9 primeiros dígitos
        nove_digitos = primeiro_num + outros_oito

        # 3. Calcula os dígitos verificadores para manter a validade matemática
        dez_digitos = nove_digitos + [calcula_digito(nove_digitos)]
        onze_digitos = dez_digitos + [calcula_digito(dez_digitos)]

        return "".join(map(str, onze_digitos))

    @staticmethod
    def data_nascimento(idade_min=18, idade_max=65):
        """Gera uma data de nascimento brasileira (dd/mm/aaaa) para um adulto."""
        dias_atras = random.randint(idade_min * 365, idade_max * 365)
        # Usando datetime.datetime.now() para garantir compatibilidade
        from datetime import datetime
        data = datetime.now() - datetime.timedelta(days=dias_atras)
        return data.strftime("%d/%m/%Y")

    @staticmethod
    def email():
        """Gera um e-mail aleatório válido."""
        prefixo = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        dominio = random.choice(["groovetech.com.br", "teste.com", "automacao.com"])
        return f"qa_{prefixo}@{dominio}"

    @staticmethod
    def telefone():
        """Gera um celular aleatório no formato 11999999999."""
        numero = ''.join(random.choices(string.digits, k=8))
        return f"119{numero}"