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
st.markdown('<div class="subtitle">ترجم وحوّر عدة سير ذاتية في نفس الوقت إلى عدة لغات باحترافية مطلقة متوافقة مع أنظمة الفرز العالمية دون أي هلوسة</div>', unsafe_allow_html=True)

# 2. جلب مفتاح الـ API بأمان في الخلفية وصمت تام
GROQ_API_KEY = st.secrets.get("API_d") or os.environ.get("API_d")

st.sidebar.header("⚙️ PolyCV AI Control Panel")

if not GROQ_API_KEY:
    api_key_input = st.sidebar.text_input("أدخل مفتاح Groq API Key الخاص بك:", type="password")
    final_api_key = api_key_input
else:
    final_api_key = GROQ_API_KEY

source_lang = st.sidebar.selectbox(
    "لغة السير الذاتية الحالية (Original Language):",
    ["Arabic", "English", "French", "Spanish", "German", "Turkish", "Hindi"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 اللغات المستهدفة (Target Languages)")

target_lang_1 = st.sidebar.selectbox("اللغة المستهدفة الأساسية:", ["English", "Arabic", "French", "Spanish", "German", "Turkish"], index=0)
num_languages = st.sidebar.radio("عدد اللغات المستهدفة للترجمة الحالية:", [1, 2, 3], index=0)

target_languages = [target_lang_1]

if num_languages >= 2:
    target_lang_2 = st.sidebar.selectbox("اللغة المستهدفة الثانية:", ["French", "Spanish", "German", "Turkish", "English", "Arabic"], index=0)
    target_languages.append(target_lang_2)

if num_languages == 3:
    target_lang_3 = st.sidebar.selectbox("اللغة المستهدفة الثالثة:", ["Spanish", "German", "Turkish", "English", "Arabic", "French"], index=0)
    target_languages.append(target_lang_3)

target_languages = list(set(target_languages))

# 3. قسم رفع ملفات متعددة (PDF)
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
                st.warning(f"⚠️ الملف '{uploaded_file.name}' يبدو فارغاً ولم نتمكن من قراءة نصه.")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف {uploaded_file.name}: {e}")
    
    if cv_dict:
        st.success(f"✅ PolyCV AI جاهز الآن لمعالجة ({len(cv_dict)}) سيرة ذاتية إلى ({len(target_languages)}) لغات!")

# 4. زر التشغيل والمعالجة عبر Groq
if st.button("بدء الترجمة الجماعية عبر PolyCV AI 🚀", use_container_width=True):
    if not final_api_key:
        st.error("❌ نعتذر، هناك مشكلة في إعدادات خادم الـ API. يرجى تزويد المفتاح في الشريط الجانبي.")
    elif not cv_dict:
        st.warning("⚠️ الرجاء رفع ملفات PDF تحتوي على نصوص واضحة أولاً.")
    else:
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
            
            file_tabs = st.tabs(list(cv_dict.keys()))
            
            for file_index, (file_name, cv_text) in enumerate(cv_dict.items()):
                with file_tabs[file_index]:
                    st.markdown(f"### 📄 معالجة الملف: **{file_name}**")
                    lang_tabs = st.tabs([f"لغة: {lang}" for lang in target_languages])
                    
                    for lang_index, t_lang in enumerate(target_languages):
                        with lang_tabs[lang_index]:
                            if source_lang == t_lang:
                                st.warning(f"⚠️ اللغة المستهدفة ({t_lang}) هي نفس اللغة الأصلية.")
                                continue
                                
                            with st.spinner(f"⚡ PolyCV AI يترجم حالياً إلى {t_lang}..."):
                                user_prompt = f"""
                                Translate this specific CV from {source_lang} to {t_lang}. Maximize ATS optimization.
                                
                                CV Input Text:
                                ---
                                {cv_text}
                                ---
                                """
                                
                                # تم التثبيت هنا على النموذج المعتمد والمتاح رسمياً للجميع حالياً من جروق لمنع الـ 404
                                completion = client.chat.completions.create(
                                    model="llama-3.1-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": user_prompt}
                                    ],
                                    temperature=0.0,
                                    max_tokens=4000
                                )
                                
                                translated_output = completion.choices.message.content
                                
                                st.success(f"🎉 تم إنهاء الترجمة والتحوير إلى {t_lang} بنجاح!")
                                st.markdown(translated_output)
                                st.text_area(f"انسخ نص الترجمة ({t_lang}) من هنا:", value=translated_output, height=200, key=f"text_{file_index}_{lang_index}")
                                
        except Exception as e:
            st.error(f"❌ حدث خطأ في خادم الـ API أو المفتاح المستخدم: {str(e)}")

st.sidebar.markdown("---")
st.sidebar.write("⚡ Powered by PolyCV AI Engine & Groq Cloud")
st.sidebar.write("Developed by Pre-revenue Startup Studio")
