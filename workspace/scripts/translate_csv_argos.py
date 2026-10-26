#!/usr/bin/env python3
"""Traduz CSVs do TraduzAI (formato id,original,traducao,status,nota) com Argos Translate.

Proposito
    Traducao offline EN->PT-BR em lote, preservando a estrutura do texto:
    quebras de linha, centralizacao, tokens do jogo ({ICON:..}, {CTL:..},
    {C:..}) e especificadores de formato (%0, %2d, %s). Aplica um pos-edicao
    de portugues europeu -> brasileiro e um glossario opcional.

Como usar
    python3 translate_csv_argos.py \
        --csv saida/ff1.csv saida/ff2.csv \
        --out-dir saida/ \
        --glossary glossary.json \
        --status pendente

    O CSV de saida tem o mesmo nome dentro de --out-dir (ou sufixo .pt.csv
    com --in-place). Linhas ja traduzidas nao sao retraduzidas (idempotente).

Dependencias
    pip install argostranslate
    argospm install translate-en_pt

Como generalizar
    Quase nada e especifico de jogo: tokens sao reconhecidos pelo padrao
    {NOME:valor}, o glossario e um JSON externo e as regras de PT-BR sao
    genericas. O unico heuristico de jogo e DEV_RE (caminhos de diretorios de
    desenvolvimento, como omake/ e mes/), que pode ser ajustado por projeto.
    Para outro par de idiomas use --from/--to.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time

CSV_HEADER = ["id", "original", "traducao", "status", "nota"]
TOKEN_RE = re.compile(r"\{[A-Z]+:[^}]*\}")
FMT_RE = re.compile(r"%(?:\d+[ds]?|[ds])")
DEV_RE = re.compile(r"(?:omake|kaisetu|itemmes|art|mes)/[\w./]*|^[\w/]+/\d+$", re.I)

# --- pos-edicao PT-PT -> PT-BR -------------------------------------------
PTBR_RULES = [
    # pronomes e possessivos
    (r"\bpor si\b", "por você"),
    (r"\bpara si\b", "para você"),
    (r"\ba ti\b", "a você"),
    (r"\bde ti\b", "de você"),
    (r"\bpara ti\b", "para você"),
    (r"\bem ti\b", "em você"),
    (r"\bcontigo\b", "com você"),
    (r"\bconvosco\b", "com vocês"),
    (r"\bconnosco\b", "conosco"),
    (r"\bteu\b", "seu"),
    (r"\btua\b", "sua"),
    (r"\bteus\b", "seus"),
    (r"\btuas\b", "suas"),
    (r"\bvosso\b", "seu"),
    (r"\bvossa\b", "sua"),
    (r"\bvos\b", "vocês"),
    (r"\bvós\b", "vocês"),
    # enclise com -te (europeu) -> forma brasileira
    (r"\b([A-Za-zÀ-ÿ]+)-te\b", r"\1 a você"),
    # construcoes e vocabulario
    (r"\bjá não\b", "não mais"),
    (r"\bde forma a\b", "para"),
    (r"\bpor forma a\b", "para"),
    (r"\ba grupo\b", "o grupo"),
    (r"\bà grupo\b", "ao grupo"),
    (r"\bequipa\b", "equipe"),
    (r"\bfacto\b", "fato"),
    (r"\bcontacto\b", "contato"),
    (r"\becrã\b", "tela"),
    (r"\bcomboio\b", "trem"),
    (r"\bautocarro\b", "ônibus"),
    (r"\btelemóvel\b", "celular"),
    (r"\bgelado\b", "sorvete"),
    (r"\bsumo\b", "suco"),
    (r"\bfrigorífico\b", "geladeira"),
    (r"\bcasa de banho\b", "banheiro"),
    (r"\bpequeno-almoço\b", "café da manhã"),
    (r"\brapariga\b", "garota"),
    (r"\bmiúdo\b", "garoto"),
    (r"\bfixe\b", "legal"),
    (r"\butilizador\b", "usuário"),
    (r"\bficheiro\b", "arquivo"),
    (r"\bregistar\b", "registrar"),
    (r"\bacção\b", "ação"),
    (r"\bacções\b", "ações"),
    (r"\bobjecto\b", "objeto"),
    (r"\bdirecção\b", "direção"),
    (r"\bactividade\b", "atividade"),
    (r"\bactual\b", "atual"),
    (r"\bóptimo\b", "ótimo"),
    (r"\bcolectivo\b", "coletivo"),
    # grafia: consoantes mudas e acentos
    (r"cç", "ç"),
    (r"\b([a-záéíóúâêôãõç]+)ó([nm])ic", r"\1ô\2ic"),
    (r"\bprémio\b", "prêmio"),
    (r"\bgénio\b", "gênio"),
    (r"\bténis\b", "tênis"),
    (r"\bAntónio\b", "Antônio"),
    # formas verbais de 2a pessoa (tu) -> voce
    (r"\bés\b", "é"),
    (r"\btens\b", "tem"),
    (r"\btens\b", "tem"),
    (r"\bvais\b", "vai"),
    (r"\bpodes\b", "pode"),
    (r"\bqueres\b", "quer"),
    (r"\bfazes\b", "faz"),
    (r"\bsabes\b", "sabe"),
    (r"\bestás\b", "está"),
    (r"\bfoste\b", "foi"),
    (r"\btiveste\b", "teve"),
    (r"\bdevias\b", "deveria"),
    (r"\bpodias\b", "poderia"),
    (r"\bquerias\b", "queria"),
    (r"\bfiques\b", "fique"),
    (r"\bconsegues\b", "consegue"),
    (r"\bprecisas\b", "precisa"),
    (r"\bachas\b", "acha"),
    (r"\bpensas\b", "pensa"),
    (r"\bfalas\b", "fala"),
    (r"\bolhas\b", "olha"),
    (r"\bouves\b", "ouve"),
    (r"\bsentes\b", "sente"),
    (r"\bvives\b", "vive"),
    (r"\bmoras\b", "mora"),
    (r"\bgostas\b", "gosta"),
    (r"\bdeixas\b", "deixa"),
    (r"\blevas\b", "leva"),
    (r"\bvoltas\b", "volta"),
    (r"\bentras\b", "entra"),
    (r"\bficas\b", "fica"),
    (r"\bchegas\b", "chega"),
    (r"\bpassas\b", "passa"),
    (r"\busas\b", "usa"),
    (r"\bganhas\b", "ganha"),
    (r"\bperdes\b", "perde"),
    (r"\bsalvas\b", "salva"),
    (r"\bcuras\b", "cura"),
    (r"\bdeves\b", "deve"),
    (r"\btu\b", "você"),
]
PTBR_RULES = [(re.compile(p, re.I), r) for p, r in PTBR_RULES]

# Formas de 2a pessoa (tu/vos) que o Argos ainda deixa passar. A conversao
# para o tratamento "voce" e feita por mapa exato para nao atingir
# substantivos parecidos (ex.: lugares, altares, perdas, pecas).
VERB2S = {
    "derrotaste": "derrotou", "viste": "viu", "encontraste": "encontrou",
    "ouviste": "ouviu", "alcançaste": "alcançou", "perdeste": "perdeu",
    "conseguiste": "conseguiu", "trouxeste": "trouxe", "ganhaste": "ganhou",
    "salvaste": "salvou", "destruíste": "destruiu", "sangraste": "sangrou",
    "conheceste": "conheceu", "mataste": "matou", "pensaste": "pensou",
    "tiraste": "tirou", "aprendeste": "aprendeu", "disseste": "disse",
    "mexeste": "mexeu", "caíste": "caiu", "chegaste": "chegou",
    "cresceste": "cresceu", "fizeste": "fez", "provaste": "provou",
    "infiltraste": "infiltrou", "voltaste": "voltou",
    "enfrentaste": "enfrentou", "pediste": "pediu", "mostraste": "mostrou",
    "recuperaste": "recuperou", "tornaste": "tornou", "cumpriste": "cumpriu",
    "mudaste": "mudou", "aguentavas": "aguentava", "estavas": "estava",
    "tinhas": "tinha", "terias": "teria", "gostarias": "gostaria",
    "dirias": "diria", "ficarias": "ficaria", "planeias": "planeja",
    "insistes": "insiste", "dizes": "diz", "vens": "vem", "vês": "vê",
    "dás": "dá", "conheces": "conhece", "pareces": "parece",
    "preocupes": "preocupe", "faças": "faça", "vás": "vá", "sejas": "seja",
    "tenhas": "tenha", "possas": "possa", "vejas": "veja",
    "podeis": "podem", "estais": "estão", "sois": "são",
    "encontrares": "encontrar", "salvares": "salvar",
    "precisares": "precisar", "desviares": "desviar",
    "entrares": "entrar", "ajudares": "ajudar", "voltares": "voltar",
    "acabares": "acabar", "afastares": "afastar", "estragares": "estragar",
    "começares": "começar", "aceitares": "aceitar",
    "contratares": "contratar", "levares": "levar",
    "combinares": "combinar", "passares": "passar", "estares": "estar",
    "quiseres": "quiser", "puderes": "puder",
    "devolveres": "devolver", "dizeres": "dizer", "meteres": "meter",
    "teres": "ter", "trazeres": "trazer", "estiveres": "estiver",
    "tiveres": "tiver", "conseguires": "conseguir",
    "desistires": "desistir", "partires": "partir",
}
_VERB2S_RE = re.compile(
    r"\b(?:%s)\b" % "|".join(sorted((re.escape(k) for k in VERB2S),
                                    key=len, reverse=True)), re.I)

# Colocacao pronominal/imperativo com clitico (PT-PT -> PT-BR).
CLITIC_FIXES = [
    (r"\bdiz-me\b", "diga-me"), (r"\bdiz-lhe\b", "diga-lhe"),
    (r"\bdiz-lhes\b", "diga-lhes"), (r"\bdeixa-me\b", "deixe-me"),
    (r"\bdeixa-o\b", "deixe-o"), (r"\bdeixa-a\b", "deixe-a"),
    (r"\bdá-me\b", "dê-me"), (r"\bperdoa-me\b", "perdoe-me"),
    (r"\bleva-o\b", "leve-o"), (r"\bleva-a\b", "leve-a"),
    (r"\bajuda-me\b", "ajude-me"), (r"\bouve-me\b", "ouça-me"),
    (r"\bescuta-me\b", "escute-me"), (r"\bsegue-me\b", "siga-me"),
    (r"\bespera-me\b", "espere-me"),
    (r"\bpermitir-me\b", "permitir-me"),
    (r"\bPermites-me\b", "Permita-me"),
    (r"\bte posso\b", "posso te"), (r"\bte possa\b", "possa te"),
    (r"\bte poderia\b", "poderia te"), (r"\bte tenha\b", "tenha te"),
    (r"\bte vamos\b", "vamos te"), (r"\bte vão\b", "vão te"),
    (r"\bnão te meteres\b", "não se meta"),
    (r"\bte desviar\b", "se desviar"),
    (r"\bpara seres\b", "para ser"),
]
CLITIC_FIXES = [(re.compile(p, re.I), r) for p, r in CLITIC_FIXES]


def _match_case(word, repl):
    return repl[0].upper() + repl[1:] if word[:1].isupper() else repl


def _apply_language_fixes(text):
    text = _VERB2S_RE.sub(lambda m: _match_case(m.group(0),
                                                VERB2S[m.group(0).lower()]), text)
    for pat, rep in CLITIC_FIXES:
        text = pat.sub(lambda m: _match_case(m.group(0), rep), text)
    return text

SPACE_FIXES = [
    (re.compile(r"\s+([,.;:!?])"), r"\1"),
    (re.compile(r"([,;:])(?=\S)"), r"\1 "),
    (re.compile(r"\s{2,}"), " "),
    (re.compile(r"\s+$"), ""),
]

VOWELS = "aeiouáéíóúâêôãõà"

# "está a fazer" (PT-PT) -> "está fazendo" (PT-BR)
GER_RE = re.compile(
    r"\b(est(?:á|ão|ava|avam|ive|iveram|ou|iveram))\s+a\s+"
    r"([a-záéíóúâêôãõç]+?)(-se|-me|-te|-lhe|-nos|-vos)?\b", re.I)
GER_IRREG = {
    "ser": "sendo", "ter": "tendo", "ir": "indo", "vir": "vindo",
    "pôr": "pondo", "dizer": "dizendo", "fazer": "fazendo",
    "trazer": "trazendo", "ver": "vendo", "ler": "lendo", "dar": "dando",
    "poder": "podendo", "querer": "querendo", "saber": "sabendo",
    "haver": "havendo", "ouvir": "ouvindo", "pedir": "pedindo",
    "dormir": "dormindo", "sentir": "sentindo", "seguir": "seguindo",
    "subir": "subindo", "sair": "saindo", "cair": "caindo",
    "construir": "construindo", "destruir": "destruindo",
}


def _gerund(inf):
    inf = inf.lower()
    if inf in GER_IRREG:
        return GER_IRREG[inf]
    if inf.endswith("ar"):
        return inf[:-2] + "ando"
    if inf.endswith("er"):
        return inf[:-2] + "endo"
    if inf.endswith("ir"):
        return inf[:-2] + "indo"
    return inf


def post_edit(text, glossary=None, space_fixes=True):
    for pat, rep in PTBR_RULES:
        text = pat.sub(rep, text)
    text = _apply_language_fixes(text)
    text = GER_RE.sub(
        lambda m: "%s %s%s" % (m.group(1), _gerund(m.group(2)), m.group(3) or ""),
        text)
    if glossary:
        for pat, rep in glossary:
            text = pat.sub(rep, text)
    if space_fixes:
        for pat, rep in SPACE_FIXES:
            text = pat.sub(rep, text)
    if text:
        text = text[0].upper() + text[1:]
    return text


def load_glossary(path):
    if not path:
        return []
    data = json.load(open(path, encoding="utf-8"))
    out = []
    for item in data.get("fixes", []):
        out.append((re.compile(item["pattern"], re.I), item["replace"]))
    return out


# --- estrutura de linhas ---------------------------------------------------

def blocks(original):
    """Divide em blocos separados por linha em branco; devolve lista de linhas."""
    return original.split("\n")


def layout(original, translated):
    """Redistribui a traducao nas linhas do original (larguras/centralizacao)."""
    if not translated:
        return translated
    orig_lines = original.split("\n")
    content = [l for l in orig_lines if l.strip()]
    if not content:
        return translated
    widths = [len(l) for l in content]
    centered = [len(l) - len(l.lstrip()) >= 2 for l in content]
    if len(content) == 1:
        # nomes/mensagens de uma linha nunca sao quebrados em varias, mas
        # textos centralizados por espacos sao re-centralizados preservando o
        # centro do original (as margens nao seguem a largura do texto).
        if centered[0]:
            line = content[0]
            lead = len(line) - len(line.lstrip())
            center = lead + len(line.strip()) / 2.0
            pad = max(0, int(round(center - len(translated.strip()) / 2.0)))
            return " " * pad + translated.strip()
        return translated
    words = translated.split()
    if not words:
        return translated
    new_lines = []
    cur = ""
    wi = 0
    for w in words:
        cap = widths[min(wi, len(widths) - 1)]
        cand = w if not cur else cur + " " + w
        if len(cand) <= cap or not cur:
            cur = cand
        else:
            new_lines.append(cur)
            wi += 1
            cur = w
    if cur:
        new_lines.append(cur)
    # aplica centralizacao onde o original era centralizado
    for i, line in enumerate(new_lines):
        if i < len(centered) and centered[i]:
            w = widths[min(i, len(widths) - 1)]
            pad = max(0, (w - len(line)) // 2)
            new_lines[i] = " " * pad + line
    # reinsere linhas em branco nas posicoes originais
    out = []
    ci = 0
    for l in orig_lines:
        if l.strip():
            if ci < len(new_lines):
                out.append(new_lines[ci])
                ci += 1
            else:
                out.append("")
        else:
            out.append("")
    while ci < len(new_lines):
        out.append(new_lines[ci])
        ci += 1
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", nargs="+", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--glossary")
    ap.add_argument("--from", dest="src", default="en")
    ap.add_argument("--to", dest="dst", default="pt")
    ap.add_argument("--status", default="pendente", help="status a traduzir")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-letters", type=int, default=2)
    ap.add_argument("--sleep", type=float, default=0.0)
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)

    import argostranslate.translate as at
    cache = {}

    def tr(text):
        if text in cache:
            return cache[text]
        out = at.translate(text, args.src, args.dst)
        cache[text] = out
        return out

    glossary = load_glossary(args.glossary)
    total = done = skipped = pending = 0
    t0 = time.time()

    for path in args.csv:
        rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
        out_rows = []
        for row in rows:
            total += 1
            status = (row.get("status") or "").strip().lower()
            original = row.get("original") or ""
            nota = row.get("nota") or ""
            if status != args.status:
                out_rows.append(row)
                continue
            letters = len(re.sub(r"[^A-Za-z]", "", original))
            if letters < args.min_letters or DEV_RE.search(original.strip()):
                row["status"] = "ignorado"
                row["nota"] = (nota + "; " if nota else "") + "texto interno/curto"
                out_rows.append(row)
                skipped += 1
                continue
            if FMT_RE.search(original):
                row["status"] = "adiado"
                row["nota"] = (nota + "; " if nota else "") + "revisar: especificador de formato"
                out_rows.append(row)
                pending += 1
                continue
            if args.limit and done >= args.limit:
                out_rows.append(row)
                continue
            # traduz segmento a segmento, preservando tokens
            result = []
            pos = 0
            for m in TOKEN_RE.finditer(original):
                seg = original[pos:m.start()]
                result.append(_translate_segment(seg, tr, glossary, row))
                result.append(m.group(0))
                pos = m.end()
            result.append(_translate_segment(original[pos:], tr, glossary, row))
            row["traducao"] = "".join(result)
            row["status"] = "traduzido"
            if not row["traducao"].strip():
                row["status"] = "adiado"
                row["nota"] = (nota + "; " if nota else "") + "traducao vazia"
            out_rows.append(row)
            done += 1
            if args.sleep:
                time.sleep(args.sleep)
        dst = os.path.join(args.out_dir, os.path.basename(path))
        with open(dst, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=CSV_HEADER)
            w.writeheader()
            for r in out_rows:
                w.writerow({k: r.get(k, "") for k in CSV_HEADER})
        print("  %s -> %s (%d linhas)" % (path, dst, len(out_rows)))

    dt = time.time() - t0
    print("  traduzidas: %d, ignoradas: %d, adiadas: %d, total: %d (%.1fs)"
          % (done, skipped, pending, total, dt))
    return 0


def _translate_segment(seg, tr, glossary, row):
    """Traduz um trecho sem tokens, respeitando paragrafos e larguras."""
    if not seg.strip():
        return seg
    lines = seg.split("\n")
    out = []
    i = 0
    while i < len(lines):
        if not lines[i].strip():
            out.append(lines[i])
            i += 1
            continue
        j = i
        while j < len(lines) and lines[j].strip():
            j += 1
        group = lines[i:j]
        text = " ".join(l.strip() for l in group)
        translated = post_edit(tr(text), glossary)
        translated = layout("\n".join(group), translated)
        out.append(translated)
        i = j
    result = "\n".join(out)
    # recupera espacos nas bordas do trecho original
    lead = seg[:len(seg) - len(seg.lstrip())]
    trail = seg[len(seg.rstrip()):]
    core = result.strip("\n")
    if seg.startswith("\n"):
        core = lead + core
    if seg.endswith("\n"):
        core = core + trail
    return core


if __name__ == "__main__":
    sys.exit(main())
