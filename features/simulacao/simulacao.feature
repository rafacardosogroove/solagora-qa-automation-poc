# language: pt
Funcionalidade: Gate 02 - Simulação de Financiamento (P1)

  Contexto: Acessar o sistema
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")

  @simulacao @smoke_test @gate02
  Esquema do Cenário: 1. Processar simulação inicial com diferentes perfis de cliente
    Quando acesso a área de criação de um novo projeto
    E preencho os dados com CPF "<cpf>", Renda "<renda>", Valor "<valor>", Distribuidor "<distribuidor>", Energia "<energia>" e Vencimento "<dia>"
    Então o sistema deve avançar para a próxima etapa da simulação
    E deve exibir a tela de resultados com a mensagem "Boas notícias! As condições foram aceitas"

    Exemplos:
      | perfil             | cpf   | renda | valor | distribuidor | energia | dia |
      | Sucesso - Dinâmico | GERAR | 5000  | 50000 | ALDO         | 1000    | 10  |



#
#
#    | Sucesso - Fixo (PF)   | 82453950053 | 15000  | 120000  | WEG          | 2500    | 15  |
#      | Limite Mínimo         | GERAR       | 2500   | 15000   | ALDO         | 500     | 05  |
#      | Projeto de Alto Valor | GERAR       | 50000  | 500000  | WEG          | 8000    | 20  |