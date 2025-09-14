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
                        "text": text,
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
                return self._parse_winston_response(result["result"])

        except httpx.TimeoutException:
            logger.error("Winston AI API timeout")
            return self._get_fallback_result("API timeout")
        except Exception as e:
            logger.error(f"Winston AI detection error: {e}")
            return self._get_fallback_result(f"Detection error: {str(e)}")

    def _parse_winston_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Winston AI API response into our standard format"""
        try:
            # Winston AI returns different response structure
            # We need to adapt it to our expected format
            is_ai_generated = False
            confidence = 0.0
            detection_methods = []
            recommendations = []

            # Parse the actual detection result
            if isinstance(result, dict):
                # Look for common Winston AI response fields
                if "is_ai_generated" in result:
                    is_ai_generated = bool(result["is_ai_generated"])
                elif "ai_probability" in result:
                    confidence = float(result["ai_probability"])
                    is_ai_generated = confidence > 0.5
                elif "confidence" in result:
                    confidence = float(result["confidence"])
                    is_ai_generated = confidence > 0.5

                # Extract confidence if available
                if "confidence" in result:
                    confidence = float(result["confidence"])
                elif "ai_probability" in result:
                    confidence = float(result["ai_probability"])

                # Extract detection methods/indicators
                if "indicators" in result and isinstance(result["indicators"], list):
                    detection_methods = [
                        {"method": "winston_ai", "indicator": indicator}
                        for indicator in result["indicators"]
                    ]
                elif "reasons" in result and isinstance(result["reasons"], list):
                    detection_methods = [
                        {"method": "winston_ai", "indicator": reason}
                        for reason in result["reasons"]
                    ]

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
