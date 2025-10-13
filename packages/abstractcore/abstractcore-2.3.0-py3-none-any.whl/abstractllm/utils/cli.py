#!/usr/bin/env python3
"""
AbstractCore CLI - Basic demonstrator for AbstractLLM capabilities.

This is a simple CLI tool that demonstrates basic AbstractCore functionality.
It provides chat, file operations, and command execution but has limitations:
- Simple chat interactions only
- Basic single tool execution
- No ReAct pattern or complex reasoning chains
- No adaptive actions or advanced reasoning patterns
- Limited to basic demonstration purposes

For production use cases requiring advanced reasoning, multi-step tool chains,
or complex agent behaviors, consider building custom solutions using the
AbstractCore framework directly.

Usage:
    python -m abstractllm.utils.cli --provider ollama --model qwen3-coder:30b
    python -m abstractllm.utils.cli --provider openai --model gpt-4o-mini --stream
    python -m abstractllm.utils.cli --provider anthropic --model claude-3-5-haiku-20241022 --prompt "What is Python?"
"""

import argparse
import sys
import time

from .. import create_llm, BasicSession
from ..tools.common_tools import list_files, read_file, write_file, execute_command
from ..processing import BasicExtractor, BasicJudge


class SimpleCLI:
    """Simplified CLI REPL for AbstractLLM"""

    def __init__(self, provider: str, model: str, stream: bool = False,
                 max_tokens: int = None, debug: bool = False, **kwargs):
        self.provider_name = provider
        self.model_name = model
        self.stream_mode = stream
        self.debug_mode = debug
        self.kwargs = kwargs

        # Auto-detect max_tokens from model capabilities if not specified
        if max_tokens is None:
            try:
                from ..architectures.detection import get_model_capabilities
                capabilities = get_model_capabilities(model)
                max_tokens = capabilities.get('max_tokens', 16384)  # Fallback to 16K if not found
                if debug:
                    print(f"🔍 Auto-detected max_tokens: {max_tokens} (from model capabilities)")
            except Exception as e:
                max_tokens = 16384  # Safe fallback
                if debug:
                    print(f"⚠️ Failed to auto-detect max_tokens, using fallback: {max_tokens} ({e})")

        self.max_tokens = max_tokens

        # Initialize provider and session with tools
        self.provider = create_llm(provider, model=model, max_tokens=max_tokens, **kwargs)
        self.session = BasicSession(
            self.provider,
            system_prompt="You are a helpful AI assistant.",
            tools=[list_files, read_file, write_file, execute_command]
        )

        print(f"🚀 AbstractLLM CLI - {provider}:{model}")
        print(f"Stream: {'ON' if stream else 'OFF'} | Debug: {'ON' if debug else 'OFF'}")
        print("Commands: /help /quit /clear /stream /debug /status /history [n] /model <spec> /compact /facts [file] /judge /system [prompt]")
        print("Tools: list_files, read_file, write_file, execute_command")
        print("=" * 60)

    def handle_command(self, user_input: str) -> bool:
        """Handle commands. Returns True if command processed, False otherwise."""
        if not user_input.startswith('/'):
            return False

        cmd = user_input[1:].strip()

        if cmd in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            sys.exit(0)

        elif cmd == 'help':
            print("\n📖 Commands:")
            print("  /help - Show this help")
            print("  /quit - Exit")
            print("  /clear - Clear history")
            print("  /stream - Toggle streaming")
            print("  /debug - Toggle CLI debug mode (timing, auto-detection info)")
            print("  /status - Show current provider, model, capabilities, and token usage")
            print("  /history [n] - Show conversation history or last n interactions")
            print("  /model <provider:model> - Change model")
            print("  /compact - Compact chat history using gemma3:1b-it-qat-it-qat")
            print("  /facts [file] - Extract facts from conversation history")
            print("  /judge - Evaluate conversation quality and provide feedback")
            print("  /system [prompt] - Show or change system prompt")
            print("  /tooltag <opening_tag> <closing_tag> - Test tool call tag rewriting")
            print("\n🛠️ Tools: list_files, read_file, write_file, execute_command\n")

        elif cmd == 'clear':
            self.session.clear_history(keep_system=True)
            print("🧹 History cleared")

        elif cmd == 'stream':
            self.stream_mode = not self.stream_mode
            print(f"🌊 Stream mode: {'ON' if self.stream_mode else 'OFF'}")

        elif cmd == 'debug':
            self.debug_mode = not self.debug_mode
            print(f"🐛 CLI Debug mode: {'ON' if self.debug_mode else 'OFF'} (controls timing & auto-detection info)")
            print("💡 Note: System debug logs are controlled by logging level, not CLI debug mode")

        elif cmd == 'status':
            self.handle_status()

        elif cmd.startswith('history'):
            # Parse /history [n] command
            parts = cmd.split()
            if len(parts) == 1:
                # Show all history
                self.handle_history(None)
            else:
                try:
                    n = int(parts[1])
                    self.handle_history(n)
                except (ValueError, IndexError):
                    print("❓ Usage: /history [n] where n is number of interactions")

        elif cmd.startswith('model '):
            try:
                model_spec = cmd[6:]
                if ':' in model_spec:
                    self.provider_name, self.model_name = model_spec.split(':', 1)
                else:
                    self.model_name = model_spec

                print(f"🔄 Switching to {self.provider_name}:{self.model_name}...")
                self.provider = create_llm(self.provider_name, model=self.model_name,
                                         max_tokens=self.max_tokens, **self.kwargs)
                self.session = BasicSession(
                    self.provider,
                    system_prompt="You are a helpful AI assistant.",
                    tools=[list_files, read_file, write_file, execute_command]
                )
                print("✅ Model switched")
            except Exception as e:
                print(f"❌ Failed to switch: {e}")

        elif cmd == 'compact':
            self.handle_compact()

        elif cmd.startswith('facts'):
            # Parse /facts [file] command
            parts = cmd.split()
            if len(parts) == 1:
                # No file specified - display facts in chat
                self.handle_facts(None)
            else:
                # File specified - save as JSON-LD
                filename = parts[1]
                self.handle_facts(filename)

        elif cmd == 'judge':
            self.handle_judge()

        elif cmd.startswith('system'):
            # Parse /system [prompt] command
            if cmd == 'system':
                # Show current system prompt
                self.handle_system_show()
            else:
                # Change system prompt - extract everything after "system "
                new_prompt = user_input[8:].strip()  # Remove "/system " prefix
                if new_prompt:
                    self.handle_system_change(new_prompt)
                else:
                    self.handle_system_show()

        elif cmd.startswith('tooltag'):
            # Parse /tooltag <opening_tag> <closing_tag> command
            parts = cmd.split()
            if len(parts) != 3:
                print("❓ Usage: /tooltag <opening_tag> <closing_tag>")
                print("   Example: /tooltag '<|tool_call|>' '</|tool_call|>'")
                print("   Example: /tooltag '<function_call>' '</function_call>'")
                print("   Example: /tooltag '<tool_call>' '</tool_call>'")
            else:
                # Strip quotes from the tags if present
                opening_tag = parts[1].strip("'\"")
                closing_tag = parts[2].strip("'\"")
                self.handle_tooltag_test(opening_tag, closing_tag)

        else:
            print(f"❓ Unknown command: /{cmd}. Type /help for help.")

        return True

    def handle_compact(self):
        """Handle /compact command - compact chat history using gemma3:1b"""
        messages = self.session.get_messages()

        if len(messages) <= 3:  # System + minimal conversation
            print("📝 Not enough history to compact (need at least 2 exchanges)")
            return

        try:
            print("🗜️  Compacting chat history...")
            print(f"   Before: {len(messages)} messages (~{self.session.get_token_estimate()} tokens)")

            # Create compact provider using gemma3:1b-it-qat for fast, local processing
            try:
                from .. import create_llm
                compact_provider = create_llm("ollama", model="gemma3:1b-it-qat")
                print("   Using gemma3:1b-it-qat for compaction...")
            except Exception as e:
                print(f"⚠️  Could not create gemma3:1b-it-qat provider: {e}")
                print("   Using current provider instead...")
                compact_provider = None

            start_time = time.time()

            # Perform in-place compaction
            self.session.force_compact(
                preserve_recent=4,  # Keep last 6 messages (3 exchanges)
                focus="key information and ongoing context"
            )

            duration = time.time() - start_time

            print(f"✅ Compaction completed in {duration:.1f}s")
            print(f"   After: {len(self.session.get_messages())} messages (~{self.session.get_token_estimate()} tokens)")

            # Show compacted structure
            messages_after = self.session.get_messages()
            print("   Structure:")
            for i, msg in enumerate(messages_after):
                if msg.role == 'system':
                    if '[CONVERSATION HISTORY]' in msg.content:
                        print(f"   {i+1}. 📚 Conversation summary ({len(msg.content)} chars)")
                    else:
                        print(f"   {i+1}. ⚙️  System prompt")
                elif msg.role == 'user':
                    preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    print(f"   {i+1}. 👤 {preview}")
                elif msg.role == 'assistant':
                    preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                    print(f"   {i+1}. 🤖 {preview}")

            print("   💡 Note: Token count may increase initially due to detailed summary")
            print("       but will decrease significantly as conversation continues")

        except Exception as e:
            print(f"❌ Compaction failed: {e}")

    def handle_facts(self, filename: str = None):
        """Handle /facts [file] command - extract facts from conversation history"""
        messages = self.session.get_messages()

        if len(messages) <= 1:  # Only system message
            print("📝 No conversation history to extract facts from")
            return

        try:
            print("🔍 Extracting facts from conversation history...")

            # Create fact extractor using current provider for consistency
            extractor = BasicExtractor(self.provider)

            # Format conversation history as text
            conversation_text = self._format_conversation_for_extraction(messages)

            if not conversation_text.strip():
                print("📝 No substantive conversation content found")
                return

            print(f"   Processing {len(conversation_text)} characters of conversation...")

            start_time = time.time()

            if filename is None:
                # Display facts as triples in chat
                result = extractor.extract(conversation_text, output_format="triples")

                duration = time.time() - start_time
                print(f"✅ Fact extraction completed in {duration:.1f}s")

                if result and result.get("simple_triples"):
                    print("\n📋 Facts extracted from conversation:")
                    print("=" * 50)
                    for i, triple in enumerate(result["simple_triples"], 1):
                        print(f"{i:2d}. {triple}")
                    print("=" * 50)

                    stats = result.get("statistics", {})
                    entities_count = stats.get("entities_count", 0)
                    relationships_count = stats.get("relationships_count", 0)
                    print(f"📊 Found {entities_count} entities and {relationships_count} relationships")
                else:
                    print("❌ No facts could be extracted from the conversation")

            else:
                # Save as JSON-LD file
                result = extractor.extract(conversation_text, output_format="jsonld")

                duration = time.time() - start_time
                print(f"✅ Fact extraction completed in {duration:.1f}s")

                if result and result.get("@graph"):
                    # Ensure filename has .jsonld extension
                    if not filename.endswith('.jsonld'):
                        filename = f"{filename}.jsonld"

                    import json
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)

                    entities = [item for item in result.get('@graph', []) if item.get('@id', '').startswith('e:')]
                    relationships = [item for item in result.get('@graph', []) if item.get('@id', '').startswith('r:')]

                    print(f"💾 Facts saved to {filename}")
                    print(f"📊 Saved {len(entities)} entities and {len(relationships)} relationships as JSON-LD")
                else:
                    print("❌ No facts could be extracted from the conversation")

        except Exception as e:
            print(f"❌ Fact extraction failed: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

    def handle_judge(self):
        """Handle /judge command - evaluate conversation quality and provide feedback"""
        messages = self.session.get_messages()

        if len(messages) <= 1:  # Only system message
            print("📝 No conversation history to evaluate")
            return

        try:
            print("⚖️  Evaluating conversation quality...")

            # Create judge using current provider for consistency
            judge = BasicJudge(self.provider)

            # Format conversation history as text
            conversation_text = self._format_conversation_for_extraction(messages)

            if not conversation_text.strip():
                print("📝 No substantive conversation content found")
                return

            print(f"   Analyzing {len(conversation_text)} characters of conversation...")

            start_time = time.time()

            # Evaluate the conversation with focus on discussion quality
            from ..processing.basic_judge import JudgmentCriteria
            criteria = JudgmentCriteria(
                is_clear=True,       # How clear is the discussion
                is_coherent=True,    # How well does it flow
                is_actionable=True,  # Does it provide useful insights
                is_relevant=True,    # Is the discussion focused
                is_complete=True,    # Does it address the topics thoroughly
                is_innovative=False, # Not focused on innovation for general chat
                is_working=False,    # Not applicable to conversation
                is_sound=True,       # Are the arguments/explanations sound
                is_simple=True       # Is the communication clear and accessible
            )

            assessment = judge.evaluate(
                content=conversation_text,
                context="conversational discussion quality",
                criteria=criteria
            )

            duration = time.time() - start_time
            print(f"✅ Evaluation completed in {duration:.1f}s")

            # Display judge's summary first (most important)
            judge_summary = assessment.get('judge_summary', '')
            if judge_summary:
                print(f"\n📝 Judge's Assessment:")
                print(f"   {judge_summary}")

            # Source reference
            source_ref = assessment.get('source_reference', '')
            if source_ref:
                print(f"\n📄 Source: {source_ref}")

            # Display assessment in a conversational format
            overall_score = assessment.get('overall_score', 0)
            print(f"\n📊 Overall Discussion Quality: {overall_score}/5")

            # Show key dimension scores
            key_scores = [
                ('clarity_score', 'Clarity'),
                ('coherence_score', 'Coherence'),
                ('actionability_score', 'Actionability'),
                ('relevance_score', 'Relevance'),
                ('completeness_score', 'Completeness'),
                ('soundness_score', 'Soundness'),
                ('simplicity_score', 'Simplicity')
            ]

            print("\n📈 Quality Dimensions:")
            for field, label in key_scores:
                score = assessment.get(field)
                if score is not None:
                    print(f"   {label:13}: {score}/5")

            # Show strengths
            strengths = assessment.get('strengths', [])
            if strengths:
                print(f"\n✅ Conversation Strengths:")
                for strength in strengths[:3]:  # Show top 3
                    print(f"   • {strength}")

            # Show improvement suggestions
            feedback = assessment.get('actionable_feedback', [])
            if feedback:
                print(f"\n💡 Suggestions for Better Discussions:")
                for suggestion in feedback[:3]:  # Show top 3
                    print(f"   • {suggestion}")

            # Show brief reasoning (shortened for chat)
            reasoning = assessment.get('reasoning', '')
            if reasoning:
                # Extract first few sentences of reasoning
                sentences = reasoning.split('. ')
                brief_reasoning = '. '.join(sentences[:2]) + '.' if len(sentences) > 2 else reasoning
                print(f"\n🤔 Assessment Summary:")
                print(f"   {brief_reasoning}")

            print(f"\n📌 Note: This is a demonstrator showing LLM-as-a-judge capabilities for objective assessment.")

        except Exception as e:
            print(f"❌ Conversation evaluation failed: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

    def _format_conversation_for_extraction(self, messages):
        """Format conversation messages for fact extraction"""
        formatted_lines = []

        for msg in messages:
            # Skip system messages for fact extraction
            if msg.role == 'system':
                continue

            content = msg.content.strip()
            if not content:
                continue

            if msg.role == 'user':
                formatted_lines.append(f"User: {content}")
            elif msg.role == 'assistant':
                formatted_lines.append(f"Assistant: {content}")

        return "\n\n".join(formatted_lines)

    def handle_history(self, n_interactions: int = None):
        """Handle /history [n] command - show conversation history verbatim"""
        messages = self.session.get_messages()

        if not messages:
            print("📝 No conversation history")
            return

        # Check for conversation summary (from compaction)
        summary_message = None
        for msg in messages:
            if msg.role == 'system' and '[CONVERSATION HISTORY]' in msg.content:
                summary_message = msg
                break

        # Filter out system messages for interaction counting
        conversation_messages = [msg for msg in messages if msg.role != 'system']

        if not conversation_messages and not summary_message:
            print("📝 No conversation history")
            return

        if n_interactions is None:
            # Show all conversation
            print("📜 Conversation History:\n")
            display_messages = conversation_messages
        else:
            # Show last n interactions (each interaction = user + assistant)
            # Calculate how many messages that represents
            messages_needed = n_interactions * 2  # user + assistant per interaction
            display_messages = conversation_messages[-messages_needed:] if messages_needed <= len(conversation_messages) else conversation_messages
            print(f"📜 Last {n_interactions} interactions:\n")

        # Show conversation summary if it exists (from compaction)
        if summary_message:
            summary_content = summary_message.content.replace('[CONVERSATION HISTORY]: ', '')
            print("📚 Earlier Conversation Summary:")
            print("─" * 50)
            print(summary_content)
            print("─" * 50)
            print()

        # Display the recent messages verbatim without numbers
        if display_messages:
            if summary_message:
                print("💬 Recent Conversation:")
                print()

            for msg in display_messages:
                if msg.role == 'user':
                    print("👤 You:")
                    print(msg.content)
                    print()  # Empty line after user message
                elif msg.role == 'assistant':
                    print("🤖 Assistant:")
                    print(msg.content)
                    print()  # Empty line after assistant message
        elif summary_message:
            print("💡 Only summary available - recent messages were preserved but may have been cleared")

        print(f"📊 Total tokens estimate: ~{self.session.get_token_estimate()}")

    def handle_system_show(self):
        """Show current system prompt - both fixed part and full prompt with tools"""
        # Get the original system prompt (fixed part)
        fixed_prompt = self.session.system_prompt or "No system prompt set"

        print("⚙️  Current System Prompt:")
        print("=" * 50)
        print(f"📝 Fixed Part:\n{fixed_prompt}\n")

        # Show full prompt as it appears to the LLM (including tool descriptions)
        messages = self.session.get_messages()
        system_messages = [msg for msg in messages if msg.role == 'system']

        if system_messages:
            print("🔧 Full Prompt (as seen by LLM):")
            for i, sys_msg in enumerate(system_messages, 1):
                if i == 1:
                    print(f"System Message {i} (Base):")
                else:
                    print(f"System Message {i}:")
                print(f"{sys_msg.content}")
                if i < len(system_messages):
                    print()  # Separator between system messages
        else:
            print("⚠️  No system messages found in session")

        print("=" * 50)

    def handle_system_change(self, new_prompt: str):
        """Change the system prompt (fixed part only, preserves tools)"""
        old_prompt = self.session.system_prompt or "No previous prompt"

        # Update the session's system prompt
        self.session.system_prompt = new_prompt

        # Update the first system message in the session if it exists
        messages = self.session.get_messages()
        for msg in messages:
            if msg.role == 'system' and not msg.content.startswith('[CONVERSATION HISTORY]'):
                # This is the original system message, update it
                msg.content = new_prompt
                break
        else:
            # No existing system message, add one at the beginning
            self.session.messages.insert(0, self.session.add_message('system', new_prompt))

        print("✅ System prompt updated!")
        print(f"📝 Old: {old_prompt[:100]}{'...' if len(old_prompt) > 100 else ''}")
        print(f"📝 New: {new_prompt[:100]}{'...' if len(new_prompt) > 100 else ''}")

    def handle_tooltag_test(self, opening_tag: str, closing_tag: str):
        """Handle /tooltag command - set tool call tags for the session"""
        from ..tools.tag_rewriter import ToolCallTags
        # Disable auto-formatting to use tags exactly as specified by user
        self.session.tool_call_tags = ToolCallTags(opening_tag, closing_tag, auto_format=False)
        print(f"🏷️ Tool call tags set to: {opening_tag}...{closing_tag}")

    def handle_status(self):
        """Handle /status command - show comprehensive system status"""
        print("📊 AbstractLLM CLI Status")
        print("=" * 60)

        # Provider and Model info
        print(f"🔧 Provider: {self.provider_name}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🌊 Streaming: {'Enabled' if self.stream_mode else 'Disabled'}")

        # Debug status - show both CLI and system logging
        print(f"🐛 CLI Debug: {'Enabled' if self.debug_mode else 'Disabled'}")

        # Try to detect system logging level
        try:
            import logging
            logger = logging.getLogger()
            current_level = logger.getEffectiveLevel()
            level_name = logging.getLevelName(current_level)

            # Check if debug messages would be shown
            if current_level <= logging.DEBUG:
                system_debug = "Enabled (DEBUG level)"
            elif current_level <= logging.INFO:
                system_debug = "Info level"
            else:
                system_debug = "Warning+ only"

            print(f"📊 System Logging: {system_debug}")
        except:
            print(f"📊 System Logging: Unknown")

        # Token usage
        current_tokens = self.session.get_token_estimate()
        print(f"💾 Token Usage: {current_tokens:,} / {self.max_tokens:,} tokens ({(current_tokens/self.max_tokens*100):.1f}%)")

        # Model capabilities
        try:
            from ..architectures.detection import get_model_capabilities
            capabilities = get_model_capabilities(self.model_name)

            print("\n🎯 Model Capabilities:")
            print(f"   Max Input Tokens: {capabilities.get('max_tokens', 'Unknown'):,}")
            print(f"   Max Output Tokens: {capabilities.get('max_output_tokens', 'Unknown'):,}")
            print(f"   Tool Support: {capabilities.get('tool_support', 'Unknown')}")
            print(f"   Structured Output: {capabilities.get('structured_output', 'Unknown')}")
            print(f"   Vision Support: {'Yes' if capabilities.get('vision_support', False) else 'No'}")
            print(f"   Audio Support: {'Yes' if capabilities.get('audio_support', False) else 'No'}")
            print(f"   Thinking Support: {'Yes' if capabilities.get('thinking_support', False) else 'No'}")

            # Show aliases if any
            aliases = capabilities.get('aliases', [])
            if aliases:
                print(f"   Model Aliases: {', '.join(aliases)}")

        except Exception as e:
            print(f"\n⚠️ Could not retrieve model capabilities: {e}")

        # Available tools
        print("\n🛠️ Available Tools:")
        tools = ["list_files", "read_file", "write_file", "execute_command"]
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {tool}")

        # Session info
        messages = self.session.get_messages()
        conversation_messages = [msg for msg in messages if msg.role != 'system']
        interactions = len(conversation_messages) // 2  # user + assistant = 1 interaction

        print(f"\n📝 Session Info:")
        print(f"   Total Messages: {len(messages)}")
        print(f"   Interactions: {interactions}")
        print(f"   System Prompt: {'Set' if self.session.system_prompt else 'Default'}")

        # Check for compaction
        has_summary = any(msg.role == 'system' and '[CONVERSATION HISTORY]' in msg.content for msg in messages)
        if has_summary:
            print(f"   History: Compacted (summary available)")
        else:
            print(f"   History: Full conversation")

        print("=" * 60)

    def generate_response(self, user_input: str):
        """Generate and display response with tool execution."""
        start_time = time.time()

        try:
            if self.debug_mode:
                print(f"🔍 Sending to {self.provider_name}:{self.model_name}")

            # Pass tool_call_tags if set
            kwargs = {}
            if hasattr(self.session, 'tool_call_tags') and self.session.tool_call_tags:
                kwargs['tool_call_tags'] = self.session.tool_call_tags

            response = self.session.generate(user_input, stream=self.stream_mode, **kwargs)

            if self.stream_mode:
                print("🤖 Assistant: ", end="", flush=True)
                full_content = ""
                for chunk in response:
                    if hasattr(chunk, 'content') and chunk.content:
                        print(chunk.content, end="", flush=True)
                        full_content += chunk.content
                print()  # New line

                # After streaming is complete, check for and execute tool calls
                self._execute_tool_calls_if_present(full_content)
            else:
                print(f"🤖 Assistant: {response.content}")
                # For non-streaming, execute tool calls immediately
                self._execute_tool_calls_if_present(response.content)

            if self.debug_mode:
                latency = (time.time() - start_time) * 1000
                print(f"⏱️ Response in {latency:.0f}ms")

        except KeyboardInterrupt:
            print("\n⏸️ Interrupted")
        except Exception as e:
            print(f"❌ Error: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()

    def _execute_tool_calls_if_present(self, content: str):
        """Parse and execute tool calls from response content."""
        import re
        import json

        if not content:
            return

        # Parse qwen3-style tool calls: <|tool_call|>{"name": "...", "arguments": {...}}</|tool_call|>
        tool_pattern = r'<\|tool_call\|>(.*?)</\|tool_call\|>'
        tool_matches = re.findall(tool_pattern, content, re.DOTALL)

        if not tool_matches:
            return

        print("\n🔧 Tool Results:")

        # Available tools mapping
        available_tools = {
            "list_files": list_files,
            "read_file": read_file,
            "write_file": write_file,
            "execute_command": execute_command
        }

        for tool_json in tool_matches:
            try:
                # Parse tool call JSON
                tool_data = json.loads(tool_json.strip())
                tool_name = tool_data.get("name")
                tool_args = tool_data.get("arguments", {})

                if tool_name not in available_tools:
                    print(f"❌ Unknown tool: {tool_name}")
                    continue

                # Display tool call for transparency
                args_str = str(tool_args) if tool_args else "{}"
                if len(args_str) > 100:
                    args_str = args_str[:97] + "..."
                print(f"**{tool_name}({args_str})**")

                # Execute the tool
                tool_function = available_tools[tool_name]

                if tool_args:
                    result = tool_function(**tool_args)
                else:
                    result = tool_function()

                print(f"✅ {result}")

            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse tool call JSON: {e}")
                print(f"   Raw content: {tool_json[:100]}...")
            except Exception as e:
                print(f"❌ Tool execution failed: {e}")
                if self.debug_mode:
                    import traceback
                    traceback.print_exc()

    def run_interactive(self):
        """Run the interactive REPL."""
        try:
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    if not user_input:
                        continue

                    # Handle commands
                    if self.handle_command(user_input):
                        continue

                    # Generate response
                    self.generate_response(user_input)

                except KeyboardInterrupt:
                    print("\n\n👋 Use /quit to exit.")
                    continue
                except EOFError:
                    print("\n👋 Goodbye!")
                    break

        except Exception as e:
            print(f"❌ Fatal error: {e}")

    def run_single_prompt(self, prompt: str):
        """Execute single prompt and exit."""
        try:
            response = self.session.generate(prompt, stream=False)
            print(response.content)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Simplified CLI REPL for AbstractLLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m abstractllm.utils.cli --provider ollama --model qwen3-coder:30b
  python -m abstractllm.utils.cli --provider openai --model gpt-4o-mini --stream
  python -m abstractllm.utils.cli --provider anthropic --model claude-3-5-haiku-20241022
  python -m abstractllm.utils.cli --provider ollama --model qwen3-coder:30b --prompt "What is Python?"

Commands:
  /help - Show help
  /quit - Exit
  /clear - Clear history
  /stream - Toggle streaming
  /debug - Toggle CLI debug mode (timing, auto-detection)
  /status - Show current status (provider, model, capabilities, tokens)
  /history [n] - Show conversation history or last n interactions
  /model <provider:model> - Change model
  /compact - Compact chat history using gemma3:1b-it-qat
  /facts [file] - Extract facts from conversation history
  /judge - Evaluate conversation quality and provide feedback
  /system [prompt] - Show or change system prompt

Tools: list_files, read_file, write_file, execute_command

Note: This is a basic demonstrator with limited capabilities. For production
use cases requiring advanced reasoning, ReAct patterns, or complex tool chains,
build custom solutions using the AbstractCore framework directly.
        """
    )

    # Required arguments
    parser.add_argument('--provider', required=True,
                       choices=['openai', 'anthropic', 'ollama', 'huggingface', 'mlx', 'lmstudio'],
                       help='LLM provider to use')
    parser.add_argument('--model', required=True, help='Model name to use')

    # Optional arguments
    parser.add_argument('--stream', action='store_true', help='Enable streaming mode')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--max-tokens', type=int, default=None, help='Maximum tokens (default: auto-detect from model capabilities)')
    parser.add_argument('--prompt', help='Execute single prompt and exit')

    # Provider-specific
    parser.add_argument('--base-url', help='Base URL (ollama, lmstudio)')
    parser.add_argument('--api-key', help='API key')
    parser.add_argument('--temperature', type=float, default=0.7, help='Temperature (default: 0.7)')

    args = parser.parse_args()

    # Build kwargs
    kwargs = {'temperature': args.temperature}
    if args.base_url:
        kwargs['base_url'] = args.base_url
    if args.api_key:
        kwargs['api_key'] = args.api_key

    # Create CLI
    cli = SimpleCLI(
        provider=args.provider,
        model=args.model,
        stream=args.stream,
        max_tokens=args.max_tokens,
        debug=args.debug,
        **kwargs
    )

    # Run
    if args.prompt:
        cli.run_single_prompt(args.prompt)
    else:
        cli.run_interactive()


if __name__ == "__main__":
    main()