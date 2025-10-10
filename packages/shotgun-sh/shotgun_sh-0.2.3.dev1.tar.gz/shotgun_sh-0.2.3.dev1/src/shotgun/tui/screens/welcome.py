"""Welcome screen for choosing between Shotgun Account and BYOK."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Markdown, Static

if TYPE_CHECKING:
    from ..app import ShotgunApp


class WelcomeScreen(Screen[None]):
    """Welcome screen for first-time setup."""

    CSS = """
        WelcomeScreen {
            layout: vertical;
            align: center middle;
        }

        #titlebox {
            width: 100%;
            height: auto;
            margin: 2 0;
            padding: 1;
            border: hkey $border;
            content-align: center middle;

            & > * {
                text-align: center;
            }
        }

        #welcome-title {
            padding: 1 0;
            text-style: bold;
            color: $text-accent;
        }

        #welcome-subtitle {
            padding: 0 1;
        }

        #options-container {
            width: 100%;
            height: auto;
            padding: 2;
            align: center middle;
        }

        #options {
            width: auto;
            height: auto;
        }

        .option-box {
            width: 45;
            height: auto;
            border: solid $primary;
            padding: 2;
            margin: 0 1;
            background: $surface;
        }

        .option-box:focus-within {
            border: solid $accent;
        }

        .option-title {
            text-style: bold;
            color: $text-accent;
            padding: 0 0 1 0;
        }

        .option-benefits {
            padding: 1 0;
        }

        .option-button {
            margin: 1 0 0 0;
            width: 100%;
        }
    """

    BINDINGS = [
        ("ctrl+c", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="titlebox"):
            yield Static("Welcome to Shotgun", id="welcome-title")
            yield Static(
                "Choose how you'd like to get started",
                id="welcome-subtitle",
            )

        with Container(id="options-container"):
            with Horizontal(id="options"):
                # Left box - Shotgun Account
                with Vertical(classes="option-box", id="shotgun-box"):
                    yield Static("Use a Shotgun Account", classes="option-title")
                    yield Markdown(
                        "**Benefits:**\n"
                        "• Use of all models in the Model Garden\n"
                        "• We'll pick the optimal models to give you the best "
                        "experience for things like web search, codebase indexing",
                        classes="option-benefits",
                    )
                    yield Button(
                        "Sign Up for/Use your Shotgun Account",
                        variant="primary",
                        id="shotgun-button",
                        classes="option-button",
                    )

                # Right box - BYOK
                with Vertical(classes="option-box", id="byok-box"):
                    yield Static("Bring Your Own Key (BYOK)", classes="option-title")
                    yield Markdown(
                        "**Benefits:**\n"
                        "• 100% Supported by the application\n"
                        "• Use your existing API keys from OpenAI, Anthropic, or Google",
                        classes="option-benefits",
                    )
                    yield Button(
                        "Configure API Keys",
                        variant="success",
                        id="byok-button",
                        classes="option-button",
                    )

    def on_mount(self) -> None:
        """Focus the first button on mount."""
        self.query_one("#shotgun-button", Button).focus()

    @on(Button.Pressed, "#shotgun-button")
    def _on_shotgun_pressed(self) -> None:
        """Handle Shotgun Account button press."""
        self.run_worker(self._start_shotgun_auth(), exclusive=True)

    @on(Button.Pressed, "#byok-button")
    def _on_byok_pressed(self) -> None:
        """Handle BYOK button press."""
        self._mark_welcome_shown()
        # Push provider config screen before dismissing
        from .provider_config import ProviderConfigScreen

        self.app.push_screen(
            ProviderConfigScreen(),
            callback=lambda _arg: self.dismiss(),
        )

    async def _start_shotgun_auth(self) -> None:
        """Launch Shotgun Account authentication flow."""
        from .shotgun_auth import ShotgunAuthScreen

        # Mark welcome screen as shown before auth
        self._mark_welcome_shown()

        # Push the auth screen and wait for result
        await self.app.push_screen_wait(ShotgunAuthScreen())

        # Dismiss welcome screen after auth
        self.dismiss()

    def _mark_welcome_shown(self) -> None:
        """Mark the welcome screen as shown in config."""
        app = cast("ShotgunApp", self.app)
        config = app.config_manager.load()
        config.shown_welcome_screen = True
        app.config_manager.save(config)
