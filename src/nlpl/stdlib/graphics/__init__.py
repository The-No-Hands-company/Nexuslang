"""
Graphics module for NLPL - OpenGL/GLFW wrapper
Provides window management and basic 2D rendering capabilities
"""

try:
    import glfw
    from OpenGL.GL import *
    GLFW_AVAILABLE = True
except ImportError:
    GLFW_AVAILABLE = False
    print("Warning: GLFW or PyOpenGL not installed. Graphics module functionality limited.")
    print("Install with: pip install glfw PyOpenGL")

class GraphicsWindow:
    """Represents an OpenGL window with GLFW"""
    
    def __init__(self, width, height, title):
        if not GLFW_AVAILABLE:
            raise RuntimeError("GLFW not available")
        
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")
        
        self.window = glfw.create_window(width, height, title, None, None)
        if not self.window:
            glfw.terminate()
            raise RuntimeError("Failed to create window")
        
        glfw.make_context_current(self.window)
        self.width = width
        self.height = height
        self.title = title
    
    def should_close(self):
        """Check if window should close"""
        return glfw.window_should_close(self.window)
    
    def poll_events(self):
        """Process window events"""
        glfw.poll_events()
    
    def swap_buffers(self):
        """Swap front and back buffers"""
        glfw.swap_buffers(self.window)
    
    def destroy(self):
        """Cleanup window"""
        glfw.destroy_window(self.window)
        glfw.terminate()


class GraphicsModule:
    """Main graphics module for NLPL"""
    
    def __init__(self):
        self.windows = {}
        self.next_window_id = 1
        self.current_window = None
    
    def create_window(self, width: int, height: int, title: str) -> int:
        """Create a new window and return its ID"""
        window = GraphicsWindow(width, height, title)
        window_id = self.next_window_id
        self.windows[window_id] = window
        self.current_window = window
        self.next_window_id += 1
        return window_id
    
    def window_should_close(self, window_id: int) -> bool:
        """Check if window should close"""
        if window_id not in self.windows:
            raise ValueError(f"Invalid window ID: {window_id}")
        return self.windows[window_id].should_close()
    
    def begin_frame(self):
        """Begin a new frame - clear buffers"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    def end_frame(self, window_id: int):
        """End frame - swap buffers and poll events"""
        if window_id not in self.windows:
            raise ValueError(f"Invalid window ID: {window_id}")
        window = self.windows[window_id]
        window.swap_buffers()
        window.poll_events()
    
    def set_clear_color(self, r: float, g: float, b: float, a: float = 1.0):
        """Set the clear color"""
        glClearColor(r, g, b, a)
    
    def draw_rect(self, x: float, y: float, width: float, height: float,
                  r: float, g: float, b: float, a: float = 1.0):
        """Draw a filled rectangle"""
        # Convert screen coords to OpenGL normalized device coords
        # This is a simplified version - would need proper projection matrix
        glColor4f(r, g, b, a)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
    
    def destroy_window(self, window_id: int):
        """Destroy a window"""
        if window_id in self.windows:
            self.windows[window_id].destroy()
            del self.windows[window_id]
    
    def cleanup(self):
        """Cleanup all windows"""
        for window_id in list(self.windows.keys()):
            self.destroy_window(window_id)


def register_graphics_functions(runtime):
    """Register graphics functions with NLPL runtime"""
    gfx = GraphicsModule()
    
    # Window management
    runtime.register_function("create_window", gfx.create_window)
    runtime.register_function("window_should_close", gfx.window_should_close)
    runtime.register_function("destroy_window", gfx.destroy_window)
    
    # Frame management
    runtime.register_function("begin_frame", gfx.begin_frame)
    runtime.register_function("end_frame", gfx.end_frame)
    
    # Rendering
    runtime.register_function("set_clear_color", gfx.set_clear_color)
    runtime.register_function("draw_rect", gfx.draw_rect)
    
    # Store reference for cleanup
    runtime._graphics_module = gfx
    
    return gfx
