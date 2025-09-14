from typing import Dict, Any
from .claude_service import ClaudeService
from .winston_ai_service import WinstonAIService
import logging

logger = logging.getLogger(__name__)

class ContentDetectionService:
    def __init__(self):
        self.claude_service = ClaudeService()
        self.winston_ai_service = WinstonAIService()

    async def detect_content(
        self,
        content: str,
        content_type: str = "post"
    ) -> Dict[str, Any]:
        """Detect if content is AI-generated using Winston AI (primary) and Claude (fallback)"""
        try:
            # Try Winston AI first (more accurate for AI detection)
            winston_result = await self.winston_ai_service.detect_ai_text(content)

            if winston_result["source"] == "winston_ai":
                # Winston AI succeeded, use its result
                result = winston_result
                logger.info(f"Winston AI detection: {winston_result['is_ai_generated']} (confidence: {winston_result['confidence']:.2f})")
            else:
                # Winston AI failed, fallback to Claude
                logger.warning(f"Winston AI failed: {winston_result['detection_methods'][0]['indicator']}, falling back to Claude")
                claude_result = await self.claude_service.detect_ai_content(content)
                result = claude_result
                logger.info(f"Claude detection: {claude_result.get('is_ai_generated', False)} (confidence: {claude_result.get('confidence', 0.5):.2f})")

            # Ensure the result has the expected structure
            if not isinstance(result, dict):
                result = self._get_fallback_detection()

            # Validate and enhance the result
            result = self._validate_and_enhance_detection(result, content, content_type)

            return result

        except Exception as e:
            logger.error(f"Error detecting content: {e}")
            return self._get_fallback_detection()

    def _validate_and_enhance_detection(
        self,
        result: Dict[str, Any],
        content: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Validate and enhance the detection result"""

        # Ensure required fields exist
        if "is_ai_generated" not in result:
            result["is_ai_generated"] = False

        if "confidence" not in result:
            result["confidence"] = 0.5

        if "indicators" not in result or not isinstance(result["indicators"], list):
            result["indicators"] = []

        if "recommendations" not in result or not isinstance(result["recommendations"], list):
            result["recommendations"] = []

        # Add additional analysis based on content characteristics
        additional_indicators = self._analyze_content_characteristics(content)
        result["indicators"].extend(additional_indicators)

        # Add content-type specific analysis
        if content_type == "post":
            result["indicators"].extend(self._analyze_post_characteristics(content))
        elif content_type == "comment":
            result["indicators"].extend(self._analyze_comment_characteristics(content))

        # Adjust confidence based on additional analysis
        result["confidence"] = self._adjust_confidence(result["confidence"], additional_indicators)

        # Generate recommendations based on detection result
        if not result["recommendations"]:
            result["recommendations"] = self._generate_recommendations(result["is_ai_generated"], result["confidence"])

        return result

    def _get_fallback_detection(self) -> Dict[str, Any]:
        """Get fallback detection result if AI analysis fails"""
        return {
            "is_ai_generated": False,
            "confidence": 0.3,
            "indicators": ["Analysis failed - unable to determine"],
            "recommendations": [{"action": "review", "reason": "Analysis inconclusive - manual review recommended"}]
        }

    def _analyze_content_characteristics(self, content: str) -> list:
        """Analyze content for AI generation characteristics"""
        indicators = []

        # Check for very formal language
        formal_words = ["furthermore", "moreover", "consequently", "therefore", "thus", "hence"]
        if any(word in content.lower() for word in formal_words):
            indicators.append("Contains formal academic language")

        # Check for repetitive patterns
        words = content.lower().split()
        if len(words) > 10:
            word_freq = {}
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1

            # Check for overused words
            for word, count in word_freq.items():
                if count > len(words) * 0.1:  # Word appears more than 10% of the time
                    indicators.append(f"Repetitive use of '{word}'")

        # Check for perfect grammar and structure
        if self._has_perfect_structure(content):
            indicators.append("Unusually perfect grammar and structure")

        # Check for generic phrases
        generic_phrases = [
            "it is important to note",
            "in conclusion",
            "it should be noted",
            "as mentioned earlier",
            "it is worth noting"
        ]
        if any(phrase in content.lower() for phrase in generic_phrases):
            indicators.append("Contains generic AI-like phrases")

        return indicators

    def _analyze_post_characteristics(self, content: str) -> list:
        """Analyze post-specific characteristics"""
        indicators = []

        # Check for very structured posts
        if content.count('\n') > 5 and len(content) > 200:
            indicators.append("Highly structured format typical of AI-generated content")

        # Check for bullet points or numbered lists
        if content.count('•') > 3 or content.count('1.') > 3:
            indicators.append("Excessive use of bullet points or numbered lists")

        # Check for very long paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if len(para) > 500:
                indicators.append("Very long paragraphs without breaks")

        return indicators

    def _analyze_comment_characteristics(self, content: str) -> list:
        """Analyze comment-specific characteristics"""
        indicators = []

        # Check for very short, generic responses
        if len(content.strip()) < 20:
            generic_responses = ["thanks", "great", "nice", "cool", "awesome", "good point"]
            if content.lower().strip() in generic_responses:
                indicators.append("Generic short response")

        # Check for overly polite language
        polite_phrases = ["thank you so much", "I really appreciate", "that's very kind", "I'm grateful"]
        if any(phrase in content.lower() for phrase in polite_phrases):
            indicators.append("Overly polite language")

        return indicators

    def _has_perfect_structure(self, content: str) -> bool:
        """Check if content has unusually perfect structure"""
        # Simple heuristic: check for proper sentence structure
        sentences = content.split('.')
        if len(sentences) < 3:
            return False

        # Check if most sentences start with capital letters
        proper_caps = sum(1 for s in sentences if s.strip() and s.strip()[0].isupper())
        return proper_caps / len(sentences) > 0.8

    def _adjust_confidence(self, base_confidence: float, indicators: list) -> float:
        """Adjust confidence based on additional indicators"""
        confidence = base_confidence

        # Increase confidence for AI indicators
        ai_indicators = [
            "Contains formal academic language",
            "Unusually perfect grammar and structure",
            "Contains generic AI-like phrases",
            "Highly structured format typical of AI-generated content"
        ]

        for indicator in indicators:
            if any(ai_indicator in indicator for ai_indicator in ai_indicators):
                confidence = min(1.0, confidence + 0.1)

        # Decrease confidence for human indicators
        human_indicators = [
            "Generic short response",
            "Overly polite language"
        ]

        for indicator in indicators:
            if any(human_indicator in indicator for human_indicator in human_indicators):
                confidence = max(0.0, confidence - 0.1)

        return confidence

    def _generate_recommendations(
        self,
        is_ai_generated: bool,
        confidence: float
    ) -> list:
        """Generate recommendations based on detection result"""
        recommendations = []

        if is_ai_generated and confidence > 0.7:
            recommendations.append({
                "action": "flag",
                "reason": "High confidence that content is AI-generated"
            })
        elif is_ai_generated and confidence > 0.5:
            recommendations.append({
                "action": "review",
                "reason": "Moderate confidence that content is AI-generated - manual review recommended"
            })
        else:
            recommendations.append({
                "action": "approve",
                "reason": "Content appears to be human-generated"
            })

        return recommendations
