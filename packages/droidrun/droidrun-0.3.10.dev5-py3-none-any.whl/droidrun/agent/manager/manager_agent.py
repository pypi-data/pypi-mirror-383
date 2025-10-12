"""
ManagerAgent - Planning and reasoning workflow.

This agent is responsible for:
- Analyzing the current state
- Creating plans and subgoals
- Tracking progress
- Deciding when tasks are complete
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from llama_index.core.llms.llm import LLM
from llama_index.core.workflow import Context, StartEvent, StopEvent, Workflow, step

from droidrun.agent.manager.events import ManagerInternalPlanEvent, ManagerThinkingEvent
from droidrun.agent.manager.prompts import parse_manager_response
from droidrun.agent.utils import convert_messages_to_chatmessages
from droidrun.agent.utils.chat_utils import remove_empty_messages
from droidrun.agent.utils.device_state_formatter import format_device_state
from droidrun.agent.utils.inference import acall_with_retries
from droidrun.agent.utils.tools import build_custom_tool_descriptions
from droidrun.config_manager.prompt_loader import PromptLoader
from droidrun.config_manager.app_card_loader import AppCardLoader

if TYPE_CHECKING:
    from droidrun.agent.droid.events import DroidAgentState
    from droidrun.tools import Tools
    from droidrun.config_manager.config_manager import AgentConfig


logger = logging.getLogger("droidrun")


class ManagerAgent(Workflow):
    """
    Planning and reasoning agent that decides what to do next.

    The Manager:
    1. Analyzes current device state and action history
    2. Creates plans with specific subgoals
    3. Tracks progress and completed steps
    4. Decides when tasks are complete or need to provide answers
    """

    def __init__(
        self,
        llm: LLM,
        tools_instance: "Tools",
        shared_state: "DroidAgentState",
        agent_config: "AgentConfig",
        custom_tools: dict = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.llm = llm
        self.config = agent_config.manager
        self.vision = self.config.vision
        self.tools_instance = tools_instance
        self.shared_state = shared_state
        self.custom_tools = custom_tools or {}
        self.agent_config = agent_config
        self.app_card_loader = self.agent_config.app_cards

        logger.info("✅ ManagerAgent initialized successfully.")

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _build_system_prompt(
        self,
        has_text_to_modify: bool,
        app_card: str = ""
    ) -> str:
        """
        Build system prompt with all context.

        Args:
            has_text_to_modify: Whether text manipulation mode is enabled
            app_card: App card content
        Returns:
            Complete system prompt
        """
        # Format error history
        error_history_text = ""
        if self.shared_state.error_flag_plan:
            k = self.shared_state.err_to_manager_thresh
            errors = [
                {
                    "action": act,
                    "summary": summ,
                    "error": err_des
                }
                for act, summ, err_des in zip(
                    self.shared_state.action_history[-k:],
                    self.shared_state.summary_history[-k:],
                    self.shared_state.error_descriptions[-k:], strict=True
                )
            ]
            error_history_text = (
                "<potentially_stuck>\n"
                "You have encountered several failed attempts. Here are some logs:\n"
            )
            for error in errors:
                error_history_text += (
                    f"- Attempt: Action: {error['action']} | "
                    f"Description: {error['summary']} | "
                    f"Outcome: Failed | "
                    f"Feedback: {error['error']}\n"
                )
            error_history_text += "</potentially_stuck>\n\n"

        # Text manipulation section
        text_manipulation_section = ""
        if has_text_to_modify:
            text_manipulation_section = """

<text_manipulation>
1. Use **TEXT_TASK:** prefix in your plan when you need to modify text in the currently focused text input field
2. TEXT_TASK is for editing, formatting, or transforming existing text content in text boxes using Python code
3. Do not use TEXT_TASK for extracting text from messages, typing new text, or composing messages
4. The focused text field contains editable text that you can modify
5. Example plan item: 'TEXT_TASK: Add "Hello World" at the beginning of the text'
6. Always use TEXT_TASK for modifying text, do not try to select the text to copy/cut/paste or adjust the text
</text_manipulation>"""

        # Device date (include tags in variable value or empty string)
        device_date = self.tools_instance.get_date()
        device_date_text = ""
        if device_date.strip():
            device_date_text = f"<device_date>\n{device_date}\n</device_date>\n\n"

        # App card (include tags in variable value or empty string)
        app_card = app_card
        app_card_text = ""
        if app_card.strip():
            app_card_text = "App card gives information on how to operate the app and perform actions.\n<app_card>\n" + app_card.strip() + "\n</app_card>\n\n"

        # Important notes (include tags in variable value or empty string)
        important_notes = ""  # TODO: implement
        important_notes_text = ""
        if important_notes.strip():
            important_notes_text = "<important_notes>\n" + important_notes + "\n</important_notes>\n\n"

        # Custom tools
        custom_tools_desc = build_custom_tool_descriptions(self.custom_tools)
        custom_tools_text = ""
        if custom_tools_desc.strip():
            custom_tools_text = """

<custom_actions>
The executor has access to these additional custom actions beyond the standard actions (click, type, swipe, etc.):
""" + custom_tools_desc + """

You can reference these custom actions or tell the Executer agent to use them in your plan when they help achieve the user's goal.
</custom_actions>"""

        # Load and format prompt
        return PromptLoader.load_prompt(
            self.agent_config.get_manager_system_prompt_path(),
            {
                "instruction": self.shared_state.instruction,
                "device_date": device_date_text,
                "app_card": app_card_text,
                "important_notes": important_notes_text,
                "error_history": error_history_text,
                "text_manipulation_section": text_manipulation_section,
                "custom_tools_descriptions": custom_tools_text
            }
        )

    def _build_messages_with_context(
        self,
        system_prompt: str,
        screenshot: str = None
    ) -> list[dict]:
        """
        Build messages from history and inject current context.

        Args:
            system_prompt: System prompt to use
            screenshot: Path to current screenshot (if vision enabled)

        Returns:
            List of message dicts ready for conversion
        """
        import copy

        # Start with system message
        messages = [
            {"role": "system", "content": [{"text": system_prompt}]}
        ]

        # Add accumulated message history (deep copy to avoid mutation)
        messages.extend(copy.deepcopy(self.shared_state.message_history))

        # ====================================================================
        # Inject memory, device state, screenshot to LAST user message
        # ====================================================================
        # Find last user message index
        user_indices = [i for i, msg in enumerate(messages) if msg['role'] == 'user']

        if user_indices:
            last_user_idx = user_indices[-1]

            # Add memory to last user message
            current_memory = (self.shared_state.memory or "").strip()
            if current_memory:
                if messages[last_user_idx]['content'] and 'text' in messages[last_user_idx]['content'][0]:
                    messages[last_user_idx]['content'][0]['text'] += f"\n<memory>\n{current_memory}\n</memory>\n"
                else:
                    messages[last_user_idx]['content'].insert(0, {"text": f"<memory>\n{current_memory}\n</memory>\n"})

            # Add CURRENT device state to last user message (use unified state)
            current_state = self.shared_state.formatted_device_state.strip()
            if current_state:
                if messages[last_user_idx]['content'] and 'text' in messages[last_user_idx]['content'][0]:
                    messages[last_user_idx]['content'][0]['text'] += f"\n<device_state>\n{current_state}\n</device_state>\n"
                else:
                    messages[last_user_idx]['content'].insert(0, {"text": f"<device_state>\n{current_state}\n</device_state>\n"})

            # Add screenshot to last user message
            if screenshot and self.vision:
                messages[last_user_idx]['content'].append({"image": screenshot})

            # Add PREVIOUS device state to SECOND-TO-LAST user message (if exists)
            if len(user_indices) >= 2:
                second_last_user_idx = user_indices[-2]
                prev_state = self.shared_state.previous_formatted_device_state.strip()

                if prev_state:
                    if messages[second_last_user_idx]['content'] and 'text' in messages[second_last_user_idx]['content'][0]:
                        messages[second_last_user_idx]['content'][0]['text'] += f"\n<device_state>\n{prev_state}\n</device_state>\n"
                    else:
                        messages[second_last_user_idx]['content'].insert(0, {"text": f"<device_state>\n{prev_state}\n</device_state>\n"})
        messages = remove_empty_messages(messages)
        return messages

    async def _validate_and_retry_llm_call(
        self,
        ctx: Context,
        initial_messages: list[dict],
        initial_response: str
    ) -> str:
        """
        Validate LLM response and retry if needed.

        Args:
            ctx: Workflow context
            initial_messages: Messages sent to LLM
            initial_response: Initial LLM response

        Returns:
            Final validated response (may be same as initial or from retry)
        """

        output_planning = initial_response
        parsed = parse_manager_response(output_planning)

        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            # Validation rules
            error_message = None

            if parsed["answer"] and not parsed["plan"]:
                # Valid: answer without plan (task complete)
                break
            elif parsed["plan"] and parsed["answer"]:
                error_message = "You cannot use both request_accomplished tag while the plan is not finished. If you want to use request_accomplished tag, please make sure the plan is finished.\nRetry again."
            elif not parsed["plan"]:
                error_message = "You must provide a plan to complete the task. Please provide a plan with the correct format."
            else:
                # Valid: plan without answer
                break

            if error_message:
                retry_count += 1
                logger.warning(f"Manager response invalid (retry {retry_count}/{max_retries}): {error_message}")

                # Retry with error message
                retry_messages = initial_messages + [
                    {"role": "assistant", "content": [{"text": output_planning}]},
                    {"role": "user", "content": [{"text": error_message}]}
                ]

                chat_messages = convert_messages_to_chatmessages(retry_messages)

                try:
                    response = await acall_with_retries(self.llm, chat_messages)
                    output_planning = response.message.content
                    parsed = parse_manager_response(output_planning)
                except Exception as e:
                    logger.error(f"LLM retry failed: {e}")
                    break  # Give up retrying

        return output_planning

    # ========================================================================
    # Workflow Steps
    # ========================================================================

    @step
    async def prepare_input(
        self,
        ctx: Context,
        ev: StartEvent
    ) -> ManagerThinkingEvent:
        """
        Gather context and prepare manager prompt.

        This step:
        1. Gets current device state (UI elements, screenshot)
        2. Detects text manipulation mode
        3. Builds message history entry with last action
        4. Stores context for think() step
        """
        logger.info("💬 Preparing manager input...")

        # ====================================================================
        # Step 1: Get and format device state using unified formatter
        # ====================================================================
        raw_state = self.tools_instance.get_state()
        formatted_text, focused_text, a11y_tree, phone_state = format_device_state(raw_state)

        # Update shared state (previous ← current, current ← new)
        self.shared_state.previous_formatted_device_state = self.shared_state.formatted_device_state
        self.shared_state.formatted_device_state = formatted_text
        self.shared_state.focused_text = focused_text
        self.shared_state.a11y_tree = a11y_tree
        self.shared_state.phone_state = phone_state

        # Extract and store package/app name
        self.shared_state.current_package_name = phone_state.get('packageName', 'Unknown')
        self.shared_state.current_app_name = phone_state.get('currentApp', 'Unknown')

        # App cards

        # ====================================================================
        # Step 2: Capture screenshot if vision enabled
        # ====================================================================
        screenshot = None
        if self.vision:
            try:
                result = self.tools_instance.take_screenshot()
                if isinstance(result, tuple):
                    success, screenshot = result
                    if not success:
                        screenshot = None

                else:
                    screenshot = result
                logger.debug("📸 Screenshot captured for Manager")
            except Exception as e:
                logger.warning(f"Failed to capture screenshot: {e}")
                screenshot = None

        # ====================================================================
        # Step 3: Detect text manipulation mode
        # ====================================================================
        focused_text_clean = focused_text.replace("'", "").strip()
        has_text_to_modify = (focused_text_clean != "")

        # ====================================================================
        # Step 5: Build user message entry
        # ====================================================================
        parts = []

        # Add context from last action
        if self.shared_state.finish_thought:
            parts.append(f"<thought>\n{self.shared_state.finish_thought}\n</thought>\n")

        if self.shared_state.last_action:
            import json
            action_str = json.dumps(self.shared_state.last_action)
            parts.append(f"<last_action>\n{action_str}\n</last_action>\n")

        if self.shared_state.last_summary:
            parts.append(f"<last_action_description>\n{self.shared_state.last_summary}\n</last_action_description>\n")


        self.shared_state.message_history.append({
            "role": "user",
            "content": [{"text": "".join(parts)}]
        })

        # Store has_text_to_modify and screenshot for next step
        self.shared_state.has_text_to_modify = has_text_to_modify
        self.shared_state.screenshot = screenshot

        logger.debug(f"  - Device state prepared (text_modify={has_text_to_modify}, screenshot={screenshot is not None})")
        return ManagerThinkingEvent()

    @step
    async def think(
        self,
        ctx: Context,
        ev: ManagerThinkingEvent
    ) -> ManagerInternalPlanEvent:
        """
        Manager reasons and creates plan.

        This step:
        1. Builds system prompt with all context
        2. Builds messages from history with injected context
        3. Calls LLM
        4. Validates and retries if needed
        5. Parses response
        6. Updates state (memory, message history)
        """
        logger.info("🧠 Manager thinking about the plan...")

        has_text_to_modify = self.shared_state.has_text_to_modify
        screenshot = self.shared_state.screenshot
        if self.app_card_loader.enabled:
            app_card = AppCardLoader.load_app_card(self.shared_state.current_package_name, self.app_card_loader.app_cards_dir)
        else:
            app_card = ""

        # ====================================================================
        # Step 1: Build system prompt
        # ====================================================================
        system_prompt = self._build_system_prompt(has_text_to_modify, app_card)

        # ====================================================================
        # Step 2: Build messages with context
        # ====================================================================
        messages = self._build_messages_with_context(
            system_prompt=system_prompt,
            screenshot=screenshot
        )

        # ====================================================================
        # Step 3: Convert messages and call LLM
        # ====================================================================
        chat_messages = convert_messages_to_chatmessages(messages)

        try:
            response = await acall_with_retries(self.llm, chat_messages)
            output_planning = response.message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError(f"Error calling LLM in manager: {e}") from e

        # ====================================================================
        # Step 4: Validate and retry if needed
        # ====================================================================
        output_planning = await self._validate_and_retry_llm_call(
            ctx=ctx,
            initial_messages=messages,
            initial_response=output_planning
        )

        # ====================================================================
        # Step 5: Parse response
        # ====================================================================
        parsed = parse_manager_response(output_planning)

        # ====================================================================
        # Step 6: Update state
        # ====================================================================
        memory_update = parsed.get("memory", "").strip()

        # Update memory (append, not replace)
        if memory_update:
            if self.shared_state.memory:
                self.shared_state.memory += "\n" + memory_update
            else:
                self.shared_state.memory = memory_update

        # Append assistant response to message history
        self.shared_state.message_history.append({
            "role": "assistant",
            "content": [{"text": output_planning}]
        })

        # Update planning fields
        self.shared_state.plan = parsed["plan"]
        self.shared_state.current_subgoal = parsed["current_subgoal"]
        self.shared_state.finish_thought = parsed["thought"]
        self.shared_state.manager_answer = parsed["answer"]

        logger.info(f"📝 Plan: {parsed['plan'][:100]}...")
        logger.debug(f"  - Current subgoal: {parsed['current_subgoal']}")
        logger.debug(f"  - Manager answer: {parsed['answer'][:50] if parsed['answer'] else 'None'}")

        event = ManagerInternalPlanEvent(
            plan=parsed["plan"],
            current_subgoal=parsed["current_subgoal"],
            thought=parsed["thought"],
            manager_answer=parsed["answer"],
            memory_update=memory_update
        )

        # Write event to stream for web interface
        ctx.write_event_to_stream(event)

        return event

    @step
    async def finalize(
        self,
        ctx: Context,
        ev: ManagerInternalPlanEvent
    ) -> StopEvent:
        """Return manager results to parent workflow."""
        logger.debug("✅ Manager planning complete")

        return StopEvent(result={
            "plan": ev.plan,
            "current_subgoal": ev.current_subgoal,
            "thought": ev.thought,
            "manager_answer": ev.manager_answer,
            "memory_update": ev.memory_update
        })
