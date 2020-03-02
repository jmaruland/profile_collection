import datetime
from IPython.terminal.prompts import Prompts, Token


class MyPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [(Token.CursorLine, f'{datetime.datetime.isoformat(datetime.datetime.now())}'),
                (Token.Prompt, ' ['),
                (Token.PromptNum, str(self.shell.execution_count)),
                (Token.Prompt, '] ' + u"\u25B6" + ' ')]


ip = get_ipython()
ip.prompts = MyPrompt(ip)
