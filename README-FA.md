# Crosshair Overlay (اورلی کراس‌هیر)

<p align="center">
  <img src="resources/icons/icon.png" alt="Crosshair Overlay" width="120"/>
</p>

<p align="center">
  <b>یک اورلی کراس‌هیر قابل شخصی‌سازی برای برنامه‌های دسکتاپ ویندوز.</b><br/>
  <b>پشتیبانی کامل از کدهای اشتراک‌گذاری Counter-Strike 2 (CS2)، VALORANT و Deadlock.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows" alt="Windows"/>
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License"/>
  <img src="https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt" alt="PySide6"/>
</p>

---

## 📖 درباره‌ی برنامه

**Crosshair Overlay** یک اورلی کراس‌هیر شفاف، کلیک‌ناپذیر (click-through) و همیشه روی صفحه برای ویندوز است. این برنامه عمدتاً برای **بازی‌های تیراندازی** طراحی شده تا با ثابت نگه‌داشتن کراس‌هیر روی صفحه، به **نو اسکوپ زدن** با اسنایپر کمک کند.

این برنامه به شما اجازه می‌دهد کراس‌هیر خود را کاملاً شخصی‌سازی کنید، پریست ذخیره کنید و کدهای اشتراک‌گذاری **Counter-Strike 2 (CS2)**، **VALORANT** و **Deadlock** را وارد یا صادر کنید.

## ✨ امکانات

- 🎯 **اورلی شفاف دسکتاپ**: کراس‌هیر بدون حاشیه، کلیک‌ناپذیر و همیشه روی صفحه.
- 🔧 **شخصی‌سازی کامل**: فاصله (Gap)، طول، ضخامت، اندازه‌ی نقطه، **مقیاس (Scale)** کلی، رنگ‌ها، حاشیه (Outline)، نقطه‌ی مرکزی، استایل T و موارد دیگر.
- 👁️ **پیش‌نمایش زنده**: پیش‌نمایش بلادرنگ در پنجره‌ی تنظیمات همراه با گزینه‌های پس‌زمینه و زوم.
- 💾 **کراس‌هیرهای ذخیره‌شده**: کراس‌هیر ساخته‌شده را به‌عنوان یک پریست نام‌دار ذخیره کنید، پریست‌ها را بارگذاری یا حذف کنید.
- 🔄 **کدهای اشتراک‌گذاری چندبازی**:
  - **CS2**: legacy-v1، legacy-v3، legacy-v4، native cs2-v1.
  - **VALORANT**: کدهای پروفایل.
  - **Deadlock**: کدهای رتیکل `DL.`.
  - تشخیص خودکار، تبدیل بین بازی‌ها و گزارش تبدیل.
- 🖥️ **پشتیبانی از چند مانیتور**: انتخاب مانیتوری که اورلی روی آن نمایش داده شود.
- ⌨️ **هاتکی‌های سراسری**: فعال/غیرفعال کردن اورلی (**F8**) و تنظیمات (**F9**) در کل سیستم.
- 📌 **سیستم تری**: دسترسی سریع به تنظیمات، فعال/غیرفعال کردن و خروج.
- 💾 **تنظیمات پایدار**: ذخیره‌ی خودکار در `%APPDATA%/CrosshairOverlay/settings.json`.
- 📏 **سازگار با DPI**: مدیریت صحیح مقیاس‌بندی نمایش ویندوز.

## 🚀 شروع کار

### اجرا از سورس‌کد


# کلون یا دانلود پروژه
git clone https://github.com/sep5ehr/duckscrosshair.git
cd duckscrosshair

# ساخت محیط مجازی
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

# ارتقای pip و نصب پیش‌نیازها
python -m pip install --upgrade pip
pip install -r requirements.txt

# اجرای برنامه
python main.py
ساخت فایل اجرایی (EXE)

# نصب PyInstaller
pip install pyinstaller

# ساخت به‌صورت پوشه‌ای (پیشنهادی برای تست)
pyinstaller --noconfirm --clean --onedir --windowed --name "CrosshairOverlay" main.py

# یا ساخت به‌صورت تک‌فایل
pyinstaller --noconfirm --clean --onefile --windowed --name "CrosshairOverlay" main.py
فایل اجرایی در پوشه‌ی dist/CrosshairOverlay/ قرار می‌گیرد.

⚠️ PyInstaller برای آیکون فایل EXE به فرمت .ico نیاز دارد. ابتدا PNG خود را به ICO تبدیل کنید (با Pillow یا یک مبدل آنلاین).

🎮 نحوه‌ی استفاده
اجرا: python main.py یا فایل اجرایی ساخته‌شده را اجرا کنید.

اورلی: در مرکز صفحه روی مانیتور اصلی ظاهر می‌شود.

تنظیمات: کلید F9 را بزنید یا روی آیکون تری کلیک کنید → Settings.

فعال/غیرفعال کردن اورلی: کلید F8 را بزنید یا از منوی تری استفاده کنید.

شخصی‌سازی: تمام ویژگی‌های کراس‌هیر را در پنجره‌ی تنظیمات تنظیم کنید.

وارد/صادر کردن کدها: هر کد پشتیبانی‌شده (CS2، VALORANT، Deadlock) را در تب Games جای‌گذاری کنید — فرمت به‌طور خودکار تشخیص داده می‌شود — سپس Import کنید؛ تنظیمات را تغییر دهید و Encode/Export کنید، یا بین بازی‌ها تبدیل کنید.

⌨️ هاتکی‌های پیش‌فرض
هاتکی	عملکرد
F8	فعال/غیرفعال کردن اورلی
F9	نمایش/مخفی کردن پنجره‌ی تنظیمات
Ctrl+Shift+Q	بستن اجباری برنامه
Esc	بستن دیالوگ‌ها / لغو عملیات
هاتکی‌ها را می‌توان در تب Shortcuts شخصی‌سازی کرد. روی یک فیلد میانبر کلیک کنید و هر ترکیب کلید یا دکمه‌ی ماوس (MouseLeft، MouseRight، MouseMiddle، MouseX1/Mouse4، MouseX2/Mouse5) را برای اتصال فشار دهید.

🧩 معماری کدک چندبازی
کدک‌های مستقل و تأییدشده برای هر بازی (کدک قدیمی داخلی برنامه در crosshair/sharecode/ برای سازگاری با نسخه‌های قبلی دست‌نخورده باقی مانده است):


crosshair/
  codecs/
    base.py            # CodecResult / DetectionResult / ConversionReport / GameCodec
    registry.py        # رجیستری کدک بازی
    cs2/               # پورت‌شده از مرجع تأییدشده csgo-sharecode@7.0.1
      formats.py       # کانتینرهای base-57، checksum، legacy CSGO-... در مقابل native CS...
      schema.py        # دیتاکلاس‌های legacy-v1 / legacy-v3 / legacy-v4 / cs2-v1
      decoder.py       # decode_cs2_crosshair(code) - تشخیص خودکار کانتینر+نسخه
      encoder.py       # encode_cs2_crosshair(settings, format="cs2-v1")
    valorant/
      parser.py        # پارسر/سریالایزر بدون‌تلفات توکن‌های semicolon
      schema.py        # بخش‌های P/A/S، نقشه‌ی کلید کامل مستند، پریست‌های رنگ
      decoder.py       # decode_valorant_crosshair(code)
      encoder.py       # encode_valorant_crosshair(settings)
    deadlock/
      protobuf_wire.py # پارس/سریالایز عمومی سیم پروتوباف (بدون چیدمان اختراعی)
      schema.py        # پیشوند DL. + base64url، اعتبارسنجی سختگیرانه
      decoder.py       # decode_deadlock_crosshair(code) - خام بدون‌تلفات + فیلدهای سیم
      encoder.py       # encode_deadlock_crosshair(settings)
  core/
    universal.py       # مدل نرمال‌شده‌ی UniversalCrosshair (+game_extensions+metadata)
    detect.py          # detect_crosshair_format(code)
    convert.py         # convert_crosshair(code, target_game) همراه با ConversionReport
    app_model.py       # پل به CrosshairSettings برنامه
    validation.py
خط لوله‌ی تبدیل: کد مبدأ → دیکودر مبدأ → مدل جهانی → انکودر مقصد → کد مقصد. کد اصلی همیشه در متادیتا نگه داشته می‌شود؛ گزارش‌های تبدیل ویژگی‌های تبدیل‌شده / پشتیبانی‌نشده / پیش‌فرض‌شده / غیرقابل‌نمایش را فهرست می‌کنند. پنجره‌ی تنظیمات یک تب جدید Games دارد.

محدوده‌ی پشتیبانی Deadlock (صادقانه)
کدهای DL. اعتبارسنجی می‌شوند (پیشوند + base64url) و رفت‌وبرگشت بایت‌به‌بایت یکسان دارند (payload خام حفظ می‌شود، پارس عمومی سیم پروتوباف شامل می‌شود). معناشناسی هر فیلد از payload DL. در این محیط در برابر یک پیاده‌سازی مرجع قابل تأیید نبود و بنابراین به‌صورت بهترین تلاش/تأییدنشده گزارش می‌شود، نه حدس. تبدیل یک کد غیر Deadlock به کد DL. رد می‌شود (به‌عنوان غیرقابل‌نمایش گزارش می‌شود) به‌جای ساختن یک payload.

📄 فرمت کد اشتراک‌گذاری CS2
برنامه فرمت فعلی کد اشتراک‌گذاری CS2 (نسخه ۱) را پیاده‌سازی می‌کند. فرمت‌های واقعی بازی پیاده‌سازی شده‌اند (پورت‌شده از مرجع تأییدشده‌ی csgo-sharecode):

فرمت	کانتینر	توضیحات
legacy-v1	CSGO-xxxxx-xxxxx-xxxxx-xxxxx-xxxxx	دوران CS:GO
legacy-v3	همان کانتینر قدیمی	مقادیر پیکسلی + ارتفاع صفحه
legacy-v4	همان کانتینر قدیمی	حالت Outline + Static Square اضافه می‌کند
cs2-v1	CS + ۴۴ کاراکتر، بدون خط تیره	CS2 بومی: Outline RGBA، تنظیمات نقطه‌ی اسکوپ، Gap منفی، آلفاهای گام ۰.۰۱
هر دو کانتینر اعداد بزرگ base-57 هستند (دیکشنری 0, 1, I, g, l, _ را حذف می‌کند)، بایت ۰ = checksum sum(bytes[1:]) % 256، بایت ۱ = نسخه. فرمت‌ها با کانتینر + نسخه شناسایی می‌شوند، نه فقط با نسخه (legacy-v1 و cs2-v1 هر دو بایت نسخه ۱ را ذخیره می‌کنند).

عملیات پشتیبانی‌شده
✅ رمزگشایی هر چهار فرمت (فیکسچرهای واقعی بازی در tests/fixtures.py).

✅ رمزگذاری هر چهار فرمت (کدهای جدید به‌طور پیش‌فرض cs2-v1 هستند).

✅ رفت‌وبرگشت بایت‌به‌بایت هر فیکسچر واقعی.

✅ اعتبارسنجی: کانتینرهای بدشکل، checksum نامعتبر، نسخه‌های پشتیبانی‌نشده (شامل legacy-v2)، ارتفاع صفحه ۰، کلمپ به سبک CS2.

✅ کدهای تولیدشده توسط کدک داخلی قبلی این برنامه همچنان وارد می‌شوند (به‌عنوان app-legacy-v1 شناسایی می‌شوند).

⚙️ تنظیمات
تنظیمات به‌طور خودکار در مسیر زیر ذخیره می‌شوند:


%APPDATA%\CrosshairOverlay\settings.json
نمونه‌ی ساختار:

json
{
  "schema_version": 1,
  "overlay": {
    "enabled": true,
    "click_through": true,
    "always_on_top": true,
    "monitor_id": "primary",
    "opacity": 1.0
  },
  "crosshair": {
    "gap": 2,
    "length": 6,
    "thickness": 2,
    "size": 6,
    "color": "#00FF00",
    "opacity": 1.0,
    "outline_enabled": true,
    "outline_color": "#000000",
    "outline_thickness": 1,
    "center_dot": false,
    "t_style": false,
    "style": 4,
    "dynamic_spread_limit": 0.0,
    "split_distance": 7,
    "inner_split_alpha": 255,
    "outer_split_alpha": 255,
    "split_size_ratio": 0.5,
    "reference_resolution": 1920,
    "scope_dot_scale": 1.0,
    "scope_dot_use_crosshair_color": false
  },
  "shortcuts": {
    "toggle_overlay": "F8",
    "toggle_settings": "F9"
  },
  "last_share_code": ""
}
⚠️ محدودیت‌های اورلی
مهم: این یک اورلی استاندارد دسکتاپ ویندوز است. با ایجاد یک پنجره‌ی شفاف، کلیک‌ناپذیر و همیشه روی صفحه کار می‌کند.

کار می‌کند با:
✅ برنامه‌های پنجره‌ای

✅ برنامه‌های پنجره‌ای بدون حاشیه

✅ اکثر برنامه‌های دسکتاپ

✅ بازی‌هایی که در حالت Borderless Windowed اجرا می‌شوند

کار نمی‌کند با:
❌ برنامه‌های تمام‌صفحه‌ی انحصاری (بسیاری از بازی‌ها)

❌ برنامه‌هایی که ترکیب دسکتاپ را دور می‌زنند

❌ برنامه‌هایی با مسدودسازی اورلی (برخی آنتی‌چیت‌ها)

این یک محدودیت ویندوز است، نه یک باگ. هیچ تزریق کد، خواندن حافظه یا دور زدن آنتی‌چیت انجام نمی‌شود.

عیب‌یابی نمایش اورلی
مطمئن شوید "Enable Overlay" در تب General تیک خورده است.

به‌طور موقت "Click Through" را غیرفعال کنید.

بررسی کنید مانیتور صحیح انتخاب شده باشد.

برای بازی‌ها: از حالت Borderless Windowed استفاده کنید، نه Exclusive Fullscreen.

برخی نرم‌افزارهای آنتی‌چیت ممکن است اورلی‌ها را مسدود کنند.

📁 ساختار پروژه

duckscrosshair/
├── main.py                 # نقطه‌ی ورود
├── requirements.txt        # وابستگی‌های پایتون
├── README.md               # این فایل
├── LICENSE                 # مجوز MIT
├── .gitignore              # قوانین Git ignore
├── CrosshairOverlay.spec   # فایل spec پایتون‌اینستالر
├── app/                    # هسته‌ی برنامه
├── crosshair/              # منطق کراس‌هیر، کدک‌ها، مدل‌ها
├── overlay/                # پنجره‌ی اورلی
├── winplatform/            # کدهای مخصوص پلتفرم (هاتکی‌ها و...)
├── storage/                # ذخیره‌سازی تنظیمات
├── ui/                     # رابط کاربری
├── resources/              # آیکون‌ها، دارایی‌ها
├── tests/                  # تست‌های واحد
└── build/                  # خروجی‌های بیلد
🧪 اجرای تست‌ها

# اجرای همه‌ی تست‌ها
pytest

# اجرای یک فایل تست خاص
pytest tests/test_round_trip.py -v

# اجرا با پوشش (coverage)
pytest --cov=crosshair --cov=overlay --cov=storage --cov=platform --cov=ui --cov=app
🛠️ توسعه
معماری
برنامه از یک معماری ماژولار پیروی می‌کند:

مدل‌ها (crosshair/models.py): کلاس‌های داده‌ی خالص برای تنظیمات.

رندرر (crosshair/renderer.py): منطق مشترک QPainter برای پیش‌نمایش و اورلی.

کدک (crosshair/sharecode/): رمزگذاری/رمزگشایی کد اشتراک‌گذاری CS2 (قدیمی).

کدک‌ها (crosshair/codecs/): سیستم کدک جدید چندبازی.

اورلی (overlay/): پنجره‌ی شفاف با استایل‌های Windows API.

رابط کاربری (ui/): پنجره‌ی تنظیمات با تب‌ها برای همه‌ی پیکربندی‌ها.

ذخیره‌سازی (storage/): پایداری JSON با نوشتن تأخیری.

پلتفرم (winplatform/): هاتکی‌های سراسری ویندوز از طریق API بومی.

📄 مجوز
این پروژه تحت مجوز MIT منتشر شده است — برای جزئیات فایل LICENSE را ببینید.

🙏 تقدیر و تشکر
تحقیقات فرمت کد اشتراک‌گذاری CS2 از:

akiver/csgo-sharecode

JDD310/CS2-Crosshair-Converter

setposgg/cs2-crosshair

PySide6/Qt برای چارچوب GUI عالی.

<p align="center">ساخته‌شده با ❤️ برای جامعه‌ی گیمرها</p> ```
