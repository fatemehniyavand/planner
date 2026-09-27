
# Focus Planner — Hourly Tasks Version

این نسخه فقط از بخش ساعت‌ها برای ثبت کار استفاده می‌کند.

## قابلیت‌ها
- همه‌چیز در یک صفحه
- تقویم ماهانه
- انتخاب هر روز
- ثبت کار برای هر ساعت از 09:00 تا 23:00
- ذخیره خودکار هر کار
- تیک انجام شدن برای هر ساعت
- حذف کار
- ذخیره جداگانه برای هر روز
- گزارش کامل ماه
- نمایش نام کار + تاریخ + ساعت + وضعیت انجام شده/نشده
- خروجی CSV
- تمام دکمه‌ها با رنگ ثابت
- بدون API

## اجرا

```bash
cd focus_planner_hourly_tasks
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

اگر محیط مجازی را قبلاً ساخته‌ای:

```bash
source .venv/bin/activate
streamlit run app.py
```

اطلاعات داخل فایل `planner.db` ذخیره می‌شود.
