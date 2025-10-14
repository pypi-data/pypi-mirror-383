"""Agent editing screen with dual-pane interface."""
import logging
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Label, Input
from textual.binding import Binding

from ai_configurator.tui.screens.base import BaseScreen
from ai_configurator.services.agent_service import AgentService
from ai_configurator.services.library_service import LibraryService
from ai_configurator.services.registry_service import RegistryService
from ai_configurator.models import Agent, ToolType, ResourcePath, AgentConfig

logger = logging.getLogger(__name__)


class AgentEditScreen(BaseScreen):
    """Agent editing interface with dual-pane layout."""
    
    BINDINGS = [
        Binding("ctrl+s", "save", "Save"),
        Binding("space", "toggle_select", "Select/Deselect"),
        Binding("escape", "cancel", "Cancel"),
    ]
    
    def __init__(self, agent: Agent, agent_service: AgentService):
        super().__init__()
        self.agent = agent
        self.agent_service = agent_service
        
        # Get available items
        from ai_configurator.tui.config import get_library_paths, get_registry_dir
        base_path, personal_path = get_library_paths()
        self.library_service = LibraryService(base_path, personal_path)
        self.registry_service = RegistryService(get_registry_dir())
        
        # Load available items
        library = self.library_service.create_library()
        self.available_files = {f.path: f for f in library.files.values()}
        
        # Load MCP servers
        import json
        servers_dir = get_registry_dir() / "servers"
        self.available_servers = {}
        
        if servers_dir.exists():
            for server_file in servers_dir.glob("*.json"):
                try:
                    data = json.loads(server_file.read_text())
                    if "mcpServers" in data:
                        for name in data["mcpServers"].keys():
                            self.available_servers[name] = data["mcpServers"][name]
                    elif "command" in data:
                        self.available_servers[server_file.stem] = data
                    else:
                        for name, config in data.items():
                            if isinstance(config, dict) and 'command' in config:
                                self.available_servers[name] = config
                except Exception as e:
                    logger.error(f"Error loading {server_file}: {e}")
        
        # Pre-select items already in agent
        self.selected_files = set(r.path for r in agent.config.resources if r.path in self.available_files)
        self.selected_servers = set(name for name in agent.config.mcp_servers.keys() if name in self.available_servers)
    
    def compose(self) -> ComposeResult:
        """Build layout."""
        yield Header()
        yield Container(
            Static(f"[bold cyan]Edit Agent: {self.agent.name}[/bold cyan]\n[dim]Space=Select Ctrl+S=Save Esc=Cancel[/dim]", id="title"),
            
            # Context patterns input
            Label("[bold]Context File Patterns[/bold] [dim](e.g., .amazonq/rules/**/*.md)[/dim]"),
            Input(placeholder="Enter file patterns, one per line", id="context_input"),
            
            Horizontal(
                # Left pane: Available items
                Vertical(
                    Label("[bold]Available Library Files[/bold]"),
                    DataTable(id="available_files", classes="left-pane-top"),
                    Label("[bold]Available MCP Servers[/bold]"),
                    DataTable(id="available_servers", classes="left-pane-bottom"),
                    classes="left-pane"
                ),
                # Right pane: Current agent config
                Vertical(
                    Label("[bold]Agent Resources[/bold]"),
                    DataTable(id="selected_files", classes="right-pane-top"),
                    Label("[bold]Agent MCP Servers[/bold]"),
                    DataTable(id="selected_servers", classes="right-pane-bottom"),
                    classes="right-pane"
                ),
                id="dual-pane"
            ),
            id="edit-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize tables and input."""
        # Setup context input
        context_input = self.query_one("#context_input", Input)
        context_input.value = "\n".join(self.agent.config.context_patterns)
        
        # Setup tables
        avail_files = self.query_one("#available_files", DataTable)
        avail_files.add_column("File")
        avail_files.cursor_type = "row"
        
        avail_servers = self.query_one("#available_servers", DataTable)
        avail_servers.add_column("Server")
        avail_servers.cursor_type = "row"
        
        sel_files = self.query_one("#selected_files", DataTable)
        sel_files.add_column("File")
        sel_files.cursor_type = "row"
        
        sel_servers = self.query_one("#selected_servers", DataTable)
        sel_servers.add_column("Server")
        sel_servers.cursor_type = "row"
        
        self.refresh_all_tables()
        avail_files.focus()
    
    def refresh_all_tables(self) -> None:
        """Refresh all tables."""
        # Available files
        avail_files = self.query_one("#available_files", DataTable)
        avail_files.clear()
        for path, f in sorted(self.available_files.items()):
            checkbox = "[X]" if path in self.selected_files else "[ ]"
            avail_files.add_row(f"{checkbox} {path}")
        
        # Available servers
        avail_servers = self.query_one("#available_servers", DataTable)
        avail_servers.clear()
        for name in sorted(self.available_servers.keys()):
            checkbox = "[X]" if name in self.selected_servers else "[ ]"
            avail_servers.add_row(f"{checkbox} {name}")
        
        # Selected files
        sel_files = self.query_one("#selected_files", DataTable)
        sel_files.clear()
        for resource in self.agent.config.resources:
            sel_files.add_row(resource.path)
        
        # Selected servers
        sel_servers = self.query_one("#selected_servers", DataTable)
        sel_servers.clear()
        for name in sorted(self.agent.config.mcp_servers.keys()):
            sel_servers.add_row(name)
    
    def action_toggle_select(self) -> None:
        """Toggle selection of item in left pane."""
        focused = self.app.focused
        if focused is None:
            return
        
        table_id = focused.id
        cursor_row = focused.cursor_row
        
        try:
            if table_id == "available_files":
                table = self.query_one("#available_files", DataTable)
                if table.cursor_row < table.row_count:
                    row = table.get_row_at(table.cursor_row)
                    path = str(row[0])[4:]  # Skip "[ ] " or "[X] "
                    
                    if path in self.selected_files:
                        self.selected_files.discard(path)
                    else:
                        self.selected_files.add(path)
                    
                    self.refresh_all_tables()
                    table.focus()
                    if table.row_count > 0:
                        table.move_cursor(row=min(cursor_row, table.row_count - 1))
            
            elif table_id == "available_servers":
                table = self.query_one("#available_servers", DataTable)
                if table.cursor_row < table.row_count:
                    row = table.get_row_at(table.cursor_row)
                    name = str(row[0])[4:]  # Skip "[ ] " or "[X] "
                    
                    if name in self.selected_servers:
                        self.selected_servers.discard(name)
                    else:
                        self.selected_servers.add(name)
                    
                    self.refresh_all_tables()
                    table.focus()
                    if table.row_count > 0:
                        table.move_cursor(row=min(cursor_row, table.row_count - 1))
                    
        except Exception as e:
            logger.error(f"Error toggling selection: {e}", exc_info=True)
    
    def action_save(self) -> None:
        """Save agent changes."""
        try:
            # Get context patterns from input
            context_input = self.query_one("#context_input", Input)
            context_patterns = [p.strip() for p in context_input.value.split('\n') if p.strip()]
            
            # Build new resource list
            new_resources = []
            for path in self.selected_files:
                if path in self.available_files:
                    file_info = self.available_files[path]
                    new_resources.append(ResourcePath(
                        path=path,
                        source=file_info.source
                    ))
            
            # Build new MCP servers dict
            new_mcp_servers = {}
            for server_name in self.selected_servers:
                if server_name in self.available_servers:
                    # Use the actual server config from registry
                    server_config = self.available_servers[server_name]
                    from ai_configurator.models.mcp_server import MCPServerConfig
                    new_mcp_servers[server_name] = MCPServerConfig(
                        command=server_config.get("command", server_name),
                        args=server_config.get("args", []),
                        env=server_config.get("env"),
                        timeout=server_config.get("timeout", 120000),
                        disabled=server_config.get("disabled", False)
                    )
                elif server_name in self.agent.config.mcp_servers:
                    # Keep existing config
                    new_mcp_servers[server_name] = self.agent.config.mcp_servers[server_name]
            
            # Create new config
            new_config = AgentConfig(
                name=self.agent.config.name,
                description=self.agent.config.description,
                prompt=self.agent.config.prompt,
                tool_type=self.agent.config.tool_type,
                resources=new_resources,
                context_patterns=context_patterns,
                mcp_servers=new_mcp_servers,
                settings=self.agent.config.settings,
                created_at=self.agent.config.created_at
            )
            
            updated_agent = Agent(config=new_config)
            
            if self.agent_service.update_agent(updated_agent):
                if updated_agent.tool_type == ToolType.Q_CLI:
                    self.agent_service.export_to_q_cli(updated_agent)
                
                self.show_notification(f"Saved agent: {self.agent.name}", "information")
                self.app.pop_screen()
            else:
                self.show_notification("Failed to save agent", "error")
                
        except Exception as e:
            logger.error(f"Error saving agent: {e}", exc_info=True)
            self.show_notification(f"Error: {e}", "error")
    
    def action_cancel(self) -> None:
        """Cancel editing and go back."""
        self.app.pop_screen()
