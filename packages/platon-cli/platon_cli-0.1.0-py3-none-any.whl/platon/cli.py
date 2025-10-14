#!/usr/bin/env python3
"""
Platon CLI - Unified tool for Vault and Kubernetes operations
"""

import os
import click
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import print as rprint
from rich.prompt import Confirm, Prompt
import questionary
from pathlib import Path

from .config import Config
from .vault import VaultManager
from .kubectl import KubectlManager
from .git import GitRepo
from .utils import (
    handle_error,
    format_output,
    export_to_file,
    watch_logs,
    fuzzy_select,
)

console = Console()
config = Config()


@click.group(invoke_without_command=True)
@click.option("--config-file", default=None, help="Path to config file")
@click.option("--profile", default="default", help="Profile to use")
@click.option("--install-completion", is_flag=True, hidden=True, help="Install shell completion")
@click.option("--show-completion", is_flag=True, hidden=True, help="Show completion script")
@click.pass_context
def cli(ctx, config_file, profile, install_completion, show_completion):
    """Platon CLI - Manage Vault secrets and Kubernetes resources"""

    if install_completion or show_completion:
        shell = Path(os.environ.get("SHELL", "bash")).name
        if show_completion:
            completion(shell)
        else:
            _install_completion(shell)
        sys.exit(0)

    ctx.ensure_object(dict)
    
    if config_file:
        config.load(config_file)
    
    ctx.obj["config"] = config
    ctx.obj["profile"] = profile
    
    # Auto-detect repo if in git directory
    try:
        repo = GitRepo.from_cwd()
        ctx.obj["repo"] = repo
        ctx.obj["vault"] = VaultManager(repo)
        ctx.obj["kubectl"] = KubectlManager(repo)
    except Exception:
        ctx.obj["repo"] = None
    
    # If no command, show interactive menu
    if ctx.invoked_subcommand is None:
        interactive_menu(ctx)


def interactive_menu(ctx):
    """Interactive TUI menu"""
    if not ctx.obj.get("repo"):
        console.print("[red]Not in a git repository![/red]")
        sys.exit(1)
    
    repo = ctx.obj["repo"]
    
    # Display repo info
    panel = Panel(
        f"[green]Repository:[/green] {repo.path}\n"
        f"[green]Vault Path:[/green] {repo.vault_path}\n"
        f"[green]Namespace:[/green] {repo.namespace}",
        title="[bold blue]Platon CLI[/bold blue]",
        border_style="blue",
    )
    console.print(panel)
    
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=[
                "🔐 Vault Operations",
                "☸️  Kubernetes Operations",
                "🔄 Sync Operations",
                "📊 Status & Info",
                "⚙️  Settings",
                "❌ Exit",
            ],
        ).ask()
        
        if choice == "❌ Exit":
            break
        elif choice == "🔐 Vault Operations":
            vault_menu(ctx)
        elif choice == "☸️  Kubernetes Operations":
            kubectl_menu(ctx)
        elif choice == "🔄 Sync Operations":
            sync_menu(ctx)
        elif choice == "📊 Status & Info":
            status_menu(ctx)
        elif choice == "⚙️  Settings":
            settings_menu(ctx)


def vault_menu(ctx):
    """Vault operations submenu"""
    vault = ctx.obj["vault"]
    
    while True:
        choice = questionary.select(
            "Vault Operations:",
            choices=[
                "List all secrets",
                "Get secret",
                "Add/Update secret",
                "Delete secret",
                "Show versions",
                "Diff versions",
                "Export secrets",
                "Import secrets",
                "Back",
            ],
        ).ask()
        
        if choice == "Back":
            break
        elif choice == "List all secrets":
            secrets = vault.list_secrets()
            table = Table(title="Vault Secrets")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            for key, value in secrets.items():
                # Mask sensitive values
                masked = value[:4] + "*" * (len(value) - 4) if len(value) > 4 else "****"
                table.add_row(key, masked)
            console.print(table)
        elif choice == "Get secret":
            key = Prompt.ask("Enter secret key")
            value = vault.get_secret(key)
            if value:
                console.print(f"[green]{key}[/green]: {value}")
        elif choice == "Add/Update secret":
            key = Prompt.ask("Enter secret key")
            value = Prompt.ask("Enter secret value", password=True)
            vault.set_secret(key, value)
            console.print(f"[green]✓[/green] Secret {key} updated")
        # ... more operations


@cli.group()
def vault():
    """Vault secret management commands"""
    pass


@vault.command("get")
@click.argument("key", required=False)
@click.option("--all", is_flag=True, help="Get all secrets")
@click.option("--format", type=click.Choice(["table", "json", "yaml", "env"]), default="table")
@click.option("--output", "-o", type=click.Path(), help="Output to file")
@click.pass_context
def vault_get(ctx, key, all, format, output):
    """Get secrets from Vault"""
    vault = ctx.obj["vault"]
    
    if all or not key:
        secrets = vault.list_secrets()
        formatted = format_output(secrets, format)
        
        if output:
            export_to_file(formatted, output, format)
            console.print(f"[green]✓[/green] Exported to {output}")
        else:
            console.print(formatted)
    else:
        value = vault.get_secret(key)
        console.print(f"{key}={value}")


@vault.command("set")
@click.argument("key")
@click.argument("value", required=False)
@click.option("--from-file", type=click.Path(exists=True), help="Read value from file")
@click.option("--from-stdin", is_flag=True, help="Read value from stdin")
@click.pass_context
def vault_set(ctx, key, value, from_file, from_stdin):
    """Set a secret in Vault"""
    vault = ctx.obj["vault"]
    
    if from_file:
        value = Path(from_file).read_text().strip()
    elif from_stdin:
        value = sys.stdin.read().strip()
    elif not value:
        value = Prompt.ask(f"Enter value for {key}", password=True)
    
    vault.set_secret(key, value)
    console.print(f"[green]✓[/green] Secret {key} updated")


@vault.command("delete")
@click.argument("key")
@click.option("--force", is_flag=True, help="Skip confirmation")
@click.pass_context
def vault_delete(ctx, key, force):
    """Delete a secret from Vault"""
    vault = ctx.obj["vault"]
    
    if not force and not Confirm.ask(f"Delete secret {key}?"):
        return
    
    vault.delete_secret(key)
    console.print(f"[green]✓[/green] Secret {key} deleted")


@vault.command("export")
@click.option("--format", type=click.Choice(["env", "json", "yaml", "dotenv"]), default="env")
@click.option("--output", "-o", type=click.Path(), help="Output file")
@click.option("--clipboard", is_flag=True, help="Copy to clipboard")
@click.pass_context
def vault_export(ctx, format, output, clipboard):
    """Export secrets to various formats"""
    vault = ctx.obj["vault"]
    secrets = vault.list_secrets()
    
    formatted = format_output(secrets, format)
    
    if clipboard:
        import pyperclip
        pyperclip.copy(formatted)
        console.print("[green]✓[/green] Copied to clipboard")
    elif output:
        export_to_file(formatted, output, format)
        console.print(f"[green]✓[/green] Exported to {output}")
    else:
        console.print(formatted)


@vault.command("diff")
@click.option("--version1", type=int, help="First version")
@click.option("--version2", type=int, help="Second version")
@click.pass_context
def vault_diff(ctx, version1, version2):
    """Compare vault secret versions"""
    vault = ctx.obj["vault"]
    diff = vault.diff_versions(version1, version2)
    
    syntax = Syntax(diff, "diff", theme="monokai", line_numbers=True)
    console.print(syntax)


@cli.group()
def k8s():
    """Kubernetes resource management"""
    pass


@k8s.command("pods")
@click.option("--watch", "-w", is_flag=True, help="Watch for changes")
@click.option("--selector", "-l", help="Label selector")
@click.pass_context
def k8s_pods(ctx, watch, selector):
    """List pods"""
    kubectl = ctx.obj["kubectl"]
    
    if watch:
        watch_logs(lambda: kubectl.get_pods(selector))
    else:
        pods = kubectl.get_pods(selector)
        table = Table(title="Pods")
        table.add_column("Name", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Restarts", style="yellow")
        table.add_column("Age", style="blue")
        
        for pod in pods:
            table.add_row(
                pod["name"],
                pod["status"],
                str(pod["restarts"]),
                pod["age"],
            )
        console.print(table)


@k8s.command("logs")
@click.argument("pod", required=False)
@click.option("--follow", "-f", is_flag=True, help="Follow logs")
@click.option("--previous", is_flag=True, help="Show previous logs")
@click.option("--tail", type=int, default=100, help="Lines to show")
@click.option("--container", "-c", help="Container name")
@click.pass_context
def k8s_logs(ctx, pod, follow, previous, tail, container):
    """View pod logs"""
    kubectl = ctx.obj["kubectl"]
    
    if not pod:
        pods = kubectl.get_pods()
        pod = fuzzy_select([p["name"] for p in pods], "Select pod:")
    
    kubectl.logs(pod, follow=follow, previous=previous, tail=tail, container=container)


@k8s.command("exec")
@click.argument("pod", required=False)
@click.option("--container", "-c", help="Container name")
@click.option("--command", default="/bin/bash", help="Command to run")
@click.pass_context
def k8s_exec(ctx, pod, container, command):
    """Execute command in pod"""
    kubectl = ctx.obj["kubectl"]
    
    if not pod:
        pods = kubectl.get_pods()
        pod = fuzzy_select([p["name"] for p in pods], "Select pod:")
    
    kubectl.exec(pod, command, container=container)


@k8s.command("scale")
@click.argument("deployment")
@click.argument("replicas", type=int)
@click.pass_context
def k8s_scale(ctx, deployment, replicas):
    """Scale deployment"""
    kubectl = ctx.obj["kubectl"]
    kubectl.scale(deployment, replicas)
    console.print(f"[green]✓[/green] Scaled {deployment} to {replicas} replicas")


@k8s.command("restart")
@click.argument("deployment")
@click.pass_context
def k8s_restart(ctx, deployment):
    """Restart deployment"""
    kubectl = ctx.obj["kubectl"]
    kubectl.restart(deployment)
    console.print(f"[green]✓[/green] Restarted {deployment}")


@cli.command("sync")
@click.option("--direction", type=click.Choice(["to-env", "from-env"]), default="to-env")
@click.option("--dry-run", is_flag=True, help="Show what would be synced")
@click.pass_context
def sync(ctx, direction, dry_run):
    """Sync secrets between Vault and environment"""
    vault = ctx.obj["vault"]
    
    if direction == "to-env":
        secrets = vault.list_secrets()
        
        if dry_run:
            console.print("[yellow]Would export:[/yellow]")
            for key in secrets:
                console.print(f"  {key}")
        else:
            for key, value in secrets.items():
                import os
                os.environ[key] = value
            console.print(f"[green]✓[/green] Exported {len(secrets)} secrets to environment")
    else:
        # Sync from env to vault
        console.print("[red]Not implemented yet[/red]")


@cli.command("status")
@click.pass_context
def status(ctx):
    """Show overall status"""
    repo = ctx.obj["repo"]
    vault = ctx.obj["vault"]
    kubectl = ctx.obj["kubectl"]
    
    # Create status panels
    vault_status = vault.health_check()
    k8s_status = kubectl.health_check()
    
    console.print(Panel(
        f"[green]Vault:[/green] {vault_status['status']}\n"
        f"[green]Secrets:[/green] {vault_status['secret_count']}\n"
        f"[green]Last Modified:[/green] {vault_status['last_modified']}",
        title="Vault Status",
        border_style="green" if vault_status["healthy"] else "red",
    ))
    
    console.print(Panel(
        f"[green]Cluster:[/green] {k8s_status['cluster']}\n"
        f"[green]Pods:[/green] {k8s_status['pod_count']}\n"
        f"[green]Deployments:[/green] {k8s_status['deployment_count']}",
        title="Kubernetes Status",
        border_style="green" if k8s_status["healthy"] else "red",
    ))


@cli.command("init")
@click.option("--template", type=click.Choice(["basic", "advanced"]), default="basic")
@click.pass_context
def init(ctx, template):
    """Initialize configuration for current repo"""
    repo = ctx.obj.get("repo")

    if not repo:
        console.print("[red]Not in a git repository[/red]")
        return

    config_file = Path(".platon.yaml")

    if config_file.exists():
        if not Confirm.ask("Config already exists. Overwrite?"):
            return

    config_data = {
        "vault_path": repo.vault_path,
        "namespace": repo.namespace,
        "template": template,
    }

    import yaml
    config_file.write_text(yaml.dump(config_data))
    console.print(f"[green]✓[/green] Created {config_file}")


def _install_completion(shell):
    """Install completion for the current shell"""
    if shell == "bash":
        rcfile = Path.home() / ".bashrc"
        marker = "# platon completion"
        script_call = 'eval "$(platon completion bash)"'
    elif shell == "zsh":
        rcfile = Path.home() / ".zshrc"
        marker = "# platon completion"
        script_call = 'eval "$(platon completion zsh)"'
    else:
        console.print(f"[red]Unsupported shell: {shell}[/red]")
        return

    if rcfile.exists():
        content = rcfile.read_text()
        if marker in content:
            console.print(f"[yellow]Completion already installed in {rcfile}[/yellow]")
            return

    with open(rcfile, "a") as f:
        f.write(f"\n{marker}\n{script_call}\n")

    console.print(f"[green]✓[/green] Completion installed to {rcfile}")
    console.print(f"[yellow]Run:[/yellow] source {rcfile}")


@cli.command("completion")
@click.argument("shell", type=click.Choice(["bash", "zsh"]), required=False)
def completion(shell):
    """Generate shell completion script"""
    if not shell:
        shell = Path(os.environ.get("SHELL", "bash")).name

    if shell == "bash":
        script = """
# Platon CLI bash completion
_platon_completion() {
    local IFS=$'\\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _PLATON_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_platon_completion_setup() {
    complete -o nosort -F _platon_completion platon
    complete -o nosort -F _platon_completion plt
}

_platon_completion_setup;
"""
        console.print(script)
        console.print("\n[green]To enable bash completion, run:[/green]")
        console.print("  platon completion bash >> ~/.bashrc")
        console.print("  source ~/.bashrc")

    elif shell == "zsh":
        script = """
# Platon CLI zsh completion
#compdef platon plt

_platon() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[platon] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _PLATON_COMPLETE=zsh_complete platon)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

compdef _platon platon
compdef _platon plt
"""
        console.print(script)
        console.print("\n[green]To enable zsh completion, run:[/green]")
        console.print("  platon completion zsh >> ~/.zshrc")
        console.print("  source ~/.zshrc")


def main():
    """Entry point"""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(130)
    except Exception as e:
        handle_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
