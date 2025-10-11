import os
import sys
import types

# Ensure prompt_toolkit is imported when available so real completions are exercised
try:  # pragma: no cover - environment guard
    import prompt_toolkit  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback to stub logic below
    prompt_toolkit = None
else:
    sys.modules.setdefault("prompt_toolkit", prompt_toolkit)

# Ensure project src is importable
ROOT_SRC = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
sys.path.insert(0, ROOT_SRC)

# Add stubs directory to path if exists
STUBS_DIR = os.path.join(os.path.dirname(__file__), "stubs")
if os.path.isdir(STUBS_DIR):
    sys.path.insert(0, STUBS_DIR)

# Stub rich if not installed
if "rich" not in sys.modules:
    rich = types.ModuleType("rich")
    console_mod = types.ModuleType("rich.console")

    class Console:
        def print(self, *args, **kwargs):
            pass

    console_mod.Console = Console
    markdown_mod = types.ModuleType("rich.markdown")

    class Markdown(str):
        pass

    markdown_mod.Markdown = Markdown
    text_mod = types.ModuleType("rich.text")

    class Text:
        def __init__(self):
            self.lines = []

        def append(self, text, style=None):
            self.lines.append(text)

    text_mod.Text = Text
    padding_mod = types.ModuleType("rich.padding")

    class Padding:
        def __init__(self, content, pad):
            self.content = content
            self.pad = pad

    padding_mod.Padding = Padding
    panel_mod = types.ModuleType("rich.panel")

    class Panel:
        def __init__(self, *args, **kwargs):
            pass

    panel_mod.Panel = Panel
    box_mod = types.ModuleType("rich.box")
    box_mod.ROUNDED = None

    rich.console = console_mod
    rich.markdown = markdown_mod
    rich.text = text_mod
    rich.padding = padding_mod
    rich.panel = panel_mod
    rich.box = box_mod

    sys.modules["rich"] = rich
    sys.modules["rich.console"] = console_mod
    sys.modules["rich.markdown"] = markdown_mod
    sys.modules["rich.text"] = text_mod
    sys.modules["rich.padding"] = padding_mod
    sys.modules["rich.panel"] = panel_mod
    sys.modules["rich.box"] = box_mod

# Stub typer if not installed
if "typer" not in sys.modules:
    typer = types.ModuleType("typer")

    class Typer:
        def __init__(self, *args, **kwargs):
            pass

        def command(self, *args, **kwargs):
            def decorator(fn):
                return fn

            return decorator

        def __call__(self, *args, **kwargs):
            pass

    typer.Typer = Typer
    typer.Option = lambda *args, **kwargs: None
    sys.modules["typer"] = typer

# Stub pydantic_ai if not installed
if "pydantic_ai" not in sys.modules:
    pai = types.ModuleType("pydantic_ai")

    class Agent:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def iter(self, *args, **kwargs):
            # This is an async generator stub for testing
            # Using empty async generator pattern
            for _ in []:
                yield

        def run_mcp_servers(self):
            # Return a context manager for MCP servers
            class MCPContext:
                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    pass

            return MCPContext()

    pai.Agent = Agent
    pai.Tool = lambda *args, **kwargs: None
    messages = types.ModuleType("pydantic_ai.messages")

    class ModelRequest:
        def __init__(self, parts=None, kind=None):
            self.parts = parts or []
            self.kind = kind

    class ToolReturnPart:
        def __init__(self, tool_name="", content="", tool_call_id="", timestamp=None, part_kind=""):
            self.tool_name = tool_name
            self.content = content
            self.tool_call_id = tool_call_id
            self.part_kind = part_kind

    messages.ModelRequest = ModelRequest
    messages.ToolReturnPart = ToolReturnPart
    pai.messages = messages
    exceptions = types.ModuleType("pydantic_ai.exceptions")

    class ModelRetry(Exception):
        pass

    class UnexpectedModelBehavior(Exception):
        pass

    exceptions.ModelRetry = ModelRetry
    exceptions.UnexpectedModelBehavior = UnexpectedModelBehavior
    pai.exceptions = exceptions
    pai.ModelRetry = ModelRetry
    pai.UnexpectedModelBehavior = UnexpectedModelBehavior
    mcp_mod = types.ModuleType("pydantic_ai.mcp")

    class MCPServerStdio:
        pass

    mcp_mod.MCPServerStdio = MCPServerStdio
    pai.mcp = mcp_mod
    sys.modules["pydantic_ai"] = pai
    sys.modules["pydantic_ai.messages"] = messages
    sys.modules["pydantic_ai.exceptions"] = exceptions
    sys.modules["pydantic_ai.mcp"] = mcp_mod

# Stub minimal prompt_toolkit pieces used in the code
if "prompt_toolkit" not in sys.modules:
    pt = types.ModuleType("prompt_toolkit")
    application = types.ModuleType("prompt_toolkit.application")

    async def run_in_terminal(func):
        return func()

    class Application:
        def __init__(self, *args, **kwargs):
            pass

        async def run_async(self):
            return None

        def exit(self, result=None):
            pass

        def invalidate(self):
            pass

        @property
        def layout(self):
            return MockLayout()

    class MockLayout:
        def focus(self, *args):
            pass

    application.Application = Application
    application.run_in_terminal = run_in_terminal
    application.current = types.ModuleType("prompt_toolkit.application.current")
    application.current.get_app = lambda: None
    key_binding = types.ModuleType("prompt_toolkit.key_binding")

    class KeyBindings:
        def add(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

    key_binding.KeyBindings = KeyBindings
    completion = types.ModuleType("prompt_toolkit.completion")

    class Completer:
        pass

    class Completion:
        def __init__(self, text, start_position=0):
            self.text = text
            self.start_position = start_position

    def merge_completers(*args):
        return None

    completion.Completer = Completer
    completion.Completion = Completion
    completion.CompleteEvent = object
    completion.merge_completers = merge_completers
    document = types.ModuleType("prompt_toolkit.document")

    class Document:
        def __init__(self, text=""):
            self.text = text

    document.Document = Document
    lexers = types.ModuleType("prompt_toolkit.lexers")

    class Lexer:
        pass

    lexers.Lexer = Lexer
    formatted_text = types.ModuleType("prompt_toolkit.formatted_text")

    class HTML(str):
        pass

    class FormattedText(list):
        pass

    # StyleAndTextTuples is a type alias for List[Tuple[str, str]]
    StyleAndTextTuples = list

    formatted_text.HTML = HTML
    formatted_text.FormattedText = FormattedText
    formatted_text.StyleAndTextTuples = StyleAndTextTuples
    shortcuts = types.ModuleType("prompt_toolkit.shortcuts")

    class PromptSession:
        def __init__(self, *a, **k):
            pass

    shortcuts.PromptSession = PromptSession
    validation = types.ModuleType("prompt_toolkit.validation")

    class Validator:
        pass

    class ValidationError(Exception):
        pass

    validation.Validator = Validator
    validation.ValidationError = ValidationError
    pt.application = application
    pt.completion = completion
    pt.validation = validation
    pt.key_binding = key_binding
    pt.formatted_text = formatted_text
    pt.document = document
    pt.lexers = lexers
    styles = types.ModuleType("prompt_toolkit.styles")

    class Style:
        def __init__(self, *args, **kwargs):
            self._style_rules = []

        @classmethod
        def from_dict(cls, style_dict):
            return cls()

        def get_attrs_for_style_str(self, style_str):
            return None

    styles.Style = Style
    pt.styles = styles
    pt.shortcuts = shortcuts

    # Add missing layout and widget modules
    buffer_mod = types.ModuleType("prompt_toolkit.buffer")

    class Buffer:
        def __init__(self, *args, **kwargs):
            self.text = ""
            self.on_text_changed = kwargs.get("on_text_changed")

    buffer_mod.Buffer = Buffer

    layout_mod = types.ModuleType("prompt_toolkit.layout")

    class Layout:
        def __init__(self, *args, **kwargs):
            pass

        def focus(self, *args):
            pass

    class FormattedTextControl:
        def __init__(self, *args, **kwargs):
            pass

    class HSplit:
        def __init__(self, *args, **kwargs):
            pass

    class VSplit:
        def __init__(self, *args, **kwargs):
            pass

    class Window:
        def __init__(self, *args, **kwargs):
            pass

    class WindowAlign:
        CENTER = "center"

    layout_mod.Layout = Layout
    layout_mod.FormattedTextControl = FormattedTextControl
    layout_mod.HSplit = HSplit
    layout_mod.VSplit = VSplit
    layout_mod.Window = Window
    layout_mod.WindowAlign = WindowAlign

    controls_mod = types.ModuleType("prompt_toolkit.layout.controls")

    class BufferControl:
        def __init__(self, *args, **kwargs):
            pass

    controls_mod.BufferControl = BufferControl

    dimension_mod = types.ModuleType("prompt_toolkit.layout.dimension")

    class Dimension:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def min(value):
            return Dimension()

        @staticmethod
        def preferred(value):
            return Dimension()

    dimension_mod.Dimension = Dimension

    search_mod = types.ModuleType("prompt_toolkit.search")

    class SearchState:
        def __init__(self):
            pass

    search_mod.SearchState = SearchState

    widgets_mod = types.ModuleType("prompt_toolkit.widgets")

    class Frame:
        def __init__(self, *args, **kwargs):
            pass

    widgets_mod.Frame = Frame

    # Add patch_stdout module
    patch_stdout_mod = types.ModuleType("prompt_toolkit.patch_stdout")

    def patch_stdout():
        class MockContext:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                pass

        return MockContext()

    patch_stdout_mod.patch_stdout = patch_stdout

    pt.buffer = buffer_mod
    pt.layout = layout_mod
    pt.search = search_mod
    pt.widgets = widgets_mod
    pt.patch_stdout = patch_stdout_mod

    sys.modules["prompt_toolkit"] = pt
    sys.modules["prompt_toolkit.application"] = application
    sys.modules["prompt_toolkit.application.current"] = application.current
    sys.modules["prompt_toolkit.key_binding"] = key_binding
    sys.modules["prompt_toolkit.completion"] = completion
    sys.modules["prompt_toolkit.formatted_text"] = formatted_text
    sys.modules["prompt_toolkit.shortcuts"] = shortcuts
    sys.modules["prompt_toolkit.lexers"] = lexers
    sys.modules["prompt_toolkit.document"] = document
    sys.modules["prompt_toolkit.validation"] = validation
    sys.modules["prompt_toolkit.styles"] = styles
    sys.modules["prompt_toolkit.buffer"] = buffer_mod
    sys.modules["prompt_toolkit.layout"] = layout_mod
    sys.modules["prompt_toolkit.layout.controls"] = controls_mod
    sys.modules["prompt_toolkit.layout.dimension"] = dimension_mod
    sys.modules["prompt_toolkit.search"] = search_mod
    sys.modules["prompt_toolkit.widgets"] = widgets_mod
    sys.modules["prompt_toolkit.patch_stdout"] = patch_stdout_mod
