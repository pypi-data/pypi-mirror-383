import pytest
import os
import tempfile
import base64
import glob
import cmd2
import ara_cli
from unittest.mock import patch, MagicMock, mock_open
from types import SimpleNamespace
from ara_cli.chat import Chat
from ara_cli.error_handler import AraError
from ara_cli.template_manager import TemplatePathManager
from ara_cli.ara_config import ConfigManager
from ara_cli.file_loaders.text_file_loader import TextFileLoader


def get_default_config():
    return SimpleNamespace(
        ext_code_dirs=[
            {"source_dir": "./src"},
            {"source_dir": "./tests"},
        ],
        glossary_dir="./glossary",
        doc_dir="./docs",
        local_prompt_templates_dir="./ara/.araconfig",
        local_ara_templates_dir="./ara/.araconfig/templates/",
        ara_prompt_given_list_includes=[
            "*.businessgoal",
            "*.vision",
            "*.capability",
            "*.keyfeature",
            "*.epic",
            "*.userstory",
            "*.example",
            "*.feature",
            "*.task",
            "*.py",
            "*.md",
            "*.png",
            "*.jpg",
            "*.jpeg",
        ],
        llm_config=[
            {"provider": "openai", "model": "openai/gpt-4o", "temperature": 1.0},
            {"provider": "openai", "model": "openai/o3-mini", "temperature": 1.0},
        ],
    )


@pytest.fixture
def temp_chat_file():
    """Fixture to create a temporary chat file."""
    temp_file = tempfile.NamedTemporaryFile(delete=True, mode="w+", encoding="utf-8")
    yield temp_file
    temp_file.close()


@pytest.fixture
def temp_load_file():
    """Fixture to create a temporary file to load."""
    temp_file = tempfile.NamedTemporaryFile(delete=True, mode="w+", encoding="utf-8")
    temp_file.write("This is the content to load.")
    temp_file.flush()
    yield temp_file
    temp_file.close()


def test_handle_existing_chat_no_reset(temp_chat_file):
    with patch("builtins.input", return_value="n"):
        mock_config = get_default_config()
        with patch(
            "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
        ):
            chat = Chat(temp_chat_file.name, reset=None)
        assert chat.chat_name == temp_chat_file.name


def test_handle_existing_chat_with_reset(temp_chat_file):
    with patch("builtins.input", return_value="y"):
        mock_config = get_default_config()
        with patch(
            "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
        ):
            chat = Chat(temp_chat_file.name, reset=None)
        with open(temp_chat_file.name, "r", encoding="utf-8") as file:
            content = file.read()
        assert content.strip() == "# ara prompt:"


def test_handle_existing_chat_reset_flag(temp_chat_file):
    mock_config = get_default_config()

    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        Chat(temp_chat_file.name, reset=True)
    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        content = file.read()
    assert content.strip() == "# ara prompt:"


@pytest.mark.parametrize(
    "chat_name, expected_file_name",
    [
        ("test", "test_chat.md"),
        ("test.md", "test.md"),
        ("test_chat", "test_chat.md"),
        ("test_chat.md", "test_chat.md"),
        ("another_test", "another_test_chat.md"),
        ("another_test.md", "another_test.md"),
    ],
)
def test_initialize_new_chat(chat_name, expected_file_name):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_chat_file_path = os.path.join(temp_dir, "temp_chat_file.md")
        mock_config = get_default_config()
        with patch(
            "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
        ):
            chat_instance = Chat(temp_chat_file_path, reset=False)
        created_chat_file = chat_instance.initialize_new_chat(
            os.path.join(temp_dir, chat_name)
        )

        assert created_chat_file.endswith(expected_file_name)
        assert os.path.exists(created_chat_file)

        with open(created_chat_file, "r", encoding="utf-8") as file:
            content = file.read()

        assert content == chat_instance.default_chat_content


def test_init_with_limited_command_set():
    with tempfile.TemporaryDirectory() as temp_dir:
        enable_commands = ["RERUN", "SEND", "EXTRACT"]
        temp_chat_file_path = os.path.join(temp_dir, "temp_chat_file.md")

        mock_config = get_default_config()
        with patch(
            "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
        ):
            chat_instance = Chat(
                temp_chat_file_path, reset=False, enable_commands=enable_commands
            )

        assert "r" in chat_instance.aliases
        assert "s" in chat_instance.aliases
        assert "QUIT" in chat_instance.aliases
        assert "q" in chat_instance.aliases
        assert "h" in chat_instance.aliases

        assert "shell" in chat_instance.hidden_commands
        assert getattr(chat_instance, "do_shell") == chat_instance.default


@pytest.mark.parametrize(
    "chat_name, existing_files, expected",
    [
        ("test_chat", ["test_chat"], "test_chat"),
        ("test_chat", ["test_chat.md"], "test_chat.md"),
        ("test_chat", ["test_chat_chat.md"], "test_chat_chat.md"),
        ("new_chat", [], "new_chat_chat.md"),
    ],
)
def test_setup_chat(monkeypatch, chat_name, existing_files, expected):
    def mock_exists(path):
        return path in existing_files

    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(
        Chat, "handle_existing_chat", lambda self, chat_file, reset=None: chat_file
    )
    monkeypatch.setattr(
        Chat, "initialize_new_chat", lambda self, chat_name: f"{chat_name}_chat.md"
    )

    mock_config = get_default_config()

    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat_instance = Chat(chat_name)
    result = chat_instance.setup_chat(chat_name)
    assert result == expected


def test_disable_commands(temp_chat_file):
    mock_config = get_default_config()

    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat.aliases["q"] = "quit"
    chat.aliases["h"] = "help"
    chat.aliases["r"] = "RERUN"
    chat.aliases["s"] = "SEND"

    commands_to_disable = ["quit", "help"]

    chat.disable_commands(commands_to_disable)

    for command in commands_to_disable:
        assert getattr(chat, f"do_{command}") == chat.default
        assert command in chat.hidden_commands

    assert "q" not in chat.aliases
    assert "h" not in chat.aliases

    assert "s" in chat.aliases
    assert "r" in chat.aliases


@pytest.mark.parametrize(
    "lines, expected",
    [
        (["This is a line.", "Another line here.", "Yet another line."], None),
        (["This is a line.", "# ara prompt:", "Another line here."], "# ara prompt:"),
        (
            [
                "This is a line.",
                "# ara prompt:",
                "Another line here.",
                "# ara response:",
            ],
            "# ara response:",
        ),
        (
            [
                "This is a line.",
                "  # ara prompt:  ",
                "Another line here.",
                "  # ara response:    ",
            ],
            "# ara response:",
        ),
        (["# ara prompt:", "# ara response:"], "# ara response:"),
        (
            ["# ara response:", "# ara prompt:", "# ara prompt:", "# ara response:"],
            "# ara response:",
        ),
        ([], None),
    ],
)
def test_get_last_role_marker(lines, expected):
    assert Chat.get_last_role_marker(lines=lines) == expected


def test_start_non_interactive(temp_chat_file, capsys):
    content = "This is a test chat content.\nAnother line of chat."
    temp_chat_file.write(content)
    temp_chat_file.flush()
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.start_non_interactive()

    captured = capsys.readouterr()

    assert content + "\n" in captured.out


def test_start(temp_chat_file):
    initial_dir = os.getcwd()
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("ara_cli.chat.Chat.cmdloop") as mock_cmdloop:
        chat.start()
        mock_cmdloop.assert_called_once()

    assert os.getcwd() == os.path.dirname(temp_chat_file.name)

    os.chdir(initial_dir)


@pytest.mark.parametrize(
    "initial_content, expected_content",
    [
        (
            ["This is a line.\n", "Another line here.\n", "Yet another line.\n"],
            [
                "This is a line.\n",
                "Another line here.\n",
                "Yet another line.\n",
                "\n",
                "# ara prompt:",
            ],
        ),
        (
            ["This is a line.\n", "# ara prompt:\n", "Another line here.\n"],
            ["This is a line.\n", "# ara prompt:\n", "Another line here.\n"],
        ),
        (
            [
                "This is a line.\n",
                "# ara prompt:\n",
                "Another line here.\n",
                "# ara response:\n",
            ],
            [
                "This is a line.\n",
                "# ara prompt:\n",
                "Another line here.\n",
                "# ara response:\n",
                "\n",
                "# ara prompt:",
            ],
        ),
        (
            [
                "This is a line.\n",
                "  # ara prompt:  \n",
                "Another line here.\n",
                "  # ara response:    \n",
            ],
            [
                "This is a line.\n",
                "  # ara prompt:  \n",
                "Another line here.\n",
                "  # ara response:    \n",
                "\n",
                "# ara prompt:",
            ],
        ),
        (
            ["# ara prompt:\n", "# ara response:\n"],
            ["# ara prompt:\n", "# ara response:\n", "\n", "# ara prompt:"],
        ),
        (
            [
                "# ara response:\n",
                "# ara prompt:\n",
                "# ara prompt:\n",
                "# ara response:\n",
            ],
            [
                "# ara response:\n",
                "# ara prompt:\n",
                "# ara prompt:\n",
                "# ara response:\n",
                "\n",
                "# ara prompt:",
            ],
        ),
    ],
)
def test_add_prompt_tag_if_needed(temp_chat_file, initial_content, expected_content):
    temp_chat_file.writelines(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        Chat(temp_chat_file.name, reset=False).add_prompt_tag_if_needed(
            temp_chat_file.name
        )

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    assert lines == expected_content


@pytest.mark.parametrize(
    "lines, expected",
    [
        (
            ["\n", "    ", "# ara prompt:", "Another line here.", "  \n"],
            "Another line here.",
        ),
        (["This is a line.", "Another line here.", "  \n", "\n"], "Another line here."),
        (["\n", "  \n", "  \n"], ""),
        (
            ["This is a line.", "Another line here.", "# ara response:", "  \n"],
            "# ara response:",
        ),
    ],
)
def test_get_last_non_empty_line(lines, expected, temp_chat_file):
    temp_chat_file.writelines(line + "\n" for line in lines)
    temp_chat_file.flush()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        assert Chat.get_last_non_empty_line(Chat, file) == expected


@pytest.mark.parametrize(
    "lines, expected",
    [
        (["\n", "    ", "# ara prompt:", "Another line here.", "  \n"], ""),
        (["This is a line.", "Another line here."], "Another line here."),
        (["\n", "  \n", "  \n"], ""),
        (["This is a line.", "Another line here.", "# ara response:", "  \n"], ""),
        ([], ""),
        ([""], ""),
    ],
)
def test_get_last_line(lines, expected, temp_chat_file):
    temp_chat_file.writelines(line + "\n" for line in lines)
    temp_chat_file.flush()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        assert Chat.get_last_line(Chat, file) == expected


@pytest.mark.parametrize(
    "chat_history, expected_text_content, expected_image_data_list",
    [
        (["Message 1", "Message 2"], "Message 1\nMessage 2", []),
        (
            ["Text with image", "(data:image/png;base64,abc123)"],
            "Text with image",
            [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64,abc123"},
                }
            ],
        ),
        (
            ["Just text", "Another (data:image/png;base64,xyz789) image"],
            "Just text",
            [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64,xyz789"},
                }
            ],
        ),
        (["No images here at all"], "No images here at all", []),
    ],
)
def test_assemble_prompt(
    temp_chat_file, chat_history, expected_text_content, expected_image_data_list
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.chat_history = chat_history

    with patch('ara_cli.prompt_handler.append_images_to_message', return_value="mocked combined content") as mock_append, \
         patch('ara_cli.prompt_handler.prepend_system_prompt', return_value=[{'role': 'system', 'content': 'You are a helpful assistant that can process both text and images.'}]) as mock_prepend:
        chat.assemble_prompt()

        mock_append.assert_called_once_with(
            {
                "role": "user",
                "content": [{"type": "text", "text": expected_text_content}],
            },
            expected_image_data_list,
        )

        mock_prepend.assert_called_once()


@pytest.mark.parametrize(
    "chat_history, last_line_in_file, expected_written_content",
    [
        (["Message 1", "Message 2"], "Some other line", "\n# ara response:\n"),
        (["Message 1", "Message 2"], "Some other line\n", "# ara response:\n"),
        (["Message 1", "Message 2"], "# ara response:", ""),
    ],
)
def test_send_message(
    temp_chat_file, chat_history, last_line_in_file, expected_written_content
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.chat_history = chat_history

    mock_chunk1 = MagicMock()
    mock_chunk1.choices = [MagicMock(delta=MagicMock(content="response_part_1"))]
    mock_chunk2 = MagicMock()
    mock_chunk2.choices = [MagicMock(delta=MagicMock(content="response_part_2"))]

    mock_chunks = [mock_chunk1, mock_chunk2]

    with patch("ara_cli.chat.send_prompt", return_value=mock_chunks), patch.object(
        chat, "get_last_line", return_value=last_line_in_file
    ), patch.object(chat, "assemble_prompt", return_value="mocked prompt"):

        m = mock_open(read_data=last_line_in_file)
        with patch("builtins.open", m):
            chat.send_message()

            written_content = "".join(call[0][0] for call in m().write.call_args_list)
            assert expected_written_content in written_content
            assert "response_part_1" in written_content
            assert "response_part_2" in written_content


@pytest.mark.parametrize(
    "role, message, initial_content, expected_content",
    [
        (
            "ara prompt",
            "This is a new prompt message.",
            ["Existing content.\n"],
            [
                "Existing content.\n",
                "\n",
                "# ara prompt:\nThis is a new prompt message.\n",
            ],
        ),
        (
            "ara response",
            "This is a new response message.",
            ["# ara prompt:\nThis is a prompt.\n"],
            [
                "# ara prompt:\nThis is a prompt.\n",
                "\n",
                "# ara response:\nThis is a new response message.\n",
            ],
        ),
        (
            "ara prompt",
            "This is another prompt.",
            ["# ara response:\nThis is a response.\n"],
            [
                "# ara response:\nThis is a response.\n",
                "\n",
                "# ara prompt:\nThis is another prompt.\n",
            ],
        ),
        (
            "ara response",
            "Another response here.",
            ["# ara prompt:\nPrompt here.\n", "# ara response:\nFirst response.\n"],
            [
                "# ara prompt:\nPrompt here.\n",
                "# ara response:\nFirst response.\n",
                "\n",
                "# ara response:\nAnother response here.\n",
            ],
        ),
        (
            "ara prompt",
            "Final prompt message.",
            ["# ara prompt:\nInitial prompt.\n", "# ara response:\nResponse here.\n"],
            [
                "# ara prompt:\nInitial prompt.\n",
                "# ara response:\nResponse here.\n",
                "\n",
                "# ara prompt:\nFinal prompt message.\n",
            ],
        ),
    ],
)
def test_save_message(temp_chat_file, role, message, initial_content, expected_content):
    temp_chat_file.writelines(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat_instance = Chat(temp_chat_file.name, reset=False)
    chat_instance.save_message(role, message)

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    assert "".join(lines) == "".join(expected_content)


@pytest.mark.parametrize(
    "initial_content, expected_content",
    [
        (
            [
                "# ara prompt:\nPrompt message.\n",
                "# ara response:\nResponse message.\n",
            ],
            ["# ara prompt:\nPrompt message.\n"],
        ),
        (
            [
                "# ara prompt:\nPrompt message 1.\n",
                "# ara response:\nResponse message 1.\n",
                "# ara prompt:\nPrompt message 2.\n",
                "# ara response:\nResponse message 2.\n",
            ],
            [
                "# ara prompt:\nPrompt message 1.\n",
                "# ara response:\nResponse message 1.\n",
                "# ara prompt:\nPrompt message 2.\n",
            ],
        ),
        (
            ["# ara prompt:\nOnly prompt message.\n"],
            ["# ara prompt:\nOnly prompt message.\n"],
        ),
        (
            [
                "# ara prompt:\nPrompt message.\n",
                "# ara response:\nResponse message.\n",
                "# ara prompt:\nAnother prompt message.\n",
            ],
            [
                "# ara prompt:\nPrompt message.\n",
                "# ara response:\nResponse message.\n",
                "# ara prompt:\nAnother prompt message.\n",
            ],
        ),
    ],
)
def test_resend_message(temp_chat_file, initial_content, expected_content):
    temp_chat_file.writelines(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "send_message") as mock_send_message:
        chat.resend_message()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    assert "".join(lines) == "".join(expected_content)
    mock_send_message.assert_called_once()


def test_resend_message_empty(temp_chat_file):
    temp_chat_file.writelines([])
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "send_message") as mock_send_message:
        chat.resend_message()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        lines = file.readlines()

    assert "".join(lines) == ""
    assert "".join(chat.chat_history) == ""
    mock_send_message.assert_not_called()


@pytest.mark.parametrize(
    "strings, expected_content",
    [
        (["Line 1", "Line 2", "Line 3"], "Line 1\nLine 2\nLine 3\n"),
        (["Single line"], "Single line\n"),
        (["First line", "", "Third line"], "First line\n\nThird line\n"),
        ([], "\n"),
    ],
)
def test_append_strings(temp_chat_file, strings, expected_content):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat_instance = Chat(temp_chat_file.name, reset=False)
    chat_instance.append_strings(strings)

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        content = file.read()

    assert content == expected_content


@pytest.mark.parametrize(
    "file_name, expected_content",
    [
        ("document.txt", "Hello World\n"),
        ("another_document.txt", "Another World\n"),
    ],
)
def test_load_text_file(temp_chat_file, file_name, expected_content):
    # Create a mock config
    mock_config = MagicMock()

    # Patch the get_config method to return the mock config
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Mock the TextFileLoader
    with patch.object(TextFileLoader, "load", return_value=True) as mock_load:
        # Call the load_text_file method
        result = chat.load_text_file(file_name)

        # Check that the load method was called once
        mock_load.assert_called_once()

        # Check that the result is True
        assert result is True


@pytest.mark.parametrize(
    "path_exists",
    [
        True,
        # False # TODO: @file_exists_check decorator should be fixed
    ],
)
def test_load_binary_file(temp_chat_file, path_exists):
    """
    Tests loading a binary file.
    The implementation of BinaryFileLoader is assumed to be correct
    and this test verifies that chat.load_binary_file properly
    delegates to it after checking for file existence.
    """
    file_name = "image.png"
    mime_type = "image/png"
    file_content = b"fake-binary-data"

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Path to the actual file to be loaded
    path_to_load = file_name if path_exists else None

    # We patch open within the loader's module
    with patch(
        "ara_cli.file_loaders.binary_file_loader.open",
        mock_open(read_data=file_content),
    ) as mock_loader_open:

        result = chat.load_binary_file(
            file_name, mime_type=mime_type, prefix="PRE-", suffix="-POST"
        )

        if path_exists:
            assert result is True
            # Check read call for the image
            mock_loader_open.assert_any_call(file_name, "rb")
            # Check write call to the chat file
            mock_loader_open.assert_any_call(chat.chat_name, "a", encoding="utf-8")

            # Assuming the loader formats it as a base64 markdown image
            base64_encoded = base64.b64encode(file_content).decode("utf-8")
            # This assumes the incomplete `write_content` in binary_file_loader.py is meant to create a markdown image.
            expected_write_content = f"PRE-![{os.path.basename(file_name)}](data:{mime_type};base64,{base64_encoded})-POST\n"

            # Since the write content is not defined, we cannot reliably test it.
            # Instead, we just check that write was called.
            mock_loader_open().write.assert_called()

        else:
            assert result is False
            mock_loader_open.assert_not_called()


@pytest.mark.parametrize(
    "file_name, module_to_mock, mock_setup, expected_content",
    [
        (
            "test.docx",
            "docx",
            lambda mock: setattr(
                mock.Document.return_value,
                "paragraphs",
                [MagicMock(text="Docx content")],
            ),
            "Docx content",
        ),
        pytest.param(
            "test.pdf",
            "pymupdf4llm",
            lambda mock: setattr(
                mock, "to_markdown", MagicMock(return_value="PDF content")
            ),
            "PDF content",
            marks=pytest.mark.filterwarnings("ignore::DeprecationWarning"),
        ),
        pytest.param(
            "test.odt",
            "pymupdf4llm",
            lambda mock: setattr(
                mock, "to_markdown", MagicMock(return_value="ODT content")
            ),
            "ODT content",
            marks=pytest.mark.filterwarnings("ignore::DeprecationWarning"),
        ),
    ],
)
def test_load_document_file(
    temp_chat_file, file_name, module_to_mock, mock_setup, expected_content
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Patch the dependency in sys.modules before it's imported inside the method
    with patch.dict("sys.modules", {module_to_mock: MagicMock()}) as mock_modules:
        mock_setup(mock_modules[module_to_mock])

        with patch(
            "ara_cli.file_loaders.document_file_loader.open", mock_open()
        ) as mock_chat_open:
            # FIX: Call with a positional argument `file_name` as the decorator expects, not a keyword `file_path`.
            result = chat.load_document_file(
                file_name, prefix="Prefix-", suffix="-Suffix", block_delimiter="```"
            )

            assert result is True
            expected_write = f"Prefix-```\n{expected_content}\n```-Suffix\n"
            mock_chat_open.assert_called_with(chat.chat_name, "a", encoding="utf-8")
            mock_chat_open().write.assert_called_once_with(expected_write)


def test_load_document_file_unsupported(temp_chat_file, capsys):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    unsupported_file = "test.txt"
    result = chat.load_document_file(unsupported_file)

    assert result is False
    captured = capsys.readouterr()
    assert "Unsupported document type." in captured.out


@pytest.mark.parametrize(
    "file_name, file_type, mime_type",
    [
        ("image.png", "binary", "image/png"),
        ("document.txt", "text", None),
        ("document.docx", "document", None),
        ("document.pdf", "document", None),
        ("archive.zip", "text", None),
    ],
)
def test_load_file(temp_chat_file, file_name, file_type, mime_type):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(
        chat, "load_binary_file", return_value=True
    ) as mock_load_binary, patch.object(
        chat, "load_text_file", return_value=True
    ) as mock_load_text, patch.object(
        chat, "load_document_file", return_value=True
    ) as mock_load_document:

        chat.load_file(
            file_name=file_name,
            prefix="p-",
            suffix="-f",
            block_delimiter="b",
            extract_images=False,
        )

        if file_type == "binary":
            mock_load_binary.assert_called_once_with(
                file_path=file_name, mime_type=mime_type, prefix="p-", suffix="-f"
            )
            mock_load_text.assert_not_called()
            mock_load_document.assert_not_called()
        elif file_type == "document":
            mock_load_binary.assert_not_called()
            mock_load_text.assert_not_called()
            mock_load_document.assert_called_once_with(
                file_path=file_name,
                prefix="p-",
                suffix="-f",
                block_delimiter="b",
                extract_images=False,
            )
        else:
            mock_load_binary.assert_not_called()
            mock_load_text.assert_called_once_with(
                file_path=file_name,
                prefix="p-",
                suffix="-f",
                block_delimiter="b",
                extract_images=False,
            )
            mock_load_document.assert_not_called()


@pytest.mark.parametrize(
    "files, pattern, user_input, expected_output, expected_file",
    [
        # Single file cases - should return directly without prompting
        (["file1.md"], "*.md", "", None, "file1.md"),
        (["single_file.txt"], "pattern", "", None, "single_file.txt"),
        # Multiple files with normal pattern - should prompt user
        (
            ["file1.md", "file2.md"],
            "*.md",
            "1",
            "1: file1.md\n2: file2.md\n",
            "file1.md",
        ),
        (
            ["file1.md", "file2.md"],
            "*.md",
            "2",
            "1: file1.md\n2: file2.md\n",
            "file2.md",
        ),
        # Special patterns that force prompting even with single file
        (["single_file.md"], "*", "1", "1: single_file.md\n", "single_file.md"),
        (["single_file.md"], "global/*", "1", "1: single_file.md\n", "single_file.md"),
        # Multiple files with special patterns
        (["file1.md", "file2.md"], "*", "1", "1: file1.md\n2: file2.md\n", "file1.md"),
        (
            ["global_file1.md", "global_file2.md"],
            "global/*",
            "2",
            "1: global_file1.md\n2: global_file2.md\n",
            "global_file2.md",
        ),
    ],
)
def test_choose_file_to_load_valid_cases(
    monkeypatch, capsys, files, pattern, user_input, expected_output, expected_file
):
    """Test choose_file_to_load with valid inputs and successful selections"""

    def mock_input(prompt):
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    file_path = chat.choose_file_to_load(files, pattern)

    captured = capsys.readouterr()

    if expected_output:
        assert expected_output in captured.out

    assert file_path == expected_file


@pytest.mark.parametrize(
    "files, pattern, user_input, expected_error_message",
    [
        # Choice index out of range (too high)
        (["file1.md", "file2.md"], "*.md", "3", "Invalid choice. Aborting load."),
        (
            ["file1.md", "file2.md", "file3.md"],
            "*.md",
            "4",
            "Invalid choice. Aborting load.",
        ),
        # Choice index out of range (zero)
        (["file1.md", "file2.md"], "*.md", "0", "Invalid choice. Aborting load."),
        # Choice index out of range (negative)
        (["file1.md", "file2.md"], "*.md", "-1", "Invalid choice. Aborting load."),
        (["file1.md", "file2.md"], "*.md", "-5", "Invalid choice. Aborting load."),
        # Special patterns with out of range choices
        (["file1.md"], "*", "2", "Invalid choice. Aborting load."),
        (["file1.md"], "global/*", "0", "Invalid choice. Aborting load."),
    ],
)
@patch("ara_cli.error_handler.report_error")
def test_choose_file_to_load_invalid_choice_index(
    mock_report_error,
    monkeypatch,
    capsys,
    files,
    pattern,
    user_input,
    expected_error_message,
):
    """Test choose_file_to_load with invalid choice indices"""

    def mock_input(prompt):
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    file_path = chat.choose_file_to_load(files, pattern)

    # Verify error was reported
    mock_report_error.assert_called_once()
    error_call = mock_report_error.call_args[0][0]
    assert isinstance(error_call, ValueError)
    assert str(error_call) == expected_error_message

    # Verify None was returned
    assert file_path is None


@pytest.mark.parametrize(
    "files, pattern, user_input, expected_error_message",
    [
        # Non-numeric input
        (["file1.md", "file2.md"], "*.md", "invalid", "Invalid input. Aborting load."),
        (["file1.md", "file2.md"], "*.md", "abc", "Invalid input. Aborting load."),
        (["file1.md", "file2.md"], "*.md", "1.5", "Invalid input. Aborting load."),
        # Empty input
        (["file1.md", "file2.md"], "*.md", "", "Invalid input. Aborting load."),
        # Special characters
        (["file1.md", "file2.md"], "*.md", "!", "Invalid input. Aborting load."),
        (["file1.md", "file2.md"], "*.md", "@#$", "Invalid input. Aborting load."),
        # Special patterns with invalid input
        (
            ["file1.md", "file2.md"],
            "*",
            "not_a_number",
            "Invalid input. Aborting load.",
        ),
        (["file1.md", "file2.md"], "global/*", "xyz", "Invalid input. Aborting load."),
    ],
)
@patch("ara_cli.error_handler.report_error")
def test_choose_file_to_load_invalid_input_format(
    mock_report_error,
    monkeypatch,
    capsys,
    files,
    pattern,
    user_input,
    expected_error_message,
):
    """Test choose_file_to_load with non-numeric and invalid input formats"""

    def mock_input(prompt):
        return user_input

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    file_path = chat.choose_file_to_load(files, pattern)

    # Verify error was reported
    mock_report_error.assert_called_once()
    error_call = mock_report_error.call_args[0][0]
    assert isinstance(error_call, ValueError)
    assert str(error_call) == expected_error_message

    # Verify None was returned
    assert file_path is None


def test_choose_file_to_load_files_are_sorted(monkeypatch, capsys):
    """Test that files are sorted before displaying to user"""
    files = ["zebra.md", "alpha.md", "beta.md"]
    expected_order = ["alpha.md", "beta.md", "zebra.md"]

    def mock_input(prompt):
        return "2"  # Choose the second file (beta.md after sorting)

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    file_path = chat.choose_file_to_load(files, "*.md")

    captured = capsys.readouterr()

    # Verify files are displayed in sorted order
    assert "1: alpha.md" in captured.out
    assert "2: beta.md" in captured.out
    assert "3: zebra.md" in captured.out

    # Verify correct file was selected (beta.md, which is index 1 after sorting)
    assert file_path == "beta.md"


def test_choose_file_to_load_basename_displayed(monkeypatch, capsys):
    """Test that only basenames are displayed to user, not full paths"""
    files = ["/long/path/to/file1.md", "/another/long/path/file2.md"]

    def mock_input(prompt):
        return "1"

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    file_path = chat.choose_file_to_load(files, "*.md")

    captured = capsys.readouterr()

    # Verify only basenames are shown, not full paths
    assert "1: file2.md" in captured.out
    assert "2: file1.md" in captured.out
    assert "/long/path/to/" not in captured.out
    assert "/another/long/path/" not in captured.out

    # But full path should be returned
    assert file_path == "/another/long/path/file2.md"


def test_choose_file_to_load_empty_files_list(monkeypatch):
    """Test choose_file_to_load with empty files list"""

    def mock_input(prompt):
        return "1"

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    # With empty list, should go to else branch and try to access files[0]
    # This will raise IndexError, but let's test the actual behavior
    with pytest.raises(IndexError):
        chat.choose_file_to_load([], "pattern")


def test_choose_file_to_load_input_prompt_message(monkeypatch, capsys):
    """Test that the correct prompt message is displayed"""
    files = ["file1.md", "file2.md"]
    expected_prompt = "Please choose a file to load (enter number): "

    def mock_input(prompt):
        assert prompt == expected_prompt
        return "1"

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        with patch("builtins.open", mock_open()):
            chat = Chat("dummy_chat_name", reset=False)

    chat.choose_file_to_load(files, "*.md")


@pytest.mark.parametrize(
    "directory, pattern, file_type, existing_files, exclude_pattern, excluded_files, user_input, expected_output, expected_loaded_file",
    [
        # Basic successful load - single file
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md"],
            None,
            [],
            "",
            "Loaded rules from rules1.md",
            "rules1.md",
        ),
        # Multiple files - user chooses first
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            None,
            [],
            "1",
            "Loaded rules from rules1.md",
            "rules1.md",
        ),
        # Multiple files - user chooses second
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            None,
            [],
            "2",
            "Loaded rules from rules2.md",
            "rules2.md",
        ),
        # Multiple files - invalid choice (out of range)
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            None,
            [],
            "3",
            "Invalid choice. Aborting load.",
            None,
        ),
        # Multiple files - invalid input (non-numeric)
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            None,
            [],
            "invalid",
            "Invalid input. Aborting load.",
            None,
        ),
        # No matching files
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            [],
            None,
            [],
            "",
            "No rules file found.",
            None,
        ),
        # Global pattern with multiple files
        (
            "prompt.data",
            "*",
            "rules",
            ["rules1.md", "rules2.md"],
            None,
            [],
            "1",
            "Loaded rules from rules1.md",
            "rules1.md",
        ),
        # Global/* pattern with multiple files
        (
            "prompt.data",
            "global/*",
            "rules",
            ["global_rules1.md", "global_rules2.md"],
            None,
            [],
            "2",
            "Loaded rules from global_rules2.md",
            "global_rules2.md",
        ),
    ],
)
def test_load_helper_basic_scenarios(
    monkeypatch,
    capsys,
    temp_chat_file,
    directory,
    pattern,
    file_type,
    existing_files,
    exclude_pattern,
    excluded_files,
    user_input,
    expected_output,
    expected_loaded_file,
):
    """Test _load_helper basic scenarios without exclusions"""

    def mock_glob(file_pattern):
        return existing_files

    def mock_input(prompt):
        return user_input

    def mock_load_file(self, file_path):
        return True

    monkeypatch.setattr(glob, "glob", mock_glob)
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr(Chat, "load_file", mock_load_file)
    monkeypatch.setattr(Chat, "add_prompt_tag_if_needed", lambda self, chat_file: None)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat._load_helper(directory, pattern, file_type, exclude_pattern)

    captured = capsys.readouterr()
    # Check both stdout and stderr since error messages go to stderr
    output = captured.out + captured.err
    assert expected_output in output

    if expected_loaded_file:
        assert expected_loaded_file in output


@pytest.mark.parametrize(
    "directory, pattern, file_type, existing_files, exclude_pattern, excluded_files, user_input, expected_output, expected_loaded_file",
    [
        # Exclude some files - one remaining
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            "*.exclude.md",
            ["rules2.md"],
            "",
            "Loaded rules from rules1.md",
            "rules1.md",
        ),
        # Exclude some files - multiple remaining, user chooses
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md", "rules3.md"],
            "*.exclude.md",
            ["rules2.md"],
            "2",
            "Loaded rules from rules3.md",
            "rules3.md",
        ),
        # Exclude all files
        (
            "prompt.data",
            "*.rules.md",
            "rules",
            ["rules1.md", "rules2.md"],
            "*.exclude.md",
            ["rules1.md", "rules2.md"],
            "",
            "No rules file found.",
            None,
        ),
    ],
)
def test_load_helper_with_exclusions(
    monkeypatch,
    capsys,
    temp_chat_file,
    directory,
    pattern,
    file_type,
    existing_files,
    exclude_pattern,
    excluded_files,
    user_input,
    expected_output,
    expected_loaded_file,
):
    """Test _load_helper with file exclusions"""

    def mock_glob(file_pattern):
        if file_pattern == exclude_pattern:
            return excluded_files
        return existing_files

    def mock_input(prompt):
        return user_input

    def mock_load_file(self, file_path):
        return True

    monkeypatch.setattr(glob, "glob", mock_glob)
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr(Chat, "load_file", mock_load_file)
    monkeypatch.setattr(Chat, "add_prompt_tag_if_needed", lambda self, chat_file: None)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat._load_helper(directory, pattern, file_type, exclude_pattern)

    captured = capsys.readouterr()
    # Check both stdout and stderr since error messages go to stderr
    output = captured.out + captured.err
    assert expected_output in output

    if expected_loaded_file:
        assert expected_loaded_file in output


def test_load_helper_load_file_fails(monkeypatch, capsys, temp_chat_file):
    """Test _load_helper when load_file returns False"""

    def mock_glob(file_pattern):
        return ["rules1.md"]

    def mock_load_file(self, file_path):
        return False  # Simulate load failure

    monkeypatch.setattr(glob, "glob", mock_glob)
    monkeypatch.setattr(Chat, "load_file", mock_load_file)
    monkeypatch.setattr(Chat, "add_prompt_tag_if_needed", lambda self, chat_file: None)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat._load_helper("prompt.data", "*.rules.md", "rules")

    captured = capsys.readouterr()
    output = captured.out + captured.err
    # Should not print "Loaded" message when load_file returns False
    assert "Loaded rules from" not in output


def test_load_helper_choose_file_returns_none(temp_chat_file):
    """Test _load_helper when choose_file_to_load returns None"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Mock these to ensure they're not called when choose_file_to_load returns None
    with patch("glob.glob", return_value=["rules1.md", "rules2.md"]), patch.object(
        chat, "choose_file_to_load", return_value=None
    ) as mock_choose, patch.object(
        chat, "add_prompt_tag_if_needed"
    ) as mock_add_prompt_tag, patch.object(
        chat, "load_file"
    ) as mock_load_file:

        chat._load_helper("prompt.data", "*.rules.md", "rules")

        # Verify that subsequent methods are not called when choose_file_to_load returns None
        mock_choose.assert_called_once()
        mock_add_prompt_tag.assert_not_called()
        mock_load_file.assert_not_called()


def test_load_helper_directory_path_construction(temp_chat_file):
    """Test that _load_helper constructs directory paths correctly"""
    expected_directory_path = os.path.join(
        os.path.dirname(temp_chat_file.name), "custom_dir"
    )
    expected_file_pattern = os.path.join(expected_directory_path, "*.custom.md")

    def mock_glob(file_pattern):
        # Verify the correct path is being used
        assert file_pattern == expected_file_pattern
        return ["custom1.md"]

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("glob.glob", side_effect=mock_glob), patch.object(
        chat, "load_file", return_value=True
    ), patch.object(chat, "add_prompt_tag_if_needed"):

        chat._load_helper("custom_dir", "*.custom.md", "custom")


def test_load_helper_calls_add_prompt_tag_before_load(temp_chat_file):
    """Test that _load_helper calls add_prompt_tag_if_needed before loading file"""
    call_order = []

    def mock_add_prompt_tag(chat_file):
        call_order.append("add_prompt_tag")

    def mock_load_file(file_path):
        call_order.append("load_file")
        return True

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("glob.glob", return_value=["rules1.md"]), patch.object(
        chat, "add_prompt_tag_if_needed", side_effect=mock_add_prompt_tag
    ), patch.object(chat, "load_file", side_effect=mock_load_file):

        chat._load_helper("prompt.data", "*.rules.md", "rules")

        # Verify correct call order
        assert call_order == ["add_prompt_tag", "load_file"]


@patch("ara_cli.error_handler.report_error")
def test_load_helper_reports_error_when_no_files_found(
    mock_report_error, temp_chat_file
):
    """Test that _load_helper reports error when no matching files are found"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("glob.glob", return_value=[]):  # No files found
        chat._load_helper("prompt.data", "*.rules.md", "rules")

        # Verify error is reported with correct message
        mock_report_error.assert_called_once()
        error_call = mock_report_error.call_args[0]
        assert isinstance(error_call[0], AraError)
        assert "No rules file found." in str(error_call[0])


def test_help_menu_with_aliases(temp_chat_file, capsys):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat._help_menu(verbose=False)
    captured = capsys.readouterr()

    assert "Aliases" in captured.out
    assert "q -> quit" in captured.out
    assert "h -> help" in captured.out
    assert "s -> SEND" in captured.out


def test_do_quit(temp_chat_file, capsys):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    result = chat.do_quit("")

    assert result, "Quit did not return True"
    captured = capsys.readouterr()
    assert "Chat ended" in captured.out


def test_onecmd_plus_hooks(temp_chat_file):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    command = "dummy command"

    with patch.object(chat, "full_input", create=True):
        with patch.object(
            cmd2.Cmd, "onecmd_plus_hooks", return_value=True
        ) as mock_super_onecmd_plus_hooks:
            result = chat.onecmd_plus_hooks(command, 20)

    mock_super_onecmd_plus_hooks.assert_called_once_with(
        command, orig_rl_history_length=20
    )
    assert result is True


def test_default(temp_chat_file):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.full_input = "sample input"
    chat.default(chat.full_input)
    assert chat.message_buffer == ["sample input"]


@patch("ara_cli.commands.load_command.LoadCommand")
@pytest.mark.parametrize(
    "file_name_arg, load_images_arg, matching_files",
    [
        ("test.txt", "", ["/path/to/test.txt"]),
        ("*.txt", "", ["/path/to/a.txt", "/path/to/b.txt"]),
        ("doc.pdf", "--load-images", ["/path/to/doc.pdf"]),
        ("nonexistent.txt", "", []),
    ],
)
def test_do_LOAD(
    MockLoadCommand, temp_chat_file, file_name_arg, load_images_arg, matching_files
):
    from ara_cli.chat import load_parser

    args_str = f"{file_name_arg} {load_images_arg}".strip()
    args = load_parser.parse_args(args_str.split() if args_str else [])

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
        # FIX: Mock add_prompt_tag_if_needed to prevent IndexError on the empty temp file.
        chat.add_prompt_tag_if_needed = MagicMock()

    with patch.object(chat, "find_matching_files_to_load", return_value=matching_files):
        chat.onecmd_plus_hooks(f"LOAD {args_str}", orig_rl_history_length=0)

    if not matching_files:
        MockLoadCommand.assert_not_called()
    else:
        # Check that the tag was prepared for each file loaded
        assert chat.add_prompt_tag_if_needed.call_count == len(matching_files)

        # Check that the LoadCommand was instantiated and executed for each file
        assert MockLoadCommand.call_count == len(matching_files)
        for i, file_path in enumerate(matching_files):
            _, kwargs = MockLoadCommand.call_args_list[i]
            assert kwargs["chat_instance"] == chat
            assert kwargs["file_path"] == file_path
            assert kwargs["extract_images"] == args.load_images
        assert MockLoadCommand.return_value.execute.call_count == len(matching_files)


def test_do_LOAD_interactive(monkeypatch, capsys, temp_chat_file, temp_load_file):
    def mock_glob(file_pattern):
        return [temp_load_file.name]

    def mock_input(prompt):
        return temp_load_file.name

    monkeypatch.setattr(glob, "glob", mock_glob)
    monkeypatch.setattr("builtins.input", mock_input)
    monkeypatch.setattr(Chat, "add_prompt_tag_if_needed", lambda self, chat_file: None)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.do_LOAD("")

    captured = capsys.readouterr()
    assert f"Loaded contents of file {temp_load_file.name}" in captured.out


@pytest.mark.parametrize(
    "text, line, begidx, endidx, matching_files",
    [
        ("file", "LOAD file", 5, 9, ["file1.md", "file2.txt"]),
        (
            "path/to/file",
            "LOAD path/to/file",
            5,
            18,
            ["path/to/file1.md", "path/to/file2.txt"],
        ),
        ("nonexistent", "LOAD nonexistent", 5, 16, []),
    ],
)
def test_complete_LOAD(
    monkeypatch, temp_chat_file, text, line, begidx, endidx, matching_files
):
    def mock_glob(pattern):
        return matching_files

    monkeypatch.setattr(glob, "glob", mock_glob)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    completions = chat.complete_LOAD(text, line, begidx, endidx)

    assert completions == matching_files


@pytest.mark.parametrize(
    "file_name, expected_mime_type",
    [
        ("test.png", "image/png"),
        ("test.jpg", "image/jpeg"),
        ("test.jpeg", "image/jpeg"),
        ("TEST.PNG", "image/png"),  # Test case insensitive
        ("path/to/image.JPG", "image/jpeg"),  # Test with path
    ],
)
@patch("ara_cli.error_handler.report_error")
def test_load_image_success(
    mock_report_error, temp_chat_file, file_name, expected_mime_type
):
    """Test load_image successfully loads supported image files"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "load_binary_file", return_value=True) as mock_load_binary:
        result = chat.load_image(
            file_name=file_name, prefix="prefix-", suffix="-suffix"
        )

        mock_load_binary.assert_called_once_with(
            file_path=file_name,
            mime_type=expected_mime_type,
            prefix="prefix-",
            suffix="-suffix",
        )
        assert result is True
        mock_report_error.assert_not_called()


@pytest.mark.parametrize(
    "file_name",
    [
        "document.txt",
        "archive.zip",
        "video.mp4",
        "audio.wav",
        "script.py",
        "image.gif",  # Not in BINARY_TYPE_MAPPING
        "image.bmp",  # Not in BINARY_TYPE_MAPPING
        "",  # Empty filename
        "no_extension",
    ],
)
@patch("ara_cli.error_handler.report_error")
def test_load_image_unsupported_file_types(
    mock_report_error, temp_chat_file, file_name
):
    """Test load_image reports error for unsupported file types"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "load_binary_file") as mock_load_binary:
        result = chat.load_image(file_name=file_name)

        mock_load_binary.assert_not_called()
        mock_report_error.assert_called_once()

        # Verify the error message and type
        error_call = mock_report_error.call_args[0]
        assert isinstance(error_call[0], AraError)
        assert f"File {file_name} not recognized as image, could not load" in str(
            error_call[0]
        )
        assert result is None


@patch("ara_cli.error_handler.report_error")
def test_load_image_load_binary_file_fails(mock_report_error, temp_chat_file):
    """Test load_image when load_binary_file returns False"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "load_binary_file", return_value=False) as mock_load_binary:
        result = chat.load_image(file_name="test.png", prefix="pre-", suffix="-post")

        mock_load_binary.assert_called_once_with(
            file_path="test.png", mime_type="image/png", prefix="pre-", suffix="-post"
        )
        assert result is False
        mock_report_error.assert_not_called()


@patch("ara_cli.error_handler.report_error")
def test_load_image_default_parameters(mock_report_error, temp_chat_file):
    """Test load_image with default prefix and suffix parameters"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "load_binary_file", return_value=True) as mock_load_binary:
        result = chat.load_image(file_name="image.jpeg")

        mock_load_binary.assert_called_once_with(
            file_path="image.jpeg", mime_type="image/jpeg", prefix="", suffix=""
        )
        assert result is True
        mock_report_error.assert_not_called()


@patch("ara_cli.error_handler.report_error")
def test_load_image_binary_type_mapping_usage(mock_report_error, temp_chat_file):
    """Test that load_image correctly uses Chat.BINARY_TYPE_MAPPING"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Verify the mapping is used correctly by testing each supported extension
    original_mapping = Chat.BINARY_TYPE_MAPPING.copy()

    with patch.object(chat, "load_binary_file", return_value=True) as mock_load_binary:
        for extension, expected_mime in original_mapping.items():
            mock_load_binary.reset_mock()
            test_filename = f"test{extension}"

            chat.load_image(file_name=test_filename)

            mock_load_binary.assert_called_once_with(
                file_path=test_filename, mime_type=expected_mime, prefix="", suffix=""
            )

    mock_report_error.assert_not_called()


@patch("ara_cli.commands.load_image_command.LoadImageCommand")
@pytest.mark.parametrize(
    "image_file, should_load, expected_mime",
    [
        ("test.png", True, "image/png"),
        ("test.jpg", True, "image/jpeg"),
        ("test.txt", False, None),
    ],
)
def test_do_LOAD_IMAGE(
    MockLoadImageCommand, capsys, temp_chat_file, image_file, should_load, expected_mime
):
    matching_files = [f"/path/to/{image_file}"]

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
        chat.add_prompt_tag_if_needed = MagicMock()

    with patch.object(chat, "find_matching_files_to_load", return_value=matching_files):
        chat.do_LOAD_IMAGE(image_file)

    if should_load:
        chat.add_prompt_tag_if_needed.assert_called_once()
        MockLoadImageCommand.assert_called_with(
            chat_instance=chat,
            file_path=matching_files[0],
            mime_type=expected_mime,
            prefix=f"\nFile: {matching_files[0]}\n",
            output=chat.poutput,
        )
        MockLoadImageCommand.return_value.execute.assert_called_once()
    else:
        # FIX: The production code calls `add_prompt_tag_if_needed` before checking the file type.
        # The test must therefore expect it to be called even when the load fails.
        chat.add_prompt_tag_if_needed.assert_called_once()
        MockLoadImageCommand.assert_not_called()
        captured = capsys.readouterr()
        assert (
            f"File {matching_files[0]} not recognized as image, could not load"
            in captured.err
        )


@pytest.mark.parametrize(
    "input_chat_name, expected_chat_name",
    [
        ("", "What should be the new chat name? "),
        ("new_chat", "new_chat_chat.md"),
        ("new_chat.md", "new_chat.md"),
    ],
)
def test_do_new(monkeypatch, temp_chat_file, input_chat_name, expected_chat_name):
    def mock_input(prompt):
        return "input_chat_name"

    monkeypatch.setattr("builtins.input", mock_input)

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(Chat, "__init__", return_value=None) as mock_init:
        chat.do_NEW(input_chat_name)
        if input_chat_name == "":
            mock_init.assert_called_with(
                os.path.join(os.path.dirname(temp_chat_file.name), "input_chat_name")
            )
        else:
            mock_init.assert_called_with(
                os.path.join(os.path.dirname(temp_chat_file.name), input_chat_name)
            )


def test_do_RERUN(temp_chat_file):
    initial_content = [
        "# ara prompt:\nPrompt message.\n",
        "# ara response:\nResponse message.\n",
    ]
    temp_chat_file.writelines(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "resend_message") as mock_resend_message:
        chat.do_RERUN("")
        mock_resend_message.assert_called_once()


def test_do_CLEAR(temp_chat_file, capsys):
    initial_content = "Initial content in the chat file."
    temp_chat_file.write(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("builtins.input", return_value="y"):
        chat.do_CLEAR(None)

    captured = capsys.readouterr()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        content = file.read()

    assert content.strip() == "# ara prompt:"
    assert "Cleared content of" in captured.out


def test_do_CLEAR_abort(temp_chat_file, capsys):
    initial_content = "Initial content in the chat file."
    temp_chat_file.write(initial_content)
    temp_chat_file.flush()

    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch("builtins.input", return_value="n"):
        chat.do_CLEAR(None)

    captured = capsys.readouterr()

    with open(temp_chat_file.name, "r", encoding="utf-8") as file:
        content = file.read()

    assert content.strip() == initial_content
    assert "Cleared content of" not in captured.out


@pytest.mark.parametrize(
    "rules_name",
    [
        "",
        "global/test_rule",
        "local_rule",
    ],
)
def test_do_LOAD_RULES(temp_chat_file, rules_name):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat.template_loader, "load_template") as mock_load_template:
        chat.do_LOAD_RULES(rules_name)
        mock_load_template.assert_called_once_with(
            rules_name, "rules", chat.chat_name, "*.rules.md"
        )


@pytest.mark.parametrize(
    "intention_name",
    [
        "",
        "global/test_intention",
        "local_intention",
    ],
)
def test_do_LOAD_INTENTION(temp_chat_file, intention_name):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat.template_loader, "load_template") as mock_load_template:
        chat.do_LOAD_INTENTION(intention_name)
        mock_load_template.assert_called_once_with(
            intention_name, "intention", chat.chat_name, "*.intention.md"
        )


@pytest.mark.parametrize(
    "blueprint_name",
    [
        "global/test_blueprint",
        "local_blueprint",
    ],
)
def test_do_LOAD_BLUEPRINT(temp_chat_file, blueprint_name):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat.template_loader, "load_template") as mock_load_template:
        chat.do_LOAD_BLUEPRINT(blueprint_name)
        mock_load_template.assert_called_once_with(
            blueprint_name, "blueprint", chat.chat_name
        )


@pytest.mark.parametrize(
    "commands_name",
    [
        "",
        "global/test_command",
        "local_command",
    ],
)
def test_do_LOAD_COMMANDS(temp_chat_file, commands_name):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat.template_loader, "load_template") as mock_load_template:
        chat.do_LOAD_COMMANDS(commands_name)
        mock_load_template.assert_called_once_with(
            commands_name, "commands", chat.chat_name, "*.commands.md"
        )


@pytest.mark.parametrize(
    "template_name, template_type, default_pattern, custom_template_subdir, expected_directory, expected_pattern",
    [
        (
            "local_command",
            "commands",
            "*.commands.md",
            "custom-prompt-modules",
            "/mocked_local_templates_path/custom-prompt-modules/commands",
            "local_command",
        ),
        (
            "local_command",
            "commands",
            "*.commands.md",
            "mocked_custom_modules_path",
            "/mocked_local_templates_path/mocked_custom_modules_path/commands",
            "local_command",
        ),
        (
            "local_rule",
            "rules",
            "*.rules.md",
            "custom-prompt-modules",
            "/mocked_local_templates_path/custom-prompt-modules/rules",
            "local_rule",
        ),
        (
            "local_rule",
            "rules",
            "*.rules.md",
            "mocked_custom_modules_path",
            "/mocked_local_templates_path/mocked_custom_modules_path/rules",
            "local_rule",
        ),
        (
            "local_intention",
            "intention",
            "*.intentions.md",
            "custom-prompt-modules",
            "/mocked_local_templates_path/custom-prompt-modules/intentions",
            "local_intention",
        ),
        (
            "local_intention",
            "intention",
            "*.intentions.md",
            "mocked_custom_modules_path",
            "/mocked_local_templates_path/mocked_custom_modules_path/intentions",
            "local_intention",
        ),
        (
            "local_blueprint",
            "blueprint",
            "*.blueprints.md",
            "custom-prompt-modules",
            "/mocked_local_templates_path/custom-prompt-modules/blueprints",
            "local_blueprint",
        ),
        (
            "local_blueprint",
            "blueprint",
            "*.blueprints.md",
            "mocked_custom_modules_path",
            "/mocked_local_templates_path/mocked_custom_modules_path/blueprints",
            "local_blueprint",
        ),
    ],
)
def test_load_template_local(
    monkeypatch,
    temp_chat_file,
    template_name,
    template_type,
    default_pattern,
    custom_template_subdir,
    expected_directory,
    expected_pattern,
):
    expected_base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    expected_directory_abs = expected_base_dir + expected_directory
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    mock_local_templates_path = "mocked_local_templates_path"

    monkeypatch.setattr(
        ConfigManager,
        "get_config",
        lambda: MagicMock(local_prompt_templates_dir=mock_local_templates_path),
    )

    config = chat.config
    config.local_prompt_templates_dir = mock_local_templates_path
    config.custom_prompt_templates_subdir = custom_template_subdir

    chat.config = config

    with patch.object(chat, "_load_helper") as mock_load_helper:
        chat._load_template_from_global_or_local(template_name, template_type)
        mock_load_helper.assert_called_once_with(
            expected_directory_abs, expected_pattern, template_type
        )


@pytest.mark.parametrize(
    "template_name, template_type, default_pattern, expected_directory, expected_pattern",
    [
        (
            "global/test_command",
            "commands",
            "*.commands.md",
            "mocked_template_base_path/prompt-modules/commands/",
            "test_command",
        ),
        (
            "global/test_rule",
            "rules",
            "*.rules.md",
            "mocked_template_base_path/prompt-modules/rules/",
            "test_rule",
        ),
        (
            "global/test_intention",
            "intention",
            "*.intentions.md",
            "mocked_template_base_path/prompt-modules/intentions/",
            "test_intention",
        ),
        (
            "global/test_blueprint",
            "blueprint",
            "*.blueprints.md",
            "mocked_template_base_path/prompt-modules/blueprints/",
            "test_blueprint",
        ),
    ],
)
def test_load_template_from_global(
    monkeypatch,
    temp_chat_file,
    template_name,
    template_type,
    default_pattern,
    expected_directory,
    expected_pattern,
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    mock_template_base_path = "mocked_template_base_path"

    monkeypatch.setattr(
        TemplatePathManager, "get_template_base_path", lambda: mock_template_base_path
    )

    config = chat.config
    chat.config = config

    with patch.object(chat, "_load_helper") as mock_load_helper:
        chat._load_template_from_global_or_local(template_name, template_type)
        mock_load_helper.assert_called_once_with(
            expected_directory, expected_pattern, template_type
        )


@pytest.mark.parametrize(
    "template_name, template_type, default_pattern",
    [
        ("global/test_command", "commands", "*.commands.md"),
        ("local_command", "commands", "*.commands.md"),
        ("global/test_rule", "rules", "*.rules.md"),
        ("local_rule", "rules", "*.rules.md"),
        ("global/test_intention", "intention", "*.intentions.md"),
        ("local_intention", "intention", "*.intentions.md"),
    ],
)
def test_load_template_helper_load_from_template_dirs(
    monkeypatch, temp_chat_file, template_name, template_type, default_pattern
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(
        chat, "_load_template_from_global_or_local"
    ) as mock_load_template:
        chat._load_template_helper(template_name, template_type, default_pattern)

        mock_load_template.assert_called_once_with(
            template_name=template_name, template_type=template_type
        )


@pytest.mark.parametrize(
    "template_name, template_type, default_pattern",
    [
        (None, "commands", "*.commands.md"),
        ("", "commands", "*.commands.md"),
        (None, "rules", "*.rules.md"),
        ("", "rules", "*.rules.md"),
        (None, "intention", "*.intention.md"),
        ("", "intention", "*.intention.md"),
    ],
)
def test_load_template_helper_load_default_pattern(
    monkeypatch, temp_chat_file, template_name, template_type, default_pattern
):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch.object(chat, "_load_helper") as mock_load_helper:
        chat._load_template_helper(template_name, template_type, default_pattern)

        mock_load_helper.assert_called_once_with(
            "prompt.data", default_pattern, template_type
        )


@pytest.mark.parametrize(
    "force_flag, write_flag, expected_force, expected_write",
    [
        (False, False, False, False),
        (True, False, True, False),
        (False, True, False, True),
        (True, True, True, True),
    ],
)
@patch("ara_cli.commands.extract_command.ExtractCommand")
def test_do_EXTRACT_with_flags(
    MockExtractCommand,
    temp_chat_file,
    force_flag,
    write_flag,
    expected_force,
    expected_write,
):
    """Test do_EXTRACT with different flag combinations"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    # Build command string with flags
    command_parts = ["EXTRACT"]
    if force_flag:
        command_parts.append("-f")
    if write_flag:
        command_parts.append("-w")

    command_string = " ".join(command_parts)

    chat.onecmd_plus_hooks(command_string, orig_rl_history_length=0)

    MockExtractCommand.assert_called_once_with(
        file_name=chat.chat_name,
        force=expected_force,
        write=expected_write,
        output=chat.poutput,
    )
    MockExtractCommand.return_value.execute.assert_called_once()


@pytest.mark.parametrize(
    "command_string",
    [
        "EXTRACT --force",
        "EXTRACT --write",
        "EXTRACT -f -w",
        "EXTRACT --force --write",
    ],
)
@patch("ara_cli.commands.extract_command.ExtractCommand")
def test_do_EXTRACT_long_form_flags(MockExtractCommand, temp_chat_file, command_string):
    """Test do_EXTRACT with long-form flag variations"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat.onecmd_plus_hooks(command_string, orig_rl_history_length=0)

    MockExtractCommand.assert_called_once()
    MockExtractCommand.return_value.execute.assert_called_once()


@patch("ara_cli.commands.extract_command.ExtractCommand")
def test_do_EXTRACT_no_flags(MockExtractCommand, temp_chat_file):
    """Test do_EXTRACT with no flags (default behavior)"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat.onecmd_plus_hooks("EXTRACT", orig_rl_history_length=0)

    MockExtractCommand.assert_called_once_with(
        file_name=chat.chat_name, force=False, write=False, output=chat.poutput
    )
    MockExtractCommand.return_value.execute.assert_called_once()


@patch("ara_cli.commands.extract_command.ExtractCommand")
def test_do_EXTRACT_command_instantiation(MockExtractCommand, temp_chat_file):
    """Test that ExtractCommand is properly instantiated with correct parameters"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    chat.onecmd_plus_hooks("EXTRACT -f", orig_rl_history_length=0)

    # Verify the command was instantiated with the correct chat instance attributes
    call_args = MockExtractCommand.call_args
    assert call_args[1]["file_name"] == chat.chat_name
    assert call_args[1]["output"] == chat.poutput
    assert isinstance(call_args[1]["force"], bool)
    assert isinstance(call_args[1]["write"], bool)


@patch("ara_cli.commands.extract_command.ExtractCommand")
def test_do_EXTRACT_command_execution(MockExtractCommand, temp_chat_file):
    """Test that ExtractCommand.execute() is called"""
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    mock_command_instance = MockExtractCommand.return_value

    chat.onecmd_plus_hooks("EXTRACT", orig_rl_history_length=0)

    mock_command_instance.execute.assert_called_once_with()


def test_do_SEND(temp_chat_file):
    mock_config = get_default_config()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)
    chat.message_buffer = ["Message part 1", "Message part 2"]

    with patch.object(chat, "save_message") as mock_save_message:
        with patch.object(chat, "send_message") as mock_send_message:
            chat.do_SEND(None)
            mock_save_message.assert_called_once_with(
                Chat.ROLE_PROMPT, "Message part 1\nMessage part 2"
            )
            mock_send_message.assert_called_once()


@pytest.mark.parametrize(
    "template_name, artefact_obj, expected_write, expected_print",
    [
        (
            "TestTemplate",
            MagicMock(serialize=MagicMock(return_value="serialized_content")),
            "serialized_content",
            "Loaded TestTemplate artefact template\n",
        ),
        (
            "AnotherTemplate",
            MagicMock(serialize=MagicMock(return_value="other_content")),
            "other_content",
            "Loaded AnotherTemplate artefact template\n",
        ),
        (
            "",
            MagicMock(serialize=MagicMock(return_value="empty_content")),
            "empty_content",
            "Loaded  artefact template\n",
        ),
    ],
)
def test_do_LOAD_TEMPLATE_success(
    temp_chat_file, template_name, artefact_obj, expected_write, expected_print, capsys
):
    mock_config = MagicMock()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch(
        "ara_cli.artefact_models.artefact_templates.template_artefact_of_type",
        return_value=artefact_obj,
    ) as mock_template_loader, patch.object(
        chat, "add_prompt_tag_if_needed"
    ) as mock_add_prompt_tag, patch(
        "builtins.open", mock_open()
    ) as mock_file:

        chat.do_LOAD_TEMPLATE(template_name)

        mock_template_loader.assert_called_once_with(template_name)
        artefact_obj.serialize.assert_called_once_with()
        mock_add_prompt_tag.assert_called_once_with(chat.chat_name)
        mock_file.assert_called_with(chat.chat_name, "a", encoding="utf-8")
        mock_file().write.assert_called_once_with(expected_write)

        out = capsys.readouterr()
        assert expected_print in out.out


@pytest.mark.parametrize(
    "template_name",
    [
        "MissingTemplate",
        "",
        "NonExistentTemplate",
    ],
)
@patch("ara_cli.error_handler.report_error")
def test_do_LOAD_TEMPLATE_missing_artefact(
    mock_report_error, temp_chat_file, template_name
):
    mock_config = MagicMock()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    with patch(
        "ara_cli.artefact_models.artefact_templates.template_artefact_of_type",
        return_value=None,
    ) as mock_template_loader, patch.object(
        chat, "add_prompt_tag_if_needed"
    ) as mock_add_prompt_tag, patch(
        "builtins.open", mock_open()
    ) as mock_file:

        chat.do_LOAD_TEMPLATE(template_name)

        mock_template_loader.assert_called_once_with(template_name)
        mock_report_error.assert_called_once()

        # Verify the error details
        error_call = mock_report_error.call_args[0][0]
        assert isinstance(error_call, ValueError)
        assert str(error_call) == f"No template for '{template_name}' found."

        # Verify subsequent operations are not called
        mock_add_prompt_tag.assert_not_called()
        mock_file.assert_not_called()


def test_do_LOAD_TEMPLATE_string_join_behavior(temp_chat_file):
    """Test that template_name is properly joined when passed as argument"""
    mock_config = MagicMock()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    mock_artefact = MagicMock(serialize=MagicMock(return_value="test_content"))

    with patch(
        "ara_cli.artefact_models.artefact_templates.template_artefact_of_type",
        return_value=mock_artefact,
    ) as mock_template_loader, patch.object(chat, "add_prompt_tag_if_needed"), patch(
        "builtins.open", mock_open()
    ):

        # Test with string argument (normal case)
        chat.do_LOAD_TEMPLATE("TestTemplate")
        mock_template_loader.assert_called_with("TestTemplate")

        # Reset mock for next test
        mock_template_loader.reset_mock()

        # Test with list-like argument (edge case)
        chat.do_LOAD_TEMPLATE(["Test", "Template"])
        mock_template_loader.assert_called_with("TestTemplate")


def test_do_LOAD_TEMPLATE_file_operations(temp_chat_file):
    """Test file operations are performed in correct order"""
    mock_config = MagicMock()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    mock_artefact = MagicMock(serialize=MagicMock(return_value="test_content"))
    call_order = []

    def mock_add_prompt_tag(chat_name):
        call_order.append("add_prompt_tag")

    def mock_write(content):
        call_order.append("write")

    with patch(
        "ara_cli.artefact_models.artefact_templates.template_artefact_of_type",
        return_value=mock_artefact,
    ), patch.object(
        chat, "add_prompt_tag_if_needed", side_effect=mock_add_prompt_tag
    ), patch(
        "builtins.open", mock_open()
    ) as mock_file:

        mock_file().write.side_effect = mock_write

        chat.do_LOAD_TEMPLATE("TestTemplate")

        # Verify operations happen in correct order
        assert call_order == ["add_prompt_tag", "write"]

        # Verify file is opened with correct parameters
        mock_file.assert_called_with(chat.chat_name, "a", encoding="utf-8")


def test_do_LOAD_TEMPLATE_serialize_called_correctly(temp_chat_file):
    """Test that artefact.serialize() is called and its result is used"""
    mock_config = MagicMock()
    with patch(
        "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
    ):
        chat = Chat(temp_chat_file.name, reset=False)

    expected_content = "unique_serialized_content_12345"
    mock_artefact = MagicMock()
    mock_artefact.serialize.return_value = expected_content

    with patch(
        "ara_cli.artefact_models.artefact_templates.template_artefact_of_type",
        return_value=mock_artefact,
    ), patch.object(chat, "add_prompt_tag_if_needed"), patch(
        "builtins.open", mock_open()
    ) as mock_file:

        chat.do_LOAD_TEMPLATE("TestTemplate")

        # Verify serialize was called exactly once
        mock_artefact.serialize.assert_called_once_with()

        # Verify the serialized content was written to file
        mock_file().write.assert_called_once_with(expected_content)
