"""Server information report generation."""

from ...models import ServerScoreCard
from ..base import BaseReport
from ..utils import get_server_info


class ServerInfoReport(BaseReport):
    """Report for server information and metadata."""

    @classmethod
    def cli_name(cls) -> str:
        return "server-info"

    @classmethod
    def cli_code(cls) -> str:
        return "SI"

    def __init__(self, scorecard: ServerScoreCard):
        """Initialize and build the server info report."""
        super().__init__(scorecard)
        self._build()

    def _build(self):
        """Build the server info section."""
        self.add_server_info()

    def add_server_info(self) -> "ServerInfoReport":
        """Add server information section."""
        info = get_server_info(self._scorecard)

        # Add title
        self.add_title("Server Information", 2)

        # Always show name and version before collapsible
        if info["name"]:
            self.add_text(f"**Name:** {info['name']}")
            self.add_blank_line()
        if info["version"]:
            self.add_text(f"**Version:** {info['version']}")
            self.add_blank_line()

        # Put remaining info in collapsible section
        if self._options.use_collapsible:
            self.add_text("<details>")
            self.add_text("<summary>Toggle details</summary>")
            self.add_blank_line()

        self.add_text(f"**Protocol Version:** {info['protocol_version']}")
        self.add_blank_line()

        self.add_text("**Instructions:**")
        self.add_blank_line()
        if info["instructions"]:
            self.add_code_block(info["instructions"])
        else:
            self.add_text("_No instructions_")
        self.add_blank_line()

        if self._options.use_collapsible:
            self.add_text("</details>")
            self.add_blank_line()

        return self
