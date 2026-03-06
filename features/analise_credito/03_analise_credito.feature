# language: pt
# Autor: Rafael Cardoso Santana Costa


Funcionalidade: Gate 03 - Análise de Crédito e Dados Cadastrais

  Contexto: Simulação finalizada com sucesso
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")
    E que realizo uma simulação completa para o distribuidor "ALDO" com vencimento "10"

  @gate03 @analise_credito @smoke_test
  Esquema do Cenário: Validar preenchimento completo da análise de crédito
    Quando decido seguir com a proposta clicando em "Quero criar uma proposta"
    E seleciono a opção de seguro "<opcao_seguro>" se o modal for exibido
    E preencho os dados do cliente com Nome "<nome>", Email "<email>", Celular "<celular>" e CEP "<cep>"
    Então o sistema deve habilitar o botão "Enviar para análise de crédito"

    Exemplos:
      | opcao_seguro | nome            | email                 | celular      | cep      |
      | COM SEGURO   | Rafael Automacao| GERAR | GERAR  | 01310100 |




    # | SEM SEGURO   | Jose Teste      | jose@teste.com        | 11888888888  | 04101300 |