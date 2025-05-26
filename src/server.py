# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from PIL import Image
import base64
import io
import re
import asyncio
from pathlib import Path
from typing import Any, Dict
import chess
import chess.svg
from pydantic import BaseModel


# Create an MCP server
mcp = FastMCP("StatelessServer", stateless_http=True)


# Add an addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return a + b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

class FenRequest(BaseModel):
    """Request model for FEN notation input."""
    fen: str
    size: int = 400  # Default board size in pixels


# Initialize FastMCP server
mcp = FastMCP("Chess Board Generator")

# Create directory for saving chess board images
CHESS_BOARDS_DIR = Path("chess_boards")
CHESS_BOARDS_DIR.mkdir(exist_ok=True)

# In-memory storage for generated chess boards metadata
_generated_boards: Dict[str, Dict[str, Any]] = {}


@mcp.tool()
async def generate_chess_board(request: FenRequest) -> dict[str, Any]:
    """
    Generate a chess board image from FEN notation.
    
    Args:
        request: FenRequest containing FEN string and optional board size
        
    Returns:
        Dictionary containing the chess board image as base64 encoded PNG
    """
    try:
        # Parse the FEN notation
        board = chess.Board(request.fen)
        
        # Generate SVG representation of the board
        svg_string = chess.svg.board(
            board=board,
            size=request.size,
            coordinates=True,  # Show coordinate labels
            flipped=False      # White pieces at bottom
        )
        
        # Convert SVG to PNG using cairosvg (you'll need to install this)
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(
                bytestring=svg_string.encode('utf-8'),
                output_width=request.size,
                output_height=request.size
            )
            
            # Save PNG to file
            board_id = f"board_{len(_generated_boards) + 1}"
            filename = f"{board_id}.png"
            filepath = CHESS_BOARDS_DIR / filename
            
            with open(filepath, 'wb') as f:
                f.write(png_bytes)
            
            file_uri = f"file://{filepath.absolute()}"
            
        except ImportError:
            # Fallback: save SVG file
            board_id = f"board_{len(_generated_boards) + 1}"
            filename = f"{board_id}.svg"
            filepath = CHESS_BOARDS_DIR / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_string)
            
            file_uri = f"file://{filepath.absolute()}"
        
        # Store metadata for the resource
        resource_uri = f"chess://board/{board_id}"
        
        _generated_boards[board_id] = {
            "uri": resource_uri,
            "file_path": str(filepath),
            "file_uri": file_uri,
            "name": f"Chess Board - {request.fen[:20]}...",
            "description": f"Chess board generated from FEN: {request.fen}",
            "mimeType": "image/png" if filepath.suffix == '.png' else "image/svg+xml",
            "fen": request.fen,
            "size": request.size
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Generated chess board from FEN: {request.fen}\n" +
                           f"Board position: {board.fen()}\n" +
                           f"Saved to: {filepath}\n" +
                           f"Available as resource: {resource_uri}\n\n" +
                           f"You can access this chess board through the resources panel."
                }
            ]
        }
        
    except chess.InvalidFenError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error: Invalid FEN notation '{request.fen}'. {str(e)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text", 
                    "text": f"Error generating chess board: {str(e)}"
                }
            ]
        }


@mcp.tool()
async def validate_fen(fen: str) -> dict[str, Any]:
    """
    Validate FEN notation and provide board information.
    
    Args:
        fen: FEN notation string to validate
        
    Returns:
        Dictionary containing validation result and board information
    """
    try:
        board = chess.Board(fen)
        
        # Get basic board information
        info = {
            "valid": True,
            "fen": board.fen(),
            "turn": "White" if board.turn else "Black",
            "castling_rights": board.castling_rights,
            "en_passant": str(board.ep_square) if board.ep_square else None,
            "halfmove_clock": board.halfmove_clock,
            "fullmove_number": board.fullmove_number,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_game_over": board.is_game_over()
        }
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"FEN Validation Results:\n" + 
                           f"Valid: {info['valid']}\n" +
                           f"Turn: {info['turn']}\n" +
                           f"Check: {info['is_check']}\n" +
                           f"Checkmate: {info['is_checkmate']}\n" +
                           f"Stalemate: {info['is_stalemate']}\n" +
                           f"Game Over: {info['is_game_over']}\n" +
                           f"Halfmove Clock: {info['halfmove_clock']}\n" +
                           f"Fullmove Number: {info['fullmove_number']}"
                }
            ]
        }
        
    except chess.InvalidFenError as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Invalid FEN notation: {str(e)}"
                }
            ]
        }


@mcp.tool()
async def list_chess_boards() -> dict[str, Any]:
    """
    List all generated chess boards available as resources.
    
    Returns:
        Dictionary containing information about all available chess board resources
    """
    if not _generated_boards:
        return {
            "content": [
                {
                    "type": "text",
                    "text": "No chess boards have been generated yet. Use the generate_chess_board tool to create some!"
                }
            ]
        }
    
    board_list = []
    for board_id, board_data in _generated_boards.items():
        board_list.append(f"- {board_data['name']} ({board_data['uri']})\n  FEN: {board_data['fen']}\n  File: {board_data['file_path']}")
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"Available chess board resources ({len(_generated_boards)} total):\n\n" + "\n\n".join(board_list)
            }
        ]
    }


@mcp.tool()
async def clear_chess_boards() -> dict[str, Any]:
    """
    Clear all generated chess board resources and delete files.
    
    Returns:
        Dictionary containing confirmation message
    """
    count = len(_generated_boards)
    
    # Delete the actual files
    for board_data in _generated_boards.values():
        try:
            filepath = Path(board_data['file_path'])
            if filepath.exists():
                filepath.unlink()
        except Exception as e:
            print(f"Error deleting {board_data['file_path']}: {e}")
    
    _generated_boards.clear()
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"Cleared {count} chess board resource(s) and deleted their files."
            }
        ]
    }


@mcp.resource("chess://board/{board_id}")
async def get_chess_board_resource(board_id: str) -> dict[str, Any]:
    """
    Get a chess board resource by ID.
    
    Args:
        board_id: The ID of the chess board to retrieve
        
    Returns:
        Dictionary containing the chess board resource
    """
    if board_id not in _generated_boards:
        raise ValueError(f"Chess board {board_id} not found")
    
    board_data = _generated_boards[board_id]
    filepath = Path(board_data['file_path'])
    
    if not filepath.exists():
        raise ValueError(f"Chess board file {filepath} not found")
    
    # Read the file and encode as base64
    with open(filepath, 'rb') as f:
        file_data = f.read()
    
    base64_data = base64.b64encode(file_data).decode('utf-8')
    
    return {
        "contents": [
            {
                "uri": board_data["uri"],
                "mimeType": board_data["mimeType"],
                "blob": base64_data
            }
        ]
    }



# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.prompt()
def review_code(code: str) -> str:
    return f"Please review this code:\n\n{code}"


@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")