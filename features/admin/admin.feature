# language: pt
# Autor: Rafael Cardoso Santana Costa

@aprovacoes
Funcionalidade: Gate 05 - Orquestração e Aprovações (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que minhas propostas sejam aprovadas instantaneamente via sistema
  Para que o projeto avance para a etapa de assinatura de forma fluida

  Contexto: Projeto com documentação enviada aguardando avaliação interna
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")
    E que realizo uma simulação completa para o distribuidor "ALDO" com vencimento "10"
    E que realizo a análise de crédito completa para o cliente "Rafael Automacao" com CEP "13282538"
    E que envio a documentação completa com origem "Local" e arquivo "conta.jpg"

  @gate05 @fluxo_admin
  Cenário: Realizar aprovações de back-end em massa e atualizar status da proposta
    Quando capturo o ID do projeto atual pela interface
    E aciono os serviços de aprovação interna, documentação e biometria via Modo Deus
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Aguardando Assinatura"