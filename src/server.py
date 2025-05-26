# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from PIL import Image
import base64
import io

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

@mcp.tool()
def create_thumbnail(image_data: str, mime_type: str = None) -> dict:
    """Create a thumbnail from a base64 encoded image
    
    Args:
        image_data: Base64 encoded image data
        mime_type: Optional MIME type of the image (image/jpeg or image/png). 
                   If not provided, will be auto-detected from image data.
    
    Returns:
        Dict containing the thumbnail as base64 data with content structure
    """
    try:
        # Decode base64 image data
        image_bytes = base64.b64decode(image_data)
        
        # Open image with PIL
        img = Image.open(io.BytesIO(image_bytes))
        
        # Auto-detect MIME type if not provided
        if mime_type is None:
            # Get format from PIL and convert to MIME type
            pil_format = img.format
            if pil_format == "JPEG":
                mime_type = "image/jpeg"
            elif pil_format == "PNG":
                mime_type = "image/png"
            else:
                # Default to JPEG for unsupported formats, but convert the image
                mime_type = "image/jpeg"
        
        # Validate MIME type
        if mime_type not in ["image/jpeg", "image/png"]:
            raise ValueError("Unsupported MIME type. Only image/jpeg and image/png are supported.")
        
        # Create thumbnail (maintains aspect ratio)
        img.thumbnail((100, 100), Image.Resampling.LANCZOS)
        
        # Determine output format based on MIME type
        output_format = "JPEG" if mime_type == "image/jpeg" else "PNG"
        
        # Convert thumbnail back to bytes
        output_buffer = io.BytesIO()
        if output_format == "JPEG":
            # Convert to RGB if necessary for JPEG (removes alpha channel)
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")
            img.save(output_buffer, format=output_format, quality=85, optimize=True)
        else:  # PNG
            img.save(output_buffer, format=output_format, optimize=True)
        
        # Encode thumbnail as base64
        thumbnail_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        # Return in MCP format for images
        return {
            "content": [
                {
                    "type": "image",
                    "data": thumbnail_base64,
                    "mimeType": mime_type
                }
            ]
        }
        
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "data": f"Error creating thumbnail: {str(e)}"
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