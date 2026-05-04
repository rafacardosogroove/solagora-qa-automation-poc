# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Edição de Celular do Cliente
  Como um administrador do sistema
  Quero editar o celular de um cliente
  Para manter os dados cadastrais atualizados mediante aprovação

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_edicao @fluxo_aprovacao
  Cenário: C02 - Submeter alteração exclusiva de celular para aprovação
    Quando busco o cliente pelo CPF para edição de celular
    E acesso a opção "Editar" do menu de ações do cliente de celular
    E altero o campo "Celular" para um novo número válido
    E submeto o formulário de edição de celular
    Então o modal de confirmação de solicitação de celular deve ser exibido
    E ao fechar o modal o cliente deve ter o badge de aguardando aprovação de celular

  @clientes_edicao @validacao_de_dados
  Cenário: C07 - Tentar submeter alteração com celular incompleto ou inválido
    Quando busco o cliente pelo CPF para edição de celular
    E acesso a opção "Editar" do menu de ações do cliente de celular
    E altero o campo "Celular" para um número incompleto
    E submeto o formulário de edição de celular
    Então o formulário de celular não deve ser enviado
    E uma mensagem de erro de validação deve ser exibida no campo Celular
    E o badge de aguardando aprovação não deve aparecer para o cliente de celular
