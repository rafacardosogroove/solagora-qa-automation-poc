# language: pt
# Autor: Rafael Cardoso Santana Costa

@faturamento
Funcionalidade: Gate 07 - Upload de Nota Fiscal e Cessão (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero enviar a nota fiscal da proposta pela interface e validar o faturamento
  Para que o projeto avance para a etapa de liberação de pagamento e equipamentos

  Contexto: Projeto assinado e com faturamento autorizado
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")
    E que realizo uma simulação completa para o distribuidor "ALDO" com vencimento "10"
    E que realizo a análise de crédito completa para o cliente "Rafael Automacao" com CEP "13282538"
    E que envio a documentação completa com origem "Local" e arquivo "conta.jpg"
    # --> Prepara Gate 05 <--
    E capturo o ID do projeto atual pela interface
    E aciono os serviços de aprovação interna, documentação e biometria via Modo Deus
    # --> Prepara Gate 06 <--
    E aciono o serviço de finalização de assinatura via Modo Deus
    E atualizo a página do portal do integrador

  @gate07 @fluxo_admin
  Cenário: Realizar upload de nota fiscal e aprovação de cessão via back-end
    Quando realizo o upload da nota fiscal de venda pela interface
    E aciono os serviços de faturamento, cessão e callbacks via Modo Deus
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Cessão de pagamento finalizada"