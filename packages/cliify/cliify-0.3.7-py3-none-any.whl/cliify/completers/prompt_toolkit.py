try:
    from prompt_toolkit.completion import WordCompleter, PathCompleter, Completer, Completion
    from prompt_toolkit.document import Document
    from prompt_toolkit.formatted_text import FormattedText
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from cliify.CommandWrapper import CommandWrapper
import logging 

logger = logging.getLogger("CommandCompleter")

# Global type-to-color mapping - can be customized
TYPE_COLORS = {
    'parser': 'ansibrightblue',
    'command': 'ansigreen', 
    'parameter': 'ansired',
    'value': 'ansicyan'
}

if PROMPT_TOOLKIT_AVAILABLE:
    class CommandCompleter(Completer):
        def __init__(self, cmd: CommandWrapper):
            self.path_completer = PathCompleter()
            self.args_completer = WordCompleter([], ignore_case=True)
            self.base_completer = WordCompleter([], ignore_case=True)
            self.completions_lists = {}
            self.cmd = cmd

        def get_completions(self, document: Document, complete_event):
            text = document.text
            commands = text.split(";")
            completion_tuples = self.cmd.getCompletions(commands[-1])
            
            remove_completions = []
            

            for completion_text, completion_type in completion_tuples:
                if completion_text.startswith("!"):
                    remove_completions.append((completion_text, completion_type))
                    remove_completions.append((completion_text[1:], completion_type))

            for completion_text, completion_type in completion_tuples:

                if completion_text == "$file":
                    path_text = document.get_word_before_cursor(WORD=True)
                    path_document = Document(path_text, len(path_text))
                    for completion in self.path_completer.get_completions(path_document, complete_event):
                        color = TYPE_COLORS.get('value', 'ansiwhite')
                        display_text = FormattedText([(color, completion.text)])
                        yield Completion(
                            text=completion.text,
                            start_position=completion.start_position,
                            display=display_text
                        )
                    remove_completions.append((completion_text, completion_type))
                    

                if completion_text =="$commands":
                    path_text = document.get_word_before_cursor(WORD=True)
                    path_document = Document(path_text, len(path_text))
                    cmds = self.cmd.getPathCompletions(path_document.text)
                    self.base_completer.words = [w for w in cmds if (w, 'command') not in remove_completions]
                    for completion in self.base_completer.get_completions(path_document, complete_event):
                        color = TYPE_COLORS.get('value', 'ansiwhite')
                        display_text = FormattedText([(color, completion.text)])
                        yield Completion(
                            text=completion.text,
                            start_position=completion.start_position,
                            display=display_text
                        )
                    remove_completions.append((completion_text, completion_type))
                    logging.warning(f"Removed $commands from completions for {path_text}")

            # Filter out removed completions
            filtered_completions = [c for c in completion_tuples if c not in remove_completions]

            # Calculate correct start position based on text structure
            word_before_cursor = document.get_word_before_cursor()
            
            # If text ends with '.', we don't want to replace anything, just append
            if text.endswith("."):
                start_position = 0
            else:
                start_position = -len(word_before_cursor)

            # Create colored completions
            for completion_text, completion_type in filtered_completions:
                color = TYPE_COLORS.get(completion_type, 'ansiwhite')
                display_text = FormattedText([(color, completion_text)])
                if completion_type == 'parameter':
                    completion_text += ":"
                
                yield Completion(
                    text=completion_text,
                    start_position=start_position,
                    display=display_text
                )
else:
    class CommandCompleter:
        """Fallback completer when prompt_toolkit is not available"""
        def __init__(self, cmd: CommandWrapper):
            self.cmd = cmd
            print("Warning: prompt_toolkit is not installed. Command completion is disabled.")