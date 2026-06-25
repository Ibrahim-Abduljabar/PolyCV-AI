import streamlit as st
from groq import Groq
from pypdf import PdfReader
from xhtml2pdf import pisa
import io
import os

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
st.markdown('<div class="subtitle">قم بترجمة سيرتك الذاتية إلى قالب HTML/PDF احترافي وجذاب مئة بالمئة</div>', unsafe_allow_html=True)

# دالة سحرية تحول الـ HTML المصمم بـ CSS إلى ملف PDF حقيقي للتحميل
def convert_html_to_pdf(html_code):
    pdf_buffer = io.BytesIO()
    pisa_status = pisa.pisaDocument(io.BytesIO(html_code.encode("utf-8")), pdf_buffer)
    if not pisa_status.err:
        return pdf_buffer.getvalue()
    return None

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

# 4. المعالجة والترجمة وصناعة الـ HTML
if st.button("🚀 ابدأ المعالجة وإنتاج قالب الـ PDF الاحترافي", use_container_width=True):
    if not GROQ_API_KEY:
        st.error("❌ لم يتم العثور على مفتاح API (API_d) في الإعدادات السرية.")
    elif not cv_dict:
        st.warning("⚠️ الرجاء رفع ملف PDF أولاً.")
    else:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            # نطلب من الموديل إخراج كود HTML منسق بالكامل بـ CSS داخلي بدلاً من النص الخام ليعطي مظهراً مبهراً
            system_instruction = """
            You are an expert CV designer. You must translate the CV and output ONLY a beautifully styled HTML resume template.
            Use inline CSS or a <style> block. Optimize for an executive corporate look (Navy blues, dark greys, clean layout).
            Do NOT include any markdown code blocks, do NOT write ```html or ```. Output raw HTML string directly starting with <html> and ending with </html>.
            Ensure no text overflows and lists look like standard bullet points.
            """
            
            file_tabs = st.tabs(list(cv_dict.keys()))
            for file_index, (file_name, cv_text) in enumerate(cv_dict.items()):
                with file_tabs[file_index]:
                    
                    lang_tabs = st.tabs([f"🌍 إلى {lang}" for lang in target_languages])
                    for lang_index, t_lang in enumerate(target_languages):
                        with lang_tabs[lang_index]:
                            
                            with st.spinner(f"⏳ يقوم PolyCV AI بصناعة القالب المترجم إلى ({t_lang})..."):
                                user_prompt = f"Translate this CV from {source_lang} to {t_lang} and format it as a professional HTML/CSS page:\n\n{cv_text}"
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": user_prompt},
                                    ],
                                    temperature=0.3
                                )
                                
                                # التعديل الجذري الصحيح لفك الـ list بأمان
                                html_output = completion.choices[0].message.content.strip()
                                
                                # عرض المعاينة الحية للموقع مباشرة للمستخدم لتسعد عينه بالشكل الجديد
                                st.components.v1.html(html_output, height=500, scrolling=True)
                                
                                # تحويل الـ HTML المصنوع إلى بايتات PDF جاهزة للتحميل بنفس الشكل والمظهر
                                pdf_data = convert_html_to_pdf(html_output)
                                
                                if pdf_data:
                                    st.download_button(
                                        label=f"📥 تحميل السيرة الذاتية بتنسيق PDF الاحترافي ({t_lang})",
                                        data=pdf_data,
                                        file_name=f"Professional_CV_{t_lang}.pdf",
                                        mime="application/pdf",
                                        key=f"btn_{file_index}_{lang_index}"
                                    )
                                else:
                                    st.error("❌ فشل في تحويل قالب الـ HTML إلى ملف PDF.")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال بالخادم: {e}")

st.sidebar.markdown("---")
st.sidebar.write("⚡ Powered by PolyCV HTML-to-PDF Template Engine")
