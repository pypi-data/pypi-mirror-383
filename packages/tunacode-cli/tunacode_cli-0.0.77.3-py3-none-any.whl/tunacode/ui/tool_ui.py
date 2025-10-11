"""
Tool confirmation UI components, separated from business logic.
"""

from typing import TYPE_CHECKING, Optional

from rich.box import ROUNDED
from rich.markdown import Markdown
from rich.padding import Padding
from rich.panel import Panel

from tunacode.configuration.settings import ApplicationSettings
from tunacode.constants import APP_NAME, TOOL_UPDATE_FILE, TOOL_WRITE_FILE, UI_COLORS
from tunacode.core.tool_handler import ToolConfirmationRequest, ToolConfirmationResponse
from tunacode.types import ToolArgs
from tunacode.ui import console as ui
from tunacode.utils.diff_utils import render_file_diff
from tunacode.utils.file_utils import DotDict
from tunacode.utils.text_utils import ext_to_lang, key_to_title

if TYPE_CHECKING:
    from tunacode.core.state import StateManager


class ToolUI:
    """Handles tool confirmation UI presentation."""

    REJECTION_FEEDBACK_SESSION = "tool_rejection_feedback"
    REJECTION_GUIDANCE_PROMPT = (
        "  Describe what the agent should do instead (leave blank to skip): "
    )

    def __init__(self):
        self.colors = DotDict(UI_COLORS)

    def _get_tool_title(self, tool_name: str) -> str:
        """
        Get the display title for a tool.

        Args:
            tool_name: Name of the tool.

        Returns:
            str: Display title.
        """
        app_settings = ApplicationSettings()
        if tool_name in app_settings.internal_tools:
            return f"Tool({tool_name})"
        else:
            return f"MCP({tool_name})"

    def _create_code_block(self, filepath: str, content: str) -> Markdown:
        """
        Create a code block for the given file path and content.

        Args:
            filepath: The path to the file.
            content: The content of the file.

        Returns:
            Markdown: A Markdown object representing the code block.
        """
        lang = ext_to_lang(filepath)
        code_block = f"```{lang}\n{content}\n```"
        return ui.markdown(code_block)

    def _render_args(self, tool_name: str, args: ToolArgs) -> str:
        """
        Render the tool arguments for display.

        Args:
            tool_name: Name of the tool.
            args: Tool arguments.

        Returns:
            str: Formatted arguments for display.
        """
        # Show diff between `target` and `patch` on file updates
        if tool_name == TOOL_UPDATE_FILE:
            return render_file_diff(args["target"], args["patch"], self.colors)

        # Show file content on write_file
        elif tool_name == TOOL_WRITE_FILE:
            lang = ext_to_lang(args["filepath"])
            code_block = f"```{lang}\n{args['content']}\n```"
            return code_block

        # Default to showing key and value on new line
        content = ""
        for key, value in args.items():
            if isinstance(value, list):
                content += f"{key_to_title(key)}:\n"
                for item in value:
                    content += f"  - {item}\n"
                content += "\n"
            else:
                # If string length is over 200 characters, split to new line
                value = str(value)
                content += f"{key_to_title(key)}:"
                if len(value) > 200:
                    content += f"\n{value}\n\n"
                else:
                    content += f" {value}\n\n"
        return content.strip()

    async def show_confirmation(
        self, request: ToolConfirmationRequest, state_manager: Optional["StateManager"] = None
    ) -> ToolConfirmationResponse:
        """
        Show tool confirmation UI and get user response.

        Args:
            request: The confirmation request.

        Returns:
            ToolConfirmationResponse: User's response to the confirmation.
        """
        title = self._get_tool_title(request.tool_name)
        content = self._render_args(request.tool_name, request.args)

        await ui.tool_confirm(title, content, filepath=request.filepath)

        # If tool call has filepath, show it under panel
        if request.filepath:
            await ui.usage(f"File: {request.filepath}")

        await ui.print("  [1] Yes (default)")
        await ui.print("  [2] Yes, and don't ask again for commands like this")
        await ui.print(f"  [3] No, and tell {APP_NAME} what to do differently")
        resp = (
            await ui.input(
                session_key="tool_confirm",
                pretext="  Choose an option [1/2/3]: ",
                state_manager=state_manager,
            )
            or "1"
        )

        if resp == "2":
            return ToolConfirmationResponse(approved=True, skip_future=True)
        if resp == "3":
            instructions = await self._prompt_rejection_feedback(state_manager)
            return ToolConfirmationResponse(
                approved=False,
                abort=True,
                instructions=instructions,
            )
        return ToolConfirmationResponse(approved=True)

    def show_sync_confirmation(self, request: ToolConfirmationRequest) -> ToolConfirmationResponse:
        """
        Show tool confirmation UI synchronously and get user response.

        Args:
            request: The confirmation request.

        Returns:
            ToolConfirmationResponse: User's response to the confirmation.
        """
        title = self._get_tool_title(request.tool_name)
        content = self._render_args(request.tool_name, request.args)

        # Display styled confirmation panel using direct console output
        # Avoid using sync wrappers that might create event loop conflicts
        panel_obj = Panel(
            Padding(content, (0, 1, 0, 1)),
            title=title,
            title_align="left",
            border_style=self.colors.warning,
            padding=(0, 1),
            box=ROUNDED,
        )
        # Add consistent spacing above panels
        from .constants import DEFAULT_PANEL_PADDING

        ui.console.print(
            Padding(
                panel_obj,
                (
                    DEFAULT_PANEL_PADDING["top"],
                    DEFAULT_PANEL_PADDING["right"],
                    DEFAULT_PANEL_PADDING["bottom"],
                    DEFAULT_PANEL_PADDING["left"],
                ),
            )
        )

        if request.filepath:
            ui.console.print(f"File: {request.filepath}", style=self.colors.muted)

        ui.console.print("  [1] Yes (default)")
        ui.console.print("  [2] Yes, and don't ask again for commands like this")
        ui.console.print(f"  [3] No, and tell {APP_NAME} what to do differently")
        resp = input("  Choose an option [1/2/3]: ").strip() or "1"

        # Add spacing after user choice for better readability
        ui.console.print()

        if resp == "2":
            return ToolConfirmationResponse(approved=True, skip_future=True)
        if resp == "3":
            instructions = self._prompt_rejection_feedback_sync()
            return ToolConfirmationResponse(approved=False, abort=True, instructions=instructions)
        return ToolConfirmationResponse(approved=True)

    async def _prompt_rejection_feedback(self, state_manager: Optional["StateManager"]) -> str:
        guidance = await ui.input(
            session_key=self.REJECTION_FEEDBACK_SESSION,
            pretext=self.REJECTION_GUIDANCE_PROMPT,
            state_manager=state_manager,
        )
        return guidance.strip() if guidance else ""

    def _prompt_rejection_feedback_sync(self) -> str:
        guidance = input(self.REJECTION_GUIDANCE_PROMPT).strip()
        ui.console.print()
        return guidance

    async def log_mcp(self, title: str, args: ToolArgs) -> None:
        """
        Display MCP tool with its arguments.

        Args:
            title: Title to display.
            args: Arguments to display.
        """
        if not args:
            return

        await ui.info(title)
        for key, value in args.items():
            if isinstance(value, list):
                value = ", ".join(value)
            await ui.muted(f"{key}: {value}", spaces=4)
