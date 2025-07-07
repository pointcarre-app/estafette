from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from typing import Set
import atexit

console = Console()

# Global bucket tracker
_created_buckets: Set[str] = set()
_cleanup_enabled = True


def panel(msg: str, title: str = "INFO", style: str = "info") -> None:
    """Print a bordered panel with the given message."""
    console.print(Panel(msg, title=title, style=style, title_align="left"))


def track_bucket(bucket_name: str) -> None:
    """Track a bucket that was created during testing."""
    _created_buckets.add(bucket_name)
    console.print(f"📝 Tracking bucket: [cyan]{bucket_name}[/cyan]")


def untrack_bucket(bucket_name: str) -> None:
    """Remove a bucket from tracking (when it's been deleted)."""
    _created_buckets.discard(bucket_name)
    console.print(f"✅ Untracked bucket: [green]{bucket_name}[/green]")


def get_tracked_buckets() -> Set[str]:
    """Get all tracked buckets."""
    return _created_buckets.copy()


def disable_cleanup() -> None:
    """Disable automatic bucket cleanup."""
    global _cleanup_enabled
    _cleanup_enabled = False
    console.print("🛡️ Bucket cleanup disabled - test buckets will be preserved")


def cleanup_tracked_buckets() -> None:
    """Clean up all tracked buckets."""
    if not _cleanup_enabled:
        console.print("⏭️ Cleanup disabled - skipping bucket deletion")
        return

    if not _created_buckets:
        console.print("✅ No buckets to clean up")
        return

    console.print(f"🧹 Cleaning up {len(_created_buckets)} test buckets...")

    try:
        from estafettes.ovh.config import OVHConfig
        from estafettes.ovh.bucket_manager import BucketManager

        config = OVHConfig(config_file="rclone.conf")
        bucket_manager = BucketManager(config)

        success_count = 0
        # Create a copy of the set to iterate over since we'll be modifying the original
        buckets_to_delete = list(_created_buckets)

        for bucket_name in buckets_to_delete:
            console.print(f"  🗑️ Deleting {bucket_name}...", end="")
            try:
                # Check if bucket still exists first
                if not bucket_manager.bucket_exists(bucket_name):
                    console.print(" ⏭️ (already deleted)")
                    _created_buckets.discard(bucket_name)
                    success_count += 1
                    continue

                success = bucket_manager.delete_bucket(bucket_name, force=True)
                if success:
                    console.print(" ✅")
                    _created_buckets.discard(bucket_name)
                    success_count += 1
                else:
                    console.print(" ❌")
            except Exception as e:
                console.print(f" ❌ Error: {e}")

        console.print(f"✅ Cleaned up {success_count}/{len(buckets_to_delete)} buckets")

    except Exception as e:
        console.print(f"❌ Cleanup error: {e}")


# Register cleanup at exit
atexit.register(cleanup_tracked_buckets)
