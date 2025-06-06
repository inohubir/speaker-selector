import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="سیستم انتخاب سخنران", layout="centered")

# استایل فارسی
st.markdown("""
    <style>
    * {
        font-family: Tahoma, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title("سیستم انتخاب سخنران بر پایه مدل AHP")

# شاخص‌ها
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

# ورود وزن‌ها توسط کاربر
st.sidebar.header("وزن شاخص‌ها بر اساس مدل AHP")
weights = []
for crit in criteria:
    w = st.sidebar.slider(f"{crit}", 0.0, 1.0, 0.125, 0.01)
    weights.append(w)

# نرمال‌سازی وزن‌ها
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
    max_score = 10 * len(criteria)
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
    df.index = df.index + 1  # رتبه‌ها از ۱ شروع شود
    df.insert(0, "رتبه", df.index)

    st.success("رتبه‌بندی نهایی:")
    st.dataframe(df[["رتبه", "نام", "امتیاز نهایی (از ۱۰۰)"]])
    st.bar_chart(df.set_index("نام")["امتیاز نهایی (از ۱۰۰)"])

    # تحلیل گزینه برتر
    top = df.iloc[0]
    top_name = top["نام"]
    top_scores = df.iloc[0]["raw_scores"]

    st.markdown("### تحلیل گزینه برتر")

    for crit, val in zip(criteria, top_scores):
        if val < 3:
            st.markdown(f"در شاخص {crit} تجربه ارزشمندی دیده نشد.")
        elif val < 5:
            st.markdown(f"در شاخص {crit} امتیاز خوبی بدست آورده است.")
        elif val < 7:
            st.markdown(f"در شاخص {crit} امتیاز رو به بالا کسب کرده است.")
        elif val < 10:
            st.markdown(f"در شاخص {crit} عملکرد بسیار خوبی داشته است.")
        elif val == 10:
            st.markdown(f"در شاخص {crit} امتیاز عالی و کاملی را بدست آورده است.")

    st.markdown(f"امتیاز نهایی این سخنران {top['امتیاز نهایی (از ۱۰۰)']} از ۱۰۰ است و به عنوان گزینه پیشنهادی انتخاب می‌شود.")
