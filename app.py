import streamlit as st
from groq import Groq
from pypdf import PdfReader
from xhtml2pdf import pisa
import json
import io
import os
import re

# 1. التهيئة وإعدادات الصفحة لواجهة المستخدم PolyCV AI
st.set_page_config(page_title="PolyCV AI - Global CV Translator", page_icon="🌐", layout="wide")

st.markdown("""
<style>
    .main-title { font-size: 34px; font-weight: bold; text-align: center; color: #1E3A8A; margin-bottom: 5px; }
    .brand-sub { font-size: 14px; font-weight: bold; text-align: center; color: #3B82F6; letter-spacing: 2px; margin-bottom: 10px; }
    .subtitle { font-size: 18px; text-align: center; color: #4B5563; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🌐 PolyCV AI</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-sub">GLOBAL MULTI-CV TRANSLATION & ATS LOCALIZATION ENGINE</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">قم بترجمة سيرتك الذاتية وحقنها داخل قوالب تنفيذية فاخرة ومصممة بأعلى معايير الـ ATS</div>', unsafe_allow_html=True)

# دالة تحويل الـ HTML إلى بايتات PDF جاهزة للتحميل
def convert_html_to_pdf(html_code):
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.pisaDocument(io.BytesIO(html_code.encode("utf-8")), pdf_buffer)
    if not pisa_status.err:
        return pdf_buffer.getvalue()
    return None

# دالة لتنظيف مخرجات الـ JSON لضمان عدم حدوث تعليق
def clean_json_string(raw_str):
    raw_str = raw_str.strip()
    if raw_str.startswith("```json"):
        raw_str = raw_str[7:]
    if raw_str.startswith("```"):
        raw_str = raw_str[3:]
    if raw_str.endswith("```"):
        raw_str = raw_str[:-3]
    return raw_str.strip()

# دالة بناء قالب الـ HTML الفاخر وحقن بيانات الـ JSON بداخله
def render_premium_template(data):
    name = data.get("name", "")
    title = data.get("professional_title", "")
    contact = data.get("contact_information", {})
    summary = data.get("professional_summary", "")
    
    contact_lines = [f"<li>{k}: {v}</li>" for k, v in contact.items() if v]
    contact_html = "".join(contact_lines)
    
    experience_html = ""
    for exp in data.get("work_experience", []):
        achievements_li = "".join([f"<li>{ach}</li>" for ach in exp.get("achievements", [])])
        experience_html += f"""
        <div class="section-item">
            <div class="item-header">
                <span class="bold">{exp.get("role", "")}</span> - {exp.get("company", "")}
                <span class="date">{exp.get("dates", "")}</span>
            </div>
            <ul>{achievements_li}</ul>
        </div>
        """
        
    education_html = ""
    for edu in data.get("education", []):
        education_html += f"""
        <div class="section-item">
            <div class="item-header">
                <span class="bold">{edu.get("degree", "")}</span> - {edu.get("institution", "")}
                <span class="date">{edu.get("dates", "")}</span>
            </div>
        </div>
        """

    skills_li = "".join([f"<li>{skin}</li>" for skin in data.get("skills", [])])
    langs_li = "".join([f"<li>{lang}</li>" for lang in data.get("languages", [])])

    html_template = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: letter; margin: 15mm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333333; line-height: 1.4; font-size: 10pt; }}
            .header {{ border-bottom: 2px solid #1E3A8A; padding-bottom: 10px; margin-bottom: 15px; }}
            .name {{ font-size: 24pt; font-weight: bold; color: #1E3A8A; text-transform: uppercase; margin: 0; }}
            .title {{ font-size: 12pt; color: #3B82F6; font-weight: bold; margin: 2px 0 5px 0; letter-spacing: 1px; }}
            .contact-list {{ list-style-type: none; padding: 0; margin: 5px 0 0 0; font-size: 9pt; color: #4B5563; }}
            .contact-list li {{ display: inline; margin-right: 15px; }}
            .section-title {{ font-size: 12pt; font-weight: bold; color: #1E3A8A; background-color: #F3F4F6; padding: 4px 8px; margin-top: 15px; margin-bottom: 8px; text-transform: uppercase; }}
            .section-item {{ margin-bottom: 10px; }}
            .item-header {{ font-size: 10pt; margin-bottom: 3px; position: relative; }}
            .bold {{ font-weight: bold; color: #111827; }}
            .date {{ float: right; color: #6B7280; font-size: 9pt; font-weight: normal; }}
            ul {{ margin-top: 2px; margin-bottom: 5px; padding-left: 20px; }}
            li {{ margin-bottom: 2px; color: #374151; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="name">{name}</div>
            <div class="title">{title}</div>
            <ul class="contact-list">{contact_html}</ul>
        </div>
        
        {f'<div class="section-title">Professional Summary</div><p>{summary}</p>' if summary else ''}
        
        {f'<div class="section-title">Work Experience</div>{experience_html}' if experience_html else ''}
        
        {f'<div class="section-title">Education</div>{education_html}' if education_html else ''}
        
        <table style="width: 100%; margin-top: 10px;">
            <tr>
                {f'<td style="width: 50%; vertical-align: top;"><div class="section-title">Skills</div><ul>{skills_li}</ul></td>' if skills_li else ''}
                {f'<td style="width: 50%; vertical-align: top;"><div class="section-title">Languages</div><ul>{langs_li}</ul></td>' if langs_li else ''}
            </tr>
        </table>
    </body>
    </html>
    """
    return html_template

# 2. إدارة مفاتيح الـ API لـ Groq (متغيرك الأصلي المعتمد)
GROQ_API_KEY = st.secrets.get("API_d") or os.environ.get("API_d")

st.sidebar.header("🌐 PolyCV AI Control Panel")
source_lang = st.sidebar.selectbox("🌐 اللغة الحالية للسيرة الذاتية:", ["Arabic", "English", "French", "Spanish", "German"])
target_lang_1 = st.sidebar.selectbox("اللغة المستهدفة الأولى:", ["English", "Arabic", "French", "Spanish", "German"])
num_languages = st.sidebar.radio("اختر عدد اللغات الإضافية:", [1, 2, 3], index=0)

target_languages = [target_lang_1]
target_languages = list(set(target_languages))

# 3. رفع ملفات الـ PDF
st.subheader("📁 ارفع ملف سيرة ذاتية أو أكثر (PDF)")
uploaded_files = st.file_uploader("اختر ملفات السير الذاتية الخاصة بك بصيغة PDF:", type=["pdf"], accept_multiple_files=True)

cv_dict = {}
if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
            extracted_pages = [page.extract_text() for page in pdf_reader.pages]
            full_text = "\n".join(extracted_pages)
            if full_text.strip():
                cv_dict[uploaded_file.name] = full_text
        except Exception as e:
            st.error(f"❌ حدث خطأ في قراءة الملف: {e}")

# 4. المعالجة والترجمة الهيكلية
if st.button("🚀 ابدأ حقن البيانات داخل القالب التنفيذي الفاخر الآن", use_container_width=True):
    if not GROQ_API_KEY:
        st.error("❌ لم يتم العثور على مفتاح API (API_d) في الإعدادات السرية.")
    elif not cv_dict:
        st.warning("⚠️ الرجاء رفع ملف PDF أولاً.")
    else:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            system_instruction = """
            You are an elite ATS CV parser and translator. You must translate the input CV text and format it into a valid JSON object matching the schema below.
            Do NOT include any markdown code block wrap. Output ONLY the raw valid JSON string.
            
            JSON Schema:
            {
                "name": "Full Name",
                "professional_title": "Target/Current Job Title",
                "contact_information": {"Phone": "...", "Email": "...", "LinkedIn": "..."},
                "professional_summary": "Short professional bio paragraph",
                "work_experience": [
                    {"role": "Job Title", "company": "Company Name", "dates": "Date Range", "achievements": ["Achievement 1", "Achievement 2"]}
                ],
                "education": [
                    {"degree": "Degree/Major", "institution": "University/School", "dates": "Date Range"}
                ],
                "skills": ["Skill 1", "Skill 2"],
                "languages": ["Language 1", "Language 2"]
            }
            """
            
            file_tabs = st.tabs(list(cv_dict.keys()))
            for file_index, (file_name, cv_text) in enumerate(cv_dict.items()):
                with file_tabs[file_index]:
                    
                    lang_tabs = st.tabs([f"🌍 إلى {lang}" for lang in target_languages])
                    for lang_index, t_lang in enumerate(target_languages):
                        with lang_tabs[lang_index]:
                            
                            with st.spinner(f"⏳ يقوم PolyCV AI بترجمة وتنسيق البيانات إلى قالب ({t_lang})..."):
                                user_prompt = f"Translate this CV from {source_lang} to {t_lang} and output the structured JSON:\n\n{cv_text}"
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": user_prompt},
                                    ],
                                    temperature=0.1
                                )
                                
                                raw_json = completion.choices[0].message.content
                                clean_json = clean_json_string(raw_json)
                                
                                try:
                                    cv_data = json.loads(clean_json)
