import json
import os
import openai
from typing import Dict, List, Any

# Configure OpenAI API from environment variable
api_key = os.environ.get('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable not set")

openai.api_key = api_key


def warmup_model():
    """Warmup the model to reduce first-call latency"""
    try:
        openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=1,
            temperature=0
        )
    except Exception:
        pass


def classify_ticket(membershipType: str, helpCategoryOptions: List[Dict], description: str) -> Dict[str, str]:
    """
    GPT-4o-mini classifier for support ticket categorization
    """
    other_category = None
    for cat in helpCategoryOptions:
        if cat['label'].lower() in ['other', 'others', 'general']:
            other_category = cat
            break
    fallback_category = other_category if other_category else helpCategoryOptions[0]

    category_list = [f"{i+1}. {cat['label']}" for i, cat in enumerate(helpCategoryOptions)]
    categories_text = "\n".join(category_list)

    prompt = f"""You must classify this query into ONE of these exact categories:

{categories_text}

Rules:
- You MUST respond with the COMPLETE and EXACT category name from the list above
- Do NOT abbreviate, modify, or rephrase the category names
- Do NOT add quotes or extra text
- If unsure, choose the closest match or "Other"

Query: {description}

Selected Category:"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict classifier. You must respond with exactly one of the provided category names. Never create new categories or modify the given names."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=25,
            temperature=0
        )

        classification = response.choices[0].message.content.strip().strip('"').strip("'")

        for category in helpCategoryOptions:
            if category['label'].lower() == classification.lower():
                return category

        classification_lower = classification.lower()
        for category in helpCategoryOptions:
            category_lower = category['label'].lower()
            if "internet" in category_lower and "phone" in category_lower:
                if any(word in classification_lower for word in ["internet", "phone", "wifi", "network", "av", "a/v"]):
                    return category
            category_words = [w for w in category_lower.split() if len(w) > 2 and w not in ['and', 'the', 'a', 'an', 'or']]
            if any(word in classification_lower for word in category_words):
                return category

        return fallback_category

    except Exception:
        raise


def handle_help_and_support_ticket_category(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        membership_type = data.get('membership_type', '')
        help_categories = data.get('options', [])
        description = data.get('description', '')

        if not description or not help_categories:
            return response_wrapper(400, "Missing required fields: description or options", False, {})

        result = classify_ticket(membership_type, help_categories, description)

        return response_wrapper(
            200,
            "Ticket Category Recommended Successfully",
            True,
            {
                "option": [
                    {
                        "id": result["id"],
                        "value": result["label"]
                    }
                ]
            }
        )

    except Exception as e:
        return response_wrapper(500, f"Failed to classify ticket: {str(e)}", False, {})


def lambda_handler(event, context):
    """
    Main Lambda entrypoint
    """
    try:
        if isinstance(event, dict) and 'body' in event:
            try:
                body = json.loads(event['body'])
            except Exception:
                return response_wrapper(400, "Invalid JSON in request body", False, {})
        else:
            body = event  # direct SDK call

        request_type = body.get("type")
        data = body.get("data", {})

        if not request_type:
            return response_wrapper(400, "Missing request type", False, {})

        # ✅ Central dispatcher — add new services here
        service_dispatcher = {
            "HELP_AND_SUPPORT": handle_help_and_support_ticket_category,

            # Example:
            # "BOOKING_INQUIRY": handle_booking_inquiry,
            # "CHECK_AVAILABILITY": handle_check_availability,
        }

        handler_function = service_dispatcher.get(request_type)
        if handler_function:
            return handler_function(data)
        else:
            return response_wrapper(400, f"Unsupported request type: {request_type}", False, {})

    except Exception as e:
        return response_wrapper(500, f"Unexpected error: {str(e)}", False, {})


def response_wrapper(status_code: int, message: str, success: bool, data: dict):
    return {
        "statusCode": status_code,
        "headers": default_headers(),
        "body": json.dumps({
            "success": success,
            "statusCode": status_code,
            "message": message,
            "data": data
        })
    }


def default_headers():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    }


# Warmup on cold start
warmup_model() 