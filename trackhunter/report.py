from datetime import datetime
from typing import List

from .models import TrackResult


def write_results(logs_dir, results: List[TrackResult]) -> None:
    """
    Gera apenas o log textual da execucao.
    Nao gera CSV/Excel.
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"log_execucao_{ts}.txt"
    missing_file = logs_dir / f"nao_encontradas_{ts}.txt"

    # Contadores de resumo.
    total = len(results)
    downloaded = sum(1 for x in results if x.status == "baixada")
    skipped = sum(1 for x in results if x.status == "ja_baixada")
    not_found = sum(1 for x in results if x.status == "nao_encontrada")
    errors = sum(1 for x in results if x.status == "erro")
    success_rows = [x for x in results if x.status == "baixada"]
    skipped_rows = [x for x in results if x.status == "ja_baixada"]
    not_found_rows = [x for x in results if x.status == "nao_encontrada"]
    error_rows = [x for x in results if x.status == "erro"]

    def write_section(fh, title: str, rows: List[TrackResult]) -> None:
        """
        Escreve uma secao do log.
        Separar por status deixa a auditoria mais rapida depois da execucao.
        """
        fh.write(f"\n{title}\n")
        if not rows:
            fh.write("- Nenhuma\n")
            return
        for row in rows:
            fh.write(f"- {row.track} | {row.detail} | {row.file_name}\n")

    with log_file.open("w", encoding="utf-8-sig") as fh:
        # Cabecalho de resumo rapido.
        fh.write("Resumo da execucao\n")
        fh.write(f"Data/Hora: {datetime.now().isoformat()}\n")
        fh.write(f"Total: {total}\n")
        fh.write(f"Baixadas: {downloaded}\n")
        fh.write(f"Ja baixadas/ignoradas: {skipped}\n")
        fh.write(f"Nao encontradas: {not_found}\n")
        fh.write(f"Erros: {errors}\n")
        # Listas detalhadas separadas por status para facilitar leitura.
        write_section(fh, "Concluidas com sucesso", success_rows)
        write_section(fh, "Ja baixadas / ignoradas", skipped_rows)
        write_section(fh, "Nao encontradas", not_found_rows)
        write_section(fh, "Erros", error_rows)

    if not_found_rows:
        with missing_file.open("w", encoding="utf-8-sig") as fh:
            for row in not_found_rows:
                fh.write(f"{row.track}\n")

    print("\nArquivos gerados:")
    print(f"- {log_file}")
    if not_found_rows:
        print(f"- {missing_file}")
