try:
    from textual.suggester import Suggester
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from cliify.CommandWrapper import CommandWrapper
import logging 
import os

logger = logging.getLogger("CommandCompleter")

if TEXTUAL_AVAILABLE:
    class CommandCompleter(Suggester):
        def __init__(self, cmd: CommandWrapper, case_sensitive: bool = False):
            super().__init__(case_sensitive=case_sensitive)
            self.cmd = cmd

        async def get_suggestion(self, value: str) -> str | None:
            """Get command completion suggestion"""
            if not value:
                return None
            
            try:
                # Split by semicolons to handle multiple commands
                commands = value.split(";")
                current_command = commands[-1].strip()
                
                if not current_command:
                    return None
                
                # Get completions from the command wrapper
                completions = self.cmd.getCompletions(current_command)
                filtered_completions = []
                
                # Process special completion markers
                for completion in completions:
                    word = str(completion).strip()
                    
                    # Skip negated completions (starting with !)
                    if word.startswith("!"):
                        continue
                    
                    # Handle file completions
                    if word == "$file":
                        # Get the last word for path completion
                        words = current_command.split()
                        if words:
                            last_word = words[-1]
                            # Simple path completion - return directory/file suggestions
                            try:
                                if os.path.isdir(last_word) or "/" in last_word:
                                    base_path = os.path.dirname(last_word) or "."
                                    filename = os.path.basename(last_word)
                                    
                                    if os.path.exists(base_path):
                                        for item in os.listdir(base_path):
                                            if item.startswith(filename):
                                                suggestion = os.path.join(base_path, item)
                                                if suggestion.startswith(last_word) and suggestion != last_word:
                                                    return current_command.rsplit(last_word, 1)[0] + suggestion
                            except (OSError, PermissionError):
                                pass
                        continue
                    
                    # Handle command completions
                    if word == "$commands":
                        # Get path completions from command wrapper
                        words = current_command.split()
                        if words:
                            last_word = words[-1]
                            path_completions = self.cmd.getPathCompletions(last_word)
                            for comp in path_completions:
                                if str(comp).startswith(last_word) and str(comp) != last_word:
                                    return current_command.rsplit(last_word, 1)[0] + str(comp)
                        continue
                    
                    filtered_completions.append(word)
                
                # Find the first completion that extends the current command
                words = current_command.split()
                if words:
                    last_word = words[-1]
                    for completion in filtered_completions:
                        if completion.startswith(last_word) and completion != last_word:
                            # Replace the last word with the completion
                            prefix = current_command.rsplit(last_word, 1)[0]
                            return prefix + completion
                else:
                    # If no words yet, suggest the first available completion
                    if filtered_completions and filtered_completions[0] != current_command:
                        return filtered_completions[0]
                        
            except Exception as e:
                logger.error(f"Error getting completions for '{value}': {e}")
            
            return None

else:
    class CommandCompleter:
        """Fallback completer when Textual is not available"""
        def __init__(self, cmd: CommandWrapper):
            self.cmd = cmd
            print("Warning: Textual is not installed. Command completion is disabled.")