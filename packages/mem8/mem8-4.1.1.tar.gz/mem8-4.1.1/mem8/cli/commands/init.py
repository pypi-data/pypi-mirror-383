#!/usr/bin/env python3
"""
Init command for workspace initialization.
"""

import typer
from typing import Annotated, Optional, Dict, Any
from pathlib import Path

from ..state import set_app_state, handle_command_error
from ..utils import get_console
from ...core.templates import TemplateManager

# Get console instance
console = get_console()


def _interactive_prompt_for_init(context: Dict[str, Any]) -> Dict[str, Any]:
    """Interactive prompts for init command configuration."""
    import typer
    from ...core.config import Config
    from ...core.smart_setup import get_git_username
    from ...integrations.github import get_consistent_github_context

    # Load saved preferences
    config = Config()
    defaults = config.get_workflow_defaults()

    # Show project type
    if context['is_claude_code_project']:
        console.print("\nClaude Code project")
    else:
        console.print(f"\n{context['project_type'].title()} project")

    # Get consistent GitHub context early
    gh_context = get_consistent_github_context(prefer_authenticated_user=True)

    # Always use GitHub as workflow provider (simplified - no choice)
    interactive_config = {"workflow_provider": "github"}

    # GitHub configuration
    console.print("\n[cyan]GitHub Configuration[/cyan]")

    # Use consistent GitHub context for defaults (prefer active account over saved preferences)
    # Use current directory name as default for repo name instead of saved preference
    # This ensures each project gets a sensible default based on its directory name
    current_dir_name = Path.cwd().name
    github_org = gh_context.get("org") or gh_context.get("username") or defaults.get('github_org') or "your-org"
    # Prioritize: detected repo > current directory name > saved preference
    github_repo = gh_context.get("repo") or current_dir_name

    if gh_context.get("org") and gh_context.get("repo"):
        console.print(f"  Detected: {github_org}/{github_repo}")
    console.print("")

    github_org = typer.prompt("GitHub org/username", default=github_org)
    github_repo = typer.prompt("Repository name", default=github_repo)
    interactive_config.update({
        "github_org": github_org,
        "github_repo": github_repo
    })

    # Template selection
    existing_memory = Path('memory').exists()
    default_template = 'claude-config' if existing_memory else defaults.get('template', 'full')
    template_choices = ["full", "claude-config", "memory-repo", "none"]

    console.print("\n[cyan]Template[/cyan]")
    console.print("  full           - Commands + memory structure")
    console.print("  claude-config  - Commands only")
    console.print("  memory-repo  - Memory structure only")
    console.print("  none           - Skip templates")
    console.print("")

    template = typer.prompt("Template", default=default_template)
    while template not in template_choices:
        console.print("[red]Choose: full, claude-config, memory-repo, or none[/red]")
        template = typer.prompt("Template", default=default_template)

    interactive_config["template"] = template if template != "none" else None

    # Username
    default_username = gh_context["username"] or get_git_username() or "user"
    interactive_username = typer.prompt("\nUsername for memory", default=default_username)
    interactive_config["username"] = interactive_username

    # Workflow automation (always GitHub, simplified)
    if template and template != "none":
        automation_choices = ["standard", "none"]
        default_automation = defaults.get('automation_level', 'standard')
        workflow_automation = typer.prompt(
            "Workflow automation (standard/none)",
            default=default_automation
        )
        while workflow_automation not in automation_choices:
            console.print("[red]Choose: standard or none[/red]")
            workflow_automation = typer.prompt("Workflow automation", default="standard")
        interactive_config["workflow_automation"] = workflow_automation

    # Skip repo discovery and shared memory - keep it simple
    interactive_config["include_repos"] = False
    interactive_config["shared_enabled"] = False

    # Remove web UI launch question - per feedback
    interactive_config["web"] = False

    # Save workflow preferences for future use
    # Note: github_repo is intentionally NOT saved as it's project-specific
    if template and template != "none":
        config.save_workflow_preferences(
            template=template,
            workflow_provider=interactive_config.get('workflow_provider', 'github'),
            automation_level=interactive_config.get('workflow_automation', 'standard'),
            github_org=interactive_config.get('github_org')
        )
        console.print("\n[dim]💾 Saved preferences for future init commands[/dim]")

    return interactive_config


def _should_skip_confirmation(force: bool, non_interactive: bool, existing_memory: bool, existing_claude: bool, should_install_templates: bool, template_type: str) -> tuple[bool, list[str]]:
    """Determine if we should skip confirmation and what issues exist."""
    needs_confirmation = False
    issues = []

    if existing_memory and not force:
        issues.append("memory/ directory already exists")
        needs_confirmation = True

    if existing_claude and should_install_templates and "claude" in (template_type or "") and not force:
        issues.append(".claude/ directory already exists")
        needs_confirmation = True

    return needs_confirmation, issues


def _handle_init_confirmation(needs_confirmation: bool, issues: list[str], force: bool, non_interactive: bool) -> bool:
    """Handle confirmation logic for init command. Returns True if should proceed."""
    if not needs_confirmation:
        return True

    if force:
        return True

    console.print("\n⚠️  [yellow]Existing directories detected:[/yellow]")
    for issue in issues:
        console.print(f"  • {issue}")

    console.print("\n💡 [cyan]What will happen:[/cyan]")
    console.print("  • Existing directories will be [bold]preserved (not overwritten)[/bold]")
    console.print("  • Only missing components will be created")
    console.print("  • Use [dim]--force[/dim] to overwrite existing directories")

    if non_interactive:
        console.print("\n❌ [red]Cannot proceed in non-interactive mode with existing data[/red]")
        console.print("💡 [dim]Use --force to proceed anyway, or run from a clean directory[/dim]")
        return False

    import typer
    proceed = typer.confirm("\nContinue with setup (will skip existing directories)?")
    if not proceed:
        console.print("❌ [yellow]Setup cancelled[/yellow]")
        return False

    return True


def _validate_init_workspace_location(force: bool, non_interactive: bool = False) -> Path:
    """Validate workspace location for init command only."""
    from ...core.utils import get_git_info
    import typer

    current_dir = Path.cwd()
    git_info = get_git_info()

    # Prefer git repository root when available
    if git_info['is_git_repo']:
        repo_root = git_info['repo_root']
        if repo_root != current_dir:
            # Notify user we're using git root instead of cwd
            typer.secho(
                f"📁 Using git repository root: {repo_root}",
                fg=typer.colors.BLUE
            )
        return repo_root

    # If not in a git repository, warn user about non-standard location
    if force:
        typer.secho(f"🔧 Force mode: Using current directory {current_dir}", fg=typer.colors.CYAN)
        return current_dir

    if non_interactive:
        typer.secho(f"⚠️  Non-interactive mode: Using current directory {current_dir} (not a git repository)", fg=typer.colors.YELLOW)
        return current_dir

    typer.secho("⚠️  Warning: Creating .claude directory outside git repository", fg=typer.colors.YELLOW)
    typer.secho(f"Current directory: {current_dir}", fg=typer.colors.WHITE)
    typer.secho("This directory is not part of a git repository.", fg=typer.colors.YELLOW)
    typer.echo()
    typer.secho("Consider running this command from a git repository root.", fg=typer.colors.BLUE)
    typer.echo()

    if not typer.confirm("Continue with current directory anyway?", default=False):
        typer.secho("Cancelled. Please run from an appropriate project root.", fg=typer.colors.RED)
        raise typer.Exit(1)

    return current_dir


def register_init_command(app: typer.Typer):
    """Register the init command."""

    @app.command()
    def init(
        template: Optional[str] = typer.Option(
            None,
            "--template", "-t",
            help="Force specific template: claude-config, memory-repo, or full (default: auto-detect)",
        ),
        template_source: Annotated[Optional[str], typer.Option(
            "--template-source", help="External template source: local path, git URL, or GitHub shorthand (org/repo)"
        )] = None,
        repos: Annotated[Optional[str], typer.Option(
            "--repos", help="Comma-separated list of repository paths to discover"
        )] = None,
        shared_dir: Annotated[Optional[Path], typer.Option(
            "--shared-dir", help="Path to shared directory for memory"
        )] = None,
        web: Annotated[bool, typer.Option(
            "--web", help="Launch web UI after setup"
        )] = False,
        force: Annotated[bool, typer.Option(
            "--force", help="⚠️  DANGEROUS: Skip all confirmations and overwrite existing directories without backup"
        )] = False,
        non_interactive: Annotated[bool, typer.Option(
            "--non-interactive", help="Non-interactive mode, use auto-detected defaults without prompts"
        )] = False,
        verbose: Annotated[bool, typer.Option(
            "--verbose", "-v", help="Enable verbose output"
        )] = False
    ):
        """Initialize mem8 workspace with interactive guided setup (default) or auto-detected defaults."""
        from ...core.smart_setup import (
            detect_project_context, generate_smart_config, setup_minimal_structure
        )

        set_app_state(verbose=verbose)

        console.print("[bold]mem8 init[/bold]")

        # INIT-SPECIFIC workspace validation - check git repository before setup
        _validate_init_workspace_location(force, non_interactive)

        try:
            # 1. Auto-detect project context
            if verbose:
                console.print("🔍 [dim]Detecting project configuration...[/dim]")
            context = detect_project_context()

            if verbose:
                console.print(f"[dim]Detected: {context['project_type']} project, "
                            f"{len(context['git_repos'])} repositories found[/dim]")

            # 2. Interactive mode: gather user preferences (default behavior)
            interactive_config = {}
            if not non_interactive and not force:  # Interactive is now the default
                interactive_config = _interactive_prompt_for_init(context)

                # Override parameters with interactive values where not explicitly set
                template = template or interactive_config.get('template')
                shared_dir = shared_dir or interactive_config.get('shared_dir')
                web = web or interactive_config.get('web', False)
                repos = repos or interactive_config.get('repos')
            elif force:
                template = template or "full"
            elif non_interactive:
                template = template or "full"

            # 3. Generate smart configuration with interactive overrides
            context['interactive_config'] = interactive_config
            config = generate_smart_config(context, repos)
            if interactive_config:
                config.update(interactive_config)

            # 3. Auto-detect if templates should be installed
            should_install_templates = False
            template_type = template  # Use explicit template if provided

            if template and template != "none":
                # User explicitly requested templates
                should_install_templates = True
            elif template == "none":
                # User explicitly doesn't want templates
                should_install_templates = False
            elif context['is_claude_code_project'] and not template:
                # Auto-detect Claude Code projects need templates
                should_install_templates = True
                template_type = "claude-config"  # Default for Claude projects

            # 3. Check for existing setup and conflicts
            existing_memory = Path('memory').exists()
            existing_claude = Path('.claude').exists()

            needs_confirmation, issues = _should_skip_confirmation(
                force, non_interactive, existing_memory, existing_claude,
                should_install_templates, template_type
            )

            # Only show repository info in verbose mode or if explicitly requested
            if verbose and config.get('repositories'):
                console.print(f"📁 [dim]Including {len(config['repositories'])} repositories[/dim]")

            if shared_dir:
                config['shared_location'] = shared_dir
                config['shared_enabled'] = True  # Enable shared when --shared-dir is provided

            # 4. Handle confirmations if needed
            if not _handle_init_confirmation(needs_confirmation, issues, force, non_interactive):
                return

            # 5. Create directory structure
            setup_result = setup_minimal_structure(config)

            # 6. Install templates if needed
            if should_install_templates and template_type != "none":
                template_name = template_type or "full"
                console.print(f"\nInstalling {template_name} template...")
                template_manager = TemplateManager()
                template_manager.install_templates(
                    template_name, Path.cwd(), force, verbose,
                    interactive_config, template_source, console
                )

            if setup_result['errors']:
                console.print("[red]Errors:[/red]")
                for error in setup_result['errors']:
                    console.print(f"  {error}")
                return

            # Show what was created (only if verbose or something actually created)
            if verbose and setup_result['created']:
                console.print("\nCreated:")
                for created in setup_result['created']:
                    console.print(f"  {created}")

            # Create ~/.mem8 shortcut
            from ...core.config import Config
            config_manager = Config()
            config_manager.create_home_shortcut()

            # Save toolbelt
            try:
                from ...core.toolbelt import save_toolbelt
                output_file = save_toolbelt()
                if verbose:
                    console.print(f"[dim]Saved toolbelt to {output_file}[/dim]")
            except Exception:
                pass  # Non-critical, don't fail on this

            # Done
            console.print("\n[green]✓[/green] Setup complete")
            console.print("  mem8 status  - verify setup")
            console.print("  mem8 search  - find memory")

        except Exception as e:
            handle_command_error(e, verbose, "setup")
