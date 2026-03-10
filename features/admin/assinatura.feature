
# language: pt
# Autor: Rafael Cardoso Santana Costa

@assinatura
Funcionalidade: Gate 06 - Assinatura Eletrônica da Proposta (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que a assinatura eletrônica seja processada pelo sistema
  Para que o projeto avance para a etapa de faturamento autorizado

  Contexto: Projeto aprovado e aguardando assinatura
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")
    E que realizo uma simulação completa para o distribuidor "ALDO" com vencimento "10"
    E que realizo a análise de crédito completa para o cliente "Rafael Automacao" com CEP "13282538"
    E que envio a documentação completa com origem "Local" e arquivo "conta.jpg"
    # --> Aqui o contexto executa o Gate 05 para preparar o terreno <--
    E capturo o ID do projeto atual pela interface
    E aciono os serviços de aprovação interna, documentação e biometria via Modo Admin
    E atualizo a página do portal do integrador

  @gate06 @fluxo_admin
  Cenário: Finalizar assinatura eletrônica da proposta via back-end
    Quando aciono o serviço de finalização de assinatura via Modo Deus
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Faturamento Autorizado"