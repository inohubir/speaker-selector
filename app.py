import streamlit as st
import pandas as pd

st.set_page_config(page_title="سیستم انتخاب سخنران", layout="centered")

# اعمال فونت فارسی Tahoma
st.markdown("""
    <style>
    * {
        font-family: Tahoma, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("سیستم انتخاب سخنران بر اساس ۸ شاخص")

# شاخص‌ها
criteria = {
    "پژوهشگر": 1.0,
    "صنعت": 1.0,
    "آموزش‌دهنده": 1.0,
    "سیاست‌گذار": 1.0,
    "ارتباطات متقابل": 1.0,
    "رسانه‌ای": 1.0,
    "رسانه اجتماعی": 1.0,
    "احساس عمومی": 1.0,
}

# تنظیم وزن شاخص‌ها
st.sidebar.header("تنظیم وزن شاخص‌ها")
for key in criteria:
    criteria[key] = st.sidebar.slider(key, 0.0, 2.0, 1.0, 0.1)

num_speakers = st.number_input("چند سخنران برای مقایسه دارید؟", min_value=1, max_value=10, value=3)

speakers = []

st.subheader("امتیازدهی به سخنران‌ها")

# ورود امتیاز برای هر سخنران
for i in range(num_speakers):
    with st.expander(f"سخنران {i+1}"):
        name = st.text_input(f"نام سخنران {i+1}", key=f"name_{i}")
        scores = {}
        for crit in criteria:
            scores[crit] = st.slider(f"{crit}", 0, 10, 5, key=f"{crit}_{i}")
        speakers.append({"name": name, "scores": scores})

# دکمه تحلیل
if st.button("تحلیل و رتبه‌بندی"):
    results = []

    max_score = sum([10 * weight for weight in criteria.values()])  # امتیاز نهایی ممکن (بر اساس وزن‌ها)

    for speaker in speakers:
        name = speaker["name"]
        weighted_score = sum(speaker["scores"][crit] * criteria[crit] for crit in criteria)
        score_out_of_100 = round(weighted_score / max_score * 100, 2)
        results.append({"نام": name, "امتیاز نهایی (از 100)": score_out_of_100})

    df = pd.DataFrame(results).sort_values("امتیاز نهایی (از 100)", ascending=False)

    st.success("رتبه‌بندی نهایی:")
    st.dataframe(df)
    st.bar_chart(df.set_index("نام"))

    # تحلیل گزینه برتر
    top_speaker = df.iloc[0]
    top_speaker_name = top_speaker["نام"]

    for speaker in speakers:
        if speaker["name"] == top_speaker_name:
            st.markdown("### تحلیل گزینه برتر")
            for crit, score in speaker["scores"].items():
                if score >= 7:
                    st.markdown(f"در شاخص {crit} عملکرد بسیار خوبی دارد.")
                elif score <= 3:
                    st.markdown(f"در شاخص {crit} نیاز به بهبود دارد.")
            st.markdown(f"با توجه به مجموع امتیازها، گزینه پیشنهادی برای سخنرانی {top_speaker_name} است با امتیاز {top_speaker['امتیاز نهایی (از 100)']} از ۱۰۰.")
