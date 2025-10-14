import cli2
import litellm
import os
import re
import subprocess
import sys
import textwrap


cli = cli2.Group()


class Context:
    def __init__(self, messages=None):
        self.messages = messages or []

    def file_add(self, path):
        key = f'What is the content of the file {path}?'
        if any([
            (
                message['role'] == 'assistant'
                and message['content'] == key
            ) for message in self.messages
        ]):
            return  # file already added

        with open(path, 'r') as f:
            try:
                content = f.read()
            except UnicodeDecodeError:  # binary
                cli2.log.debug('failed to attach binary file', path=path)
                return

        self.messages += [
            dict(
                role='assistant',
                content=key,
            ),
            dict(
                role='user',
                content=content,
            ),
        ]

    def command_add(self, command):
        cli2.log.warn(
            'Running command, might take some time ...',
            command=command,
        )

        # Use Popen for live output
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            env=os.environ,
            text=True,  # Ensures output is treated as text (not bytes)
        )

		# Stream the output in real-time
        stdout = ''
        while True:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                break
            if output:
                stdout += output
                sys.stdout.write(output)
                sys.stdout.flush()  # Ensure immediate display

        print('\n')

        # Get the return code
        return_code = proc.poll()
        self.messages += [
            dict(
                role='assistant',
                content=f'What is the output of command {command}?',
            ),
            dict(
                role='user',
                content=stdout,
            ),
        ]
        return str(stdout)


class Model:
    def __init__(self):
        args, self.kwargs = self.configuration_parse(os.getenv(
            'MODEL',
            'openrouter/deepseek/deepseek-r1:free',  # some default model
        ).split())
        self.name = args[0]

    @staticmethod
    def configuration_parse(tokens):
        # convert "a bar=1" string into args=['a'] kwargs={'b': 1}
        args = list()
        kwargs = dict()
        for token in tokens:
            key = None
            if '=' in token:
                key, value = token.split('=')
            else:
                value = token

            try:
                value = float(value)
            except ValueError:
                try:
                    value = int(value)
                except ValueError:
                    pass

            if key:
                kwargs[key] = value
            else:
                args.append(value)
        return args, kwargs

    async def send(self, messages):
        if os.getenv('LITELLM_DEBUG'):
            litellm._turn_on_debug()
        stream = await litellm.acompletion(
            messages=messages,
            stream=True,
            model=self.name,
            **self.kwargs,
        )

        full_content = ''
        printed_lines = 0
        full_reasoning = ''
        reasoning_printed = False
        code_open = False
        async for chunk in stream:
            if hasattr(chunk, 'choices') and chunk.choices:
                delta = chunk.choices[0].delta
                if reasoning := getattr(delta, 'reasoning_content', None):
                    if stream:
                        if not reasoning_printed:
                            print(cli2.t.o.b('REASONING'), file=sys.stderr)
                            reasoning_printed = True
                        print(
                            cli2.t.G(delta.reasoning_content),
                            end='',
                            flush=True,
                            file=sys.stderr,
                        )
                    full_reasoning += reasoning

                if content := getattr(delta, 'content', ''):
                    if reasoning_printed:
                        # separate reasoning output visually
                        print('\n', file=sys.stderr)
                        reasoning_printed = False

                    full_content += content
                    if not content.endswith('\n'):
                        continue

                    new_lines = full_content.split('\n')[printed_lines:]
                    for new_line in new_lines:
                        if new_line.strip().startswith('```'):
                            code_open = not code_open

                    if not new_lines:
                        continue

                    highlight_content = full_content
                    if code_open:
                        # manuall close code block for pygments to highlight
                        if not highlight_content.endswith('\n'):
                            highlight_content += '\n'
                        highlight_content += '```'

                    highlighted = cli2.highlight(highlight_content, 'Markdown')
                    highlighted_lines = highlighted.split('\n')

                    if code_open:
                        highlighted_lines = highlighted_lines[:-1]

                    print(
                        '\n'.join(highlighted_lines[printed_lines:]),
                        flush=True,
                        file=sys.stderr,
                    )
                    printed_lines = len(highlighted_lines)

        new_lines = full_content.split('\n')[printed_lines:]
        for new_line in new_lines:
            if new_line.strip().startswith('```'):
                code_open = not code_open

        highlight_content = full_content
        if code_open:
            # manuall close code block for pygments to highlight code
            if not highlight_content.endswith('\n'):
                highlight_content += '\n'
            highlight_content += '```'

        highlighted = cli2.highlight(highlight_content, 'Markdown')
        highlighted_lines = highlighted.split('\n')

        if code_open:
            highlighted_lines = highlighted_lines[:-1]

        print(
            '\n'.join(highlighted_lines[printed_lines:]),
            flush=True,
            file=sys.stderr,
        )

        return full_content or full_reasoning, stream


@cli.cmd(color='green')
async def shoot(*prompt):
    """
    One-shot LLM query, without looping.

    However, you're building the context in the prompt itself because
    the prompt will be parsed and:

    - Find any path in the prompt and automatically attach content.
    - Find any command between brackets, run it and attach its output.
    - For any path in the output, attach the contents if the path is relative
      to the current directory.

    Examples:

    # shoot to explain foo.py and attach the ./foo.py file to the context
    artinator shoot explain my/foo.py

    # run "your command", parse the output and attach it to the context
    # if the output contains relative paths to the current directory, attach
    # them to the output, useful to debug tracebacks
    artinator shoot what breaks ^my command^ is it a bug in foo.py
    """
    model = Model()
    if litellm.supports_function_calling(model.name):
        cli2.log.warn('function calling not yet implemented, using old code')

    NOTOOL_SYSTEM_PROMPT = textwrap.dedent('''
        You are a systems and networks senior programmer called by an automated
        Agentic Systems and Network coding assistant.
        Always reply in Markdown.
    ''')
    prompt = ' '.join(prompt)
    context = Context([
        dict(
            role='system',
            content=NOTOOL_SYSTEM_PROMPT,
        ),
        dict(
            role='user',
            content=prompt,
        )
    ])

    def files_find(content):
        for token in content.split():
            names = re.findall('([/.\\w]+)', token)
            for name in names:
                if os.path.exists(name) and os.path.isfile(name):
                    context.file_add(name)

    files_find(prompt)

    in_cmd = []
    for token in prompt.split():
        if token.startswith('^'):
            if token.endswith('^'):
                # one word command case
                in_cmd = [token[1:-1]]
            else:
                in_cmd = [token[1:]]
                continue

        elif in_cmd:
            if token.endswith('^'):
                in_cmd.append(token[:-1])
            else:
                in_cmd.append(token)
                continue

        if in_cmd:
            output = context.command_add(' '.join(in_cmd))
            # reset in_cmd to initial state
            in_cmd = []
            # attach any relative file from the output
            files_find(output)

    cli2.log.debug('messages', json=context.messages)

    await model.send(context.messages)


@cli.cmd
async def loop(*prompt):
    """
    Let the LLM run bash commands until it can answer your query.

    Example: artinator loop fix some test

    """
    NOTOOL_SYSTEM_PROMPT = textwrap.dedent('''
        You are a systems and networks senior programmer called by an automated
        Agentic Systems and Network coding assistant.

        If you need more context, suggest commands to run in ```bash blocks.
        Only suggest one command per ```bash block only, it can be multiline.
        If the user is asking you to check or fix a command, make sure to run
        it first to get the output, with verbose flags if you know any.
        Only suggest complete shell commands that are ready to execute, without
        placeholders.
        Do not suggest interactive shell commands.
        No need to suggest to many commands, only suggest the actually
        necessary ones that you need to gather context.
        Consider that you are in a project directory, don't assume anything
        about the project, use commands like ls commands to navigate the tree
        and cat or grep to inspect source code until you have enough context.

        When you have enough context to provide a relevant answer, which means
        that you don't need the user to ensure anything for you, then don't
        suggest any more command, until you have enough context, keep
        suggesting commands.

        Always reply in Markdown.
    ''')
    NOTOOL_SYSTEM_PROMPT = textwrap.dedent('''
	You are a senior systems and networks programmer acting as an automated Agentic Systems and Network coding assistant.

	- Suggest one complete, executable shell command per ```suggestedcommand``` block to gather context when needed. Use verbose flags if applicable.
	- Avoid interactive commands or placeholders in suggestions.
	- Assume you are in a project directory but make no assumptions about its structure. Use commands like `ls`, `cat`, or `grep` to inspect files and navigate.
	- Suggest only necessary commands to gain sufficient context.
	- When you have enough context to provide a complete, relevant answer, stop suggesting commands and respond directly.
	- If checking or fixing a user-provided command, execute it first to capture output, using verbose flags if known.
	- Always respond in Markdown.
    ''')

    prompt = ' '.join(prompt)
    context = Context([
        dict(
            role='system',
            content=NOTOOL_SYSTEM_PROMPT,
        ),
        dict(
            role='user',
            content=prompt,
        )
    ])
    model = Model()
    if litellm.supports_function_calling(model.name):
        cli2.log.warn('function calling not yet implemented, using old code')

    answer = None
    while True:
        text, response = await model.send(context.messages)

        context.messages.append({
            'role': 'assistant',
            'content': text,
        })

        cmds = []
        in_bash = False
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('```suggestedcommand'):
                in_bash = True
                continue
            if in_bash:
                if line == '```':
                    in_bash = False
                else:
                    cmds.append(line)

        for cmd in cmds:
            if answer != 'a':
                answer = cli2.choice(
                    f'Run command {cmd}? '
                    '(yes/no/Accept all for this session/Ctrl+C to exit)',
                    ['y', 'n', 'a'],
                )

            if answer in ('a', 'y'):
                context.command_add(cmd)

        if not cmds:
            return

    cli2.print(context.messages)
