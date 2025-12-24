"""
NLPL Language Server
====================

Main LSP server implementation handling client-server communication.
"""

import json
import sys
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(
    filename='/tmp/nlpl-lsp.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nlpl-lsp')


@dataclass
class Position:
    """Position in a text document (line, character)."""
    line: int
    character: int
    
    def to_dict(self):
        return {"line": self.line, "character": self.character}


@dataclass
class Range:
    """Range in a text document."""
    start: Position
    end: Position
    
    def to_dict(self):
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}


@dataclass
class Location:
    """Location in a document."""
    uri: str
    range: Range
    
    def to_dict(self):
        return {"uri": self.uri, "range": self.range.to_dict()}


@dataclass
class TextDocumentIdentifier:
    """Text document identifier."""
    uri: str


@dataclass
class TextDocumentPosition:
    """Position in a text document."""
    text_document: TextDocumentIdentifier
    position: Position


class NLPLLanguageServer:
    """
    NLPL Language Server implementing LSP protocol.
    
    Capabilities:
    - textDocument/completion
    - textDocument/definition
    - textDocument/hover
    - textDocument/publishDiagnostics
    - textDocument/rename
    - textDocument/formatting
    - workspace/symbol
    """
    
    def __init__(self):
        self.documents: Dict[str, str] = {}  # URI -> content
        self.initialization_options = {}
        
        # Import providers
        from ..lsp.completions import CompletionProvider
        from ..lsp.definitions import DefinitionProvider
        from ..lsp.hover import HoverProvider
        from ..lsp.diagnostics import DiagnosticsProvider
        from ..lsp.symbols import SymbolProvider
        
        self.completion_provider = CompletionProvider(self)
        self.definition_provider = DefinitionProvider(self)
        self.hover_provider = HoverProvider(self)
        self.diagnostics_provider = DiagnosticsProvider(self)
        self.symbol_provider = SymbolProvider(self)
        
        logger.info("NLPL Language Server initialized")
    
    def start(self):
        """Start the language server (stdio communication)."""
        logger.info("Starting NLPL Language Server")
        
        while True:
            try:
                message = self._read_message()
                if message is None:
                    break
                
                response = self._handle_message(message)
                if response:
                    self._write_message(response)
                    
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
    
    def _read_message(self) -> Optional[Dict]:
        """Read a JSON-RPC message from stdin."""
        try:
            # Read headers
            headers = {}
            while True:
                line = sys.stdin.buffer.readline().decode('utf-8')
                if line == '\r\n':
                    break
                key, value = line.strip().split(': ', 1)
                headers[key] = value
            
            # Read content
            content_length = int(headers.get('Content-Length', 0))
            if content_length == 0:
                return None
            
            content = sys.stdin.buffer.read(content_length).decode('utf-8')
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None
    
    def _write_message(self, message: Dict):
        """Write a JSON-RPC message to stdout."""
        try:
            content = json.dumps(message)
            content_bytes = content.encode('utf-8')
            
            response = (
                f"Content-Length: {len(content_bytes)}\r\n"
                f"\r\n"
                f"{content}"
            )
            
            sys.stdout.buffer.write(response.encode('utf-8'))
            sys.stdout.buffer.flush()
            
        except Exception as e:
            logger.error(f"Error writing message: {e}")
    
    def _handle_message(self, message: Dict) -> Optional[Dict]:
        """Handle incoming LSP message."""
        method = message.get('method')
        msg_id = message.get('id')
        params = message.get('params', {})
        
        logger.debug(f"Handling method: {method}")
        
        # Handle requests
        if method == 'initialize':
            return self._handle_initialize(msg_id, params)
        
        elif method == 'initialized':
            logger.info("Client initialized")
            return None
        
        elif method == 'textDocument/didOpen':
            self._handle_did_open(params)
            return None
        
        elif method == 'textDocument/didChange':
            self._handle_did_change(params)
            return None
        
        elif method == 'textDocument/didClose':
            self._handle_did_close(params)
            return None
        
        elif method == 'textDocument/completion':
            return self._handle_completion(msg_id, params)
        
        elif method == 'textDocument/definition':
            return self._handle_definition(msg_id, params)
        
        elif method == 'textDocument/hover':
            return self._handle_hover(msg_id, params)
        
        elif method == 'textDocument/formatting':
            return self._handle_formatting(msg_id, params)
        
        elif method == 'workspace/symbol':
            return self._handle_workspace_symbol(msg_id, params)
        
        elif method == 'shutdown':
            logger.info("Shutdown requested")
            return {"jsonrpc": "2.0", "id": msg_id, "result": None}
        
        elif method == 'exit':
            logger.info("Exit requested")
            sys.exit(0)
        
        else:
            logger.warning(f"Unhandled method: {method}")
            return None
    
    def _handle_initialize(self, msg_id: int, params: Dict) -> Dict:
        """Handle initialize request."""
        self.initialization_options = params.get('initializationOptions', {})
        
        capabilities = {
            "textDocumentSync": {
                "openClose": True,
                "change": 1,  # Full sync
                "save": {"includeText": True}
            },
            "completionProvider": {
                "resolveProvider": False,
                "triggerCharacters": [" ", "."]
            },
            "definitionProvider": True,
            "hoverProvider": True,
            "documentFormattingProvider": True,
            "workspaceSymbolProvider": True,
            "renameProvider": True
        }
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "capabilities": capabilities,
                "serverInfo": {
                    "name": "NLPL Language Server",
                    "version": "0.1.0"
                }
            }
        }
    
    def _handle_did_open(self, params: Dict):
        """Handle textDocument/didOpen notification."""
        text_document = params['textDocument']
        uri = text_document['uri']
        text = text_document['text']
        
        self.documents[uri] = text
        logger.info(f"Opened document: {uri}")
        
        # Send diagnostics
        diagnostics = self.diagnostics_provider.get_diagnostics(uri, text)
        self._publish_diagnostics(uri, diagnostics)
    
    def _handle_did_change(self, params: Dict):
        """Handle textDocument/didChange notification."""
        text_document = params['textDocument']
        uri = text_document['uri']
        changes = params['contentChanges']
        
        # Full sync - take the full text
        if changes:
            self.documents[uri] = changes[0]['text']
            
            # Send diagnostics
            diagnostics = self.diagnostics_provider.get_diagnostics(uri, changes[0]['text'])
            self._publish_diagnostics(uri, diagnostics)
    
    def _handle_did_close(self, params: Dict):
        """Handle textDocument/didClose notification."""
        uri = params['textDocument']['uri']
        if uri in self.documents:
            del self.documents[uri]
        logger.info(f"Closed document: {uri}")
    
    def _handle_completion(self, msg_id: int, params: Dict) -> Dict:
        """Handle textDocument/completion request."""
        uri = params['textDocument']['uri']
        position = Position(
            params['position']['line'],
            params['position']['character']
        )
        
        text = self.documents.get(uri, '')
        completions = self.completion_provider.get_completions(text, position)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {"items": completions}
        }
    
    def _handle_definition(self, msg_id: int, params: Dict) -> Dict:
        """Handle textDocument/definition request."""
        uri = params['textDocument']['uri']
        position = Position(
            params['position']['line'],
            params['position']['character']
        )
        
        text = self.documents.get(uri, '')
        location = self.definition_provider.get_definition(text, position, uri)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": location.to_dict() if location else None
        }
    
    def _handle_hover(self, msg_id: int, params: Dict) -> Dict:
        """Handle textDocument/hover request."""
        uri = params['textDocument']['uri']
        position = Position(
            params['position']['line'],
            params['position']['character']
        )
        
        text = self.documents.get(uri, '')
        hover_info = self.hover_provider.get_hover(text, position)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": hover_info
        }
    
    def _handle_formatting(self, msg_id: int, params: Dict) -> Dict:
        """Handle textDocument/formatting request."""
        uri = params['textDocument']['uri']
        text = self.documents.get(uri, '')
        
        # TODO: Implement formatter
        edits = []
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": edits
        }
    
    def _handle_workspace_symbol(self, msg_id: int, params: Dict) -> Dict:
        """Handle workspace/symbol request."""
        query = params.get('query', '')
        symbols = self.symbol_provider.find_symbols(query, self.documents)
        
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": symbols
        }
    
    def _publish_diagnostics(self, uri: str, diagnostics: List[Dict]):
        """Publish diagnostics to client."""
        notification = {
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        }
        self._write_message(notification)


__all__ = ['NLPLLanguageServer', 'Position', 'Range', 'Location']
