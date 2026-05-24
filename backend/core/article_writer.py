import os
import httpx

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

async def write_full_article(topic: str, sections: list) -> dict:
    """
    Calls Groq LLaMA 3.3 to write a full article based on the provided section plan.
    """
    if not GROQ_API_KEY:
        return {"error": "Chưa cấu hình GROQ_API_KEY"}
        
    prompt = f"Bạn là một chuyên gia viết content SEO hàng đầu bằng Tiếng Việt. Hãy viết một bài viết hoàn chỉnh và chuyên sâu về chủ đề: '{topic}'.\n\n"
    prompt += "Tuân thủ nghiêm ngặt dàn ý sau:\n"
    for sec in sections:
        prompt += f"## {sec.get('heading')} (Khoảng {sec.get('word_target', 300)} từ)\n"
        if sec.get('strategic_angle'):
            prompt += f"- Góc độ tiếp cận (Angle): {sec.get('strategic_angle')}\n"
        if sec.get('engagement_hook'):
            prompt += f"- Mở bài (Hook): {sec.get('engagement_hook')}\n"
        if sec.get('knowledge_gaps') and len(sec.get('knowledge_gaps')) > 0:
            prompt += f"- Bắt buộc đề cập: {', '.join(sec.get('knowledge_gaps'))}\n"
        if sec.get('cta'):
            prompt += f"- Lời kêu gọi (CTA): {sec.get('cta')}\n"
        prompt += "\n"
            
    prompt += "Yêu cầu định dạng:\n"
    prompt += "- Trả về văn bản Markdown.\n"
    prompt += "- Sử dụng H2 (##) cho các tiêu đề phần.\n"
    prompt += "- Viết nội dung cực kỳ tự nhiên, thu hút, có giá trị cao, không dùng những từ ngữ sáo rỗng của AI (như 'trong kỷ nguyên số', 'tóm lại').\n"

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a top-tier Vietnamese SEO content writer. Produce high-quality, engaging, and formatting-rich Markdown articles."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 8000
                },
                timeout=180.0
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"content": content}
    except httpx.HTTPStatusError as e:
        return {"error": f"Lỗi HTTP {e.response.status_code} khi gọi Groq API: {e.response.text}"}
    except Exception as e:
        return {"error": f"Lỗi gọi Groq API: {str(e)}"}
