# language: pt
# Autor: Rafael Cardoso Santana Costa

@faturamento @gate07
Funcionalidade: Gate 07 - Upload de Notas Fiscais e Equipamentos
  Como um parceiro integrador da SolAgora
  Quero localizar um projeto autorizado e enviar as notas fiscais
  Para que o faturamento seja processado e o projeto avance para cessão

  Contexto: Projeto assinado e com faturamento autorizado
    Dado que o contrato do projeto foi assinado eletronicamente

  @fluxo_admin
  Cenário: Realizar upload de notas fiscais de equipamento e serviço com sucesso
    Quando pesquiso o projeto pelo CPF do cliente na listagem
    E seleciono a opção de continuar o projeto faturamento na engrenagem
    E prossigo para o envio de notas no modal de sucesso
    E preencho os dados da Nota Fiscal de Equipamento com número "123456" e valor "45000"
    E preencho os dados da Nota Fiscal de Serviço com número "7890" e valor "5000"
    E seleciono o fabricante do inversor "WEG" e quantidade "1"
    E seleciono o fabricante do módulo "CANADIAN" e quantidade "10"
    E finalizo o envio das notas e informações
    Então o sistema deve exibir a tela de análise de notas fiscais