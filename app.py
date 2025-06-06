import streamlit as st
import pandas as pd
import numpy as np
from persiantools.jdatetime import JalaliDate

st.set_page_config(page_title="سیستم انتخاب سخنران", layout="centered")

# استایل کلی و کامل
st.markdown("""
    <style>
    * {
        font-family: Tahoma, sans-serif !important;
    }
    html, body, [class*="css"] {
        background-color: #3a3a3a;
        color: #ffffff;
    }
    .block-container {
        padding: 2rem;
    }
    .stButton > button {
        color: white !important;
        background-color: #2563eb !important;
    }
    a {
        color: #93c5fd !important;
        text-decoration: none;
    }
    .centered {
        text-align: center;
    }
    h1 {
        font-size: 1.5rem !important;
    }
    /* استایل نوار expander */
    section[data-testid="stExpander"] div[role="button"] {
        background-color: #4a4a4a !important;
        color: white !important;
    }
    /* استایل محتوای داخلی expander */
    section[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        background-color: #4a4a4a !important;
        padding: 1rem;
        border-radius: 0 0 8px 8px;
    }
    </style>
""", unsafe_allow_html=True)

# لوگو بالا
st.image("logo.png", width=100)

# تاریخ شمسی + نام روز
today = JalaliDate.today()
weekday_map = {
    'Saturday': 'شنبه', 'Sunday': 'یکشنبه', 'Monday': 'دوشنبه', 'Tuesday': 'سه‌شنبه',
    'Wednesday': 'چهارشنبه', 'Thursday': 'پنج‌شنبه', 'Friday': 'جمعه'
}
weekday_fa = weekday_map[today.to_gregorian().strftime('%A')]
st.markdown(f"تاریخ امروز: {weekday_fa}، {today.strftime('%Y/%m/%d')}")

# خوش‌آمدگویی و راهنما
if "شروع" not in st.session_state:
    st.session_state["شروع"] = False

if not st.session_state["شروع"]:
    st.markdown("<h2 class='centered'>خوش آمدید به سیستم انتخاب سخنران</h2>", unsafe_allow_html=True)

    st.markdown("""
    <div class='centered'>
    این نرم‌افزار توسط <a href='https://inohub.ir' target='_blank'>شرکت اینوهاب</a> طراحی و توسعه داده شده و کلیه حقوق مادی و معنوی آن متعلق به همین شرکت است.

    <br><br>
    راهنمای استفاده:
    این ابزار بر پایه روش تحلیل سلسله‌مراتبی و تصمیم‌گیری چندشاخصه طراحی شده است.
    کاربر می‌تواند برای هر گزینه سخنرانی، امتیازاتی در ۸ شاخص ثبت نماید.
    سپس با وزن‌دهی به شاخص‌ها، گزینه بهینه برای سخنرانی از نظر تحلیلی مشخص خواهد شد.

    <br><br>
    پشتیبانی نرم‌افزار: آقای دکتر احسان ابراهیمی - ۰۹۱۲۴۴۰۸۷۷۳
    </div>
    """, unsafe_allow_html=True)

    if st.button("شروع"):
        st.session_state["شروع"] = True
    st.stop()

# اجرای اصلی اپلیکیشن

st.title("سیستم انتخاب سخنران بر پایه تحلیل سلسله‌مراتبی")

criteria = [
    "پژوهشگر",
    "صنعت",
    "آموزش‌دهنده",
    "سیاست‌گذار",
    "ارتباطات متقابل",
    "رسانه‌ای",
    "رسانه اجتماعی",
    "احساس عمومی"
]

st.sidebar.header("وزن شاخص‌ها")
weights = []
for crit in criteria:
    w = st.sidebar.slider(f"{crit}", 0.0, 1.0, 0.125, 0.01)
    weights.append(w)

weights = np.array(weights)
weights = weights / np.sum(weights)

num_speakers = st.number_input("تعداد سخنران‌ها برای مقایسه", min_value=1, max_value=10, value=3)
speakers = []

st.subheader("امتیازدهی به سخنران‌ها (۰ تا ۱۰)")

for i in range(num_speakers):
    with st.expander(f"سخنران {i+1}"):
        name = st.text_input(f"نام سخنران {i+1}", key=f"name_{i}")
        scores = []
        for crit in criteria:
            score = st.slider(f"{crit}", 0, 10, 5, key=f"{crit}_{i}")
            scores.append(score)
        speakers.append({"name": name, "scores": scores})

if st.button("تحلیل و رتبه‌بندی"):
    results = []

    for speaker in speakers:
        weighted_score = np.dot(speaker["scores"], weights)
        score_out_of_100 = round((weighted_score / 10) * 100, 2)
        results.append({
            "نام": speaker["name"],
            "امتیاز نهایی (از ۱۰۰)": score_out_of_100,
            "raw_scores": speaker["scores"]
        })

    df = pd.DataFrame(results).sort_values("امتیاز نهایی (از ۱۰۰)", ascending=False).reset_index(drop=True)
    df.index = df.index + 1
    df.insert(0, "رتبه", df.index)

    st.success("رتبه‌بندی نهایی:")
    st.dataframe(df[["رتبه", "نام", "امتیاز نهایی (از ۱۰۰)"]])
    st.bar_chart(df.set_index("نام")["امتیاز نهایی (از ۱۰۰)"])

    top = df.iloc[0]
    top_name = top["نام"]
    top_scores = df.iloc[0]["raw_scores"]

    st.markdown("### تحلیل گزینه برتر")

    strong_criteria = []
    for crit, val in zip(criteria, top_scores):
        if val >= 7:
            if val == 10:
                strong_criteria.append(f"در شاخص {crit} امتیاز عالی و کامل کسب کرده است.")
            else:
                strong_criteria.append(f"در شاخص {crit} عملکرد بسیار خوبی داشته است.")

    if strong_criteria:
        st.markdown("شاخص‌های بارز گزینه برتر:")
        for line in strong_criteria:
            st.markdown(f"- {line}")

    st.markdown(f"امتیاز نهایی: {top['امتیاز نهایی (از ۱۰۰)']} از ۱۰۰")

    st.markdown("---")
    st.markdown("تمام حقوق و مالکیت این نرم‌افزار متعلق به شرکت <a href='https://inohub.ir' target='_blank'>اینوهاب</a> است.", unsafe_allow_html=True)

    st.image("logo.png", width=100)
