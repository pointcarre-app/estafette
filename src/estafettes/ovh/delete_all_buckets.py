#!/usr/bin/env python3
"""Delete all OVH buckets safely with date confirmation."""

from estafettes.ovh import OVHEstafette
from datetime import date
import sys


def main():
    try:
        # Get today's date
        today = date.today().strftime("%Y-%m-%d")

        # Initialize estafette
        estafette = OVHEstafette(
            config_file="rclone.conf",
            region="EU-WEST-PAR",  # Change to your region
        )

        # Get all buckets
        print("🔍 Fetching bucket list...")
        buckets = estafette.list_buckets()

        if not buckets:
            print("✅ No buckets found!")
            return

        # Display buckets
        print(f"\n📋 Found {len(buckets)} buckets:")
        for i, bucket in enumerate(buckets, 1):
            print(f"  {i}. {bucket.name}")

        # Confirm deletion with today's date
        print(f"\n⚠️  This will DELETE ALL {len(buckets)} buckets and their contents!")
        print(f"🗓️  To confirm, please type today's date: {today}")
        confirm = input("Enter date (YYYY-MM-DD): ").strip()

        if confirm != today:
            print("❌ Cancelled - incorrect date or buckets preserved")
            return

        # Double confirmation
        final_confirm = (
            input(f"\n🚨 Final confirmation: Delete {len(buckets)} buckets? (yes/no): ")
            .strip()
            .lower()
        )
        if final_confirm != "yes":
            print("❌ Cancelled - buckets preserved")
            return

        # Delete each bucket
        print(f"\n🗑️  Deleting {len(buckets)} buckets...")
        success_count = 0

        for i, bucket in enumerate(buckets, 1):
            print(f"  [{i}/{len(buckets)}] Deleting {bucket.name}...", end="")
            try:
                success = estafette.delete_bucket(bucket.name, force=True)
                if success:
                    print(" ✅")
                    success_count += 1
                else:
                    print(" ❌")
            except Exception as e:
                print(f" ❌ Error: {e}")

        print(f"\n✅ Deleted {success_count}/{len(buckets)} buckets successfully")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
