"""
Console logger component for displaying backend operations.
"""
import streamlit as st
from datetime import datetime
from typing import List


class ConsoleLogger:
    """A console-style logger for displaying backend operations in Streamlit."""
    
    def __init__(self, key: str = "console_logs"):
        self.key = key
        if self.key not in st.session_state:
            st.session_state[self.key] = []
    
    def log(self, message: str, level: str = "info"):
        """
        Add a log message.
        
        Args:
            message: The log message
            level: Log level (info, success, warning, error)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Icon mapping
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️",
            "error": "❌",
            "processing": "⏳"
        }
        
        icon = icons.get(level, "📝")
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "level": level,
            "icon": icon
        }
        st.session_state[self.key].append(log_entry)
    
    def clear(self):
        """Clear all logs."""
        st.session_state[self.key] = []
    
    def get_logs(self) -> List[dict]:
        """Get all log entries."""
        return st.session_state.get(self.key, [])
    
    def render(self, height: int = 300):
        """
        Render the console in Streamlit.
        
        Args:
            height: Height of the console container in pixels
        """
        st.markdown("### 🖥️ Console Output")
        
        logs = self.get_logs()
        
        if not logs:
            st.markdown(
                """
                <div style="
                    background-color: #1e1e1e;
                    color: #00ff00;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    height: 100px;
                ">
                    <span style="color: #888;">Waiting for operations...</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            return
        
        # Build console HTML
        log_lines = []
        for log in logs:
            color = {
                "info": "#00bfff",
                "success": "#00ff00",
                "warning": "#ffa500",
                "error": "#ff4444",
                "processing": "#ffff00"
            }.get(log["level"], "#ffffff")
            
            log_lines.append(
                f'<div style="margin: 2px 0;">'
                f'<span style="color: #888;">[{log["timestamp"]}]</span> '
                f'<span style="color: {color};">{log["icon"]} {log["message"]}</span>'
                f'</div>'
            )
        
        console_html = f"""
        <div style="
            background-color: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: {height}px;
            overflow-y: auto;
        ">
            {''.join(log_lines)}
        </div>
        """
        
        st.markdown(console_html, unsafe_allow_html=True)
        
        # Clear button
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("🗑️ Clear", key="clear_console"):
                self.clear()
                st.rerun()


def render_console(logs: List[str] = None, height: int = 300):
    """
    Standalone function to render console with list of log strings.
    
    Args:
        logs: List of log message strings
        height: Height of console container
    """
    st.markdown("### 🖥️ Console Output")
    
    if not logs:
        logs = ["Waiting for operations..."]
    
    log_lines = []
    for log in logs:
        # Auto-detect log type from content
        if "✅" in log or "success" in log.lower():
            color = "#00ff00"
        elif "❌" in log or "error" in log.lower():
            color = "#ff4444"
        elif "⚠️" in log or "warning" in log.lower():
            color = "#ffa500"
        elif "⏳" in log or "processing" in log.lower():
            color = "#ffff00"
        else:
            color = "#00bfff"
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_lines.append(
            f'<div style="margin: 2px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: {color};">{log}</span>'
            f'</div>'
        )
    
    console_html = f"""
    <div style="
        background-color: #1e1e1e;
        color: #00ff00;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        height: {height}px;
        overflow-y: auto;
    ">
        {''.join(log_lines)}
    </div>
    """
    
    st.markdown(console_html, unsafe_allow_html=True)
