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
        moderation_style: str = "moderate",
        brief_description: str = None,
        target_audience: str = None,
        content_types: List[str] = None,
        community_goals: str = None,
        moderation_philosophy: str = None,
        language: str = "en",
        age_restriction: str = "all",
        content_rating: str = "general"
    ) -> Dict[str, Any]:
        """Generate complete subreddit configuration using AI"""
        try:
            result = await self.claude_service.generate_comprehensive_subreddit_config(
                name=name,
                description=description,
                topics=topics,
                moderation_style=moderation_style,
                brief_description=brief_description,
                target_audience=target_audience,
                content_types=content_types,
                community_goals=community_goals,
                moderation_philosophy=moderation_philosophy,
                language=language,
                age_restriction=age_restriction,
                content_rating=content_rating
            )

            # Ensure the result has the expected structure
            if not isinstance(result, dict):
                result = self._get_fallback_comprehensive_config(name, description, topics, moderation_style)

            # Validate and enhance the result
            result = self._validate_and_enhance_comprehensive_config(result, name, description, topics, moderation_style)

            return result

        except Exception as e:
            logger.error(f"Error generating subreddit config: {e}")
            return self._get_fallback_comprehensive_config(name, description, topics, moderation_style)

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

    def _validate_and_enhance_comprehensive_config(
        self,
        config: Dict[str, Any],
        name: str,
        description: str,
        topics: List[str],
        moderation_style: str
    ) -> Dict[str, Any]:
        """Validate and enhance the comprehensive generated configuration"""

        # Ensure required fields exist
        if "display_name" not in config:
            config["display_name"] = name.title()

        if "description" not in config:
            config["description"] = description

        # Ensure rules have required fields
        if "rules" in config and isinstance(config["rules"], list):
            for rule in config["rules"]:
                if "severity" not in rule:
                    rule["severity"] = "medium"
                if "category" not in rule:
                    rule["category"] = "community"
                if "enforcement_level" not in rule:
                    rule["enforcement_level"] = "warning"
                if "examples" not in rule:
                    rule["examples"] = []
                if "exceptions" not in rule:
                    rule["exceptions"] = ""
                if "rationale" not in rule:
                    rule["rationale"] = ""
        else:
            config["rules"] = self._get_default_rules(moderation_style)

        # Ensure moderation_guidelines is an object
        if "moderation_guidelines" not in config or not isinstance(config["moderation_guidelines"], dict):
            config["moderation_guidelines"] = self._get_default_moderation_guidelines_dict(moderation_style)

        # Ensure auto_moderation_settings exists
        if "auto_moderation_settings" not in config:
            config["auto_moderation_settings"] = self._get_default_auto_mod_settings(moderation_style)

        # Ensure community_settings exists
        if "community_settings" not in config:
            config["community_settings"] = self._get_default_community_settings()

        # Ensure other required fields
        if "suggested_tags" not in config:
            config["suggested_tags"] = topics[:5] if topics else ["discussion"]

        if "community_type" not in config:
            config["community_type"] = "discussion"

        if "estimated_activity_level" not in config:
            config["estimated_activity_level"] = "medium"

        # Enhance rules based on topics
        config["rules"] = self._enhance_rules_for_topics(config["rules"], topics)

        # Enhance auto-moderation settings based on moderation style
        config["auto_moderation_settings"] = self._enhance_auto_mod_settings(
            config["auto_moderation_settings"],
            moderation_style
        )

        return config

    def _get_fallback_comprehensive_config(
        self,
        name: str,
        description: str,
        topics: List[str],
        moderation_style: str
    ) -> Dict[str, Any]:
        """Get fallback comprehensive configuration"""
        return {
            "display_name": name.title(),
            "description": description,
            "rules": self._get_default_rules(moderation_style),
            "moderation_guidelines": self._get_default_moderation_guidelines_dict(moderation_style),
            "auto_moderation_settings": self._get_default_auto_mod_settings(moderation_style),
            "community_settings": self._get_default_community_settings(),
            "suggested_tags": topics[:5] if topics else ["discussion"],
            "community_type": "discussion",
            "estimated_activity_level": "medium",
            "configuration_notes": "Generated using fallback configuration due to AI service issues."
        }

    def _get_fallback_config(self, name: str, description: str) -> Dict[str, Any]:
        """Get fallback configuration if AI generation fails"""
        return {
            "display_name": name.title(),
            "description": description,
            "rules": self._get_default_rules("moderate"),
            "moderation_guidelines": self._get_default_moderation_guidelines("moderate"),
            "auto_moderation_settings": self._get_default_auto_mod_settings("moderate")
        }

    def _get_default_rules(self, moderation_style: str) -> List[Dict[str, Any]]:
        """Get default rules based on moderation style with enhanced format"""
        base_rules = [
            {
                "title": "Be respectful",
                "description": "Treat others with respect and civility. No personal attacks, harassment, or hate speech.",
                "severity": "high",
                "category": "behavior",
                "enforcement_level": "warning",
                "examples": ["Personal attacks", "Harassment", "Hate speech"],
                "exceptions": "Constructive criticism is allowed",
                "rationale": "Maintains a welcoming environment for all community members"
            },
            {
                "title": "No spam or self-promotion",
                "description": "No spam, excessive self-promotion, or off-topic content. Follow Reddit's 9:1 rule.",
                "severity": "high",
                "category": "spam",
                "enforcement_level": "removal",
                "examples": ["Repeated promotional posts", "Off-topic content", "Excessive self-promotion"],
                "exceptions": "Relevant self-promotion with community value",
                "rationale": "Prevents spam and maintains content quality"
            },
            {
                "title": "Stay on topic",
                "description": "Keep discussions relevant to the subreddit's purpose and topics.",
                "severity": "medium",
                "category": "content",
                "enforcement_level": "warning",
                "examples": ["Off-topic posts", "Unrelated discussions"],
                "exceptions": "Meta discussions about the subreddit itself",
                "rationale": "Maintains focus and community identity"
            }
        ]

        if moderation_style == "strict":
            base_rules.extend([
                {
                    "title": "No low-effort posts",
                    "description": "Posts must be substantial and well-thought-out. No simple questions or low-effort content.",
                    "severity": "medium",
                    "category": "content",
                    "enforcement_level": "removal",
                    "examples": ["Simple yes/no questions", "One-word posts", "Low-effort memes"],
                    "exceptions": "High-quality simple posts with community value",
                    "rationale": "Maintains high content quality standards"
                },
                {
                    "title": "Use descriptive titles",
                    "description": "Post titles must clearly describe the content and be informative.",
                    "severity": "medium",
                    "category": "content",
                    "enforcement_level": "warning",
                    "examples": ["Vague titles like 'Help!' or 'Question'", "Clickbait titles"],
                    "exceptions": "Creative titles that still describe the content",
                    "rationale": "Helps users find relevant content and improves searchability"
                },
                {
                    "title": "No duplicate posts",
                    "description": "Search before posting to avoid duplicates. Check if your question has been asked recently.",
                    "severity": "medium",
                    "category": "content",
                    "enforcement_level": "removal",
                    "examples": ["Reposting the same question", "Duplicate content within 24 hours"],
                    "exceptions": "Updates to previous posts or significantly different angles",
                    "rationale": "Prevents clutter and encourages users to search first"
                }
            ])
        elif moderation_style == "lenient":
            base_rules.append({
                "title": "Be constructive",
                "description": "Try to contribute positively to discussions and help build a supportive community.",
                "severity": "low",
                "category": "behavior",
                "enforcement_level": "warning",
                "examples": ["Negative comments without value", "Trolling"],
                "exceptions": "Constructive criticism and honest feedback",
                "rationale": "Encourages positive community interaction"
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
        """Get default auto-moderation settings with enhanced format"""
        base_settings = {
            "auto_remove_spam": True,
            "require_approval": False,
            "content_filters": ["spam", "offensive"],
            "min_account_age_hours": 0,
            "min_karma_required": 0,
            "max_posts_per_hour": 5,
            "max_comments_per_hour": 20,
            "keyword_filters": [],
            "domain_blacklist": [],
            "user_blacklist": [],
            "auto_approve_trusted_users": True,
            "remove_duplicate_posts": True,
            "remove_low_effort_posts": False,
            "require_post_flair": False,
            "require_comment_approval": False,
            "auto_lock_controversial_posts": False,
            "auto_remove_reported_content": True,
            "rate_limit_new_users": True,
            "require_email_verification": False
        }

        if moderation_style == "strict":
            base_settings.update({
                "require_approval": True,
                "min_account_age_hours": 24,
                "min_karma_required": 10,
                "content_filters": ["spam", "offensive", "low_effort", "duplicate"],
                "max_posts_per_hour": 3,
                "max_comments_per_hour": 10,
                "remove_low_effort_posts": True,
                "require_post_flair": True,
                "auto_lock_controversial_posts": True,
                "rate_limit_new_users": True,
                "require_email_verification": True
            })
        elif moderation_style == "lenient":
            base_settings.update({
                "content_filters": ["spam"],
                "max_posts_per_hour": 10,
                "max_comments_per_hour": 50,
                "auto_approve_trusted_users": True,
                "rate_limit_new_users": False
            })

        return base_settings

    def _enhance_rules_for_topics(self, rules: List[Dict[str, Any]], topics: List[str]) -> List[Dict[str, Any]]:
        """Enhance rules based on specific topics"""
        topic_rules = []

        if "programming" in topics or "coding" in topics:
            topic_rules.append({
                "title": "Use proper code formatting",
                "description": "Format code properly using markdown or code blocks for better readability.",
                "severity": "medium",
                "category": "content",
                "enforcement_level": "warning",
                "examples": ["Unformatted code in posts", "Code without proper indentation"],
                "exceptions": "Short code snippets or pseudocode",
                "rationale": "Improves code readability and helps other developers understand your code"
            })

        if "ai" in topics or "artificial intelligence" in topics:
            topic_rules.append({
                "title": "Disclose AI-generated content",
                "description": "Clearly mark any AI-generated content or responses to maintain transparency.",
                "severity": "medium",
                "category": "content",
                "enforcement_level": "warning",
                "examples": ["AI-generated posts without disclosure", "Using AI tools without mentioning"],
                "exceptions": "AI tools used for formatting or minor assistance",
                "rationale": "Maintains transparency and helps users understand content sources"
            })

        if "startup" in topics or "business" in topics:
            topic_rules.append({
                "title": "No self-promotion spam",
                "description": "Limit self-promotion and focus on providing value to the community.",
                "severity": "medium",
                "category": "spam",
                "enforcement_level": "warning",
                "examples": ["Excessive promotion of own products", "Spammy business posts"],
                "exceptions": "Relevant business discussions and valuable insights",
                "rationale": "Maintains community focus on discussion rather than advertising"
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

    def _get_default_moderation_guidelines_dict(self, moderation_style: str) -> Dict[str, str]:
        """Get default moderation guidelines as a dictionary"""
        if moderation_style == "strict":
            return {
                "general_approach": "Moderate content strictly according to community rules. Maintain high standards and remove low-quality content.",
                "content_standards": "Only high-quality, substantial content is allowed. No low-effort posts or simple questions.",
                "user_behavior_expectations": "Users should contribute meaningfully and follow all rules strictly.",
                "enforcement_strategy": "Remove violations immediately. Issue warnings for minor infractions, bans for repeated violations.",
                "appeal_process": "Users can appeal moderation actions by messaging moderators with a clear explanation of why the action was incorrect."
            }
        elif moderation_style == "lenient":
            return {
                "general_approach": "Moderate with a light touch. Focus on removing harmful content while allowing diverse opinions.",
                "content_standards": "Most content is allowed as long as it's not harmful or spam. Encourage creativity and discussion.",
                "user_behavior_expectations": "Be respectful and constructive. Diverse opinions are welcome.",
                "enforcement_strategy": "Only remove clearly harmful content. Use warnings for minor issues.",
                "appeal_process": "Users can easily appeal actions through modmail. Most appeals will be considered favorably."
            }
        else:  # moderate
            return {
                "general_approach": "Balance between maintaining quality and allowing diverse discussions. Moderate fairly according to community rules.",
                "content_standards": "Content should be relevant and contribute to discussion. Some low-effort content may be allowed if it adds value.",
                "user_behavior_expectations": "Be respectful and constructive. Follow community rules and Reddiquette.",
                "enforcement_strategy": "Remove clear violations. Use warnings for minor issues, escalate for repeated violations.",
                "appeal_process": "Users can appeal actions through modmail. Appeals will be reviewed fairly and promptly."
            }

    def _get_default_community_settings(self) -> Dict[str, bool]:
        """Get default community settings"""
        return {
            "allow_images": True,
            "allow_videos": True,
            "allow_links": True,
            "allow_polls": True,
            "allow_live_chat": False,
            "post_approval_required": False,
            "comment_approval_required": False,
            "user_flair_enabled": True,
            "post_flair_enabled": True,
            "wiki_enabled": True,
            "events_enabled": False
        }
