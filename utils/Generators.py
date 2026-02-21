import datetime
import random


class Generators:
    @staticmethod
    def cpf():
        """Gera um CPF aleatório e válido para testes."""

        def calcula_digito(digitos):
            soma = 0
            peso = len(digitos) + 1
            for d in digitos:
                soma += int(d) * peso
                peso -= 1

            resto = soma % 11
            return 0 if resto < 2 else 11 - resto

        # Gera os 9 primeiros dígitos aleatórios
        nove_digitos = [random.randint(0, 9) for _ in range(9)]

        # Calcula o 10º dígito
        primeiro_digito = calcula_digito(nove_digitos)
        nove_digitos.append(primeiro_digito)

        # Calcula o 11º dígito
        segundo_digito = calcula_digito(nove_digitos)
        nove_digitos.append(segundo_digito)

        return "".join(map(str, nove_digitos))

    @staticmethod
    def data_nascimento(idade_min=18, idade_max=65):
        """Gera uma data de nascimento brasileira (dd/mm/aaaa) para um adulto."""
        dias_atras = random.randint(idade_min * 365, idade_max * 365)
        data = datetime.now() - datetime.timedelta(days=dias_atras)
        return data.strftime("%d/%m/%Y")