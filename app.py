import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import re

# Инициализация клиента Gemini
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    try:
        # Получаем список всех доступных субтитров для видео
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Выбираем первые доступные субтитры (любой язык)
        transcript = next(iter(transcript_list))
        transcript_data = transcript.fetch()
        return " ".join([t['text'] for t in transcript_data]), None
    except Exception as e:
        return None, str(e)

st.title("Генератор саммари проповедей")

url = st.text_input("Вставьте ссылку на YouTube:")

if st.button("Сгенерировать саммари"):
    if url:
        video_id = get_video_id(url)
        if video_id:
            with st.spinner("Извлечение текста из YouTube..."):
                text, error_msg = get_transcript(video_id)
                
            if text:
                with st.spinner("Генерация саммари через Gemini..."):
                    prompt = f"""
                    Ты помощник служителя. Сделай краткую выжимку из предоставленного текста проповеди для публикации в чате церкви. 
                    Выдели главную мысль и 3-4 ключевых тезиса.
                    
                    Текст проповеди:
                    {text}
                    """
                    try:
                        response = model.generate_content(prompt)
                        st.subheader("Результат:")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"Ошибка API Gemini: {e}")
            else:
                st.error("Не удалось получить субтитры.")
                st.warning(f"Техническая деталь ошибки: {error_msg}")
        else:
            st.error("Неверный формат ссылки.")
