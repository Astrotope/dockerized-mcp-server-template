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
def create_thumbnail(image_data: str) -> dict:
    """Create a thumbnail from a base64 encoded image
    
    Args:
        image_data: Base64 encoded image data or data URI
    
    Returns:
        Dict containing the thumbnail as base64 data with content structure
    """
    try:
        # Check if it's a data URI format
        if image_data.startswith('data:'):
            # Parse data URI: data:image/png;base64,<data>
            match = re.match(r'data:image/(\w+);base64,(.+)', image_data)
            if not match:
                raise ValueError("Invalid data URI format. Expected: data:image/png;base64,<data>")
            
            format_type, base64_data = match.groups()
            
            # Only accept PNG images
            if format_type.lower() != 'png':
                raise ValueError(f"Only PNG images are supported. Received: image/{format_type}")
            
            # Use the base64 part
            cleaned_data = base64_data
        else:
            # Assume it's just base64 data
            cleaned_data = image_data.strip()
        
        # Remove any whitespace/newlines from base64 data
        cleaned_data = cleaned_data.replace('\n', '').replace('\r', '').replace(' ', '')
        
        # Decode base64 image data
        try:
            image_bytes = base64.b64decode(cleaned_data)
        except Exception as decode_error:
            raise ValueError(f"Failed to decode base64 data: {str(decode_error)}")
        
        # Validate we have actual image data
        if len(image_bytes) == 0:
            raise ValueError("Decoded image data is empty")
        
        # Check PNG magic bytes (89 50 4E 47 0D 0A 1A 0A)
        png_signature = b'\x89PNG\r\n\x1a\n'
        if not image_bytes.startswith(png_signature):
            magic_bytes = image_bytes[:8].hex() if len(image_bytes) >= 8 else "N/A"
            raise ValueError(f"Not a valid PNG image. Magic bytes: {magic_bytes}")
        
        # Open image with PIL
        image_buffer = io.BytesIO(image_bytes)
        try:
            img = Image.open(image_buffer)
            # Force load to verify it's a valid image
            img.load()
            
            # Double-check it's PNG format
            if img.format != 'PNG':
                raise ValueError(f"Expected PNG format, got {img.format}")
                
        except Exception as pil_error:
            raise ValueError(f"PIL cannot open image: {str(pil_error)}")
        
        # Create thumbnail (maintains aspect ratio)
        img.thumbnail((100, 100), Image.Resampling.LANCZOS)
        
        # Convert thumbnail back to PNG bytes
        output_buffer = io.BytesIO()
        img.save(output_buffer, format='PNG', optimize=True)
        
        # Encode thumbnail as base64
        thumbnail_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        # Return in MCP format for images
        return {
            "content": [
                {
                    "type": "image",
                    "data": thumbnail_base64,
                    "mimeType": "image/png"
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

@mcp.prompt()
def debug_error(error: str) -> list[base.Message]:
    return [
        base.UserMessage("I'm seeing this error:"),
        base.UserMessage(error),
        base.AssistantMessage("I'll help debug that. What have you tried so far?"),
    ]



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