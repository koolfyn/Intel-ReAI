from typing import List, Dict, Any
from .claude_service import ClaudeService
import logging

logger = logging.getLogger(__name__)

class AutoConfigService:
    def __init__(self):
        self.claude_service = ClaudeService()

    async def generate_subreddit_config(
        self,
        name: str,
        description: str,
        topics: List[str],
        moderation_style: str = "moderate"
    ) -> Dict[str, Any]:
        """Generate complete subreddit configuration using AI"""
        try:
            result = await self.claude_service.generate_subreddit_config(
                name=name,
                description=description,
                topics=topics,
                moderation_style=moderation_style
            )

            # Ensure the result has the expected structure
            if not isinstance(result, dict):
                result = self._get_fallback_config(name, description)

            # Validate and enhance the result
            result = self._validate_and_enhance_config(result, name, description, topics, moderation_style)

            return result

        except Exception as e:
            logger.error(f"Error generating subreddit config: {e}")
            return self._get_fallback_config(name, description)

    def _validate_and_enhance_config(
        self,
        config: Dict[str, Any],
        name: str,
        description: str,
        topics: List[str],
        moderation_style: str
    ) -> Dict[str, Any]:
        """Validate and enhance the generated configuration"""

        # Ensure required fields exist
        if "display_name" not in config:
            config["display_name"] = name.title()

        if "description" not in config:
            config["description"] = description

        if "rules" not in config or not isinstance(config["rules"], list):
            config["rules"] = self._get_default_rules(moderation_style)

        if "moderation_guidelines" not in config:
            config["moderation_guidelines"] = self._get_default_moderation_guidelines(moderation_style)

        if "auto_moderation_settings" not in config:
            config["auto_moderation_settings"] = self._get_default_auto_mod_settings(moderation_style)

        # Enhance rules based on topics
        config["rules"] = self._enhance_rules_for_topics(config["rules"], topics)

        # Enhance auto-moderation settings based on moderation style
        config["auto_moderation_settings"] = self._enhance_auto_mod_settings(
            config["auto_moderation_settings"],
            moderation_style
        )

        return config

    def _get_fallback_config(self, name: str, description: str) -> Dict[str, Any]:
        """Get fallback configuration if AI generation fails"""
        return {
            "display_name": name.title(),
            "description": description,
            "rules": self._get_default_rules("moderate"),
            "moderation_guidelines": self._get_default_moderation_guidelines("moderate"),
            "auto_moderation_settings": self._get_default_auto_mod_settings("moderate")
        }

    def _get_default_rules(self, moderation_style: str) -> List[Dict[str, str]]:
        """Get default rules based on moderation style"""
        base_rules = [
            {"title": "Be respectful", "description": "Treat others with respect and civility", "severity": "high"},
            {"title": "No spam", "description": "No spam, self-promotion, or off-topic content", "severity": "high"},
            {"title": "Stay on topic", "description": "Keep discussions relevant to the subreddit", "severity": "medium"}
        ]

        if moderation_style == "strict":
            base_rules.extend([
                {"title": "No low-effort posts", "description": "Posts must be substantial and well-thought-out", "severity": "medium"},
                {"title": "Use descriptive titles", "description": "Post titles must clearly describe the content", "severity": "medium"},
                {"title": "No duplicate posts", "description": "Search before posting to avoid duplicates", "severity": "medium"}
            ])
        elif moderation_style == "lenient":
            base_rules.append({
                "title": "Be constructive",
                "description": "Try to contribute positively to discussions",
                "severity": "low"
            })

        return base_rules

    def _get_default_moderation_guidelines(self, moderation_style: str) -> str:
        """Get default moderation guidelines"""
        if moderation_style == "strict":
            return "Moderate content strictly according to community rules. Remove low-effort posts, enforce title guidelines, and maintain high-quality discussions."
        elif moderation_style == "lenient":
            return "Moderate content with a light touch. Focus on removing spam and harmful content while allowing diverse opinions and casual discussions."
        else:  # moderate
            return "Moderate content fairly according to community rules. Balance between maintaining quality and allowing diverse discussions. Remove spam and rule violations."

    def _get_default_auto_mod_settings(self, moderation_style: str) -> Dict[str, Any]:
        """Get default auto-moderation settings"""
        base_settings = {
            "auto_remove_spam": True,
            "require_approval": False,
            "content_filters": ["spam", "offensive"],
            "min_account_age_hours": 0,
            "min_karma_required": 0
        }

        if moderation_style == "strict":
            base_settings.update({
                "require_approval": True,
                "min_account_age_hours": 24,
                "min_karma_required": 10,
                "content_filters": ["spam", "offensive", "low_effort", "duplicate"]
            })
        elif moderation_style == "lenient":
            base_settings.update({
                "content_filters": ["spam"]
            })

        return base_settings

    def _enhance_rules_for_topics(self, rules: List[Dict[str, str]], topics: List[str]) -> List[Dict[str, str]]:
        """Enhance rules based on specific topics"""
        topic_rules = []

        if "programming" in topics or "coding" in topics:
            topic_rules.append({
                "title": "Use proper code formatting",
                "description": "Format code properly using markdown or code blocks",
                "severity": "medium"
            })

        if "ai" in topics or "artificial intelligence" in topics:
            topic_rules.append({
                "title": "Disclose AI-generated content",
                "description": "Clearly mark any AI-generated content or responses",
                "severity": "medium"
            })

        if "startup" in topics or "business" in topics:
            topic_rules.append({
                "title": "No self-promotion spam",
                "description": "Limit self-promotion and focus on providing value to the community",
                "severity": "medium"
            })

        return rules + topic_rules

    def _enhance_auto_mod_settings(
        self,
        settings: Dict[str, Any],
        moderation_style: str
    ) -> Dict[str, Any]:
        """Enhance auto-moderation settings based on moderation style"""

        # Add topic-specific filters
        if "ai" in settings.get("content_filters", []):
            settings["content_filters"].extend(["ai_generated", "low_quality"])

        if "programming" in settings.get("content_filters", []):
            settings["content_filters"].extend(["unformatted_code", "homework_help"])

        # Remove duplicates
        if "content_filters" in settings:
            settings["content_filters"] = list(set(settings["content_filters"]))

        return settings
