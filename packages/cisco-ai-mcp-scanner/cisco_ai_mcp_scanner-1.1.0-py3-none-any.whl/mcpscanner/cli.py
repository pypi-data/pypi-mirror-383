# Copyright 2025 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0


#!/usr/bin/env python3
"""
MCP Security Scanner

A comprehensive security scanning tool for Model Context Protocol (MCP) servers.
This tool analyzes MCP tools for potential security vulnerabilities using multiple
analysis engines including API-based classification, YARA pattern matching,
and LLM-powered threat detection.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional
from mcpscanner.utils.logging_config import get_logger

from mcpscanner import Config, Scanner
from mcpscanner.core.models import AnalyzerEnum
from mcpscanner.core.report_generator import (
    OutputFormat,
    ReportGenerator,
    SeverityFilter,
    results_to_json,
)
from mcpscanner.utils.logging_config import set_verbose_logging
from mcpscanner.core.auth import Auth
from mcpscanner.core.mcp_models import StdioServer

logger = get_logger(__name__)

from dotenv import load_dotenv

load_dotenv()


def _get_endpoint_from_env() -> str:
    return os.environ.get("MCP_SCANNER_ENDPOINT", "")


def _build_config(
    selected_analyzers: List[AnalyzerEnum], endpoint_url: Optional[str] = None
) -> Config:
    api_key = os.environ.get("MCP_SCANNER_API_KEY", "")
    llm_api_key = os.environ.get("MCP_SCANNER_LLM_API_KEY", "")
    llm_base_url = os.environ.get("MCP_SCANNER_LLM_BASE_URL")
    llm_api_version = os.environ.get("MCP_SCANNER_LLM_API_VERSION")
    llm_model = os.environ.get("MCP_SCANNER_LLM_MODEL")
    endpoint_url = endpoint_url or _get_endpoint_from_env()

    config_params = {
        "api_key": api_key if AnalyzerEnum.API in selected_analyzers else "",
        "endpoint_url": endpoint_url,
        "llm_provider_api_key": (
            llm_api_key if AnalyzerEnum.LLM in selected_analyzers else ""
        ),
        "llm_model": llm_model if AnalyzerEnum.LLM in selected_analyzers else "",
    }

    if llm_base_url:
        config_params["llm_base_url"] = llm_base_url
    if llm_api_version:
        config_params["llm_api_version"] = llm_api_version

    return Config(**config_params)


async def scan_mcp_server_direct(
    server_url: str,
    analyzers: List[AnalyzerEnum],
    output_file: Optional[str] = None,
    verbose: bool = False,
    rules_path: Optional[str] = None,
    endpoint_url: Optional[str] = None,
) -> List[Any]:
    """
    Perform comprehensive security scanning of an MCP server using Scanner directly.

    Args:
        server_url: URL of the MCP server to scan
        analyzers: List of analyzers to run
        output_file: Optional file to save the scan results
        verbose: Whether to print verbose output
        rules_path: Optional custom path to YARA rules directory

    Returns:
        List of scan results
    """
    if verbose:
        enabled_analyzers = [analyzer.value.upper() for analyzer in analyzers]
        print(f"🔍 Scanning MCP server: {server_url}")
        print(
            f"   Analyzers: {', '.join(enabled_analyzers) if enabled_analyzers else 'None'}"
        )
        if rules_path:
            print(f"   Custom YARA Rules: {rules_path}")

    try:
        config = _build_config(analyzers, endpoint_url)
        scanner = Scanner(config, rules_dir=rules_path)

        # Scan all tools on the server
        start_time = time.time()
        results = await scanner.scan_remote_server_tools(
            server_url, auth=None, analyzers=analyzers
        )
        elapsed_time = time.time() - start_time

        if verbose:
            print(
                f"✅ Scan completed in {elapsed_time:.2f}s - Found {len(results)} tools"
            )

        # Normalize ScanResult objects
        json_results = await results_to_json(results)

        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(json_results, f, indent=2)
            if verbose:
                print(f"Results saved to {output_file}")

        return json_results

    except Exception as e:
        # Handle MCP-specific exceptions gracefully
        if e.__class__.__name__ in ('MCPConnectionError', 'MCPAuthenticationError', 'MCPServerNotFoundError'):
            print(f"❌ Connection Error: {e}")
            if verbose:
                print("💡 Troubleshooting tips:")
                print(f"   • Make sure an MCP server is running at {server_url}")
                print("   • Verify the URL is correct (including protocol and port)")
                print("   • Check if the server is accessible from your network")
            return []
        # All other exceptions
        print(f"❌ Error scanning server: {e}")
        if verbose:
            traceback.print_exc()
        return []


def display_results(results: Dict[str, Any], detailed: bool = False) -> None:
    """
    Display the scan results in a readable format.

    Args:
        results: Scan results from the MCP Scanner API
        detailed: Whether to show detailed results
    """
    print("\n=== MCP Scanner Results ===\n")

    print(f"Server URL: {results.get('server_url', 'N/A')}")

    # Display scan results
    scan_results = results.get("scan_results", [])
    print(f"Tools scanned: {len(scan_results)}")

    safe_tools = [tool for tool in scan_results if tool.get("is_safe", False)]
    unsafe_tools = [tool for tool in scan_results if not tool.get("is_safe", False)]

    print(f"Safe tools: {len(safe_tools)}")
    print(f"Unsafe tools: {len(unsafe_tools)}")

    # Display unsafe tools
    if unsafe_tools:
        print("\n=== Unsafe Tools ===\n")
        for i, tool in enumerate(unsafe_tools, 1):
            print(f"{i}. {tool.get('tool_name', 'Unknown')}")
            findings = tool.get("findings", {})

            # Count total findings across all analyzers
            total_findings = sum(
                analyzer_data.get("total_findings", 0)
                for analyzer_data in findings.values()
                if isinstance(analyzer_data, dict)
            )
            print(f"   Findings: {total_findings}")

            if detailed and findings:
                finding_num = 1
                for analyzer_name, analyzer_data in findings.items():
                    if (
                        isinstance(analyzer_data, dict)
                        and analyzer_data.get("total_findings", 0) > 0
                    ):
                        # Clean up analyzer name for display
                        clean_analyzer_name = analyzer_name.replace(
                            "_analyzer", ""
                        ).upper()

                        print(
                            f"   {finding_num}. {analyzer_data.get('threat_summary', 'No summary')}"
                        )
                        print(
                            f"      Severity: {analyzer_data.get('severity', 'Unknown')}"
                        )
                        print(f"      Analyzer: {clean_analyzer_name}")

                        # Display threat types if available
                        threat_names = analyzer_data.get("threat_names", [])
                        if threat_names:
                            threat_display = ", ".join(
                                [t.replace("_", " ").title() for t in threat_names]
                            )
                            print(f"      Threats: {threat_display}")

                        print()
                        finding_num += 1
            print()


async def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="MCP Security Scanner - Comprehensive security analysis for MCP servers",
        epilog="""Examples:
  %(prog)s                                                    # Basic security scan with summary (all analyzers)
  %(prog)s --api-key YOUR_API_KEY --endpoint-url <your-endpoint> # Scan with an endpoint
  %(prog)s --format detailed --api-key YOUR_API_KEY         # Detailed vulnerability report with API
  %(prog)s --format by_analyzer --llm-api-key YOUR_LLM_KEY  # Group findings by analysis engine with LLM
  %(prog)s --format table --analyzers yara                  # YARA-only scanning with table format
  %(prog)s --analyzers api,yara --severity-filter high      # API and YARA analysis, high severity only
  %(prog)s --analyzer-filter llm_analyzer --stats           # Show only LLM analysis with statistics
  %(prog)s --tool-filter "database" --output results.json  # Filter and save results to file
  %(prog)s --analyzers llm --raw                            # LLM-only scan with raw JSON output
  %(prog)s --analyzers api,llm --hide-safe                  # API and LLM scan, hide safe results
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Subcommands for scan modes (remote, stdio, config, known-configs)
    subparsers = parser.add_subparsers(dest="cmd")

    p_remote = subparsers.add_parser(
        "remote", help="Scan a remote MCP server (SSE or streamable HTTP)"
    )
    p_remote.add_argument(
        "--server-url",
        required=True,
        help="URL of the MCP server to scan",
    )
    p_remote.add_argument(
        "--bearer-token",
        help="Bearer token to use for remote MCP server authentication (Authorization: Bearer <token>)",
    )

    # API key and endpoint configuration
    parser.add_argument(
        "--api-key",
        help="Cisco AI Defense API key (overrides MCP_SCANNER_API_KEY environment variable)",
    )
    parser.add_argument(
        "--endpoint-url",
        help="Cisco AI Defense endpoint URL (overrides MCP_SCANNER_ENDPOINT environment variable)",
    )
    parser.add_argument(
        "--llm-api-key",
        help="LLM provider API key for LLM analysis (overrides environment variable)",
    )

    parser.add_argument(
        "--analyzers",
        default="api,yara,llm",
        help="Comma-separated list of analyzers to run. Options: api, yara, llm (default: %(default)s)",
    )

    parser.add_argument("--output", "-o", help="Save scan results to a file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output"
    )
    parser.add_argument(
        "--detailed", "-d", action="store_true", help="Show detailed results"
    )
    parser.add_argument(
        "--raw", "-r", action="store_true", help="Print raw JSON output to terminal"
    )

    parser.add_argument(
        "--server-url",
        default="https://mcp.deepwiki.com/mcp",
        help="URL of the MCP server to scan (default: %(default)s)",
    )
    parser.add_argument(
        "--scan-known-configs",
        action="store_true",
        help="Scan all well-known MCP client config files on this machine (windsurf, cursor, claude, vscode)",
    )
    parser.add_argument(
        "--config-path",
        help="Scan all servers defined in a specific MCP config file (e.g., ~/.codeium/windsurf/mcp_config.json)",
    )
    parser.add_argument(
        "--stdio-command",
        help="Run a stdio-based MCP server using the given command (e.g., 'uvx')",
    )
    parser.add_argument(
        "--stdio-args",
        nargs="*",
        default=[],
        help="Arguments passed to the stdio command (space-separated)",
    )
    parser.add_argument(
        "--stdio-arg",
        action="append",
        help="[Deprecated] Repeatable single arg; use --stdio-args instead",
    )
    parser.add_argument(
        "--stdio-env",
        action="append",
        default=[],
        help="Environment variables for the stdio server in KEY=VALUE form; can be repeated",
    )
    parser.add_argument(
        "--stdio-tool",
        help="If provided, only scan this specific tool name on the stdio server",
    )

    # Back-compat bearer
    parser.add_argument(
        "--bearer-token",
        help="Bearer token to use for remote MCP server authentication (Authorization: Bearer <token>)",
    )

    parser.add_argument(
        "--format",
        choices=[
            "raw",
            "summary",
            "detailed",
            "by_tool",
            "by_analyzer",
            "by_severity",
            "table",
        ],
        default="summary",
        help="Output format (default: %(default)s)",
    )
    parser.add_argument(
        "--tool-filter", help="Filter results by tool name (partial match)"
    )
    parser.add_argument(
        "--analyzer-filter",
        choices=["api_analyzer", "yara_analyzer", "llm_analyzer"],
        help="Filter results by specific analyzer",
    )
    parser.add_argument(
        "--severity-filter",
        choices=["all", "high", "unknown", "medium", "low", "safe"],
        default="all",
        help="Filter results by severity level (default: %(default)s)",
    )
    parser.add_argument(
        "--hide-safe", action="store_true", help="Hide safe tools from output"
    )
    parser.add_argument(
        "--stats", action="store_true", help="Show statistics about scan results"
    )
    parser.add_argument(
        "--rules-path",
        help="Path to directory containing custom YARA rules",
    )

    args = parser.parse_args()

    # Parse analyzers argument into AnalyzerEnum list
    analyzer_names = [a.strip().lower() for a in args.analyzers.split(",")]
    valid_analyzer_names = {e.value for e in AnalyzerEnum}

    # Validate analyzer names
    invalid_analyzers = set(analyzer_names) - valid_analyzer_names
    if invalid_analyzers:
        parser.error(
            f"Invalid analyzers: {', '.join(invalid_analyzers)}. Valid options: {', '.join(valid_analyzer_names)}"
        )

    # Convert to AnalyzerEnum list
    selected_analyzers = [AnalyzerEnum(name) for name in analyzer_names]

    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        logging.getLogger("mcpscanner").setLevel(logging.DEBUG)
        set_verbose_logging(True)
        logger.info("Verbose output enabled - detailed analyzer logs will be shown")
    else:
        logging.basicConfig(
            level=logging.WARNING,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        logging.getLogger("mcpscanner").setLevel(logging.WARNING)
        set_verbose_logging(False)

    if args.api_key:
        os.environ["MCP_SCANNER_API_KEY"] = args.api_key
    if args.endpoint_url:
        os.environ["MCP_SCANNER_ENDPOINT"] = args.endpoint_url
    if args.llm_api_key:
        os.environ["MCP_SCANNER_LLM_API_KEY"] = args.llm_api_key

    try:
        if args.cmd == "remote":
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            auth = Auth.bearer(args.bearer_token) if args.bearer_token else None
            results_raw = await scanner.scan_remote_server_tools(
                args.server_url, auth=auth, analyzers=selected_analyzers
            )
            results = await results_to_json(results_raw)

        elif args.cmd == "stdio":
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            env_dict = {}
            for item in args.stdio_env or []:
                if "=" in item:
                    k, v = item.split("=", 1)
                    env_dict[k] = v
            stdio_args = list(args.stdio_args or [])
            if getattr(args, "stdio_arg", None):
                print("[warning] --stdio-arg is deprecated; use --stdio-args")
                stdio_args.extend(args.stdio_arg)
            stdio = StdioServer(
                command=args.stdio_command, args=stdio_args, env=env_dict or None
            )
            if args.stdio_tool:
                scan_result = await scanner.scan_stdio_server_tool(
                    stdio, args.stdio_tool, analyzers=selected_analyzers
                )
                results = await results_to_json([scan_result])
            else:
                scan_results = await scanner.scan_stdio_server_tools(
                    stdio, analyzers=selected_analyzers
                )
                results = await results_to_json(scan_results)

        elif args.cmd == "config":
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            auth = Auth.bearer(args.bearer_token) if args.bearer_token else None
            scan_results = await scanner.scan_mcp_config_file(
                args.config_path, analyzers=selected_analyzers, auth=auth
            )
            results = await results_to_json(scan_results)

        elif args.cmd == "known-configs":
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            auth = Auth.bearer(args.bearer_token) if args.bearer_token else None
            results_by_cfg = await scanner.scan_well_known_mcp_configs(
                analyzers=selected_analyzers, auth=auth
            )
            if args.raw:
                output = {}
                for cfg_path, scan_results in results_by_cfg.items():
                    output[cfg_path] = await results_to_json(scan_results)
                print(json.dumps(output, indent=2))
                return
            flattened = []
            for scan_results in results_by_cfg.values():
                flattened.extend(scan_results)
            results = await results_to_json(flattened)

        # Backward compatibility path (no subcommand used)
        elif args.stdio_command:
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            env_dict = {}
            for item in args.stdio_env or []:
                if "=" in item:
                    k, v = item.split("=", 1)
                    env_dict[k] = v
            stdio_args = list(args.stdio_args or [])
            if args.stdio_arg:
                print("[warning] --stdio-arg is deprecated; use --stdio-args")
                stdio_args.extend(args.stdio_arg)
            stdio = StdioServer(
                command=args.stdio_command,
                args=stdio_args,
                env=env_dict or None,
            )
            if args.stdio_tool:
                scan_result = await scanner.scan_stdio_server_tool(
                    stdio, args.stdio_tool, analyzers=selected_analyzers
                )
                results = await results_to_json([scan_result])
            else:
                scan_results = await scanner.scan_stdio_server_tools(
                    stdio, analyzers=selected_analyzers
                )
                results = await results_to_json(scan_results)

        elif args.scan_known_configs or args.config_path:
            cfg = _build_config(selected_analyzers)
            scanner = Scanner(cfg, rules_dir=args.rules_path)
            if args.config_path:
                auth = Auth.bearer(args.bearer_token) if args.bearer_token else None
                scan_results = await scanner.scan_mcp_config_file(
                    args.config_path, analyzers=selected_analyzers, auth=auth
                )
                results = await results_to_json(scan_results)
            else:
                auth = Auth.bearer(args.bearer_token) if args.bearer_token else None
                results_by_cfg = await scanner.scan_well_known_mcp_configs(
                    analyzers=selected_analyzers, auth=auth
                )
                if args.raw:
                    output = {}
                    for cfg_path, scan_results in results_by_cfg.items():
                        output[cfg_path] = await results_to_json(scan_results)
                    print(json.dumps(output, indent=2))
                    return
                flattened = []
                for cfg_path, scan_results in results_by_cfg.items():
                    # Add config path and server info to each result
                    for result in scan_results:
                        # Extract server name from config path for display
                        config_name = (
                            cfg_path.split("/")[-1] if "/" in cfg_path else cfg_path
                        )
                        result.server_source = f"{config_name}"
                    flattened.extend(scan_results)
                results = await results_to_json(flattened)

        else:
            # Run the security scan against a server URL
            if args.bearer_token:
                cfg = _build_config(selected_analyzers)
                scanner = Scanner(cfg, rules_dir=args.rules_path)
                results_raw = await scanner.scan_remote_server_tools(
                    args.server_url,
                    auth=Auth.bearer(args.bearer_token),
                    analyzers=selected_analyzers,
                )
                results = await results_to_json(results_raw)
            else:
                # Fallback path (from `main` branch)
                results = await scan_mcp_server_direct(
                    server_url=args.server_url,
                    analyzers=selected_analyzers,
                    output_file=args.output,
                    verbose=args.verbose,
                    rules_path=args.rules_path,
                    endpoint_url=args.endpoint_url,
                )

    except Exception as e:
        print(f"Error during scanning: {e}", file=sys.stderr)
        sys.exit(1)

    # Display the results using the new report generator
    if not args.raw and not args.detailed:
        # Choose an appropriate label for display based on scanning mode
        server_label = args.server_url
        if hasattr(args, "cmd") and args.cmd == "stdio":
            label_args = []
            if getattr(args, "stdio_arg", None):
                label_args.extend(args.stdio_arg)
            if getattr(args, "stdio_args", None):
                label_args.extend(args.stdio_args)
            server_label = f"stdio:{args.stdio_command} {' '.join(label_args)}".strip()
        elif hasattr(args, "cmd") and args.cmd == "config":
            server_label = args.config_path
        elif hasattr(args, "cmd") and args.cmd == "known-configs":
            server_label = "well-known-configs"
        elif args.stdio_command:
            label_args = []
            if getattr(args, "stdio_arg", None):
                label_args.extend(args.stdio_arg)
            if getattr(args, "stdio_args", None):
                label_args.extend(args.stdio_args)
            server_label = f"stdio:{args.stdio_command} {' '.join(label_args)}".strip()
        elif args.config_path:
            server_label = args.config_path
        elif args.scan_known_configs:
            server_label = "well-known-configs"

        results_dict = {
            "server_url": server_label,
            "scan_results": results,
            "requested_analyzers": selected_analyzers,
        }
        formatter = ReportGenerator(results_dict)

        if args.stats:
            stats = formatter.get_statistics()
            print("=== Scan Statistics ===")
            print(f"Total tools: {stats['total_tools']}")
            print(f"Safe tools: {stats['safe_tools']}")
            print(f"Unsafe tools: {stats['unsafe_tools']}")
            print(f"Severity breakdown: {stats['severity_counts']}")
            print(f"Analyzer stats: {stats['analyzer_stats']}")
            print()

        # Determine output format
        if args.format == "raw":
            output_format = OutputFormat.RAW
        elif args.format == "summary":
            output_format = OutputFormat.SUMMARY
        elif args.format == "detailed":
            output_format = OutputFormat.DETAILED
        elif args.format == "by_tool":
            output_format = OutputFormat.BY_TOOL
        elif args.format == "by_analyzer":
            output_format = OutputFormat.BY_ANALYZER
        elif args.format == "by_severity":
            output_format = OutputFormat.BY_SEVERITY
        elif args.format == "table":
            output_format = OutputFormat.TABLE
        else:
            output_format = OutputFormat.SUMMARY

        # Determine severity filter
        if args.severity_filter == "all":
            severity_filter = SeverityFilter.ALL
        elif args.severity_filter == "high":
            severity_filter = SeverityFilter.HIGH
        elif args.severity_filter == "unknown":
            severity_filter = SeverityFilter.UNKNOWN
        elif args.severity_filter == "medium":
            severity_filter = SeverityFilter.MEDIUM
        elif args.severity_filter == "low":
            severity_filter = SeverityFilter.LOW
        elif args.severity_filter == "safe":
            severity_filter = SeverityFilter.SAFE
        else:
            severity_filter = SeverityFilter.ALL

        # Generate and display report
        formatted_output = formatter.format_output(
            format_type=output_format,
            tool_filter=args.tool_filter,
            analyzer_filter=args.analyzer_filter,
            severity_filter=severity_filter,
            show_safe=not args.hide_safe,
        )
        print(formatted_output)

    elif args.raw:
        print(json.dumps(results, indent=2))
    else:
        # Choose an appropriate label for display based on scanning mode
        server_label = args.server_url
        if args.stdio_command:
            label_args = []
            if args.stdio_arg:
                label_args.extend(args.stdio_arg)
            if args.stdio_args:
                label_args.extend(args.stdio_args)
            server_label = f"stdio:{args.stdio_command} {' '.join(label_args)}".strip()
        elif args.config_path:
            server_label = args.config_path
        elif args.scan_known_configs:
            server_label = "well-known-configs"

        results_dict = {"server_url": server_label, "scan_results": results}
        display_results(results_dict, detailed=args.detailed)


def cli_entry_point():
    """Entry point for the mcp-scanner CLI command."""
    import sys
    import logging
    import warnings
    
    # Suppress warnings from MCP library cleanup issues
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*coroutine.*never awaited.*")
    warnings.filterwarnings("ignore", category=RuntimeWarning, message=".*async.*generator.*")
    
    # Suppress asyncio shutdown errors from MCP library cleanup bugs
    def custom_exception_handler(loop, context):
        exception = context.get("exception")
        message = context.get("message", "")
        
        # Suppress RuntimeError from MCP library task cleanup
        if isinstance(exception, RuntimeError) and "cancel scope" in str(exception):
            return
        # Suppress task destroyed warnings
        if "Task was destroyed but it is pending" in message:
            return
        # Suppress other MCP library cleanup errors
        if "streamablehttp_client" in message or "async_generator" in message:
            return
        # For other exceptions, use default handling
        loop.default_exception_handler(context)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_exception_handler(custom_exception_handler)
    
    try:
        loop.run_until_complete(main())
    finally:
        # Suppress warnings during loop close
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            loop.close()


if __name__ == "__main__":
    asyncio.run(main())
