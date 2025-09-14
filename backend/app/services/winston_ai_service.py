import httpx
import json
import logging
from typing import Dict, Any, Optional
from ..config import settings

logger = logging.getLogger(__name__)

class WinstonAIService:
    """Service for Winston AI text detection using their MCP API"""

    def __init__(self):
        self.api_key = settings.WINSTON_AI_API_KEY
        self.base_url = settings.WINSTON_AI_BASE_URL
        self.enabled = settings.WINSTON_AI_ENABLED

        if not self.api_key and self.enabled:
            logger.warning("Winston AI API key not found. AI detection will be disabled.")
            self.enabled = False

    async def detect_ai_text(
        self,
        text: str,
        min_length: int = 300
    ) -> Dict[str, Any]:
        """
        Detect if text is AI-generated using Winston AI

        Args:
            text: Text to analyze
            min_length: Minimum text length required (Winston AI requirement)

        Returns:
            Dict containing detection results
        """
        if not self.enabled:
            return self._get_fallback_result("Winston AI disabled")

        if len(text.strip()) < min_length:
            return self._get_fallback_result(f"Text too short (minimum {min_length} characters)")

        try:
            # Prepare JSON-RPC 2.0 request
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "ai-text-detection",
                    "arguments": {
                        "text": text.strip(),
                        "apiKey": self.api_key
                    }
                }
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"Winston AI API error: {response.status_code} - {response.text}")
                    return self._get_fallback_result(f"API error: {response.status_code}")

                result = response.json()

                # Handle JSON-RPC response
                if "error" in result:
                    logger.error(f"Winston AI API error: {result['error']}")
                    return self._get_fallback_result(f"API error: {result['error'].get('message', 'Unknown error')}")

                if "result" not in result:
                    logger.error("Invalid Winston AI response format")
                    return self._get_fallback_result("Invalid API response")

                # Parse Winston AI response
                # The result might be wrapped in a content array
                actual_result = result["result"]
                logger.info(f"Winston AI raw result: {actual_result}")

                if isinstance(actual_result, dict) and "content" in actual_result:
                    # Extract the actual JSON from the content array
                    content = actual_result["content"]
                    logger.info(f"Winston AI content: {content}")

                    if isinstance(content, list) and len(content) > 0:
                        content_item = content[0]
                        logger.info(f"Winston AI content item: {content_item}")

                        if isinstance(content_item, dict) and "text" in content_item:
                            import json
                            try:
                                json_text = content_item["text"]
                                logger.info(f"Winston AI JSON text: {json_text[:200]}...")

                                # Winston AI returns text with explanation + JSON
                                # Extract JSON from the text (look for "Full API Response :")
                                if "Full API Response :" in json_text:
                                    json_start = json_text.find("Full API Response :") + len("Full API Response :")
                                    json_text = json_text[json_start:].strip()

                                actual_result = json.loads(json_text)
                                logger.info(f"Parsed Winston AI result: {actual_result}")
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse Winston AI JSON response: {e}")
                                logger.error(f"JSON text was: {json_text}")
                                return self._get_fallback_result("Invalid JSON response from Winston AI")

                return self._parse_winston_response(actual_result)

        except httpx.TimeoutException:
            logger.error("Winston AI API timeout")
            return self._get_fallback_result("API timeout")
        except Exception as e:
            logger.error(f"Winston AI detection error: {e}")
            return self._get_fallback_result(f"Detection error: {str(e)}")

    def _parse_winston_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Winston AI API response into our standard format"""
        try:
            # Winston AI returns a specific response structure
            # Based on the actual API response format
            is_ai_generated = False
            confidence = 0.0
            detection_methods = []
            recommendations = []

            # Parse the actual detection result
            if isinstance(result, dict):
                # Winston AI uses 'score' field: 0-100 range, where higher = more AI
                if "score" in result:
                    score = float(result["score"])
                    # Winston AI returns percentage (0-100), convert to 0-1 range
                    confidence = score / 100.0
                    is_ai_generated = confidence > 0.5
                elif "is_ai_generated" in result:
                    is_ai_generated = bool(result["is_ai_generated"])
                elif "ai_probability" in result:
                    confidence = float(result["ai_probability"])
                    is_ai_generated = confidence > 0.5

                # Extract confidence if not already set
                if confidence == 0.0 and "confidence" in result:
                    confidence = float(result["confidence"])
                elif confidence == 0.0 and "ai_probability" in result:
                    confidence = float(result["ai_probability"])

                # Extract detection methods/indicators
                if "sentences" in result and isinstance(result["sentences"], list):
                    # Analyze sentence-level scores
                    sentence_scores = [s.get("score", 0) for s in result["sentences"] if isinstance(s, dict)]
                    if sentence_scores:
                        avg_sentence_score = sum(sentence_scores) / len(sentence_scores)
                        detection_methods.append({
                            "method": "winston_ai",
                            "indicator": f"Average sentence score: {avg_sentence_score:.2f}"
                        })

                # Add readability score as indicator
                if "readability_score" in result:
                    readability = float(result["readability_score"])
                    detection_methods.append({
                        "method": "winston_ai",
                        "indicator": f"Readability score: {readability:.2f}"
                    })

                # Add attack detection indicators
                if "attack_detected" in result and isinstance(result["attack_detected"], dict):
                    attacks = [k for k, v in result["attack_detected"].items() if v]
                    if attacks:
                        detection_methods.append({
                            "method": "winston_ai",
                            "indicator": f"Attack patterns detected: {', '.join(attacks)}"
                        })

                # Generate recommendations based on confidence
                if is_ai_generated and confidence > 0.7:
                    recommendations.append({
                        "action": "flag",
                        "reason": f"High confidence AI-generated content ({confidence:.1%})"
                    })
                elif is_ai_generated and confidence > 0.5:
                    recommendations.append({
                        "action": "review",
                        "reason": f"Moderate confidence AI-generated content ({confidence:.1%})"
                    })
                else:
                    recommendations.append({
                        "action": "approve",
                        "reason": "Content appears to be human-generated"
                    })

            return {
                "is_ai_generated": is_ai_generated,
                "confidence": min(1.0, max(0.0, confidence)),
                "detection_methods": detection_methods,
                "recommendations": recommendations,
                "source": "winston_ai",
                "raw_response": result
            }

        except Exception as e:
            logger.error(f"Error parsing Winston AI response: {e}")
            return self._get_fallback_result(f"Response parsing error: {str(e)}")

    def _get_fallback_result(self, reason: str) -> Dict[str, Any]:
        """Get fallback result when Winston AI is unavailable"""
        return {
            "is_ai_generated": False,
            "confidence": 0.3,
            "detection_methods": [{"method": "fallback", "indicator": reason}],
            "recommendations": [{"action": "review", "reason": "AI detection unavailable - manual review recommended"}],
            "source": "fallback",
            "raw_response": {"error": reason}
        }

    async def health_check(self) -> Dict[str, Any]:
        """Check if Winston AI service is healthy"""
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "Winston AI is disabled"
            }

        if not self.api_key:
            return {
                "status": "error",
                "message": "Winston AI API key not configured"
            }

        try:
            # Test with a simple request
            test_text = "This is a test message to check if the Winston AI service is working properly. " * 10
            result = await self.detect_ai_text(test_text)

            if result["source"] == "winston_ai":
                return {
                    "status": "healthy",
                    "message": "Winston AI service is operational"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Winston AI service error: {result['detection_methods'][0]['indicator']}"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Winston AI health check failed: {str(e)}"
            }
