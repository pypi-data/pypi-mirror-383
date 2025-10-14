#!/usr/bin/env python3
"""
Nexus Delta SDK CLI
Command-line interface for the enhanced SDK with multi-model AI support
"""

import argparse
import json
import sys
from typing import Optional

from . import NexusDeltaSDK, MultiModelOrchestrator


class CLI:
    """Command-line interface for Nexus Delta SDK"""

    def __init__(self):
        self.orchestrator = MultiModelOrchestrator()

    def setup_parser(self) -> argparse.ArgumentParser:
        """Setup command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Nexus Delta SDK CLI - Multi-Model AI Orchestration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Query with automatic model routing
  nexusdelta-cli query "Write a Python function to reverse a string"

  # Query specific model
  nexusdelta-cli query --model grok "Explain how neural networks work"

  # Query with GitHub context (routes to Jules)
  nexusdelta-cli query --context "github.com/microsoft/vscode" "Generate documentation"

  # Check model capabilities
  nexusdelta-cli models

  # Test API keys
  nexusdelta-cli test-keys

  # SDK status
  nexusdelta-cli status
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Query command
        query_parser = subparsers.add_parser('query', help='Query AI models')
        query_parser.add_argument('prompt', help='The prompt to send to AI')
        query_parser.add_argument('--model', choices=['auto', 'grok', 'gemini', 'jules'],
                                default='auto', help='AI model to use (default: auto)')
        query_parser.add_argument('--context', help='Additional context for routing')
        query_parser.add_argument('--max-tokens', type=int, default=1000,
                                help='Maximum tokens in response')
        query_parser.add_argument('--temperature', type=float, default=0.7,
                                help='Creativity temperature (0.0-1.0)')
        query_parser.add_argument('--output', choices=['text', 'json'], default='text',
                                help='Output format')

        # Models command
        subparsers.add_parser('models', help='List available models and capabilities')

        # Test keys command
        subparsers.add_parser('test-keys', help='Test API key configurations')

        # Status command
        subparsers.add_parser('status', help='Show SDK status')

        return parser

    def handle_query(self, args) -> int:
        """Handle query command"""
        try:
            # For now, use the orchestrator directly (no SDK auth required for AI queries)
            if args.model == 'auto':
                result = self.orchestrator.orchestrate_query(
                    args.prompt,
                    args.context or "",
                    max_tokens=args.max_tokens,
                    temperature=args.temperature
                )
            else:
                # Query specific model
                if args.model == 'grok':
                    result = self.orchestrator.query_grok(
                        args.prompt,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature
                    )
                elif args.model == 'gemini':
                    result = self.orchestrator.query_gemini(
                        args.prompt,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature
                    )
                elif args.model == 'jules':
                    result = self.orchestrator.query_jules(args.prompt, args.context)
                else:
                    print(f"Error: Unknown model '{args.model}'")
                    return 1

            if args.output == 'json':
                print(json.dumps(result, indent=2))
            else:
                if 'error' in result:
                    print(f"Error: {result['error']}")
                    return 1
                else:
                    print(f"Model: {result.get('model', 'unknown')}")
                    print(f"Response: {result.get('response', 'No response')}")
                    if 'session_url' in result:
                        print(f"Session URL: {result['session_url']}")

        except Exception as e:
            print(f"Error: {str(e)}")
            return 1

        return 0

    def handle_models(self, args) -> int:
        """Handle models command"""
        print("Available AI Models and Capabilities:")
        print("=" * 50)

        for model, capabilities in self.orchestrator.model_capabilities.items():
            print(f"\n{model.upper()}:")
            for cap in capabilities:
                print(f"  • {cap.replace('_', ' ').title()}")

        print("\nRouting Intelligence:")
        print("  • Automatic model selection based on task type")
        print("  • Context-aware routing (GitHub repos → Jules)")
        print("  • Code generation → Gemini, Reasoning → Grok")

        return 0

    def handle_test_keys(self, args) -> int:
        """Handle test-keys command"""
        print("Testing API Key Configurations:")
        print("=" * 40)

        keys_status = {
            "Grok (xAI)": bool(self.orchestrator.grok_key),
            "Gemini (Google)": bool(self.orchestrator.gemini_key),
            "Jules (Google)": bool(self.orchestrator.jules_key)
        }

        configured_count = sum(configured for configured in keys_status.values())

        for service, configured in keys_status.items():
            status = "✓ Configured" if configured else "✗ Not configured"
            print(f"{service}: {status}")

        print(f"\nKeys configured: {configured_count}/3")
        if configured_count == 0:
            print("\nNote: Set environment variables:")
            print("  XAI_API_KEY - for Grok (xAI)")
            print("  GEMINI_API_KEY - for Gemini (Google)")
            print("  JULES_API_KEY - for Jules (Google)")
        return 0

    def handle_status(self, args) -> int:
        """Handle status command"""
        print("Nexus Delta SDK v2.1.0 Status:")
        print("=" * 40)

        # Check API keys
        keys_configured = sum([
            bool(self.orchestrator.grok_key),
            bool(self.orchestrator.gemini_key),
            bool(self.orchestrator.jules_key)
        ])

        print(f"Multi-Model AI: {'Enabled' if keys_configured > 0 else 'Limited'}")
        print(f"API Keys Configured: {keys_configured}/3")
        print(f"Models Available: {len(self.orchestrator.model_capabilities)}")
        print("Status: Ready for orchestration" if keys_configured > 0 else "Status: Basic functionality only")

        return 0

    def run(self, argv: Optional[list] = None) -> int:
        """Main CLI entry point"""
        parser = self.setup_parser()
        args = parser.parse_args(argv)

        if not args.command:
            parser.print_help()
            return 0

        command_handlers = {
            'query': self.handle_query,
            'models': self.handle_models,
            'test-keys': self.handle_test_keys,
            'status': self.handle_status
        }

        handler = command_handlers.get(args.command)
        if handler:
            return handler(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1


def main():
    """CLI entry point"""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()