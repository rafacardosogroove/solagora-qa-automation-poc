# language: pt
# Autor: Rafael Cardoso
@clientes @gestao_cadastral
Funcionalidade: Validação de Campos Obrigatórios no Formulário de Edição
  Como um administrador do sistema
  Quero que o formulário valide campos obrigatórios
  Para impedir envio de dados incompletos ou inválidos

  Contexto: Acessar a listagem de clientes
    Dado que o administrador está devidamente autenticado no portal
    E o componente de navegação carrega a página de "Clientes"

  @clientes_edicao @validacao_de_dados
  Cenário: C08 - Tentar submeter formulário de edição limpando campos obrigatórios
    Quando busco o cliente pelo CPF para validação de campos
    E acesso a opção "Editar" do menu de ações para validação
    E apago os dados dos campos "Email" e "Celular" deixando-os em branco
    E submeto o formulário com campos em branco
    Então o formulário não deve ser enviado por campos obrigatórios
    E mensagens de campos obrigatórios devem ser exibidas
    E o badge de aguardando aprovação não deve aparecer após submissão inválida
