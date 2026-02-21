# language: pt
# Autor: Rafael Cardoso

Funcionalidade: Fluxo de Simulação Solar

  @simulacao @pf @aldo_componentes @regressivo
  Esquema do Cenário: Simulação Aldo PF completa com sucesso
    Dado que acesso o sistema pela URL de autenticação
    E realizo o login com usuario "<usuario>" e senha "<senha>"
    E navego até o simulador de novo projeto
    Quando preencho os dados do CPF "<cpf>", distribuidor "<distribuidor>" e vencimento "<vencimento>"

    Exemplos:
      | cenario            | usuario      | senha    | cpf            | distribuidor                  | vencimento | parcela | escolha_seguro | nome          | email           | celular         | cep       |
      | Simulacao_Aldo_PF  | qaautomacao  | solagora | 824.539.500-53 | ALDO COMPONENTES ELETRONICOS  | 22         | 25x     | Não            | Rafael Teste  | rafa@email.com  | (11) 99999-9999 | 01310-100 |