# language: pt
# Autor: Rafael Cardoso Santana Costa

@equipamentos
Funcionalidade: Gate 08 - Confirmação de Entrega e Monitoração (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que o sistema registre a entrega dos equipamentos
  Para que o projeto seja concluído e a usina entre em monitoração

  Contexto: Projeto com cessão finalizada e nota fiscal aprovada
    Dado que o ambiente de homologação está respondendo na página de login
    E que executo o fluxo completo de login válido ("qaautomacao", "solagora")
    E que realizo uma simulação completa para o distribuidor "ALDO" com vencimento "10"
    E que realizo a análise de crédito completa para o cliente "Rafael Automacao" com CEP "13282538"
    E que envio a documentação completa com origem "Local" e arquivo "conta.jpg"
    # --> Prepara Gate 05, 06 e 07 <--
    E capturo o ID do projeto atual pela interface
    E aciono os serviços de aprovação interna, documentação e biometria via Modo Deus
    E aciono o serviço de finalização de assinatura via Modo Deus
    E realizo o upload da nota fiscal de venda pela interface
    E aciono os serviços de faturamento, cessão e callbacks via Modo Deus
    E atualizo a página do portal do integrador

  @gate08 @fluxo_admin
  Cenário: Realizar confirmação de entrega de equipamento via back-end
    Quando aciono os serviços de equipamentos e monitoração via Modo Deus
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Dados para monitoração da usina"