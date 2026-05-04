# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Edição Simultânea de E-mail e Celular do Cliente
  Como um administrador do sistema
  Quero editar e-mail e celular de um cliente ao mesmo tempo
  Para submeter múltiplas alterações em uma única solicitação

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_edicao @fluxo_aprovacao
  Cenário: C03 - Submeter alteração simultânea de e-mail e celular para aprovação
    Quando busco o cliente pelo CPF para edição simultânea
    E acesso a opção "Editar" do menu de ações para edição simultânea
    E altero o campo "Email" e o campo "Celular" com novos dados válidos
    E submeto o formulário de edição simultânea
    Então o modal de confirmação de múltiplas alterações deve ser exibido
    E ao fechar o modal o cliente deve ter o badge de aguardando aprovação simultânea
