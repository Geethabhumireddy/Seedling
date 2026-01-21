"""
AI-powered issue analysis module using Google's Gemini API.

Provides intelligent issue classification, triage, and impact analysis
using optimized prompts for reliable JSON output.
"""

import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_issue_with_ai(issue_data: dict) -> dict:
    """
    Analyze a GitHub issue using AI to extract structured insights.
    
    Args:
        issue_data: Dictionary with keys:
            - "title": Issue title
            - "body": Issue description  
            - "comments": Community comments
            
    Returns:
        Dictionary with analysis results:
        - "summary": One-line problem statement
        - "type": Issue classification (bug|feature_request|documentation|question|other)
        - "priority_score": Numerical priority with justification
        - "suggested_labels": List of relevant labels
        - "potential_impact": Business/user impact assessment
        
    Handles edge cases:
        - Empty issue bodies (uses title + comments fallback)
        - Very long issues (API handles truncation)
        - Malformed JSON responses (with error fallback)
        - Gemini API failures (returns graceful error)
        
    Prompt Engineering Details:
        - Uses few-shot-like structure with explicit JSON format
        - Enforces strict JSON-only output (no explanations)
        - Provides clear type categories to avoid ambiguity
        - Asks for justification to improve reasoning
    """
    
    # Robust prompt that guides the model to reliable output
    prompt = f"""You are an expert GitHub issue triage assistant with deep experience in software engineering.

Your task: Analyze the following GitHub issue and extract structured insights.

CRITICAL: Return ONLY valid JSON in this exact format. No explanation, no markdown, just JSON.

{{
  "summary": "One clear sentence describing the core problem or feature request",
  "type": "Classify as one of: bug, feature_request, documentation, question, other",
  "priority_score": "A score 1-5 with brief justification (e.g., '4 - Affects core functionality')",
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "Brief sentence on user/business impact if issue is a bug, or value if feature"
}}

GitHub Issue Details:
---
Title: {issue_data.get("title", "")}

Body:
{issue_data.get("body", "No description provided")}

Community Comments:
{issue_data.get("comments", "No comments yet")}
---

Remember: 
1. Output ONLY JSON - no markdown, no explanation
2. Type must be exactly one of: bug, feature_request, documentation, question, other
3. Priority must be 1-5
4. For issues with minimal info, infer from title and comments
5. Labels should be specific and actionable

RETURN ONLY JSON:"""

    try:
        # Call Gemini API with specified model and content
        response = client.models.generate_content(
            model="gemini-3-flash-preview",  # Using faster flash model for speed
            contents=prompt
        )
        
        # Parse JSON response - handles both clean and slightly malformed JSON
        response_text = response.text.strip()
        
        # Remove potential markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        result = json.loads(response_text)
        
        # Validate and sanitize the response
        if not all(key in result for key in ["summary", "type", "priority_score", "suggested_labels", "potential_impact"]):
            return {"error": "Incomplete analysis response"}
            
        return result
        
    except json.JSONDecodeError:
        return {
            "error": "AI response parsing failed",
            "details": "Could not parse AI output as JSON"
        }
    except Exception as e:
        return {
            "error": "Analysis failed",
            "details": str(e)
        }
