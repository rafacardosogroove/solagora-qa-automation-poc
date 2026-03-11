# language: pt
# Autor: Rafael Cardoso Santana Costa

@aprovacoes
Funcionalidade: Gate 05 - Orquestração e Aprovações (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que minhas propostas sejam aprovadas instantaneamente via sistema
  Para que o projeto avance para a etapa de assinatura de forma fluida

  Contexto: Projeto com documentação enviada aguardando avaliação interna
    Dado que a documentação do projeto foi enviada com sucesso

  @gate05 @fluxo_admin
  Cenário: Realizar aprovações de back-end em massa e atualizar status da proposta
    Quando capturo o ID do projeto atual pela interface
    E aciono os serviços de aprovação interna, documentação e biometria via Modo Admin
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Aguardando Assinatura"