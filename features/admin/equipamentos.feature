# language: pt
# Autor: Rafael Cardoso Santana Costa

@equipamentos
Funcionalidade: Gate 08 - Confirmação de Entrega e Monitoração (Fluxo Admin)
  Como um parceiro integrador da SolAgora
  Quero que o sistema registre a entrega dos equipamentos
  Para que o projeto seja concluído e a usina entre em monitoração

  Contexto: Projeto com cessão finalizada e nota fiscal aprovada
    Dado que as notas fiscais do projeto foram enviadas e aprovadas

  @gate08 @fluxo_admin
  Cenário: Realizar confirmação de entrega de equipamento via back-end
    Quando aciono os serviços de equipamentos e monitoração via Modo Admin
    E atualizo a página do portal do integrador
    Então o sistema deve exibir o status do projeto como "Dados para monitoração da usina"
