# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Aprovação e Reprovação de Alterações Cadastrais
  Como um administrador do sistema
  Quero aprovar ou reprovar solicitações de alteração de dados
  Para garantir controle e auditoria das mudanças cadastrais

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_analise @aprovacao_positiva @smoke_test
  Cenário: C04 - Aprovar com sucesso uma solicitação de alteração de dados pendente
    Dado que o cliente possui uma solicitação de alteração pendente aguardando aprovação
    Quando acesso os detalhes do cliente com solicitação pendente
    E navego até o bloco de Análise
    E seleciono a opção "Aprovar"
    E salvo a decisão de aprovação
    Então o badge de aguardando deve ser removido da listagem
    E os novos dados devem estar efetivados no cadastro

  @clientes_analise @aprovacao_negativa
  Cenário: C05 - Reprovar uma solicitação de alteração de dados pendente
    Dado que o cliente possui uma solicitação de alteração pendente aguardando reprovação
    Quando acesso os detalhes do cliente com solicitação pendente para reprovar
    E navego até o bloco de Análise para reprovar
    E seleciono a opção "Reprovar"
    E salvo a decisão de reprovação
    Então o badge de aguardando deve ser removido após reprovação
    E os dados originais devem ser mantidos no cadastro
