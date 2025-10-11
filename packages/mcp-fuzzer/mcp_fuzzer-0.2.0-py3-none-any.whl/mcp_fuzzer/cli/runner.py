#!/usr/bin/env python3
import asyncio
import os
import signal
import sys
from typing import Any, Dict, List

from rich.console import Console

from ..transport import create_transport
from ..safety_system.policy import configure_network_policy
from ..safety_system import start_system_blocking, stop_system_blocking


def create_transport_with_auth(args, client_args: Dict[str, Any]):
    try:
        auth_headers = None
        if client_args.get("auth_manager"):
            auth_headers = client_args["auth_manager"].get_auth_headers_for_tool("")

        factory_kwargs = {"timeout": args.timeout}
        if args.protocol == "http" and auth_headers:
            factory_kwargs["auth_headers"] = auth_headers

        transport = create_transport(
            args.protocol,
            args.endpoint,
            **factory_kwargs,
        )
        return transport
    except Exception as transport_error:
        console = Console()
        console.print(f"[bold red]Unexpected error:[/bold red] {transport_error}")
        sys.exit(1)


def prepare_inner_argv(args) -> List[str]:
    argv: List[str] = [sys.argv[0]]
    mode = args.mode
    argv += ["--mode", mode]
    argv += ["--protocol", args.protocol]
    argv += ["--endpoint", args.endpoint]
    if args.runs is not None:
        argv += ["--runs", str(args.runs)]
    if args.runs_per_type is not None:
        argv += ["--runs-per-type", str(args.runs_per_type)]
    if args.timeout is not None:
        argv += ["--timeout", str(args.timeout)]
    if getattr(args, "tool_timeout", None) is not None:
        argv += ["--tool-timeout", str(args.tool_timeout)]
    if args.protocol_type:
        argv += ["--protocol-type", args.protocol_type]
    if args.verbose:
        argv += ["--verbose"]
    if getattr(args, "no_network", False):
        argv += ["--no-network"]
    if getattr(args, "allow_hosts", None):
        for h in args.allow_hosts:
            argv += ["--allow-host", h]
    return argv


def start_safety_if_enabled(args) -> bool:
    if getattr(args, "enable_safety_system", False):
        start_system_blocking()
        return True
    return False


def stop_safety_if_started(started: bool) -> None:
    if started:
        try:
            stop_system_blocking()
        except Exception:
            pass


def execute_inner_client(args, unified_client_main, argv):
    old_argv = sys.argv
    sys.argv = argv
    should_exit = False
    try:
        if os.environ.get("PYTEST_CURRENT_TEST"):
            asyncio.run(unified_client_main())
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Check if aiomonitor is enabled
        enable_aiomonitor = getattr(args, 'enable_aiomonitor', False)
        
        if enable_aiomonitor:
            try:
                import aiomonitor
                print("AIOMonitor enabled! Connect with: telnet localhost 20101")
                print("Try commands: ps, where <task_id>, console, monitor")
                print("=" * 60)
            except ImportError:
                print(
                    "AIOMonitor requested but not installed. "
                    "Install with: pip install aiomonitor"
                )
                enable_aiomonitor = False

        # Print an immediate notice on first SIGINT/SIGTERM, then cancel tasks
        _signal_notice = {"printed": False}

        def _cancel_all_tasks():  # pragma: no cover
            if not _signal_notice["printed"]:
                try:
                    Console().print(
                        "\n[yellow]Received Ctrl+C from user; stopping now[/yellow]"
                    )
                except Exception:
                    pass
                _signal_notice["printed"] = True
            for task in asyncio.all_tasks(loop):
                task.cancel()

        if not getattr(args, "retry_with_safety_on_interrupt", False):
            try:
                loop.add_signal_handler(signal.SIGINT, _cancel_all_tasks)
                loop.add_signal_handler(signal.SIGTERM, _cancel_all_tasks)
            except NotImplementedError:
                pass
        try:
            # Configure network policy overrides
            deny = True if getattr(args, "no_network", False) else None
            extra = getattr(args, "allow_hosts", None)
            # Reset extra allowed hosts to prevent accumulation across runs
            # Reset network policy
            configure_network_policy(
                reset_allowed_hosts=True, deny_network_by_default=None
            )
            configure_network_policy(
                deny_network_by_default=deny, extra_allowed_hosts=extra
            )
            
            # Run with or without aiomonitor
            if enable_aiomonitor:
                import aiomonitor
                # Start aiomonitor with better monitoring configuration
                with aiomonitor.start_monitor(
                    loop,
                    console_enabled=True,
                    locals=True,  # Enable locals inspection
                ):
                    loop.run_until_complete(unified_client_main())
            else:
                loop.run_until_complete(unified_client_main())
        except asyncio.CancelledError:
            Console().print("\n[yellow]Fuzzing interrupted by user[/yellow]")
            should_exit = True
        finally:
            try:
                # Cancel all remaining tasks more aggressively
                pending = [t for t in asyncio.all_tasks(loop) if not t.done()]
                for t in pending:
                    t.cancel()

                # Wait for cancellation with a short timeout
                if pending:
                    gathered = asyncio.gather(*pending, return_exceptions=True)
                    try:
                        loop.run_until_complete(asyncio.wait_for(gathered, timeout=2.0))
                    except asyncio.TimeoutError:
                        # Force kill any remaining tasks
                        for t in pending:
                            if not t.done():
                                t.cancel()
            except Exception:
                pass
            loop.close()
    finally:
        sys.argv = old_argv
        if should_exit:
            raise SystemExit(130)


def run_with_retry_on_interrupt(args, unified_client_main, argv) -> None:
    try:
        execute_inner_client(args, unified_client_main, argv)
    except KeyboardInterrupt:
        console = Console()
        if (not getattr(args, "enable_safety_system", False)) and getattr(
            args, "retry_with_safety_on_interrupt", False
        ):
            console.print(
                "\n[yellow]Interrupted. Retrying once with safety system "
                "enabled...[/yellow]"
            )
            started = False
            try:
                start_system_blocking()
                started = True
            except Exception:
                pass
            try:
                execute_inner_client(args, unified_client_main, argv)
            finally:
                stop_safety_if_started(started)
        else:
            console.print("\n[yellow]Fuzzing interrupted by user[/yellow]")
            sys.exit(130)
