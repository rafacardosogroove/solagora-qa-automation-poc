# language: pt
# Autor: Rafael Cardoso Santana Costa

@login
Funcionalidade: Gate 01 - Controle de Acesso e Autenticação
  Como um sistema de controle de qualidade (CI/CD)
  Quero garantir que a autenticação principal e suas restrições estejam operantes
  Para permitir que novas implementações sejam mescladas no repositório

  Contexto: Acessar a página inicial
    Dado que o ambiente de homologação está respondendo na página de login

  @gate01 @pr_blocker @smoke_test @auth
  Cenário: 1. Validar a liberação de acesso ao portal do Integrador (Login com sucesso)
    Quando o processo de autenticação é submetido com credenciais válidas ("qaautomacao" e "solagora")
    Então o sistema deve autorizar o acesso e redirecionar para a dashboard
    E o componente de navegação deve carregar o menu de "Projetos"

  @auth @login_invalido
  Esquema do Cenário: 2 e 3. Validar bloqueios de login (Senha ou CPF inválidos)
    Quando o processo de autenticação é submetido com usuario "<usuario>" e senha "<senha>"
    Então o sistema deve manter o usuário na tela de login
    E exibir a mensagem de erro "<mensagem_erro>"

    Exemplos:
      | cenario              | usuario         | senha        | mensagem_erro                        |
      | Senha invalida       | qaautomacao     | senharada    | Nome de usuário ou senha inválida.   |
      | CPF/Usuario Invalido | 00000000000     | solagora     | Nome de usuário ou senha inválida.   |

  @auth @logout
  Cenário: 4. Logout encerra sessão com sucesso
    Dado que o sistema está autenticado com credenciais válidas ("qaautomacao" e "solagora")
    Quando aciono a opção de sair do sistema
    Então o sistema deve encerrar a sessão e redirecionar para a tela de login

  @auth @acesso_negado
  Cenário: 5. Usuário sem permissão bloqueia acesso à tela Admin
    Dado que o sistema está autenticado com credenciais válidas ("qaautomacao" e "solagora")
    Quando tento acessar a URL restrita de administração diretamente
    Então o sistema deve bloquear o acesso e exibir mensagem de permissão negada