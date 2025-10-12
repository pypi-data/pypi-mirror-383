"""
This module defines the TextBlock for displaying text content.

"""

from typing import Any, Callable, Dict, List, Optional, Union

import dash_bootstrap_components as dbc
import pandas as pd
from dash import dcc, html
from dash.development.base_component import Component

from dashboard_lego.blocks.base import BaseBlock


class TextBlock(BaseBlock):
    """
    A block for displaying dynamic text content, with support for Markdown and
    customizable styling.

    This block subscribes to a state and uses a generator function to render
    its content based on the data from a datasource.

        :hierarchy: [Blocks | Text | TextBlock]
        :relates-to:
          - motivated_by: "Architectural Conclusion: Dynamic text blocks are
            essential for displaying model summaries and other formatted
            content with customizable styling"
          - implements: "block: 'TextBlock'"
          - uses: ["interface: 'BaseBlock'"]

        :rationale: "Enhanced with style customization parameters to allow
         fine-grained control over text block appearance while maintaining
         backward compatibility."
        :contract:
          - pre: "A `subscribes_to` state ID and a `content_generator` function
            must be provided."
          - post: "The block renders a card with content that updates on state
            change with customizable styling applied."

    """

    def __init__(
        self,
        block_id: str,
        datasource: Any,
        subscribes_to: Union[str, List[str]],
        content_generator: Callable[[pd.DataFrame], Component | str],
        title: Optional[str] = None,
        # Style customization parameters
        card_style: Optional[Dict[str, Any]] = None,
        card_className: Optional[str] = None,
        title_style: Optional[Dict[str, Any]] = None,
        title_className: Optional[str] = None,
        content_style: Optional[Dict[str, Any]] = None,
        content_className: Optional[str] = None,
        loading_type: str = "default",
    ):
        """
        Initializes the TextBlock with customizable styling.

        Args:
            block_id: A unique identifier for this block instance.
            datasource: An instance of a class that implements the
                BaseDataSource interface.
            subscribes_to: The state ID(s) to which this block subscribes to
                receive updates. Can be a single state ID string or a list of
                state IDs.
            content_generator: A function that takes a DataFrame and returns a
                Dash Component or a Markdown string.
            title: An optional title for the block's card.
            card_style: Optional style dictionary for the card component.
            card_className: Optional CSS class name for the card component.
            title_style: Optional style dictionary for the title component.
            title_className: Optional CSS class name for the title component.
            content_style: Optional style dictionary for the content container.
            content_className: Optional CSS class name for the content
                container.
            loading_type: Type of loading indicator to display.

        """
        self.title = title
        self.content_generator = content_generator

        # Store style customization parameters
        self.card_style = card_style
        self.card_className = card_className
        self.title_style = title_style
        self.title_className = title_className
        self.content_style = content_style
        self.content_className = content_className
        self.loading_type = loading_type

        # Normalize subscribes_to to list and build subscribes dict
        state_ids = self._normalize_subscribes_to(subscribes_to)
        subscribes_dict = {state_id: self._update_content for state_id in state_ids}

        super().__init__(block_id, datasource, subscribes=subscribes_dict)

    def _update_content(self, *args) -> Component:
        """
        Callback function to update the block's content based on datasource
        changes with customizable styling.

        :hierarchy: [Blocks | Text | TextBlock | Update Logic]
        :relates-to:
         - motivated_by: "PRD: Need to display dynamic text content with
           customizable styling"
         - implements: "method: '_update_content' with style overrides"
         - uses: ["attribute: 'content_generator'", "attribute: 'title_style'"]

        :rationale: "Enhanced to apply style customization parameters to
         content and title components."
        :contract:
         - pre: "Datasource is available and content generator is set."
         - post: "Returns a styled CardBody with current content and title."

        """
        try:
            df = self.datasource.get_processed_data()
            generated_content = self.content_generator(df)

            # If the generator returns a string, wrap it in dcc.Markdown
            if isinstance(generated_content, str):
                content_component = dcc.Markdown(generated_content)
            else:
                content_component = generated_content

            # Apply content styling if provided
            if self.content_style or self.content_className:
                content_props = {}
                if self.content_style:
                    content_props["style"] = self.content_style
                if self.content_className:
                    content_props["className"] = self.content_className
                content_component = html.Div(content_component, **content_props)

            children = [content_component]
            if self.title:
                # Build title props with style overrides
                title_props = {
                    "className": self.title_className or "card-title",
                }
                if self.title_style:
                    title_props["style"] = self.title_style
                children.insert(0, html.H4(self.title, **title_props))

            return dbc.CardBody(children)
        except Exception as e:
            return dbc.Alert(
                f"Ошибка генерации текстового блока: {str(e)}", color="danger"
            )

    def layout(self) -> Component:
        """
        Defines the initial layout of the block with theme-aware styling.

        :hierarchy: [Blocks | Text | TextBlock | Layout]
        :relates-to:
         - motivated_by: "PRD: Automatic theme application to text blocks"
         - implements: "method: 'layout' with theme integration"
         - uses: ["method: '_get_themed_style'", "attribute: 'card_style'"]

        :rationale: "Uses theme system for consistent styling with user override capability."
        :contract:
         - pre: "Block is properly initialized, theme_config may be available."
         - post: "Returns a themed Card component with automatic styling."

        """
        # Initialize with current content instead of empty container
        initial_content = self._update_content()

        # Build card props with theme-aware style
        themed_card_style = self._get_themed_style(
            "card", "background", self.card_style
        )
        # h-100 ensures equal height when multiple blocks in same row
        # Note: mb-4 removed, handled by Row.mb-4
        base_classes = "h-100"
        card_props = {
            "className": (
                f"{base_classes} {self.card_className}"
                if self.card_className
                else base_classes
            )
        }
        if themed_card_style:
            card_props["style"] = themed_card_style

        return dbc.Card(
            dcc.Loading(
                id=self._generate_id("loading"),
                type=self.loading_type,
                children=html.Div(
                    id=self._generate_id("container"), children=initial_content
                ),
            ),
            **card_props,
        )
