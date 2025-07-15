import datetime
from IPython.terminal.prompts import Prompts, Token


class ProposalIDPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [
            (Token.CursorLine, f"{datetime.datetime.isoformat(datetime.datetime.now(), timespec='seconds')} - "),
            (
                Token.Prompt,
                f"{RE.md.get('data_session', 'N/A')} - {RE.md.get('project_name', 'N/A')} [",
            ),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, '] ' + u"\u25B6" + ' '),
        ]

ip = get_ipython()
ip.prompts = ProposalIDPrompt(ip)
