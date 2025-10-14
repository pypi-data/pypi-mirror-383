from collections.abc import Generator, Iterable
from pathlib import Path

import mlflow
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from architxt.bucket.zodb import ZODBTreeBucket
from architxt.metrics import Metrics
from architxt.schema import Schema
from architxt.tree import Tree

__all__ = ['console', 'load_forest', 'show_metrics', 'show_schema']


console = Console()


def show_schema(schema: Schema) -> None:
    schema_str = schema.as_cfg()
    mlflow.log_text(schema_str, 'schema.txt')

    console.print(
        Panel(
            schema_str,
            title="Schema as CFG (labelled nodes only)",
            subtitle='[green]Valid Schema[/]' if schema.verify() else '[red]Invalid Schema[/]',
        )
    )


def show_metrics(metrics: Metrics) -> None:
    with console.status("[cyan]Computing metrics. This may take a while. Please wait..."):
        metrics_table = Table("Metric", "Value", title="Valid instance")

        metrics_table.add_row("Coverage ▲", f"{metrics.coverage():.3f}")
        metrics_table.add_row("Redundancy (1.0) ▼", f"{metrics.redundancy(tau=1.0):.3f}")
        metrics_table.add_row("Redundancy (0.7) ▼", f"{metrics.redundancy(tau=0.7):.3f}")
        metrics_table.add_row("Redundancy (0.5) ▼", f"{metrics.redundancy(tau=0.5):.3f}")

        metrics_table.add_section()

        metrics_table.add_row("Cluster Mutual Information ▲", f"{metrics.cluster_ami():.3f}")
        metrics_table.add_row("Cluster Completeness ▲", f"{metrics.cluster_completeness():.3f}")

        grammar_metrics_table = Table("Metric", "Before Value", "After Value", title="Schema grammar")
        grammar_metrics_table.add_row(
            "Productions ▼",
            str(metrics.num_productions_origin()),
            f"{metrics.num_productions()} ({metrics.ratio_productions() * 100:.3f}%)",
        )
        grammar_metrics_table.add_row(
            "Overlap ▼", f"{metrics.group_overlap_origin():.3f}", f"{metrics.group_overlap():.3f}"
        )
        grammar_metrics_table.add_row(
            "Balance ▲", f"{metrics.group_balance_score_origin():.3f}", f"{metrics.group_balance_score():.3f}"
        )

        console.print(Columns([metrics_table, grammar_metrics_table]))


def load_forest(files: Iterable[str | Path]) -> Generator[Tree, None, None]:
    """
    Load a forest from a list of zodb files.

    :param files: List of file paths to read into a forest.
    :yield: Trees from the list of data files.

    >>> forest = load_forest(['forest1.data', 'forest2.data']) # doctest: +SKIP
    """
    with Progress() as progress:
        task_ids = [progress.add_task(f'Reading {file_path}...', start=False) for file_path in files]

        for file_path, task_id in zip(files, task_ids):
            progress.start_task(task_id)

            with ZODBTreeBucket(storage_path=Path(file_path), read_only=True) as forest:
                for tree in progress.track(forest, task_id=task_id):
                    yield tree.copy()
