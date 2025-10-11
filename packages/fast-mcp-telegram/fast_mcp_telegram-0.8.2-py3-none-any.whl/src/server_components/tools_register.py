from typing import Literal

from fastmcp import FastMCP

from src.server_components import auth as server_auth
from src.server_components import bot_restrictions
from src.server_components import errors as server_errors
from src.tools.contacts import find_chats_impl, get_chat_info_impl
from src.tools.messages import (
    edit_message_impl,
    read_messages_by_ids,
    send_message_impl,
    send_message_to_phone_impl,
)
from src.tools.mtproto import invoke_mtproto_impl
from src.tools.search import search_messages_impl


def mcp_tool_with_restrictions(operation_name: str):
    """
    Combined decorator for MCP tools that applies error handling, auth context, and bot restrictions.

    This reduces repetition of the three common decorators:
    - @server_errors.with_error_handling
    - @server_auth.with_auth_context
    - @bot_restrictions.restrict_non_bridge_for_bot_sessions

    Args:
        operation_name: Name of the operation for error reporting and bot restrictions
    """

    def decorator(func):
        # Apply the three decorators in the correct order
        decorated_func = server_errors.with_error_handling(operation_name)(func)
        decorated_func = server_auth.with_auth_context(decorated_func)
        return bot_restrictions.restrict_non_bridge_for_bot_sessions(operation_name)(
            decorated_func
        )

    return decorator


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    @mcp_tool_with_restrictions("search_messages_globally")
    async def search_messages_globally(
        query: str,
        limit: int = 50,
        min_date: str | None = None,
        max_date: str | None = None,
        chat_type: Literal["private", "group", "channel"] | None = None,
        auto_expand_batches: int = 2,
        include_total_count: bool = False,
    ):
        """
        Search messages across all Telegram chats (global search).

        FEATURES:
        - Multiple queries: "term1, term2, term3"
        - Date filtering: ISO format (min_date="2024-01-01")
        - Chat type filter: "private", "group", "channel"

        EXAMPLES:
        search_messages_globally(query="deadline", limit=20)  # Global search
        search_messages_globally(query="project, launch", limit=30)  # Multi-term search
        search_messages_globally(query="proj", limit=20)  # Partial word search

        Args:
            query: Search terms (comma-separated). Required for global search.
            limit: Max results (recommended: ≤50)
            chat_type: Filter by chat type ("private"/"group"/"channel")
            min_date: Min date filter (ISO format: "2024-01-01")
            max_date: Max date filter (ISO format: "2024-12-31")
            auto_expand_batches: Extra result batches for filtered searches
            include_total_count: Include total matching messages count (ignored in global mode)
        """
        return await search_messages_impl(
            query=query,
            chat_id=None,
            limit=limit,
            min_date=min_date,
            max_date=max_date,
            chat_type=chat_type,
            auto_expand_batches=auto_expand_batches,
            include_total_count=include_total_count,
        )

    @mcp.tool()
    @mcp_tool_with_restrictions("search_messages_in_chat")
    async def search_messages_in_chat(
        chat_id: str,
        query: str | None = None,
        limit: int = 50,
        min_date: str | None = None,
        max_date: str | None = None,
        auto_expand_batches: int = 2,
        include_total_count: bool = False,
    ):
        """
        Search messages within a specific Telegram chat.

        FEATURES:
        - Multiple queries: "term1, term2, term3"
        - Date filtering: ISO format (min_date="2024-01-01")
        - Total count support for per-chat searches
        - No query = returns latest messages from the chat

        EXAMPLES:
        search_messages_in_chat(chat_id="me", limit=10)      # Saved Messages
        search_messages_in_chat(chat_id="-1001234567890", query="launch")  # Specific chat
        search_messages_in_chat(chat_id="telegram", query="update, news")  # Multi-term search

        Args:
            chat_id: Target chat ID ('me' for Saved Messages) or specific chat
            query: Optional search terms (comma-separated). If omitted, returns latest messages.
            limit: Max results (recommended: ≤50)
            min_date: Min date filter (ISO format: "2024-01-01")
            max_date: Max date filter (ISO format: "2024-12-31")
            auto_expand_batches: Extra result batches for filtered searches
            include_total_count: Include total matching messages count (per-chat only)
        """
        return await search_messages_impl(
            query=query,
            chat_id=chat_id,
            limit=limit,
            min_date=min_date,
            max_date=max_date,
            chat_type=None,
            auto_expand_batches=auto_expand_batches,
            include_total_count=include_total_count,
        )

    @mcp.tool()
    @mcp_tool_with_restrictions("send_message")
    async def send_message(
        chat_id: str,
        message: str,
        reply_to_msg_id: int | None = None,
        parse_mode: Literal["markdown", "html"] | None = None,
        files: str | list[str] | None = None,
    ):
        """
        Send new message in Telegram chat, optionally with files.

        FORMATTING:
        - parse_mode=None: Plain text
        - parse_mode="markdown": *bold*, _italic_, [link](url), `code`
        - parse_mode="html": <b>bold</b>, <i>italic</i>, <a href="url">link</a>, <code>code</code>

        FILE SENDING:
        - files: Single file or list of files (URLs or local paths)
        - URLs work in all modes (http:// or https://)
        - Local file paths only work in stdio mode
        - Supports images, videos, documents, audio, and other file types
        - When files are provided, message becomes the caption

        EXAMPLES:
        send_message(chat_id="me", message="Hello!")  # Send text to Saved Messages
        send_message(chat_id="-1001234567890", message="New message", reply_to_msg_id=12345)  # Reply
        send_message(chat_id="me", message="Check this", files="https://example.com/doc.pdf")  # Send file from URL
        send_message(chat_id="me", message="Photos", files=["https://ex.com/1.jpg", "https://ex.com/2.jpg"])  # Multiple files
        send_message(chat_id="me", message="Report", files="/path/to/file.pdf")  # Local file (stdio mode only)

        Args:
            chat_id: Target chat ID ('me' for Saved Messages, numeric ID, or username)
            message: Message text to send (becomes caption when files are provided)
            reply_to_msg_id: Reply to specific message ID (optional)
            parse_mode: Text formatting ("markdown", "html", or None)
            files: Single file or list of files to send (URLs or local paths, optional)
        """
        return await send_message_impl(
            chat_id, message, reply_to_msg_id, parse_mode, files
        )

    @mcp.tool()
    @mcp_tool_with_restrictions("edit_message")
    async def edit_message(
        chat_id: str,
        message_id: int,
        message: str,
        parse_mode: Literal["markdown", "html"] | None = None,
    ):
        """
        Edit existing message in Telegram chat.

        FORMATTING:
        - parse_mode=None: Plain text
        - parse_mode="markdown": *bold*, _italic_, [link](url), `code`
        - parse_mode="html": <b>bold</b>, <i>italic</i>, <a href="url">link</a>, <code>code</code>

        EXAMPLES:
        edit_message(chat_id="me", message_id=12345, message="Updated text")  # Edit Saved Messages
        edit_message(chat_id="-1001234567890", message_id=67890, message="*Updated* message")  # Edit with formatting

        Args:
            chat_id: Target chat ID ('me' for Saved Messages, numeric ID, or username)
            message_id: Message ID to edit (required)
            message: New message text
            parse_mode: Text formatting ("markdown", "html", or None)
        """
        return await edit_message_impl(chat_id, message_id, message, parse_mode)

    @mcp.tool()
    @mcp_tool_with_restrictions("read_messages")
    async def read_messages(chat_id: str, message_ids: list[int]):
        """
        Read specific messages by their IDs from a Telegram chat.

        SUPPORTED CHAT FORMATS:
        - 'me': Saved Messages
        - Numeric ID: User/chat ID (e.g., 133526395)
        - Username: @channel_name or @username
        - Channel ID: -100xxxxxxxxx

        USAGE:
        - First use search_messages_globally() or search_messages_in_chat() to find message IDs
        - Then read specific messages using those IDs
        - Returns full message content with metadata

        EXAMPLES:
        read_messages(chat_id="me", message_ids=[680204, 680205])  # Saved Messages
        read_messages(chat_id="-1001234567890", message_ids=[123, 124])  # Channel

        Args:
            chat_id: Target chat identifier (use 'me' for Saved Messages)
            message_ids: List of message IDs to retrieve (from search results)
        """
        return await read_messages_by_ids(chat_id, message_ids)

    @mcp.tool()
    @mcp_tool_with_restrictions("find_chats")
    async def find_chats(
        query: str,
        limit: int = 20,
        chat_type: Literal["private", "group", "channel"] | None = None,
    ):
        """
        Find Telegram chats (users, groups, channels) by name, username, or phone number.

        SEARCH SCOPE:
        - Your saved contacts
        - Global Telegram users
        - Public channels and groups

        QUERY TYPES:
        - Name: "John Doe" or "Иванов"
        - Username: "@username" (without @)
        - Phone: "+1234567890"

        MULTI-TERM QUERIES:
        - Comma-separated terms are supported: "john, @telegram, +123"
        - Each term is searched independently, then results are merged and deduplicated by chat_id
        - The final list is truncated to the requested limit

        WORKFLOW:
        1. Find chat: find_chats("John Doe")
        2. Get chat_id from results
        3. Search messages: search_messages_in_chat(chat_id=chat_id, query="topic")

        EXAMPLES:
        find_chats("@telegram")      # Find user by username
        find_chats("John Smith")     # Find by name
        find_chats("+1234567890")    # Find by phone

        Args:
            query: Search term(s). Supports comma-separated multi-queries.
            limit: Max results (default: 20, recommended: ≤50)
            chat_type: Optional filter ("private"|"group"|"channel")
        """
        return await find_chats_impl(query, limit, chat_type)

    @mcp.tool()
    @mcp_tool_with_restrictions("get_chat_info")
    async def get_chat_info(chat_id: str):
        """
        Get detailed profile information for a specific Telegram user or chat.

        USE CASES:
        - Get full user profile after finding chat_id
        - Retrieve contact details, bio, status and subscribers count
        - Check if user is online/bot/channel

        SUPPORTED FORMATS:
        - Numeric user ID: 133526395
        - Username: "telegram" (without @)
        - Channel ID: -100xxxxxxxxx

        EXAMPLES:
        get_chat_info("133526395")      # User by ID
        get_chat_info("telegram")       # User by username
        get_chat_info("-1001234567890") # Channel by ID

        Args:
            chat_id: Target chat/user identifier (numeric ID, username, or channel ID)
        """
        return await get_chat_info_impl(chat_id)

    @mcp.tool()
    @mcp_tool_with_restrictions("send_message_to_phone")
    async def send_message_to_phone(
        phone_number: str,
        message: str,
        first_name: str = "Contact",
        last_name: str = "Name",
        remove_if_new: bool = False,
        reply_to_msg_id: int | None = None,
        parse_mode: Literal["markdown", "html"] | None = None,
        files: str | list[str] | None = None,
    ):
        """
        Send message to phone number, auto-managing Telegram contacts, optionally with files.

        FEATURES:
        - Auto-creates contact if phone not in contacts
        - Sends message immediately after contact creation
        - Optional contact cleanup after sending
        - Full message formatting support
        - File sending support (URLs or local paths)

        CONTACT MANAGEMENT:
        - Checks existing contacts first
        - Creates temporary contact only if needed
        - Removes temporary contact if remove_if_new=True

        FILE SENDING:
        - files: Single file or list of files (URLs or local paths)
        - URLs work in all modes (http:// or https://)
        - Local file paths only work in stdio mode
        - Supports images, videos, documents, audio, and other file types
        - When files are provided, message becomes the caption

        REQUIREMENTS:
        - Phone number must be registered on Telegram
        - Include country code: "+1234567890"

        EXAMPLES:
        send_message_to_phone("+1234567890", "Hello from Telegram!")  # Basic send
        send_message_to_phone("+1234567890", "*Important*", remove_if_new=True)  # Auto cleanup
        send_message_to_phone("+1234567890", "Check this", files="https://example.com/doc.pdf")  # Send with file

        Args:
            phone_number: Target phone number with country code (e.g., "+1234567890")
            message: Message text to send (becomes caption when files are provided)
            first_name: Contact first name (for new contacts only)
            last_name: Contact last name (for new contacts only)
            remove_if_new: Remove contact after sending if newly created
            reply_to_msg_id: Reply to specific message ID
            parse_mode: Text formatting ("markdown", "html", or None)
            files: Single file or list of files to send (URLs or local paths, optional)

        Returns:
            Message send result + contact management info (contact_was_new, contact_removed)
        """
        return await send_message_to_phone_impl(
            phone_number=phone_number,
            message=message,
            first_name=first_name,
            last_name=last_name,
            remove_if_new=remove_if_new,
            reply_to_msg_id=reply_to_msg_id,
            parse_mode=parse_mode,
            files=files,
        )

    @mcp.tool()
    @server_errors.with_error_handling("invoke_mtproto")
    @server_auth.with_auth_context
    async def invoke_mtproto(
        method_full_name: str,
        params_json: str,
        allow_dangerous: bool = False,
        resolve: bool = True,
    ):
        """
        Execute low-level Telegram MTProto API methods directly.

        USE CASES:
        - Access advanced Telegram API features
        - Custom queries not covered by standard tools
        - Administrative operations

        METHOD FORMAT:
        - Full class name: "messages.GetHistory", "users.GetFullUser"
        - Telegram API method names with proper casing (case-insensitive)
        - Methods are automatically normalized to correct format

        PARAMETERS:
        - JSON string with method parameters
        - Parameter names match Telegram API documentation
        - Supports complex nested objects

        ENTITY RESOLUTION:
        - Set resolve=true to automatically resolve entity-like parameters
        - Handles: peer, user, chat, channel, etc. (strings/ints → TL objects)
        - Useful for simplifying parameter preparation

        SECURITY:
        - Dangerous methods (delete operations) blocked by default
        - Pass allow_dangerous=true to override for destructive operations

        EXAMPLES:
        invoke_mtproto("users.GetFullUser", '{"id": {"_": "inputUserSelf"}}')  # Get self info
        invoke_mtproto("messages.GetHistory", '{"peer": "username", "limit": 10}')  # Auto-resolve peer (default)
        invoke_mtproto("messages.DeleteMessages", '{"id": [123]}', allow_dangerous=True)  # Dangerous operation

        Args:
            method_full_name: Telegram API method name (e.g., "messages.GetHistory")
            params_json: Method parameters as JSON string
            allow_dangerous: Allow dangerous methods like delete operations (default: False)
            resolve: Automatically resolve entity-like parameters (default: True)

        Returns:
            API response as dict, or error details if failed
        """
        return await invoke_mtproto_impl(
            method_full_name=method_full_name,
            params_json=params_json,
            allow_dangerous=allow_dangerous,
            resolve=resolve,
        )
