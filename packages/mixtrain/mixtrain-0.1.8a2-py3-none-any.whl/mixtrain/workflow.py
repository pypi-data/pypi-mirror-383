"""Mixtrain Workflow CLI Commands"""

import json
from typing import Optional

import typer
from rich import print as rprint
from rich.table import Table

from mixtrain import MixClient

app = typer.Typer(help="Manage workflows.", invoke_without_command=True)


@app.callback()
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command(name="list")
def list_workflows():
    """List all workflows in the current workspace."""
    try:
        response = MixClient().list_workflows()
        workflows = response.get("data", [])

        if not workflows:
            rprint("[yellow]No workflows found.[/yellow]")
            rprint("Use 'mixtrain workflow create' to create one.")
            return

        # Show workflows
        rprint("[bold]Workflows:[/bold]")
        table = Table("ID", "Name", "Description", "Created At")
        for workflow in workflows:
            table.add_row(
                str(workflow.get("id", "")),
                workflow.get("name", ""),
                workflow.get("description", "")[:50] + "..."
                if len(workflow.get("description", "")) > 50
                else workflow.get("description", ""),
                workflow.get("created_at", ""),
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="create")
def create_workflow(
    workflow_file: str = typer.Argument(..., help="Path to workflow Python file"),
    name: str = typer.Option(None, "--name", "-n", help="Workflow name (defaults to filename)"),
    description: str = typer.Option("", "--description", "-d", help="Workflow description"),
    src_files: Optional[list[str]] = typer.Option(None, "--src", "-s", help="Additional source files to include (can be specified multiple times)"),
):
    """Create a new workflow from a Python file.

    The workflow file should be a Python script that defines your workflow logic.
    You can optionally include additional source files that the workflow depends on.

    Examples:
      mixtrain workflow create train.py --name my-training-workflow
      mixtrain workflow create workflow.py --src utils.py --src config.json
      mixtrain workflow create main.py --name inference --description "Run inference"
    """
    try:
        import os

        # Validate workflow file exists
        if not os.path.exists(workflow_file):
            rprint(f"[red]Error:[/red] Workflow file not found: {workflow_file}")
            raise typer.Exit(1)

        # Default name to filename without extension if not provided
        if not name:
            name = os.path.splitext(os.path.basename(workflow_file))[0]

        # Validate source files exist
        if src_files:
            for src_file in src_files:
                if not os.path.exists(src_file):
                    rprint(f"[red]Error:[/red] Source file not found: {src_file}")
                    raise typer.Exit(1)

        # Create workflow with files
        result = MixClient().create_workflow_with_files(
            name=name,
            description=description,
            workflow_file=workflow_file,
            src_files=src_files or [],
        )
        workflow_data = result.get("data", {})
        rprint(
            f"[green]✓[/green] Successfully created workflow '{workflow_data.get('name')}' (ID: {workflow_data.get('id')})"
        )
        rprint(f"  Uploaded workflow file: {workflow_file}")
        if src_files:
            rprint(f"  Uploaded {len(src_files)} additional source file(s)")

    except FileNotFoundError as e:
        rprint(f"[red]Error:[/red] File not found: {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="get")
def get_workflow(workflow_id: int = typer.Argument(..., help="Workflow ID")):
    """Get details of a specific workflow."""
    try:
        result = MixClient().get_workflow(workflow_id)
        workflow = result.get("data", {})

        rprint(f"[bold]Workflow: {workflow.get('name')}[/bold]")
        rprint(f"ID: {workflow.get('id')}")
        rprint(f"Description: {workflow.get('description')}")
        rprint(f"Created: {workflow.get('created_at')}")
        rprint(f"Updated: {workflow.get('updated_at')}")

        # Show runs
        runs = workflow.get('runs', [])
        if runs:
            rprint(f"\n[bold]Recent Runs ({len(runs)}):[/bold]")
            table = Table("Run ID", "Status", "Started", "Triggered By")
            for run in runs[:10]:  # Show last 10 runs
                # Display user name, email, or ID as fallback
                triggered_by = run.get("triggered_by_name") or run.get("triggered_by_email") or f"User {run.get('triggered_by', 'Unknown')}"
                table.add_row(
                    str(run.get("id", "")),
                    run.get("status", ""),
                    run.get("started_at", "N/A"),
                    triggered_by,
                )
            rprint(table)
        else:
            rprint("\n[yellow]No runs yet.[/yellow]")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="delete")
def delete_workflow(
    workflow_id: int = typer.Argument(..., help="Workflow ID"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Delete a workflow."""
    try:
        if not yes:
            confirm = typer.confirm(
                f"Delete workflow {workflow_id}? This will permanently delete all workflow runs."
            )
            if not confirm:
                rprint("Deletion cancelled.")
                return

        MixClient().delete_workflow(workflow_id)
        rprint(f"[green]✓[/green] Successfully deleted workflow {workflow_id}")

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="run")
def run_workflow(workflow_id: int = typer.Argument(..., help="Workflow ID")):
    """Start a new workflow run."""
    try:
        result = MixClient().start_workflow_run(workflow_id)
        run_data = result.get("data", {})
        rprint(
            f"[green]✓[/green] Started workflow run (Run ID: {run_data.get('id')}, Status: {run_data.get('status')})"
        )

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="cancel")
def cancel_run(
    workflow_id: int = typer.Argument(..., help="Workflow ID"),
    run_id: int = typer.Argument(..., help="Run ID"),
):
    """Cancel a running workflow."""
    try:
        result = MixClient().cancel_workflow_run(workflow_id, run_id)
        run_data = result.get("data", {})
        rprint(
            f"[green]✓[/green] Cancelled workflow run {run_id} (Status: {run_data.get('status')})"
        )

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command(name="runs")
def list_runs(workflow_id: int = typer.Argument(..., help="Workflow ID")):
    """List all runs for a workflow."""
    try:
        response = MixClient().list_workflow_runs(workflow_id)
        runs = response.get("data", [])

        if not runs:
            rprint("[yellow]No runs found for this workflow.[/yellow]")
            return

        rprint(f"[bold]Workflow Runs (Total: {len(runs)}):[/bold]")
        table = Table("Run ID", "Status", "Started", "Completed", "Triggered By")
        for run in runs:
            # Display user name, email, or ID as fallback
            triggered_by = run.get("triggered_by_name") or run.get("triggered_by_email") or f"User {run.get('triggered_by', 'Unknown')}"
            table.add_row(
                str(run.get("id", "")),
                run.get("status", ""),
                run.get("started_at", "N/A"),
                run.get("completed_at", "N/A"),
                triggered_by,
            )
        rprint(table)

    except Exception as e:
        rprint(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)
