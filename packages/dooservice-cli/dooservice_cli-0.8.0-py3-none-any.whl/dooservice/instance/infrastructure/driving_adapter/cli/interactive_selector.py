"""Interactive selector utility for instance selection."""

from typing import List, Optional

import questionary
from rich.console import Console
from rich.table import Table

from dooservice.instance.domain.entities.instance_info import (
    InstanceInfo,
    InstanceStatus,
)


class InteractiveSelector:
    """Utility class for interactive instance selection."""

    def __init__(self):
        self.console = Console()

    def select_instance(
        self, instances: List[InstanceInfo], only_created: bool = True
    ) -> Optional[str]:
        """
        Display an interactive menu for selecting an instance.

        Args:
            instances: List of available instances
            only_created: If True, show only created instances.
                         If False, show only not created.

        Returns:
            Selected instance name or None if cancelled
        """
        # Filter instances based on creation status
        if only_created:
            filtered_instances = [
                inst for inst in instances if inst.status != InstanceStatus.NOT_CREATED
            ]
            filter_msg = "created"
        else:
            filtered_instances = [
                inst for inst in instances if inst.status == InstanceStatus.NOT_CREATED
            ]
            filter_msg = "not created"

        if not filtered_instances:
            self.console.print(f"[yellow]No {filter_msg} instances available[/yellow]")
            return None

        # Show info about available instances after filtering
        total = len(instances)
        available = len(filtered_instances)
        if available != total:
            self.console.print(
                f"[dim]({available} {filter_msg} instance(s) available "
                f"out of {total} total)[/dim]"
            )

        # Build choices with formatted display
        choices = []

        # Calculate max widths for alignment
        max_name_len = (
            max(len(inst.name) for inst in filtered_instances)
            if filtered_instances
            else 0
        )

        for instance in filtered_instances:
            status_symbol = self._get_status_symbol(instance.status.value)

            # Build parts of the display
            name_part = instance.name.ljust(max_name_len)
            status_part = f"[{instance.status.value}]"

            # Version info
            version_info = ""
            if instance.odoo_version and instance.odoo_version != "Unknown":
                version_info = f"Odoo {instance.odoo_version}"

            # Domain info
            domain_info = ""
            if instance.domain:
                domain_info = f"→ {instance.domain}"

            # Services count
            services_info = ""
            if instance.services:
                running_services = sum(
                    1 for s in instance.services if s.status.value == "running"
                )
                total_services = len(instance.services)
                services_info = f"({running_services}/{total_services} services)"

            # Combine all parts with proper spacing
            display_parts = [
                f"{status_symbol}",
                name_part,
                status_part,
            ]

            if version_info:
                display_parts.append(version_info)
            if services_info:
                display_parts.append(services_info)
            if domain_info:
                display_parts.append(domain_info)

            display = " ".join(display_parts)

            choices.append(
                questionary.Choice(
                    title=display,
                    value=instance.name,
                )
            )

        # Show interactive selection menu
        try:
            selected = questionary.select(
                "Select an instance:",
                choices=choices,
                style=questionary.Style(
                    [
                        ("selected", "fg:green bold"),
                        ("pointer", "fg:green bold"),
                        ("highlighted", "fg:green"),
                    ]
                ),
            ).ask()

            return selected  # noqa: RET504

        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Selection cancelled[/yellow]")
            return None

    def display_instances_table(self, instances: List[InstanceInfo]) -> None:
        """
        Display instances in a rich formatted table.

        Args:
            instances: List of instances to display
        """
        if not instances:
            self.console.print("[yellow]No instances found[/yellow]")
            return

        table = Table(
            title="Available Instances",
            show_header=True,
            header_style="bold cyan",
            border_style="blue",
        )

        table.add_column("Instance Name", style="white", no_wrap=True)
        table.add_column("Status", style="white", justify="center")
        table.add_column("Version", justify="center")
        table.add_column("Domain", style="dim")
        table.add_column("Services", justify="center")

        for instance in instances:
            # Status with color
            status_text = self._format_status(instance.status.value)

            # Version
            version = (
                instance.odoo_version
                if instance.odoo_version and instance.odoo_version != "Unknown"
                else "-"
            )

            # Domain
            domain = instance.domain if instance.domain else "-"

            # Services count
            services_count = f"{len(instance.services)}" if instance.services else "0"

            table.add_row(
                instance.name,
                status_text,
                version,
                domain,
                services_count,
            )

        self.console.print(table)

    def _get_status_symbol(self, status: str) -> str:
        """Get emoji/symbol for status."""
        status_symbols = {
            "running": "🟢",
            "stopped": "🔴",
            "partial": "🟡",
            "error": "❌",
            "unknown": "❓",
            "not_created": "⚫",
        }
        return status_symbols.get(status.lower(), "⚪")

    def _format_status(self, status: str) -> str:
        """Format status with color for rich table."""
        status_colors = {
            "running": "[green]●[/green] Running",
            "stopped": "[red]●[/red] Stopped",
            "partial": "[yellow]●[/yellow] Partial",
            "error": "[red]✗[/red] Error",
            "unknown": "[white]?[/white] Unknown",
            "not_created": "[dim]○[/dim] Not Created",
        }
        return status_colors.get(status.lower(), f"[white]?[/white] {status}")

    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Ask for user confirmation.

        Args:
            message: Confirmation message
            default: Default answer

        Returns:
            True if user confirmed, False otherwise
        """
        try:
            return questionary.confirm(message, default=default).ask()
        except (KeyboardInterrupt, EOFError):
            return False
