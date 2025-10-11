# kalibr/kalibr_app.py - Full App-Level Implementation

from fastapi import FastAPI, Request, UploadFile, File, Depends
from fastapi.responses import JSONResponse, StreamingResponse as FastAPIStreamingResponse
from typing import Callable, Dict, Any, List, Optional, get_type_hints
import inspect
import asyncio
from datetime import datetime
import uuid

from kalibr.types import FileUpload, Session, WorkflowState


class KalibrApp:
    """
    Enhanced app-level Kalibr framework with advanced capabilities:
    - File upload handling
    - Session management
    - Streaming responses
    - Complex workflows
    - Multi-model schema generation
    """
    
    def __init__(self, title="Kalibr Enhanced API", version="2.0.0", base_url="http://localhost:8000"):
        """
        Initialize the Kalibr enhanced app.
        
        Args:
            title: API title
            version: API version
            base_url: Base URL for schema generation
        """
        self.app = FastAPI(title=title, version=version)
        self.base_url = base_url
        
        # Storage for different action types
        self.actions = {}           # Regular actions
        self.file_handlers = {}     # File upload handlers
        self.session_actions = {}   # Session-aware actions
        self.stream_actions = {}    # Streaming actions
        self.workflows = {}         # Workflow handlers
        
        # Session storage (in-memory for simplicity)
        self.sessions: Dict[str, Session] = {}
        
        # Workflow state storage
        self.workflow_states: Dict[str, WorkflowState] = {}
        
        self._setup_routes()
    
    def action(self, name: str, description: str = ""):
        """
        Decorator to register a regular action.
        
        Usage:
            @app.action("greet", "Greet someone")
            def greet(name: str):
                return {"message": f"Hello, {name}!"}
        """
        def decorator(func: Callable):
            self.actions[name] = {
                "func": func,
                "description": description,
                "params": self._extract_params(func)
            }
            
            endpoint_path = f"/proxy/{name}"
            
            async def endpoint_handler(request: Request):
                params = {}
                if request.method == "POST":
                    try:
                        body = await request.json()
                        params = body if isinstance(body, dict) else {}
                    except:
                        params = {}
                else:
                    params = dict(request.query_params)
                
                try:
                    result = func(**params)
                    if inspect.isawaitable(result):
                        result = await result
                    return JSONResponse(content=result)
                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=500)
            
            self.app.post(endpoint_path)(endpoint_handler)
            self.app.get(endpoint_path)(endpoint_handler)
            
            return func
        return decorator
    
    def file_handler(self, name: str, allowed_extensions: List[str] = None, description: str = ""):
        """
        Decorator to register a file upload handler.
        
        Usage:
            @app.file_handler("process_document", [".pdf", ".docx"])
            async def process_document(file: FileUpload):
                return {"filename": file.filename, "size": file.size}
        """
        def decorator(func: Callable):
            self.file_handlers[name] = {
                "func": func,
                "description": description,
                "allowed_extensions": allowed_extensions or [],
                "params": self._extract_params(func)
            }
            
            endpoint_path = f"/files/{name}"
            
            async def file_endpoint(file: UploadFile = File(...)):
                try:
                    # Validate file extension
                    if allowed_extensions:
                        file_ext = "." + file.filename.split(".")[-1] if "." in file.filename else ""
                        if file_ext not in allowed_extensions:
                            return JSONResponse(
                                content={"error": f"File type {file_ext} not allowed. Allowed: {allowed_extensions}"},
                                status_code=400
                            )
                    
                    # Read file content
                    content = await file.read()
                    
                    # Create FileUpload object
                    file_upload = FileUpload(
                        filename=file.filename,
                        content_type=file.content_type or "application/octet-stream",
                        size=len(content),
                        content=content
                    )
                    
                    # Call handler
                    result = func(file_upload)
                    if inspect.isawaitable(result):
                        result = await result
                    
                    return JSONResponse(content=result)
                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=500)
            
            self.app.post(endpoint_path)(file_endpoint)
            
            return func
        return decorator
    
    def session_action(self, name: str, description: str = ""):
        """
        Decorator to register a session-aware action.
        
        Usage:
            @app.session_action("save_data", "Save data to session")
            async def save_data(session: Session, data: dict):
                session.set("my_data", data)
                return {"saved": True}
        """
        def decorator(func: Callable):
            self.session_actions[name] = {
                "func": func,
                "description": description,
                "params": self._extract_params(func)
            }
            
            endpoint_path = f"/session/{name}"
            
            async def session_endpoint(request: Request):
                try:
                    # Get or create session
                    session_id = request.headers.get("X-Session-ID") or request.cookies.get("session_id")
                    
                    if not session_id or session_id not in self.sessions:
                        session_id = str(uuid.uuid4())
                        session = Session(session_id=session_id)
                        self.sessions[session_id] = session
                    else:
                        session = self.sessions[session_id]
                        session.last_accessed = datetime.now()
                    
                    # Get request parameters
                    body = await request.json() if request.method == "POST" else {}
                    
                    # Call function with session
                    sig = inspect.signature(func)
                    if 'session' in sig.parameters:
                        # Remove 'session' from params, pass separately
                        func_params = {k: v for k, v in body.items() if k != 'session'}
                        result = func(session=session, **func_params)
                    else:
                        result = func(**body)
                    
                    if inspect.isawaitable(result):
                        result = await result
                    
                    # Return result with session ID
                    response = JSONResponse(content=result)
                    response.set_cookie("session_id", session_id)
                    response.headers["X-Session-ID"] = session_id
                    
                    return response
                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=500)
            
            self.app.post(endpoint_path)(session_endpoint)
            
            return func
        return decorator
    
    def stream_action(self, name: str, description: str = ""):
        """
        Decorator to register a streaming action.
        
        Usage:
            @app.stream_action("live_feed", "Stream live data")
            async def live_feed(count: int = 10):
                for i in range(count):
                    yield {"item": i, "timestamp": datetime.now().isoformat()}
                    await asyncio.sleep(0.5)
        """
        def decorator(func: Callable):
            self.stream_actions[name] = {
                "func": func,
                "description": description,
                "params": self._extract_params(func)
            }
            
            endpoint_path = f"/stream/{name}"
            
            async def stream_endpoint(request: Request):
                try:
                    # Get parameters
                    params = dict(request.query_params) if request.method == "GET" else {}
                    if request.method == "POST":
                        body = await request.json()
                        params.update(body)
                    
                    # Convert parameter types based on function signature
                    sig = inspect.signature(func)
                    type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
                    converted_params = {}
                    for key, value in params.items():
                        if key in sig.parameters:
                            param_type = type_hints.get(key, str)
                            try:
                                if param_type == int:
                                    converted_params[key] = int(value)
                                elif param_type == float:
                                    converted_params[key] = float(value)
                                elif param_type == bool:
                                    converted_params[key] = value.lower() in ('true', '1', 'yes')
                                else:
                                    converted_params[key] = value
                            except (ValueError, AttributeError):
                                converted_params[key] = value
                    
                    # Call generator function
                    result = func(**converted_params)
                    
                    # Create streaming generator
                    async def generate():
                        if inspect.isasyncgen(result):
                            async for item in result:
                                import json
                                yield json.dumps(item) + "\n"
                        elif inspect.isgenerator(result):
                            for item in result:
                                import json
                                yield json.dumps(item) + "\n"
                    
                    return FastAPIStreamingResponse(generate(), media_type="application/x-ndjson")
                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=500)
            
            self.app.get(endpoint_path)(stream_endpoint)
            self.app.post(endpoint_path)(stream_endpoint)
            
            return func
        return decorator
    
    def workflow(self, name: str, description: str = ""):
        """
        Decorator to register a workflow.
        
        Usage:
            @app.workflow("process_order", "Process customer order")
            async def process_order(order_data: dict, workflow_state: WorkflowState):
                workflow_state.step = "validation"
                # ... process steps
                return {"workflow_id": workflow_state.workflow_id}
        """
        def decorator(func: Callable):
            self.workflows[name] = {
                "func": func,
                "description": description,
                "params": self._extract_params(func)
            }
            
            endpoint_path = f"/workflow/{name}"
            
            async def workflow_endpoint(request: Request):
                try:
                    # Get workflow ID from headers or create new
                    workflow_id = request.headers.get("X-Workflow-ID")
                    
                    if not workflow_id or workflow_id not in self.workflow_states:
                        workflow_id = str(uuid.uuid4())
                        workflow_state = WorkflowState(
                            workflow_id=workflow_id,
                            step="init",
                            status="running"
                        )
                        self.workflow_states[workflow_id] = workflow_state
                    else:
                        workflow_state = self.workflow_states[workflow_id]
                        workflow_state.updated_at = datetime.now()
                    
                    # Get request data
                    body = await request.json() if request.method == "POST" else {}
                    
                    # Call workflow function
                    sig = inspect.signature(func)
                    if 'workflow_state' in sig.parameters:
                        func_params = {k: v for k, v in body.items() if k != 'workflow_state'}
                        result = func(workflow_state=workflow_state, **func_params)
                    else:
                        result = func(**body)
                    
                    if inspect.isawaitable(result):
                        result = await result
                    
                    # Return result with workflow ID
                    response = JSONResponse(content=result)
                    response.headers["X-Workflow-ID"] = workflow_id
                    
                    return response
                except Exception as e:
                    return JSONResponse(content={"error": str(e)}, status_code=500)
            
            self.app.post(endpoint_path)(workflow_endpoint)
            
            return func
        return decorator
    
    def _extract_params(self, func: Callable) -> Dict:
        """Extract parameter information from function signature."""
        sig = inspect.signature(func)
        params = {}
        type_hints = get_type_hints(func) if hasattr(func, '__annotations__') else {}
        
        for param_name, param in sig.parameters.items():
            # Skip special parameters
            if param_name in ['session', 'workflow_state', 'file']:
                continue
            
            param_type = "string"
            
            if param_name in type_hints:
                anno = type_hints[param_name]
            elif param.annotation != inspect.Parameter.empty:
                anno = param.annotation
            else:
                anno = str
            
            # Map types
            if anno == int:
                param_type = "integer"
            elif anno == bool:
                param_type = "boolean"
            elif anno == float:
                param_type = "number"
            elif anno == list:
                param_type = "array"
            elif anno == dict:
                param_type = "object"
            
            is_required = param.default == inspect.Parameter.empty
            
            params[param_name] = {
                "type": param_type,
                "required": is_required
            }
        
        return params
    
    def _setup_routes(self):
        """Setup core API routes."""
        from kalibr.schema_generators import (
            OpenAPISchemaGenerator,
            MCPSchemaGenerator,
            GeminiSchemaGenerator,
            CopilotSchemaGenerator
        )
        
        # Initialize schema generators
        openapi_gen = OpenAPISchemaGenerator()
        mcp_gen = MCPSchemaGenerator()
        gemini_gen = GeminiSchemaGenerator()
        copilot_gen = CopilotSchemaGenerator()
        
        @self.app.get("/")
        def root():
            """Root endpoint with API information."""
            return {
                "message": "Kalibr Enhanced API is running",
                "actions": list(self.actions.keys()),
                "file_handlers": list(self.file_handlers.keys()),
                "session_actions": list(self.session_actions.keys()),
                "stream_actions": list(self.stream_actions.keys()),
                "workflows": list(self.workflows.keys()),
                "schemas": {
                    "gpt_actions": f"{self.base_url}/gpt-actions.json",
                    "openapi_swagger": f"{self.base_url}/openapi.json",
                    "claude_mcp": f"{self.base_url}/mcp.json",
                    "gemini": f"{self.base_url}/schemas/gemini",
                    "copilot": f"{self.base_url}/schemas/copilot"
                }
            }
        
        @self.app.get("/gpt-actions.json")
        def gpt_actions_schema():
            """Generate GPT Actions schema from all registered actions."""
            # Combine all action types for schema generation
            all_actions = {**self.actions, **self.file_handlers, **self.session_actions}
            return openapi_gen.generate_schema(all_actions, self.base_url)
        
        @self.app.get("/mcp.json")
        def mcp_manifest():
            """Generate Claude MCP manifest."""
            all_actions = {**self.actions, **self.file_handlers, **self.session_actions}
            return mcp_gen.generate_schema(all_actions, self.base_url)
        
        @self.app.get("/schemas/gemini")
        def gemini_schema():
            """Generate Gemini Extensions schema."""
            all_actions = {**self.actions, **self.file_handlers, **self.session_actions}
            return gemini_gen.generate_schema(all_actions, self.base_url)
        
        @self.app.get("/schemas/copilot")
        def copilot_schema():
            """Generate Microsoft Copilot schema."""
            all_actions = {**self.actions, **self.file_handlers, **self.session_actions}
            return copilot_gen.generate_schema(all_actions, self.base_url)
        
        # Health check
        @self.app.get("/health")
        def health_check():
            return {
                "status": "healthy",
                "service": "Kalibr Enhanced API",
                "features": ["actions", "file_uploads", "sessions", "streaming", "workflows"]
            }
        
        # Override FastAPI OpenAPI for Swagger UI
        def custom_openapi():
            if self.app.openapi_schema:
                return self.app.openapi_schema
            
            from fastapi.openapi.utils import get_openapi
            openapi_schema = get_openapi(
                title=self.app.title,
                version=self.app.version,
                routes=self.app.routes,
            )
            openapi_schema["servers"] = [{"url": self.base_url}]
            self.app.openapi_schema = openapi_schema
            return self.app.openapi_schema
        
        self.app.openapi = custom_openapi
