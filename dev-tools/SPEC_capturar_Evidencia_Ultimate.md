# [QA Tooling] Ferramenta de Captura e Geração de Evidências de Teste

## Contexto e Motivação

O processo de coleta de evidências de testes manuais e exploratórios exige que o QA tire prints manualmente, cole em um documento Word, formate as imagens e insira as legendas passo a passo. Além de ser repetitivo, existe o risco de falhas de compliance (prints sem barra de tarefas com data e hora) ou esquecimento do logo da empresa no documento oficial.

## História de Usuário

Como **Analista de Qualidade (QA)**,  
quero uma ferramenta desktop auxiliar para gerenciar meus passos de teste e capturar a tela,  
para gerar automaticamente o documento final de evidências (`.docx`) formatado e padronizado.

## Critérios de Aceite

### Critério 1 — Múltiplos Modos de Captura
- Permitir capturar "Tela Inteira" ou "Área Selecionada" específica
- Suportar seleção do monitor alvo em setups com múltiplas telas

### Critério 2 — Resolução Real e Barra de Tarefas (DPI Awareness)
- Ignorar o escalonamento de tela do Windows (Zoom)
- Mapear a resolução real do monitor
- Garantir que a barra de tarefas (com data e hora) não seja cortada nas capturas de tela inteira

### Critério 3 — Trava de Segurança (Fail-Fast)
- Impedir início da captura sem upload prévio da Logo da empresa
- Exibir alerta em tela se logo não estiver carregada

### Critério 4 — Modo Compacto (Modo Flutuante)
- Possuir "Modo Compacto" com janela pequena e flutuante
- Exibir apenas botões "Capturar" e "Expandir" no modo compacto
- Aplicar leve transparência para não obstruir o sistema sendo testado

### Critério 5 — Fila de Passos de Teste
- Receber lista de passos/cenários em texto
- Transformá-los em fila interativa
- Marcar automaticamente como `✅ DONE` o passo atual após captura
- Avançar para o próximo passo automaticamente

### Critério 6 — Geração Automatizada do Relatório (Word)
O `.docx` gerado deve conter:
- Cabeçalho com Logo da empresa e título padronizado
- Tabela de metadados do teste (Demanda, Responsável, Data, Ambiente, Cenário)
- Regras de preenchimento destacadas
- Imagens dimensionadas corretamente com legendas dos passos
- Nome do arquivo sugerido automaticamente com base na Demanda (Test Key) e Cenário

## Informações Técnicas

| Item | Detalhe |
|------|---------|
| Linguagem | Python 3+ |
| Interface Gráfica | Tkinter (nativa) |
| Captura de Tela | `mss` (multi-monitor, alta performance) |
| Manipulação de Documentos | `python-docx` |
| Sistema Operacional | Windows (`ctypes.windll.shcore` para bypass de DPI) |

## Dependências

```
mss
python-docx
```

## Como Executar

```bash
python dev-tools/capturar_Evidencia_Ultimate.py
```

## Melhorias Identificadas (Backlog)

- [ ] Cleanup automático dos `temp_*.png` em `on_closing` — evita arquivos órfãos se o Word não for gerado
- [ ] Atalho de teclado `Ctrl+Shift+P` para captura rápida no modo compacto
- [ ] Scrollbar na `Listbox` de passos para listas longas
