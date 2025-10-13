#!/usr/bin/env python3
"""Command-line interface for Penguin Tamer."""
import sys
from pathlib import Path

# Добавляем parent (src) в sys.path для локального запуска
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Сначала импортируем настройки
from penguin_tamer.config_manager import config
from penguin_tamer.utils.lazy_import import lazy_import

# Ленивый импорт i18n с инициализацией
_i18n_initialized = False


def _ensure_i18n():
    global _i18n_initialized, t, translator
    if not _i18n_initialized:
        from penguin_tamer.i18n import t, translator
        # Initialize translator language from config (default 'en')
        try:
            translator.set_language(getattr(config, 'language', 'en'))
        except Exception:
            pass
        _i18n_initialized = True


def t_lazy(text, **kwargs):
    """Ленивая загрузка переводчика"""
    _ensure_i18n()
    return t(text, **kwargs)


# Используем t_lazy вместо t для отложенной инициализации
t = t_lazy


# === Ленивые импорты через декоратор ===

@lazy_import
def get_theme():
    """Ленивый импорт get_theme"""
    from penguin_tamer.themes import get_theme
    return get_theme


@lazy_import
def get_console_class():
    """Ленивый импорт Console"""
    from rich.console import Console
    return Console


@lazy_import
def get_markdown_class():
    """Ленивый импорт Markdown"""
    from rich.markdown import Markdown
    return Markdown


@lazy_import
def get_script_executor():
    """Ленивый импорт command_executor"""
    from penguin_tamer.command_executor import run_code_block
    return run_code_block


@lazy_import
def get_execute_handler():
    """Ленивый импорт execute_and_handle_result для выполнения команд"""
    from penguin_tamer.command_executor import execute_and_handle_result
    return execute_and_handle_result


@lazy_import
def get_formatter_text():
    """Ленивый импорт text_utils"""
    from penguin_tamer.text_utils import extract_labeled_code_blocks
    return extract_labeled_code_blocks


# Импортируем только самое необходимое для быстрого старта
from penguin_tamer.llm_client import OpenRouterClient, LLMConfig
from penguin_tamer.arguments import parse_args
from penguin_tamer.error_handlers import connection_error
from penguin_tamer.dialog_input import DialogInputFormatter
from penguin_tamer.prompts import get_system_prompt, get_educational_prompt


# === Основная логика ===
def run_single_query(chat_client: OpenRouterClient, query: str, console) -> None:
    """Run a single query (optionally streaming)"""
    try:
        chat_client.ask_stream(query)
    except Exception as e:
        console.print(connection_error(e))


def _is_exit_command(prompt: str) -> bool:
    """Check if user wants to exit."""
    return prompt.lower() in ['exit', 'quit', 'q']


def _add_command_to_context(
    chat_client: OpenRouterClient, command: str, result: dict, block_number: int = None
) -> None:
    """Add executed command and its result to chat context.

    Args:
        chat_client: LLM client to add context to
        command: Executed command
        result: Execution result dictionary
        block_number: Optional code block number
    """
    # Формируем сообщение пользователя о выполнении команды
    if block_number is not None:
        user_message = t("Execute code block #{number}:").format(number=block_number) + f"\n```\n{command}\n```"
    else:
        user_message = t("Execute command: {command}").format(command=command)

    # Формируем системное сообщение с результатом
    if result['interrupted']:
        system_message = t("Command execution was interrupted by user (Ctrl+C).")
    elif result['success']:
        output_parts = []
        if result['stdout']:
            output_parts.append(t("Output:") + f"\n{result['stdout']}")
        if result['stderr']:
            output_parts.append(t("Errors:") + f"\n{result['stderr']}")

        if output_parts:
            system_message = t("Command executed successfully (exit code: 0).") + "\n" + "\n".join(output_parts)
        else:
            system_message = t("Command executed successfully (exit code: 0). No output.")
    else:
        output_parts = [t("Command failed with exit code: {code}").format(code=result['exit_code'])]
        if result['stdout']:
            output_parts.append(t("Output:") + f"\n{result['stdout']}")
        if result['stderr']:
            output_parts.append(t("Errors:") + f"\n{result['stderr']}")
        system_message = "\n".join(output_parts)

    # Добавляем в контекст диалога
    chat_client.messages.append({"role": "user", "content": user_message})
    chat_client.messages.append({"role": "system", "content": system_message})


def _handle_direct_command(console, chat_client: OpenRouterClient, prompt: str) -> bool:
    """Execute direct shell command (starts with dot) and add to context.

    Args:
        console: Rich console for output
        chat_client: LLM client to add command context
        prompt: User input

    Returns:
        True if command was handled, False otherwise
    """
    if not prompt.startswith('.'):
        return False

    command = prompt[1:].strip()
    if not command:
        console.print(t("[dim]Empty command after '.' - skipping.[/dim]"))
        return True

    console.print(t("[dim]>>> Executing command:[/dim] {command}").format(command=command))

    # Выполняем команду и получаем результат
    result = get_execute_handler()(console, command)
    console.print()

    # Записываем действие пользователя в демо ПОСЛЕ выполнения
    if chat_client.demo_manager and chat_client.demo_manager.is_recording():
        context = f"Exit code: {result.get('exit_code', -1)}, Success: {result.get('success', False)}"
        chat_client.demo_manager.record_action_only('command', prompt, context)

    # Добавляем команду и результат в контекст
    _add_command_to_context(chat_client, command, result)

    return True


def _handle_code_block_execution(console, chat_client: OpenRouterClient, prompt: str, code_blocks: list) -> bool:
    """Execute code block by number and add to context.

    Args:
        console: Rich console for output
        chat_client: LLM client to add command context
        prompt: User input
        code_blocks: List of available code blocks

    Returns:
        True if code block was executed, False otherwise
    """
    if not prompt.isdigit():
        return False

    block_index = int(prompt)
    if 1 <= block_index <= len(code_blocks):
        code = code_blocks[block_index - 1]

        # Выполняем блок кода и получаем результат
        result = get_script_executor()(console, code_blocks, block_index)
        console.print()

        # Записываем действие пользователя в демо ПОСЛЕ выполнения
        if chat_client.demo_manager and chat_client.demo_manager.is_recording():
            context = f"Exit code: {result.get('exit_code', -1)}, Success: {result.get('success', False)}"
            chat_client.demo_manager.record_action_only('code_block', prompt, context)

        # Добавляем команду и результат в контекст
        _add_command_to_context(chat_client, code, result, block_number=block_index)

        return True

    console.print(t("[dim]Code block #{number} not found.[/dim]").format(number=prompt))
    return True


def _process_ai_query(chat_client: OpenRouterClient, console, prompt: str) -> list:
    """Send query to AI and extract code blocks from response.

    Returns:
        List of code blocks from AI response
    """
    # Записываем действие пользователя в демо
    if chat_client.demo_manager and chat_client.demo_manager.is_recording():
        chat_client.demo_manager.add_user_action('query', prompt)

    reply = chat_client.ask_stream(prompt)
    code_blocks = []

    # Извлекаем блоки кода только если получен непустой ответ
    if reply:
        code_blocks = get_formatter_text()(reply)

    console.print()
    return code_blocks


def _process_initial_prompt(chat_client: OpenRouterClient, console, prompt: str) -> list:
    """Process initial user prompt if provided.

    Returns:
        List of code blocks from response
    """
    if not prompt:
        return []

    try:
        return _process_ai_query(chat_client, console, prompt)
    except Exception as e:
        console.print(connection_error(e))
        console.print()
        return []


def run_dialog_mode(chat_client: OpenRouterClient, console, initial_user_prompt: str = None) -> None:
    """Interactive dialog mode with educational prompt for code block numbering.

    Args:
        chat_client: Initialized LLM client
        console: Rich console for output
        initial_user_prompt: Optional initial prompt to process before entering dialog loop
    """
    # Setup
    history_file_path = config.user_config_dir / "cmd_history"
    input_formatter = DialogInputFormatter(history_file_path)

    # Initialize dialog mode with educational prompt
    educational_prompt = get_educational_prompt()
    chat_client.init_dialog_mode(educational_prompt)

    # Process initial prompt if provided
    last_code_blocks = _process_initial_prompt(chat_client, console, initial_user_prompt)

    # Проверяем режим robot
    is_robot_mode = chat_client.demo_manager and chat_client.demo_manager.is_robot_mode()
    robot_presenter = None

    if is_robot_mode:
        from penguin_tamer.demo import RobotPresenter
        robot_presenter = RobotPresenter(console, chat_client.demo_manager, t)

    # Main dialog loop
    while True:
        try:
            # В режиме robot автоматически получаем следующее действие
            if is_robot_mode:
                action = chat_client.demo_manager.get_next_user_action()
                if action:
                    # Используем presenter для визуализации
                    action_type, code_blocks = robot_presenter.present_action(
                        action,
                        has_code_blocks=bool(last_code_blocks)
                    )

                    # Обновляем code_blocks если получили новые
                    if code_blocks:
                        last_code_blocks = code_blocks

                    # Выполняем действия если нужно
                    user_prompt = action['value']
                    if action_type == 'command':
                        _handle_direct_command(console, chat_client, user_prompt)
                    elif action_type == 'code_block':
                        _handle_code_block_execution(console, chat_client, user_prompt, last_code_blocks)

                    continue
                else:
                    # Нет больше действий - переходим в обычный режим
                    is_robot_mode = False
                    robot_presenter = None
                    user_prompt = input_formatter.get_input(
                        console,
                        has_code_blocks=bool(last_code_blocks),
                        t=t
                    )
            else:
                # Обычный режим - запрашиваем ввод у пользователя
                user_prompt = input_formatter.get_input(
                    console,
                    has_code_blocks=bool(last_code_blocks),
                    t=t
                )

            if not user_prompt:
                continue

            # Check for exit
            if _is_exit_command(user_prompt):
                break

            # Handle direct command execution (with context)
            if _handle_direct_command(console, chat_client, user_prompt):
                continue

            # Handle code block execution (with context)
            if _handle_code_block_execution(console, chat_client, user_prompt, last_code_blocks):
                continue

            # Process as AI query
            last_code_blocks = _process_ai_query(chat_client, console, user_prompt)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(connection_error(e))

    # Stop demo manager before exiting dialog mode
    if chat_client.demo_manager:
        chat_client.demo_manager.stop()


def _create_chat_client(console, demo_manager=None):
    """Ленивое создание LLM клиента только когда он действительно нужен"""

    # Убеждаемся, что i18n инициализирован перед созданием клиента
    _ensure_i18n()

    llm_config = config.get_current_llm_config()

    # Создаём полную конфигурацию LLM (подключение + генерация)
    full_llm_config = LLMConfig(
        # Connection parameters
        api_key=llm_config["api_key"],
        api_url=llm_config["api_url"],
        model=llm_config["model"],
        # Generation parameters
        temperature=config.get("global", "temperature", 0.7),
        max_tokens=config.get("global", "max_tokens", None),
        top_p=config.get("global", "top_p", 0.95),
        frequency_penalty=config.get("global", "frequency_penalty", 0.0),
        presence_penalty=config.get("global", "presence_penalty", 0.0),
        stop=config.get("global", "stop", None),
        seed=config.get("global", "seed", None)
    )

    # Создаём клиент с единой конфигурацией
    chat_client = OpenRouterClient(
        console=console,
        system_message=get_system_prompt(),
        llm_config=full_llm_config
    )

    # Устанавливаем demo_manager если он был создан
    if demo_manager:
        chat_client._demo_manager = demo_manager

    return chat_client


def _create_console():
    """Создание Rich Console с темой из конфига."""
    Console = get_console_class()
    theme_name = config.get("global", "markdown_theme", "default")
    markdown_theme = get_theme()(theme_name)
    if markdown_theme is None:
        # Use default theme if unknown theme name
        markdown_theme = get_theme()("default")
    return Console(theme=markdown_theme)


def main() -> None:
    """Main entry point for Penguin Tamer CLI."""
    try:
        args = parse_args()

        # Settings mode - не нужен LLM клиент
        if args.settings:
            from penguin_tamer.menu.config_menu import main_menu
            main_menu()
            return 0

        # Check if API key exists for current LLM before proceeding
        try:
            llm_config = config.get_current_llm_config()
            api_key = llm_config.get("api_key", "").strip()

            if not api_key:
                # API key is missing - open settings with modal dialog
                from penguin_tamer.menu.config_menu import main_menu
                main_menu(show_api_key_dialog=True)

                # After settings closed, check again if key was added
                config.reload()
                llm_config = config.get_current_llm_config()
                api_key = llm_config.get("api_key", "").strip()

                if not api_key:
                    # User didn't add key - exit gracefully
                    return 0
        except Exception:
            # If we can't check config, let it fail later with proper error
            pass

        # Создаем консоль и клиент только если они нужны для AI операций
        console = _create_console()

        # Создаем DemoManager если указан demo mode
        demo_manager = None
        if hasattr(args, 'demo_mode') and args.demo_mode:
            from penguin_tamer.demo import DemoManager
            demo_manager = DemoManager(
                mode=args.demo_mode,
                demo_file=args.demo_file,
                console=console
            )

        chat_client = _create_chat_client(console, demo_manager)

        # Always run in dialog mode
        prompt_parts: list = args.prompt or []
        prompt: str = " ".join(prompt_parts).strip()

        # Dialog mode with optional initial prompt
        run_dialog_mode(chat_client, console, prompt if prompt else None)

    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Show where demo was saved if recording
        if demo_manager and demo_manager.is_recording():
            saved_path = demo_manager.get_saved_path()
            if saved_path:
                console.print(f"\n[green]Demo recording saved to:[/green] [cyan]{saved_path}[/cyan]")

        print()  # print empty line anyway

    return 0


if __name__ == "__main__":
    sys.exit(main())
