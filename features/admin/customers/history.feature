# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Histórico de Auditoria e Propagação de Alterações
  Como um administrador do sistema
  Quero que todas as decisões sejam registradas com auditoria completa
  Para garantir rastreabilidade e conformidade das alterações cadastrais

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_status @fluxo_riscos
  Cenário: C09 - Validar nomenclatura exata do status para pedidos em atendimento
    Quando submeto uma alteração de dados para o cliente de nomenclatura
    Então o status atribuído deve ser exatamente "Aguardando aprovação da alteração"
    E esse status deve estar visível na listagem de clientes

  @clientes_analise @aprovacao_cascata @historico @smoke_test
  Cenário: C10 - Validar propagação da alteração aprovada para os projetos do cliente
    Dado que o cliente possui uma solicitação de novo e-mail aprovada
    Quando acesso os projetos vinculados ao cliente
    Então todos os projetos devem exibir o novo e-mail aprovado

  @clientes_analise @historico_auditoria
  Cenário: C11 - Validar o registro de histórico após a decisão da equipe de riscos
    Dado que uma decisão de aprovação foi registrada para o cliente de histórico
    Quando verifico o histórico de alterações do cliente
    Então o histórico deve conter os dados de de/para com autor e data/hora
    E os campos status processado_em e por devem estar preenchidos
