import os
import requests
from datetime import datetime
from .simfetcher import fetch_content
from .processor import process_content
from .archiver import save_as_markdown
import yaml
from .imp_clip import update_sources_from_clipboard, is_clipboard_content_valid
import asyncio
import pyperclip
from .playwright_writer import write_to_note, read_from_note, SimplenoteWriter
from .session_manager import (
    create_session_note,
    get_active_session,
    clear_active_session,
    search_and_select_note
)
from .session_sharing import (
    publish_session_note,
    unpublish_session_note,
    add_session_collaborator,
    remove_session_collaborator,
    list_session_collaborators,
    share_session_note
)

# Config file in user's home directory (not package directory)
CONFIG_FILE = os.path.expanduser('~/.simexp/simexp.yaml')

def init_config():
    # Create config directory if it doesn't exist
    config_dir = os.path.dirname(CONFIG_FILE)
    os.makedirs(config_dir, exist_ok=True)

    config = {
        'BASE_PATH': input("Enter the base path for saving content: "),
        'SOURCES': []
    }
    while True:
        url = input("Enter source URL (or 'done' to finish): ")
        if url.lower() == 'done':
            break
        filename = input("Enter filename for this source: ")
        config['SOURCES'].append({'url': url, 'filename': filename})

    with open(CONFIG_FILE, 'w') as config_file:
        yaml.safe_dump(config, config_file)
    print(f"✅ Configuration saved to {CONFIG_FILE}")


def write_command(note_url, content=None, mode='append', headless=False, cdp_url=None):
    """
    Write content to Simplenote note via Playwright

    Args:
        note_url: Simplenote note URL
        content: Content to write (if None, read from stdin)
        mode: 'append' or 'replace'
        headless: Run browser in headless mode
        cdp_url: Chrome DevTools Protocol URL
    """
    import sys

    # Read from stdin if no content provided
    if content is None:
        print("📝 Reading content from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided")
            return

    print(f"♠️🌿🎸🧵 SimExp Write Mode - {mode.upper()}")
    print(f"🌐 Target: {note_url}")
    print(f"📄 Content length: {len(content)} chars")

    # Execute async write
    result = asyncio.run(write_to_note(
        note_url=note_url,
        content=content,
        mode=mode,
        headless=headless,
        debug=True,
        cdp_url=cdp_url
    ))

    if result['success']:
        print(f"\n✅ Write successful!")
        print(f"📊 Written: {result['content_length']} characters")
        print(f"📝 Preview: {result['preview']}")
    else:
        print(f"\n❌ Write failed - verification mismatch")


def read_command(note_url, headless=True):
    """
    Read content from Simplenote note via Playwright

    Args:
        note_url: Simplenote note URL
        headless: Run browser in headless mode
    """
    print(f"♠️🌿🎸🧵 SimExp Read Mode")
    print(f"🌐 Source: {note_url}")

    # Execute async read
    content = asyncio.run(read_from_note(
        note_url=note_url,
        headless=headless,
        debug=True
    ))

    print(f"\n📖 Content ({len(content)} chars):")
    print("=" * 60)
    print(content)
    print("=" * 60)

    return content


# ═══════════════════════════════════════════════════════════════
# SESSION COMMAND SUITE
# ♠️🌿🎸🧵 G.Music Assembly - Session-Aware Notes
# ═══════════════════════════════════════════════════════════════

def session_start_command(ai_assistant='claude', issue_number=None, cdp_url='http://localhost:9223'):
    """
    Start a new session and create a Simplenote note for it

    Args:
        ai_assistant: AI assistant name (claude or gemini)
        issue_number: GitHub issue number being worked on
        cdp_url: Chrome DevTools Protocol URL
    """
    print(f"♠️🌿🎸🧵 Starting New Session")

    session_data = asyncio.run(create_session_note(
        ai_assistant=ai_assistant,
        issue_number=issue_number,
        cdp_url=cdp_url
    ))

    print(f"\n✅ Session started successfully!")
    print(f"🔮 Session ID: {session_data['session_id']}")
    print(f"🔑 Search Key: {session_data['search_key']}")
    print(f"💡 Tip: Use 'simexp session write' to add content to your session note")


def session_write_command(content=None, cdp_url='http://localhost:9223'):
    """
    Write to the current session's note using search

    Args:
        content: Content to write (if None, read from stdin)
        cdp_url: Chrome DevTools Protocol URL
    """
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    # Read from stdin if no content provided
    if content is None:
        print("📝 Reading content from stdin (Ctrl+D to finish)...")
        content = sys.stdin.read()
        if not content.strip():
            print("❌ No content provided")
            return

    print(f"♠️🌿🎸🧵 Writing to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"📄 Content length: {len(content)} chars")

    # Execute search and write
    async def write_to_session():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=cdp_url
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return False

            # Write content to the note (it's already selected)
            editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
            await editor.click()
            await asyncio.sleep(0.5)

            # Go to end and append
            await writer.page.keyboard.press('Control+End')
            await asyncio.sleep(0.3)
            await writer.page.keyboard.type(f"\n\n{content}", delay=10)  # Slow typing for reliability

            # Wait longer for Simplenote autosave (critical!)
            print(f"⏳ Waiting for Simplenote to autosave...")
            await asyncio.sleep(3)  # Increased from 1 to 3 seconds

            print(f"✅ Write successful!")
            return True

    success = asyncio.run(write_to_session())
    if not success:
        print(f"\n❌ Write failed")


def session_read_command(cdp_url='http://localhost:9223'):
    """
    Read content from the current session's note using search

    Args:
        cdp_url: Chrome DevTools Protocol URL
    """
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Reading Session Note")
    print(f"🔮 Session: {session['session_id']}")

    # Execute search and read
    async def read_from_session():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=cdp_url
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return None

            # Read content from the note
            editor = await writer.page.wait_for_selector('div.note-editor', timeout=5000)
            content = await editor.text_content()
            return content

    content = asyncio.run(read_from_session())

    if content:
        print(f"\n📖 Session Content ({len(content)} chars):")
        print("=" * 60)
        print(content)
        print("=" * 60)
    else:
        print(f"\n❌ Could not read session note")


def session_open_command(cdp_url='http://localhost:9223'):
    """
    Open session note in browser using Playwright automation

    Args:
        cdp_url: Chrome DevTools Protocol URL
    """
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Opening Session Note in Browser")
    print(f"🔮 Session: {session['session_id']}")

    # Execute search and open
    async def open_session_note():
        async with SimplenoteWriter(
            note_url='https://app.simplenote.com/',
            headless=False,
            debug=True,
            cdp_url=cdp_url
        ) as writer:
            # Navigate to Simplenote
            await writer.page.goto('https://app.simplenote.com/')
            await writer.page.wait_for_load_state('networkidle')

            # Search for and select the session note
            found = await search_and_select_note(
                session['session_id'],
                writer.page,
                debug=True
            )

            if not found:
                print("❌ Could not find session note. Note may have been deleted.")
                return False

            print(f"✅ Session note opened in browser!")
            print(f"💡 Browser will stay open for you to view/edit the note")

            # Keep the browser open by waiting (user can Ctrl+C to close)
            print(f"\n🎯 Press Ctrl+C when done viewing/editing...")
            try:
                await asyncio.sleep(300)  # Wait 5 minutes or until Ctrl+C
            except KeyboardInterrupt:
                print(f"\n👋 Closing browser connection...")

            return True

    success = asyncio.run(open_session_note())
    if success:
        print(f"✅ Done!")
    else:
        print(f"❌ Failed to open session note")


def session_url_command():
    """Print the session search key"""
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"🔑 Session search key: {session['search_key']}")
    print(f"💡 Use this in Simplenote search to find your session note")


def session_status_command():
    """Show current session status"""
    import sys

    # Get active session
    session = get_active_session()
    if not session:
        print("❌ No active session")
        print("💡 Run 'simexp session start' to create a new session")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Active Session Status")
    print(f"🔮 Session ID: {session['session_id']}")
    print(f"🔑 Search Key: {session['search_key']}")
    print(f"🤝 AI Assistant: {session['ai_assistant']}")
    if session.get('issue_number'):
        print(f"🎯 Issue: #{session['issue_number']}")
    print(f"📅 Created: {session['created_at']}")


def session_clear_command():
    """Clear the current session"""
    clear_active_session()
    print("✅ Session cleared")


def session_publish_command(cdp_url='http://localhost:9223'):
    """Publish the current session's note"""
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Publishing Session Note")
    print(f"🔮 Session: {session['session_id']}")

    public_url = asyncio.run(publish_session_note(cdp_url=cdp_url))

    if public_url:
        # Copy to clipboard
        try:
            pyperclip.copy(public_url)
            clipboard_status = "📋 Copied to clipboard!"
        except Exception as e:
            clipboard_status = f"⚠️  Could not copy to clipboard: {e}"

        print(f"\n✅ Note published successfully!")
        print(f"🌐 Public URL: {public_url}")
        print(f"{clipboard_status}")
    else:
        print(f"\n⚠️  Publish completed but could not extract URL")
        print(f"💡 Check Simplenote UI for the public URL")


def session_unpublish_command(cdp_url='http://localhost:9223'):
    """Unpublish the current session's note"""
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Unpublishing Session Note")
    print(f"🔮 Session: {session['session_id']}")

    success = asyncio.run(unpublish_session_note(cdp_url=cdp_url))

    if success:
        print(f"\n✅ Note unpublished successfully!")
    else:
        print(f"\n❌ Unpublish failed")


def session_collab_add_command(email, cdp_url='http://localhost:9223'):
    """Add a collaborator to the current session's note"""
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Adding Collaborator to Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"👤 Collaborator: {email}")

    success = asyncio.run(add_session_collaborator(email, cdp_url=cdp_url))

    if success:
        print(f"\n✅ Collaborator added successfully!")
    else:
        print(f"\n❌ Failed to add collaborator")


def session_collab_remove_command(email, cdp_url='http://localhost:9223'):
    """Remove a collaborator from the current session's note"""
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Removing Collaborator from Session Note")
    print(f"🔮 Session: {session['session_id']}")
    print(f"👤 Collaborator: {email}")

    success = asyncio.run(remove_session_collaborator(email, cdp_url=cdp_url))

    if success:
        print(f"\n✅ Collaborator removed successfully!")
    else:
        print(f"\n❌ Failed to remove collaborator")


def session_collab_list_command(cdp_url='http://localhost:9223'):
    """List all collaborators on the current session's note"""
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Listing Collaborators on Session Note")
    print(f"🔮 Session: {session['session_id']}")

    collaborators = asyncio.run(list_session_collaborators(cdp_url=cdp_url))

    if collaborators:
        print(f"\n✅ Found {len(collaborators)} collaborator(s):")
        for email in collaborators:
            print(f"   👤 {email}")
    else:
        print(f"\n📭 No collaborators found")


def session_share_command(identifier, cdp_url='http://localhost:9223'):
    """
    Share session note using glyph/alias/group/email

    Examples:
        simexp session share ♠️              - Share with Nyro
        simexp session share nyro            - Share with Nyro (alias)
        simexp session share assembly        - Share with all Assembly members
        simexp session share user@email.com  - Share with custom email
    """
    import sys

    session = get_active_session()
    if not session:
        print("❌ No active session. Run 'simexp session start' first.")
        sys.exit(1)

    print(f"♠️🌿🎸🧵 Sharing Session Note via Glyph Resolution")
    print(f"🔮 Session: {session['session_id']}")
    print(f"🔑 Identifier: {identifier}")

    result = asyncio.run(share_session_note(identifier, cdp_url=cdp_url, debug=True))

    # Result dict already prints summary in share_session_note()
    # Just handle exit code based on success
    if not result['success']:
        sys.exit(1)


def run_extraction():
    """
    Original extraction workflow - fetches content from clipboard/config sources
    This is the legacy feature of simexp
    """
    # Update sources from clipboard
    update_sources_from_clipboard()

    # Load configuration from YAML file
    config_path = CONFIG_FILE
    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found. Please run 'simexp init' to create it.")
        return

    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Check if clipboard content is valid
    if not is_clipboard_content_valid():
        print("Invalid clipboard content. Proceeding with existing websites from configuration.")
        sources = config['SOURCES']
    else:
        sources = config['CLIPBOARD_SOURCES']

    base_path = config['BASE_PATH']

    # Create a folder for the current date
    current_date = datetime.now().strftime('%Y%m%d')
    daily_folder = os.path.join(base_path, current_date)
    os.makedirs(daily_folder, exist_ok=True)

    # Fetch, process, and save content for each source
    for source in sources:
        url = source['url']
        filename = source['filename']
        raw_content = fetch_content(url)
        title, cleaned_content = process_content(raw_content)
        save_as_markdown(title, cleaned_content, filename)


def main():
    """
    Main CLI entry point - parses arguments FIRST, then dispatches to appropriate command
    This fixes Issue #9 - CLI commands now work without requiring valid config/clipboard
    """
    import sys

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'init':
            init_config()

        elif command == 'write':
            import argparse
            parser = argparse.ArgumentParser(
                description='Write content to a Simplenote note.',
                prog='simexp write')
            parser.add_argument('content', help='The content to write. If not provided, reads from stdin.')
            parser.add_argument('--note-url', default='https://app.simplenote.com/', help='The URL of the Simplenote note. Defaults to the main page, which will select the most recent note.')
            parser.add_argument('--mode', choices=['append', 'replace'], default='append', help='Write mode.')
            parser.add_argument('--headless', action='store_true', help='Run in headless mode.')
            parser.add_argument('--cdp-url', default=None, help='Chrome DevTools Protocol URL to connect to an existing browser.')
            
            args = parser.parse_args(sys.argv[2:])

            write_command(args.note_url, args.content, mode=args.mode, headless=args.headless, cdp_url=args.cdp_url)

        elif command == 'read':
            # Usage: simexp read <note_url>
            if len(sys.argv) < 3:
                print("Usage: simexp read <note_url>")
                sys.exit(1)

            note_url = sys.argv[2]
            read_command(note_url, headless=True)

        elif command == 'session':
            # Session command suite
            if len(sys.argv) < 3:
                print("Usage: simexp session <subcommand>")
                print("\nSession Management:")
                print("  start [--ai <assistant>] [--issue <number>]  - Start new session")
                print("  write <message>                              - Write to session note")
                print("  read                                         - Read session note")
                print("  open                                         - Open session note in browser")
                print("  url                                          - Print session note URL")
                print("  status                                       - Show session status")
                print("  clear                                        - Clear active session")
                print("\nSharing & Publishing (Issue #6):")
                print("  share <glyph|alias|group|email>              - Share with collaborator(s)")
                print("  publish                                      - Publish note (get public URL)")
                print("  unpublish                                    - Unpublish note (make private)")
                print("  collab add <email>                           - Add collaborator")
                print("  collab remove <email>                        - Remove collaborator")
                print("  collab list                                  - List all collaborators")
                sys.exit(1)

            subcommand = sys.argv[2]

            if subcommand == 'start':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Start a new session',
                    prog='simexp session start')
                parser.add_argument('--ai', default='claude', choices=['claude', 'gemini'], help='AI assistant name')
                parser.add_argument('--issue', type=int, help='GitHub issue number')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_start_command(ai_assistant=args.ai, issue_number=args.issue, cdp_url=args.cdp_url)

            elif subcommand == 'write':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Write to session note',
                    prog='simexp session write')
                parser.add_argument('content', nargs='?', help='Content to write (optional, reads from stdin if not provided)')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_write_command(content=args.content, cdp_url=args.cdp_url)

            elif subcommand == 'read':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Read session note',
                    prog='simexp session read')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_read_command(cdp_url=args.cdp_url)

            elif subcommand == 'open':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Open session note in browser',
                    prog='simexp session open')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_open_command(cdp_url=args.cdp_url)

            elif subcommand == 'url':
                session_url_command()

            elif subcommand == 'status':
                session_status_command()

            elif subcommand == 'clear':
                session_clear_command()

            elif subcommand == 'publish':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Publish session note',
                    prog='simexp session publish')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_publish_command(cdp_url=args.cdp_url)

            elif subcommand == 'unpublish':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Unpublish session note',
                    prog='simexp session unpublish')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_unpublish_command(cdp_url=args.cdp_url)

            elif subcommand == 'collab':
                # Collaborator management subcommands
                if len(sys.argv) < 4:
                    print("Usage: simexp session collab <add|remove|list> [email]")
                    print("\nSubcommands:")
                    print("  add <email>     - Add collaborator by email")
                    print("  remove <email>  - Remove collaborator by email")
                    print("  list            - List all collaborators")
                    sys.exit(1)

                collab_action = sys.argv[3]

                if collab_action == 'add':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Add collaborator',
                        prog='simexp session collab add')
                    parser.add_argument('email', help='Collaborator email address')
                    parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_add_command(args.email, cdp_url=args.cdp_url)

                elif collab_action == 'remove':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='Remove collaborator',
                        prog='simexp session collab remove')
                    parser.add_argument('email', help='Collaborator email address')
                    parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_remove_command(args.email, cdp_url=args.cdp_url)

                elif collab_action == 'list':
                    import argparse
                    parser = argparse.ArgumentParser(
                        description='List collaborators',
                        prog='simexp session collab list')
                    parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                    args = parser.parse_args(sys.argv[4:])
                    session_collab_list_command(cdp_url=args.cdp_url)

                else:
                    print(f"Unknown collab action: {collab_action}")
                    print("Run 'simexp session collab' for usage information")
                    sys.exit(1)

            elif subcommand == 'share':
                import argparse
                parser = argparse.ArgumentParser(
                    description='Share session note with collaborator(s) using glyph/alias/group/email',
                    prog='simexp session share')
                parser.add_argument('identifier', help='Glyph (♠️), alias (nyro), group (assembly), or email address')
                parser.add_argument('--cdp-url', default='http://localhost:9223', help='Chrome DevTools Protocol URL')

                args = parser.parse_args(sys.argv[3:])
                session_share_command(args.identifier, cdp_url=args.cdp_url)

            else:
                print(f"Unknown session subcommand: {subcommand}")
                print("Run 'simexp session' for usage information")
                sys.exit(1)

        elif command == 'help' or command == '--help' or command == '-h':
            print("♠️🌿🎸🧵 SimExp - Simplenote Web Content Extractor & Writer")
            print("\nCommands:")
            print("  simexp                       - Run extraction from clipboard/config")
            print("  simexp init                  - Initialize configuration")
            print("  simexp write <url> [msg]     - Write to Simplenote note")
            print("  simexp read <url>            - Read from Simplenote note")
            print("  simexp session <subcommand>  - Session management")
            print("  simexp help                  - Show this help")
            print("\nSession Commands:")
            print("  simexp session start [--ai <assistant>] [--issue <number>]")
            print("                               - Start new session with Simplenote note")
            print("  simexp session write <msg>   - Write to current session's note")
            print("  simexp session read          - Read current session's note")
            print("  simexp session open          - Open session note in browser")
            print("  simexp session url           - Print session note URL")
            print("  simexp session status        - Show current session info")
            print("  simexp session clear         - Clear active session")
            print("\nSharing Commands (Issue #6):")
            print("  simexp session share <glyph|alias|group|email>  - Share with collaborator(s)")
            print("  simexp session publish       - Publish note (get public URL)")
            print("  simexp session unpublish     - Unpublish note (make private)")
            print("  simexp session collab add <email>    - Add collaborator")
            print("  simexp session collab remove <email> - Remove collaborator")
            print("  simexp session collab list   - List all collaborators")
            print("\nExamples:")
            print("  # Original features:")
            print("  simexp write https://app.simplenote.com/p/0ZqWsQ 'Hello!'")
            print("  echo 'Message' | simexp write https://app.simplenote.com/p/0ZqWsQ")
            print("  simexp read https://app.simplenote.com/p/0ZqWsQ")
            print("\n  # Session-aware notes:")
            print("  simexp session start --ai claude --issue 42")
            print("  simexp session write 'Implemented feature X'")
            print("  echo 'Progress update' | simexp session write")
            print("  simexp session status")
            print("  simexp session open")
            print("\n  # Sharing & publishing:")
            print("  simexp session share ♠️                        # Share with Nyro (glyph)")
            print("  simexp session share nyro                     # Share with Nyro (alias)")
            print("  simexp session share assembly                 # Share with Assembly group")
            print("  simexp session share custom@example.com       # Share with custom email")
            print("  simexp session publish")
            print("  simexp session collab add jerry@example.com")
            print("  simexp session collab list")
            print("  simexp session unpublish")

        else:
            print(f"Unknown command: {command}")
            print("Run 'simexp help' for usage information")
            sys.exit(1)

    else:
        # No arguments - run normal extraction
        run_extraction()

if __name__ == "__main__":
    main()
