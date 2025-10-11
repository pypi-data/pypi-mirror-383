# File: autobyteus/tools/browser/session_aware/browser_session_aware_tool.py

from autobyteus.tools.base_tool import BaseTool
from autobyteus.tools.tool_config import ToolConfig
from autobyteus.tools.browser.session_aware.shared_browser_session_manager import SharedBrowserSessionManager
from autobyteus.events.event_types import EventType
from typing import Optional

class BrowserSessionAwareTool(BaseTool):
    def __init__(self, config: Optional[ToolConfig] = None):
        super().__init__(config=config)
        self.shared_browser_session_manager = SharedBrowserSessionManager()

    async def _execute(self, **kwargs):
        shared_session = self.shared_browser_session_manager.get_shared_browser_session()
        
        if not shared_session:
            webpage_url = kwargs.get('webpage_url')
            if not webpage_url:
                raise ValueError("The 'webpage_url' keyword argument must be specified when creating a new shared session.")
            
            await self.shared_browser_session_manager.create_shared_browser_session()
            shared_session = self.shared_browser_session_manager.get_shared_browser_session()
            await shared_session.page.goto(webpage_url)
            self.emit(EventType.SHARED_BROWSER_SESSION_CREATED, shared_session=shared_session)
        
        return await self.perform_action(shared_session, **kwargs)

    async def perform_action(self, shared_session, **kwargs):
        raise NotImplementedError("Subclasses must implement this method")
