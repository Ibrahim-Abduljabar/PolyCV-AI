import streamlit as st
from groq import Groq
from pypdf import PdfReader
from fpdf import FPDF
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
st.markdown('<div class="subtitle">قم بترجمة سيرتك الذاتية إلى عدة لغات احترافية في ثوانٍ معدودة بدقة متناهية مع نظام تحسين معايير الـ ATS</div>', unsafe_allow_html=True)

# دالة توليد الـ PDF الاحترافية والمحدثة لتنسيق المظهر وتلوين العناوين والنقاط
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
            
        # تنظيف علامات النجوم الخاصة بالتضخيم لتجنب تشويه الكلمات
        line = line.replace("**", "").replace("*", "")
        safe_line = line.encode('latin-1', 'replace').decode('latin-1')
        
        # 1. تحويل العناوين الرئيسية (مثل الاسم والأقسام الكبرى)
        if safe_line.startswith('# '):
            pdf.ln(4)
            pdf.set_font("Helvetica", style="B", size=16)
            pdf.set_text_color(30, 58, 138)  # لون أزرق داكن احترافي للمؤسسات
            pdf.multi_cell(170, 8, txt=safe_line.replace('# ', ''))
            pdf.ln(2)
            
        # 2. تحويل العناوين الفرعية
        elif safe_line.startswith('## ') or safe_line.startswith('### '):
            pdf.ln(2)
            pdf.set_font("Helvetica", style="B", size=13)
            pdf.set_text_color(59, 130, 246)  # لون أزرق فاتح أنيق
            header_text = safe_line.replace('## ', '').replace('### ', '')
            pdf.multi_cell(170, 7, txt=header_text)
            pdf.ln(1)
            
        # 3. تحويل نقاط الخبرات والإنجازات إلى نقاط مرتبة ومزاحة
        elif safe_line.startswith('+ ') or safe_line.startswith('- '):
            pdf.set_font("Helvetica", style="", size=11)
            pdf.set_text_color(75, 85, 99)  # لون رمادي غامق مريح للعين
            bullet_text = safe_line.replace('+ ', '').replace('- ', '')
            pdf.multi_cell(170, 6, txt=f"   - {bullet_text}")
            
        # 4. النصوص العادية وحقول المعلومات
        else:
            pdf.set_font("Helvetica", style="", size=11)
            pdf.set_text_color(0, 0, 0)  # لون أسود سادة للنصوص
            pdf.multi_cell(170, 6, txt=safe_line)
            
    return bytes(pdf.output())

# 2. إدارة مفاتيح الـ API لـ Groq (باستخدام متغيرك الأصلي المعتمد)
GROQ_API_KEY = st.secrets.get("API_d") or os.environ.get("API_d")

st.sidebar.header("🌐 PolyCV AI Control Panel")

source_lang = st.sidebar.selectbox(
    "🌐 اللغة الحالية للسيرة الذاتية (Original Language):",
    ["Arabic", "English", "French", "Spanish", "German", "Turkish", "Hindi"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 اللغات المستهدفة (Target Languages)")

target_lang_1 = st.sidebar.selectbox("اللغة المستهدفة الأولى:", ["English", "Arabic", "French", "Spanish", "German", "Turkish"], index=0)

num_languages = st.sidebar.radio("اختر عدد اللغات الإضافية المُراد الترجمة إليها:", [1, 2, 3], index=0)

target_languages = [target_lang_1]

if num_languages >= 2:
    target_lang_2 = st.sidebar.selectbox("اللغة المستهدفة الثانية:", ["French", "Spanish", "German", "Turkish", "English", "Arabic"], index=0)
    target_languages.append(target_lang_2)

if num_languages == 3:
    target_lang_3 = st.sidebar.selectbox("اللغة المستهدفة الثالثة:", ["Spanish", "German", "Turkish", "English", "Arabic", "French"], index=0)
    target_languages.append(target_lang_3)

target_languages = list(set(target_languages))

# 3. رفع ملفات السير الذاتية (PDF)
st.subheader("📁 ارفع ملف سيرة ذاتية أو أكثر (PDF)")
uploaded_files = st.file_uploader("اختر ملفات السير الذاتية الخاصة بك بصيغة PDF وسيقوم نظام PolyCV AI بمعالجتها فوراً وضمان ربطها بذكاء وعبر واجهة برمجية واحدة", type=["pdf"], accept_multiple_files=True)

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
                st.warning(f"⚠️ الملف {uploaded_file.name} فارغ أو لا يحتوي على نصوص مقروءة بشكل صحيح.")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء قراءة ملف {uploaded_file.name}: {e}")

# 4. زر التفعيل والمعالجة والترجمة
if st.button("🚀 ابدأ المعالجة عبر PolyCV AI الآن", use_container_width=True):
    if not GROQ_API_KEY:
        st.error("❌ لم يتم العثور على مفتاح API الخاص بصاحب الموقع في الإعدادات السرية (Secrets).")
    elif not cv_dict:
        st.warning("⚠️ الرجاء رفع ملف PDF يحتوي على نصوص واضحة أولاً.")
    else:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            system_instruction = """
            UNBREAKABLE INSTRUCTIONS TO PREVENT HALLUCINATION:
            1. Never alter, forge, change, omit, or add any numbers, years, dates, phone numbers, email addresses, websites, or hyperlinks. They must remain exactly as they appear in the source.
            2. For proper nouns (names of universities, companies, cities, or people), keep them accurate, only translate or transliterate them properly to the target language without changes.
            3. Translate the professional skills, responsibilities, and achievements into executive, high-level corporate terminology appropriate for ATS optimization.
            4. Do NOT output any conversational text, pleasantries, or introductory sentences like 'Here is your translation:'. Output ONLY the finalized professional Markdown format of the translated CV.
            5. Double-check all dates and contacts against the input before outputting.
            """
            
            file_tabs = st.tabs(list(cv_dict.keys()))
            
            for file_index, (file_name, cv_text) in enumerate(cv_dict.items()):
                with file_tabs[file_index]:
                    st.markdown(f"### 📄 السيرة الذاتية للملف: **{file_name}**")
                    
                    lang_tabs = st.tabs([f"🌍 إلى {lang}" for lang in target_languages])
                    
                    for lang_index, t_lang in enumerate(target_languages):
                        with lang_tabs[lang_index]:
                            if source_lang == t_lang:
                                st.warning(f"⚠️ اللغة المستهدفة ({t_lang}) هي نفس لغة السيرة الذاتية الأصلية.")
                                continue
                            
                            with st.spinner(f"⏳ يقوم PolyCV AI الآن بترجمة وتطوير السيرة الذاتية إلى ({t_lang})..."):
                                user_prompt = f"""
                                Translate this specific CV from {source_lang} to {t_lang}. Maximize ATS optimization.
                                
                                CV Input Text:
                                ---
                                {cv_text}
                                ---
                                """
                                
                                completion = client.chat.completions.create(
                                    model="llama-3.3-70b-versatile",
                                    messages=[
                                        {"role": "system", "content": system_instruction},
                                        {"role": "user", "content": user_prompt},
                                    ],
                                    temperature=0.2,
                                    max_tokens=4000
                                )
                                
                                translated_output = completion.choices.message.content
                                
                                st.success(f"✅ تم إنتاج السيرة الذاتية باللغة {t_lang} بنجاح واحترافية عالية!")
                                st.markdown(translated_output)
                                
                                # توليد الـ PDF بالدالة الذكية والمنسقة الجديدة
                                pdf_data = create_pdf(translated_output)
                                
                                st.download_button(
                                    label=f"📥 تحميل السيرة الذاتية المترجمة ({t_lang}) كملف PDF",
                                    data=pdf_data,
                                    file_name=f"Translated_CV_{t_lang}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{file_index}_{lang_index}"
                                )
        except Exception as e:
            st.error(f"❌ حدث خطأ في معالجة الـ API: {e}")

st.sidebar.markdown("---")
st.sidebar.write("⚡ Powered by PolyCV AI Engine & Groq Cloud")
st.sidebar.write("Developed by Pre-Revenue Startup Studio™")
