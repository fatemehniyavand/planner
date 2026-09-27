
import streamlit as st
from datetime import date
import calendar
import pandas as pd

from db import (
    init_db,
    get_hourly_tasks,
    save_hourly_task,
    toggle_hourly_task,
    delete_hourly_task,
    get_month_report,
)

st.set_page_config(
    page_title="Focus Planner",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_db()

# -------------------------
# SESSION STATE
# -------------------------
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()

if "calendar_anchor" not in st.session_state:
    st.session_state.calendar_anchor = date.today().replace(day=1)

# -------------------------
# FIXED VISUAL THEME
# -------------------------
st.markdown("""
<style>
:root{
    --bg:#F4F7FB;
    --panel:#FFFFFF;
    --panel-soft:#F8FAFC;
    --text:#172033;
    --muted:#6B7280;
    --border:#DDE3EC;
    --primary:#3157D5;
    --soft:#EAF0FF;
    --success:#168A59;
    --danger:#C84646;
    --shadow:0 8px 24px rgba(20,34,70,.07);
}

.stApp{
    background:var(--bg);
    color:var(--text);
}

.block-container{
    max-width:1600px;
    padding-top:1rem;
    padding-bottom:2rem;
}

#MainMenu, footer, header, [data-testid="stToolbar"]{
    visibility:hidden;
}

.hero{
    background:linear-gradient(135deg,#3157D5,#5A78E6);
    color:#fff;
    border-radius:22px;
    padding:24px 28px;
    box-shadow:var(--shadow);
    margin-bottom:18px;
}
.hero h1{
    margin:0;
    font-size:1.9rem;
    font-weight:800;
}
.hero p{
    margin:6px 0 0;
    opacity:.92;
}

.section-title{
    font-size:1.05rem;
    font-weight:800;
    color:var(--text);
    margin-bottom:4px;
}

.section-sub{
    font-size:.82rem;
    color:var(--muted);
    margin-bottom:12px;
}

.metric-card{
    background:#fff;
    border:1px solid var(--border);
    border-radius:16px;
    padding:15px 16px;
    box-shadow:var(--shadow);
}
.metric-label{
    color:var(--muted);
    font-size:.78rem;
}
.metric-value{
    font-size:1.5rem;
    font-weight:800;
    margin-top:4px;
    color:var(--text);
}

.selected-date-box{
    background:var(--soft);
    border:1px solid #C8D5FF;
    border-radius:14px;
    padding:12px 14px;
    margin-top:12px;
}
.selected-label{
    color:var(--primary);
    font-size:.75rem;
    font-weight:700;
}
.selected-value{
    color:var(--text);
    font-size:1rem;
    font-weight:800;
    margin-top:3px;
}

.calendar-title{
    text-align:center;
    font-size:1.08rem;
    font-weight:800;
    padding-top:.45rem;
}

.calendar-weekday{
    text-align:center;
    color:var(--muted);
    font-size:.72rem;
    font-weight:700;
    padding:3px 0;
}

.hour-label{
    font-weight:800;
    color:var(--primary);
    padding-top:.55rem;
}

.status-done{
    color:var(--success);
    font-weight:700;
    font-size:.82rem;
}
.status-pending{
    color:var(--danger);
    font-weight:700;
    font-size:.82rem;
}

/* FIXED BUTTON COLORS IN EVERY STATE */
.stButton > button,
.stDownloadButton > button,
button[kind="primary"],
button[kind="secondary"]{
    background:#3157D5 !important;
    color:#FFFFFF !important;
    border:1px solid #3157D5 !important;
    border-radius:12px !important;
    font-weight:700 !important;
    min-height:40px !important;
    box-shadow:none !important;
    transition:none !important;
}

.stButton > button:hover,
.stButton > button:focus,
.stButton > button:active,
.stDownloadButton > button:hover,
.stDownloadButton > button:focus,
.stDownloadButton > button:active,
button[kind="primary"]:hover,
button[kind="primary"]:focus,
button[kind="primary"]:active,
button[kind="secondary"]:hover,
button[kind="secondary"]:focus,
button[kind="secondary"]:active{
    background:#3157D5 !important;
    color:#FFFFFF !important;
    border-color:#3157D5 !important;
    box-shadow:none !important;
    transform:none !important;
}

div[data-testid="stTextInput"] input{
    background:#FFFFFF !important;
    color:#172033 !important;
    border:1px solid #DDE3EC !important;
    border-radius:12px !important;
}

div[data-testid="stTextInput"] input:focus{
    border-color:#3157D5 !important;
    box-shadow:none !important;
}

div[data-testid="stCheckbox"] label span{
    color:#172033 !important;
}

hr{
    border-color:#E7EBF1 !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HELPERS
# -------------------------
def change_month(delta):
    current = st.session_state.calendar_anchor
    year = current.year
    month = current.month + delta
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    st.session_state.calendar_anchor = date(year, month, 1)

selected = st.session_state.selected_date
anchor = st.session_state.calendar_anchor

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div class="hero">
    <h1>🗓️ Focus Planner</h1>
    <p>تقویم + برنامه ساعتی + تیک انجام شدن + گزارش کامل، همه در یک صفحه</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# METRICS FOR SELECTED DAY
# -------------------------
day_rows = get_hourly_tasks(selected.isoformat())
active_rows = [r for r in day_rows if r["task_text"].strip()]
total = len(active_rows)
completed = sum(1 for r in active_rows if r["done"])
pending = total - completed
rate = int((completed / total) * 100) if total else 0

m1, m2, m3, m4 = st.columns(4)
for col, label, value in [
    (m1, "کارهای روز", total),
    (m2, "انجام‌شده", completed),
    (m3, "انجام‌نشده", pending),
    (m4, "درصد تکمیل", f"{rate}%"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("")

left, right = st.columns([1.15, 2.85], gap="large")

# -------------------------
# CALENDAR
# -------------------------
with left:
    st.markdown('<div class="section-title">تقویم</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">روی هر روز بزن؛ برنامه همان روز باز می‌شود.</div>',
        unsafe_allow_html=True
    )

    n1, n2, n3 = st.columns([1, 2.4, 1])
    with n1:
        if st.button("←", key="prev_month", use_container_width=True):
            change_month(-1)
            st.rerun()
    with n2:
        st.markdown(
            f'<div class="calendar-title">{calendar.month_name[anchor.month]} {anchor.year}</div>',
            unsafe_allow_html=True
        )
    with n3:
        if st.button("→", key="next_month", use_container_width=True):
            change_month(1)
            st.rerun()

    weekdays = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    wd_cols = st.columns(7)
    for i, name in enumerate(weekdays):
        with wd_cols[i]:
            st.markdown(
                f'<div class="calendar-weekday">{name}</div>',
                unsafe_allow_html=True
            )

    month_calendar = calendar.Calendar(firstweekday=0).monthdatescalendar(
        anchor.year, anchor.month
    )

    for week in month_calendar:
        cols = st.columns(7)
        for i, d in enumerate(week):
            with cols[i]:
                if d.month != anchor.month:
                    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
                    continue

                text = f"● {d.day}" if d == selected else str(d.day)
                if st.button(text, key=f"day_{d.isoformat()}", use_container_width=True):
                    st.session_state.selected_date = d
                    st.rerun()

    st.markdown(
        f"""
        <div class="selected-date-box">
            <div class="selected-label">روز انتخاب‌شده</div>
            <div class="selected-value">{selected.strftime("%A, %d %B %Y")}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("امروز", key="go_today", use_container_width=True):
        st.session_state.selected_date = date.today()
        st.session_state.calendar_anchor = date.today().replace(day=1)
        st.rerun()

# -------------------------
# HOURLY TASK LIST
# -------------------------
with right:
    st.markdown('<div class="section-title">لیست کارهای ساعتی</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'فقط همین‌جا کارها را ثبت کن. هر متن به صورت خودکار ذخیره می‌شود و کنار همان ساعت تیک انجام شدن دارد.'
        '</div>',
        unsafe_allow_html=True
    )

    rows_by_hour = {r["hour"]: r for r in day_rows}

    for hour in range(9, 24):
        hour_label = f"{hour:02d}:00"
        row = rows_by_hour.get(hour_label, {
            "task_text": "",
            "done": 0
        })

        c1, c2, c3, c4 = st.columns([0.8, 5.2, 0.9, 0.9])

        with c1:
            st.markdown(
                f'<div class="hour-label">{hour_label}</div>',
                unsafe_allow_html=True
            )

        with c2:
            task_text = st.text_input(
                f"task_{hour_label}",
                value=row["task_text"],
                placeholder="کار این ساعت را بنویس...",
                key=f"task_{selected.isoformat()}_{hour_label}",
                label_visibility="collapsed"
            )

            if task_text != row["task_text"]:
                save_hourly_task(
                    selected.isoformat(),
                    hour_label,
                    task_text,
                    row["done"]
                )

        with c3:
            checked = st.checkbox(
                "done",
                value=bool(row["done"]),
                key=f"done_{selected.isoformat()}_{hour_label}",
                label_visibility="collapsed"
            )

            if checked != bool(row["done"]):
                toggle_hourly_task(
                    selected.isoformat(),
                    hour_label,
                    int(checked)
                )
                st.rerun()

        with c4:
            if st.button(
                "حذف",
                key=f"delete_{selected.isoformat()}_{hour_label}",
                use_container_width=True
            ):
                delete_hourly_task(selected.isoformat(), hour_label)
                st.rerun()

    st.markdown("")
    st.progress(rate / 100 if total else 0)
    st.caption(f"{completed} از {total} کار این روز انجام شده است.")

# -------------------------
# FULL MONTH REPORT
# -------------------------
st.markdown("")
st.markdown("---")
st.markdown('<div class="section-title">گزارش کامل ماه</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">'
    'تمام کارهایی که ثبت کرده‌ای با تاریخ، ساعت و وضعیت انجام‌شده یا انجام‌نشده.'
    '</div>',
    unsafe_allow_html=True
)

report = get_month_report(anchor.year, anchor.month)

if not report:
    st.info("برای این ماه هنوز کاری ثبت نشده.")
else:
    report_df = pd.DataFrame(report)
    report_df["Status"] = report_df["done"].apply(
        lambda x: "انجام‌شده" if x else "انجام‌نشده"
    )
    report_df = report_df.rename(columns={
        "task_date": "Date",
        "hour": "Time",
        "task_text": "Task",
    })

    report_df = report_df[["Date", "Time", "Task", "Status"]]

    st.dataframe(
        report_df,
        use_container_width=True,
        hide_index=True
    )

    csv = report_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "دانلود گزارش کامل CSV",
        data=csv,
        file_name=f"focus_planner_{anchor.year}_{anchor.month:02d}.csv",
        mime="text/csv",
        use_container_width=True
    )
