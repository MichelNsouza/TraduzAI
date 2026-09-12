# Pipeline — ciclo de tradução

O agente executa as 9 etapas em sequência. A cada etapa: gere um relatório em `workspace/reports/` e, ao terminar, **promova** o que for reutilizável por outros jogos.

## Etapas → artefatos → o que promover

1. **Analisar a ISO**
   - Entrada: `workspace/input/`
   - Saída: relatório em `workspace/reports/`
   - Promover: docs do formato detectado em `workspace/context/`

2. **Extrair arquivos**
   - Ferramentas: `7z` / `binwalk` — script: `workspace/scripts/analyze_iso.sh`
   - Saída: `workspace/extracted/`
   - Promover: wrappers de extração genéricos

3. **Identificar formatos**
   - Saída: relatório (`file`/`strings`)
   - Promover: documentar formatos identificados com exemplos

4. **Localizar textos**
   - Promover: heurísticas e padrões de localização de texto

5. **Exportar textos**
   - Saída: CSV de tradução (schema abaixo)
   - Promover: decoder de encoding e extractor genérico

6. **Traduzir**
   - Feita pelo agente LLM sobre o CSV
   - Promover: glossário do jogo em `workspace/context/glossario.md`

7. **Reinserir**
   - Voltar do CSV para o binário preservando bytes de controle
   - Promover: reinjector genérico

8. **Reconstruir a ISO**
   - Promover: ferramentas de rebuild (ex.: conversão Mode2→ISO)

9. **Validar no emulador**
   - Relatório obrigatório — templates em `workspace/context/templates/`
   - Promover: checklist de validação

## Schema do CSV de tradução

Cabeçalho obrigatório:

```
id,original,traducao,status,nota
```

- `id`: referência à posição/registro no arquivo (nunca alterar).
- `original`: texto exibido no jogo (exato).
- `traducao`: texto traduzido.
- `status`: `pendente | traduzido | ignorado | adiado`.
- `nota`: contexto/aviso livre.

Regras:

- Nunca alterar `id`.
- Respeitar o limite de bytes do registro original.
- Nunca quebrar bytes de controle/separadores.