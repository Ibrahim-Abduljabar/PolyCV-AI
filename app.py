import streamlit as st
from groq import Groq
from pypdf import PdfReader
import io
import os

# 1. إعدادات الصفحة وواجهة المستخدم المتقدمة باسم المنتج PolyCV AI
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
st.markdown('<div class="subtitle">ترجم وحوّر عدة سير ذاتية في نفس الوقت باحترافية مطلقة متوافقة مع أنظمة الفرز العالمية دون أي هلوسة أو مساس ببياناتك الحساسة</div>', unsafe_allow_html=True)

# 2. جلب مفتاح الـ API بأمان متوافق مع Streamlit Cloud
GROQ_API_KEY = st.secrets.get("API_d") or os.environ.get("API_d")

st.sidebar.header("⚙️ PolyCV AI Control Panel")
if not GROQ_API_KEY:
    api_key_input = st.sidebar.text_input("أدخل مفتاح Groq API Key يدوياً:", type="password")
    final_api_key = api_key_input
else:
    st.sidebar.success("✅ تم جلب مفتاح API_d بأمان من الـ Secrets!")
    final_api_key = GROQ_API_KEY

source_lang = st.sidebar.selectbox(
    "لغة السير الذاتية الحالية (Original Language):",
    ["Arabic", "English", "French", "Spanish", "German", "Turkish", "Hindi"]
)

target_lang = st.sidebar.selectbox(
    "اللغة المستهدفة للترجمة (Target Language):",
    ["English", "Arabic", "French", "Spanish", "German", "Turkish", "Urdu"],
    index=0
)

# 3. قسم رفع ملفات متعددة (الميزة الاحترافية)
st.subheader("📁 ارفع ملف سيرة ذاتية واحد أو أكثر (PDF)")
uploaded_files = st.file_uploader("يمكنك اختيار عدة ملفات PDF معاً وترجمتها دفعة واحدة عبر PolyCV AI:", type=["pdf"], accept_multiple_files=True)

cv_dict = {}

if uploaded_files:
    for uploaded_file in uploaded_files:
        try:
            pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
            extracted_pages = [page.extract_text() for page in pdf_reader.pages]
            full_text = "\n".join(extracted_pages)
            if full_text.strip():
                cv_dict[uploaded_file.name] = full_text
            else:
                st.warning(f"⚠️ الملف '{uploaded_file.name}' يبدو فارغاً أو عبارة عن صور ولم نتمكن من قراءة نصه.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف {uploaded_file.name}: {e}")
    
    if cv_dict:
        st.success(f"✅ PolyCV AI جاهز الآن لمعالجة ({len(cv_dict)}) سيرة ذاتية فوراً!")

# 4. زر التشغيل والمعالجة عبر Groq
if st.button("بدء الترجمة الجماعية عبر PolyCV AI 🚀", use_container_width=True):
    if not final_api_key:
        st.error("❌ الرجاء التأكد من وجود مفتاح Groq API Key في الـ Secrets أو إدخاله في الشريط الجانبي!")
    elif not cv_dict:
        st.warning("⚠️ الرجاء رفع ملفات PDF تحتوي على نصوص واضحة أولاً.")
    elif source_lang == target_lang:
        st.warning("⚠️ لغة المدخلات هي نفسها لغة المخرجات المستهدفة. يرجى تغيير اللغة المستهدفة.")
    else:
        result_tabs = st.tabs(list(cv_dict.keys()))
        
        try:
            client = Groq(api_key=final_api_key)
            
            system_instruction = """
            You are PolyCV AI, an advanced, strict, non-conversational CV Translator and ATS Optimization expert.
            Your ultimate priority is zero-hallucination. You must preserve the integrity of the data with 100% fidelity.
            
            UNBREAKABLE INSTRUCTIONS TO PREVENT HALLUCINATION:
            1. NEVER alter, forge, change, omit, or add any numbers, years, dates, phone numbers, email addresses, websites, or hyperlinks. They must remain exactly as they appear in the original source text.
            2. For proper nouns (names of universities, companies, cities, or people), keep them accurate, only translate or transliterate them properly to the target language without changing the entity itself.
            3. Translate the professional skills, responsibilities, and achievements into executive, high-level corporate terminology appropriate for ATS optimization.
            4. Do NOT output any conversational text, pleasantries, or introductory sentences like "Here is your translation". Output ONLY the finalized professional Markdown format of the CV.
            5. Double-check all dates and contacts against the input before outputting.
            """
            
            for index, (file_name, cv_text) in enumerate(cv_dict.items()):
                with result_tabs[index]:
                    with st.spinner(f"⚡ PolyCV AI يترجم حالياً: {file_name}..."):
                        
                        user_prompt = f"""
                        Translate this specific CV from {source_lang} to {target_lang}. Maximize ATS optimization.
                        
                        CV Input Text:
                        ---
                        {cv_text}
                        ---
                        """
                        
                        completion = client.chat.completions.create(
                            model="llama3-70b-8192",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "user", "content": user_prompt}
                            ],
                            temperature=0.0,
                            max_tokens=4000
                        )
                        
                        translated_output = completion.choices.message.content
                        
                        st.success(f"🎉 تم إنهاء ترجمة: {file_name}")
                        st.markdown(f"### 📄 السيرة الذاتية المترجمة لملف: {file_name}")
                        st.markdown(translated_output)
                        st.text_area(f"انسخ نص {file_name} المترجم من هنا:", value=translated_output, height=250, key=f"text_{index}")
                        
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء الاتصال بخوادم Groq: {e}")

st.sidebar.markdown("---")
st.sidebar.write("⚡ Powered by PolyCV AI Engine & Groq Cloud")
st.sidebar.write("Developed by Ibrahim - Pre-revenue Startup Studio")
