import google.generativeai as genai
from flask import current_app


def get_ai_response(user_message_text, chat_history=None):
    api_key = current_app.config.get('GOOGLE_API_KEY')
    if not api_key:
        current_app.logger.error("GOOGLE_API_KEY not configured.")
        return "AI Service Error: API Key is missing."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    system_instruction = "You are a friendly and helpful chat assistant. Keep your responses concise and engaging."
    messages_for_api = [{'role': 'user', 'parts': [system_instruction]}]

    if chat_history:
        for msg in chat_history:
            role = "user" if not msg.is_from_ai else "model"
            messages_for_api.append({'role': role, 'parts': [msg.content]})

    messages_for_api.append({'role': 'user', 'parts': [user_message_text]})

    try:
        response = model.generate_content(messages_for_api)

        if not response.candidates or not response.text:
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                reason = response.prompt_feedback.block_reason.name
                current_app.logger.warning(f"AI response blocked. Reason: {reason}")
                return f"AI Error: Response blocked ({reason})."
            return "AI Error: No valid response."

        return response.text

    except Exception as e:
        current_app.logger.error(f"Google AI API Error: {e}")
        if "API key not valid" in str(e):
            return "AI Service Error: Invalid API key."
        if "quota" in str(e).lower():
            return "AI Service Error: Quota exceeded."
        return f"AI Service Error: {type(e).__name__}"
