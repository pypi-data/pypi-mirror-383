import logging
import sys

import click
from colorama import Fore

from tecton import tecton_context
from tecton.cli import printer
from tecton.cli import repo
from tecton.cli import workspace_utils
from tecton.cli.command import TectonGroup
from tecton.cli.engine import update_tecton_state
from tecton.cli.workspace_utils import WorkspaceType
from tecton.cli.workspace_utils import switch_to_workspace


logger = logging.getLogger(__name__)

PROD_WORKSPACE_NAME = "prod"


@click.group("workspace", cls=TectonGroup, is_main_command=True)
def workspace():
    """Manage Tecton Workspaces."""


@workspace.command()
@click.argument("workspace", type=WorkspaceType())
def select(workspace):
    """Select Tecton Workspace."""
    workspace_utils.check_workspace_exists(workspace)
    switch_to_workspace(workspace)


@workspace.command()
def list():
    """List available Tecton Workspaces."""
    current_workspace = tecton_context.get_current_workspace()
    workspaces = workspace_utils.list_workspaces()
    materializable = [w.name for w in workspaces if w.capabilities.materializable]
    nonmaterializable = [w.name for w in workspaces if not w.capabilities.materializable]

    if materializable:
        printer.safe_print("Live Workspaces:")
        for name in materializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")

    # Print whitespace between the two sections if needed.
    if materializable and nonmaterializable:
        printer.safe_print()

    if nonmaterializable:
        printer.safe_print("Development Workspaces:")
        for name in nonmaterializable:
            marker = "*" if name == current_workspace else " "
            printer.safe_print(f"{marker} {name}")


@workspace.command()
def show():
    """Show active Workspace."""
    workspace_name = tecton_context.get_current_workspace()
    workspace = workspace_utils.get_workspace(workspace_name)
    workspace_type = "Live" if workspace.capabilities.materializable else "Development"
    printer.safe_print(f"{workspace_name} ({workspace_type})")


@workspace.command()
@click.argument("workspace")
@click.option(
    "--live/--no-live",
    # Kept for backwards compatibility
    "--automatic-materialization-enabled/--automatic-materialization-disabled",
    default=False,
    help="Create a live Workspace, which enables materialization and online serving.",
)
def create(workspace, live):
    """Create a new Tecton Workspace"""
    # There is a check for this on the server side too, but we optimistically validate
    # here as well to show a pretty error message.
    workspace_names = {w.name for w in workspace_utils.list_workspaces()}
    if workspace in workspace_names:
        printer.safe_print(f"Workspace {workspace} already exists", file=sys.stderr)
        sys.exit(1)

    # create
    workspace_utils.create_workspace(workspace, live)

    # switch to new workspace
    switch_to_workspace(workspace)
    printer.safe_print(
        """
You have created a new, empty workspace. Workspaces let
you create and manage an isolated feature repository.
Running "tecton plan" will compare your local repository
against the remote repository, which is initially empty.
    """
    )


@workspace.command()
@click.argument("workspace", type=WorkspaceType())
@click.option("--yes", "-y", is_flag=True)
def delete(workspace, yes):
    """Delete a Tecton Workspace."""
    # validate
    if workspace == PROD_WORKSPACE_NAME:
        printer.safe_print(f"Deleting Workspace '{PROD_WORKSPACE_NAME}' not allowed.")
        sys.exit(1)

    is_live = workspace_utils.is_live_workspace(workspace)

    # confirm deletion
    confirmation = "y" if yes else None
    while confirmation not in ("y", "n", ""):
        confirmation_text = f'Are you sure you want to delete the workspace "{workspace}"? (y/N)'
        if is_live:
            confirmation_text = f"{Fore.RED}Warning{Fore.RESET}: This will delete any materialized data in this workspace.\n{confirmation_text}"
        confirmation = input(confirmation_text).lower().strip()
    if confirmation == "n" or confirmation == "":
        printer.safe_print("Cancelling delete action.")
        sys.exit(1)

    # archive all fcos in the remote state unconditionally.
    # This will need to be updated when workspaces support materialization.
    update_tecton_state(
        objects=[],
        repo_root="",
        repo_config=None,
        repo_files=[],
        apply=True,
        # Set interactive to False to avoid duplicate confirmation.
        # Confirmation of this action is handled above already.
        interactive=False,
        upgrade_all=False,
        workspace_name=workspace,
    )

    # delete
    workspace_utils.delete_workspace(workspace)

    # switch to prod if deleted current
    if workspace == tecton_context.get_current_workspace():
        switch_to_workspace(PROD_WORKSPACE_NAME)


workspace.add_command(repo.restore)
