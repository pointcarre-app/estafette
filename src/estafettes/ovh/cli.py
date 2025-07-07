from __future__ import annotations

import typer
from rich.console import Console
from pathlib import Path

from .ovh_estafette import OVHEstafette

app = typer.Typer(help="OVH Estafette command-line interface")
console = Console()


def _estafette(config: Path | str, region: str) -> OVHEstafette:
    return OVHEstafette(config_file=str(config), region=region, console=console)


@app.command()
def buckets(
    list: bool = typer.Option(False, "--list", help="List buckets"),  # noqa: A002
    delete: str = typer.Option(None, "--delete", help="Delete a bucket by name"),
    force: bool = typer.Option(False, "--force", help="Force delete contents first"),
    config: Path = typer.Option("rclone.conf", "--config", help="rclone.conf path"),
    region: str = typer.Option("EU-WEST-PAR", "--region"),
):
    """Bucket utilities."""
    est = _estafette(config, region)
    if list:
        buckets = est.list_buckets()
        console.rule("[bold yellow]Buckets")
        console.print("\n".join(b.name for b in buckets))
    elif delete:
        est.delete_bucket(delete, force=force)
    else:
        console.print("[red]No action provided. Use --list or --delete.")


@app.command()
def deploy(
    bucket: str = typer.Option(..., "--bucket", help="Target bucket name"),
    source: Path = typer.Option(..., "--source", help="Directory to upload"),
    static_website: bool = typer.Option(False, "--static-website/--no-static-website"),
    skip_cors: bool = typer.Option(False, "--skip-cors/--apply-cors"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview actions without executing"),
    config: Path = typer.Option("rclone.conf", "--config"),
    region: str = typer.Option("EU-WEST-PAR", "--region"),
):
    """Deploy directory contents to a bucket."""
    est = _estafette(config, region)
    result = est.deploy(
        bucket_name=bucket,
        source_dir=str(source),
        static_website=static_website,
        skip_cors=skip_cors,
        dry_run=dry_run,
    )
    if result.success and not dry_run:
        from tests._utils import panel

        panel("\n".join(result.direct_urls), title="Direct URLs", style="cyan")
        if result.website_url:
            panel(result.website_url, title="Website", style="magenta")


@app.command()
def cors_apply(
    bucket: str = typer.Option(..., "--bucket"),
    config: Path = typer.Option("rclone.conf", "--config"),
    region: str = typer.Option("EU-WEST-PAR", "--region"),
):
    """Apply default CORS policy to bucket."""
    est = _estafette(config, region)
    est.cors_manager.apply_cors_policy(bucket, region=region)


if __name__ == "__main__":
    app()
