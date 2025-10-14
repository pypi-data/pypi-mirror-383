from IPython.core.magic import Magics, line_magic, magics_class
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
from IPython.core.events import EventManager
import io
import ast
import inspect


@magics_class
class PollywogMagics(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.autodownload_enabled = False
        self._original_to_lfcalc = None
        
    @line_magic
    @magic_arguments()
    @argument('command', choices=['on', 'off', 'status'], help='Enable/disable autodownload')
    def pollywog(self, line):
        """
        Pollywog magic commands.
        
        Usage:
        %pollywog autodownload on   - Enable automatic downloads
        %pollywog autodownload off  - Disable automatic downloads  
        %pollywog autodownload status - Show current status
        """
        args = line.strip().split()
        
        if len(args) < 2 or args[0] != 'autodownload':
            print("Usage: %pollywog autodownload [on|off|status]")
            return
            
        command = args[1]
        
        if command == 'on':
            self._enable_autodownload()
            print("Pollywog autodownload enabled")
        elif command == 'off':
            self._disable_autodownload()
            print("Pollywog autodownload disabled")
        elif command == 'status':
            status = "enabled" if self.autodownload_enabled else "disabled"
            print(f"Pollywog autodownload is {status}")
            
    def _enable_autodownload(self):
        if not self.autodownload_enabled:
            try:
                from pollywog.core import CalcSet
                from pollywog.jupyterlite_utils import is_jupyterlite, download_file
                
                if is_jupyterlite():
                    # Monkey patch CalcSet.to_lfcalc in JupyterLite
                    if self._original_to_lfcalc is None:
                        self._original_to_lfcalc = CalcSet.to_lfcalc
                        
                    def patched_to_lfcalc(self, filepath_or_buffer, sort_items=True):
                        if isinstance(filepath_or_buffer, (str, type(None).__class__.__bases__[0])):  # str or Path
                            # Generate file content and trigger download
                            buffer = io.BytesIO()
                            self._original_to_lfcalc(buffer, sort_items=sort_items)
                            download_file(buffer.getvalue(), str(filepath_or_buffer), "application/octet-stream")
                        else:
                            # Call original method for file-like objects
                            self._original_to_lfcalc(filepath_or_buffer, sort_items=sort_items)
                    
                    CalcSet._original_to_lfcalc = CalcSet.to_lfcalc
                    CalcSet.to_lfcalc = patched_to_lfcalc
                    self.autodownload_enabled = True
                else:
                    print("Autodownload only works in JupyterLite environment")
                    
            except ImportError as e:
                print(f"Could not enable autodownload: {e}")
                
    def _disable_autodownload(self):
        if self.autodownload_enabled and self._original_to_lfcalc is not None:
            try:
                from pollywog.core import CalcSet
                CalcSet.to_lfcalc = self._original_to_lfcalc
                self.autodownload_enabled = False
            except ImportError:
                pass


def load_ipython_extension(ipython):
    """Load the extension in IPython."""
    ipython.register_magic_function(PollywogMagics(ipython).pollywog, 'line', 'pollywog')
    

def unload_ipython_extension(ipython):
    """Unload the extension from IPython."""
    # Clean up if needed
    pass