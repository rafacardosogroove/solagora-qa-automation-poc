# language: pt
# Autor: Rafael Cardoso

Funcionalidade: Gate 02 - Simulação Técnica de Financiamento
  Como um sistema de controle de qualidade (CI/CD)
  Quero garantir que o motor de cálculo e simulação responda corretamente
  Para permitir que novas implementações sejam mescladas no repositório

  @gate02 @pr_blocker @simulacao
  Cenário: Validar a geração de condições de financiamento com sucesso
    Dado que o sistema está autenticado e na tela de novo projeto
    Quando os dados técnicos são preenchidos com distribuidor "ALDO COMPONENTES ELETRONICOS" e vencimento "24"
    Então o motor de cálculo deve processar a simulação
    E o sistema deve apresentar as condições de financiamento com sucesso