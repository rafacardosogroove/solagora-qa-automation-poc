# language: pt
# Autor: Rafael Cardoso Santana Costa

# language: pt
# Autor: Rafael Cardoso Santana Costa

@documentacao
Funcionalidade: Gate 04 - Documentação e Dados Cadastrais Finais
  Como um parceiro integrador da SolAgora
  Quero enviar os documentos comprobatórios e dados finais do cliente
  Para que o projeto avance para a etapa final de assinatura

  Contexto: Cliente aprovado na análise de crédito
    Dado que o cliente foi aprovado na análise de crédito

  @gate04 @documentacao
  Esquema do Cenário: Realizar upload de documentos e preenchimento total do formulário
    Quando realizo o upload da conta de energia "<origem>" com o arquivo "<arquivo>"
    E preencho o endereço de instalação com Número "<numero>" e Complemento "<complemento>"
    E defino que o endereço de cobrança "<endereco_igual>" ao de instalação
    E informo o documento de identidade RG "<rg>"
    E preencho os contatos com Email "<email>", Celular "<celular>", Segundo Celular "<celular_2>" e Fixo "<fixo>"
    Então o sistema deve habilitar o botão e concluir o envio da documentação

    Exemplos:
      | origem | arquivo   | numero | complemento | endereco_igual | rg           | email | celular | celular_2 | fixo       |
      | Local  | conta.jpg | 980    | Bloco A     | Sim            | 34661561-6   | GERAR | GERAR   | GERAR     | 1133334444 |
#     | Remoto | conta.jpg | 500    | Casa 2      | Sim            | 88.888.888-Y | GERAR | GERAR   | GERAR     | 1122223333 |