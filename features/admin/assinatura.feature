# language: pt
# Autor: Rafael Cardoso Santana Costa

@assinatura
Funcionalidade: Gate 06 - Assinatura Eletrônica da Proposta (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que a assinatura eletrônica seja processada pelo sistema
  Para que o projeto avance para a etapa de faturamento autorizado

  Contexto: Projeto aprovado e aguardando assinatura
    Dado que o projeto foi aprovado pela mesa interna

  @gate06 @fluxo_admin
  Cenário: Finalizar assinatura eletrônica da proposta via back-end
    Quando aciono o serviço de finalização de assinatura via Modo Admin
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Faturamento Autorizado"