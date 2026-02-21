# language: pt
# Autor: Rafael Cardoso

Funcionalidade: Gate 01 - Controle de Acesso e Autenticação
  Como um sistema de controle de qualidade (CI/CD)
  Quero garantir que a autenticação principal esteja operante
  Para permitir que novas implementações sejam mescladas no repositório

  @gate01 @pr_blocker @smoke_test @auth
  Cenário: Validar a liberação de acesso ao portal do Integrador
    Dado que o ambiente de homologação está respondendo na página de login
    Quando o processo de autenticação é submetido com credenciais válidas ("qaautomacao" e "solagora")
    Então o sistema deve autorizar o acesso e redirecionar para a dashboard
    E o componente de navegação deve carregar o menu de "Projetos"