# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Edição de E-mail do Cliente
  Como um administrador do sistema
  Quero editar o e-mail de um cliente
  Para manter os dados cadastrais atualizados mediante aprovação

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_edicao @fluxo_aprovacao @smoke_test
  Cenário: C01 - Submeter alteração exclusiva de e-mail para aprovação
    Quando busco o cliente pelo CPF para edição de e-mail
    E acesso a opção "Editar" do menu de ações
    E altero o campo "Email" para um novo endereço válido
    E submeto o formulário de edição
    Então o modal de confirmação de solicitação deve ser exibido
    E ao fechar o modal o cliente deve ter o badge de aguardando aprovação

  @clientes_edicao @validacao_de_dados
  Cenário: C06 - Tentar submeter alteração com formato de e-mail inválido
    Quando busco o cliente pelo CPF para edição de e-mail
    E acesso a opção "Editar" do menu de ações
    E altero o campo "Email" para um formato inválido
    E submeto o formulário de edição
    Então o formulário não deve ser enviado
    E uma mensagem de erro de validação deve ser exibida no campo Email
    E o badge de aguardando aprovação não deve aparecer para o cliente
