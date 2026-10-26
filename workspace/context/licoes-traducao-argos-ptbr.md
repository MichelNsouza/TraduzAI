# Tradução offline EN→PT-BR com Argos Translate

Lições para traduzir milhares de strings de jogo sem API paga e sem rede.

## Instalação

```bash
python3 -m pip install --user argostranslate
python3 -c "import argostranslate.package as p; p.update_package_index()"
# instala o par en->pt
python3 - <<'EOF'
import argostranslate.package as p
pkg = next(x for x in p.get_available_packages()
           if x.from_code == 'en' and x.to_code == 'pt')
p.install_from_path(pkg.download())
EOF
```

Modelo fica em `~/.local/share/argos-translate/packages/`. Funciona 100%
offline depois de instalado.

## Desempenho

- ~9 mil strings curtas (média 30 caracteres) em ~20 minutos
  (~0,11 s por string, um núcleo).
- Cache por string de origem: scripts com muitos nomes repetidos
  (itens, bestiário) caem para ~40% do tempo.
- Vale memorizar traduções: o mesmo texto original aparece centenas de vezes
  em tabelas duplicadas.

## Qualidade

- EN→PT do Argos é **português europeu** ("por si", "já não", "tu podes",
  "imploro-te", "junta-se à festa"). Precisa de pós-edição para PT-BR.
- Nomes próprios costumam ser preservados, mas o modelo inventa artigo
  ("O Garland") e traduz mal termos de jogo ("party" → "festa").
- Saída é melhor quando se traduz **parágrafo inteiro**, não linha a linha:
  quebras de linha de caixa de diálogo devem ser removidas antes e
  reaplicadas depois.

## Pós-edição PT-PT → PT-BR (ordem importa)

1. Pronomes/possessivos: `por si→por você`, `teu/tua→seu/sua`,
   `contigo→com você`, `vós→vocês`.
2. Ênclise com `-te` (europeu) → `... a você`.
3. Verbos de 2ª pessoa: `tens→tem`, `podes→pode`, `fazes→faz`,
   `devias→deveria`, `fiques→fique` (lista em `workspace/scripts/translate_csv_argos.py`).
4. Vocabulário: `equipa→equipe`, `ecrã→tela`, `comboio→trem`,
   `autocarro→ônibus`, `sumo→suco`, `gelado→sorvete`,
   `casa de banho→banheiro`, `pequeno-almoço→café da manhã`.
5. Ortografia: `cç→ç` (`acção→ação`), `-ó[mn]ico→-ô[mn]ico`
   (`tónico→tônico`), `prémio→prêmio`.
6. Normalização de espaços antes de pontuação e capitalização inicial.

## Preservação de estrutura (essencial em jogos)

- Tokens do jogo (`{ICON:4D}`, `{CTL:05}`, `{C:FA}`, `{FMT:%2d}`) devem ser
  retirados antes de traduzir e recolocados na mesma posição. O script divide
  o texto nos tokens e traduz só os trechos de texto.
- Especificadores de formato (`%0`, `%2d`, `%s`) **nunca** podem ser
  traduzidos nem convertidos de largura: o motor os substitui. Strings que os
  contêm devem ser traduzidas à mão (poucas dezenas).
- Larguras de linha: guardar as larguras das linhas originais e reflowar a
  tradução para elas. Strings de uma linha (nomes de menu) nunca devem ser
  quebradas.
- Textos centralizados por espaços à esquerda (comuns em mensagens de
  "obteve item") precisam ser re-centralizados na largura original.

## Alternativas avaliadas

| Serviço | Resultado |
|---------|-----------|
| Google Translate (endpoint web) | 429/bloqueado, sem chave |
| MyMemory | qualidade inutilizável para diálogo |
| LibreTranslate público | instável/limitado |
| **Argos Translate local** | **melhor custo/benefício; offline e previsível** |
| LLM (agente) | ótima qualidade, inviável para 250 mil caracteres no tempo disponível |
