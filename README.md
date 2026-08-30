# 🩺 TelegramMediChat — Intelligent Medical & Pharmaceutical AI Assistant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/Telegram%20Bot%20API-v21.0%2B-0088cc.svg)](https://core.telegram.org/bots/api)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **TelegramMediChat** is an enterprise-grade, evidence-based medical and pharmaceutical consultation Telegram bot powered by modern LLMs (OpenRouter, OpenAI, DeepSeek, Anthropic, Meta Llama, and custom OpenAI-compatible endpoints). It features multi-turn conversation memory, dynamic patient health profiling, drug interaction checking, emergency triage guidance, and an interactive in-bot **Admin Control Panel** with live AI and quota management.

---

## 📑 Table of Contents
- [English Documentation](#-english-documentation)
  - [Key Features](#-key-features)
  - [Bot Architecture](#-bot-architecture)
  - [Interactive Admin Panel (`/admin`)](#-interactive-admin-panel-admin)
  - [Quick Start Guide](#-quick-start-guide)
  - [Production Server Deployment](#-production-server-deployment)
  - [Environment Variables](#-environment-variables)
  - [Available Bot Commands](#-available-bot-commands)
  - [Safety & Clinical Disclaimer](#-safety--clinical-disclaimer)
- [راهنمای فارسی (Persian Documentation)](#-راهنمای-فارسی-persian-documentation)
  - [ویژگی‌های کلیدی](#ویژگیهای-کلیدی)
  - [پنل مدیریت پیشرفته درون ربات](#پنل-مدیریت-پیشرفته-درون-ربات-admin)
  - [راهنمای راه‌اندازی و استقرار روی سرور](#راهنمای-راهاندازی-و-استقرار-روی-سرور)
  - [جدول متغیرهای محیطی](#جدول-متغیرهای-محیطی-env)
  - [دستورات ربات](#دستورات-ربات)
  - [سلب مسئولیت پزشکی](#سلب-مسئولیت-پزشکی)

---

# 🇬🇧 English Documentation

## 🌟 Key Features

### 1. 🩺 Clinical & Pharmaceutical AI Consultation
- Multi-turn conversation memory with persistent context retention.
- Evidence-based symptom triage and differential discussion.
- Structured medical response formatting (Assessment, Causes, Suggested Steps, Questions for Doctor, Red Flags).

### 2. 📋 Interactive Patient Health Profile
- Allows patients to save and update clinical context:
  - **Age, Biological Gender, Weight**
  - **Known Drug & Food Allergies**
  - **Chronic Medical Conditions** (Hypertension, Diabetes, Asthma, etc.)
  - **Current Medications & Dosages**
- Profile details are automatically injected into the AI context for personalized, safer consultations.

### 3. 💊 Dedicated Drug & Interaction Checker
- Analyzes drug-drug, drug-food, and drug-supplement interactions.
- Provides dosage timing recommendations and contraindication warnings.

### 4. 🚨 Red Flag Emergency Triage
- Instant access to critical red flag symptoms (Cardiovascular, Stroke FAST protocol, Respiratory distress, Anaphylaxis).
- International emergency hotline numbers (911, 112, 999, 115, 000).

### 5. 👑 Dynamic In-Bot Admin Control Panel (`/admin`)
- Accessible strictly by authorized Telegram IDs defined in `ADMIN_IDS`.
- Modify AI settings and quotas **in real time directly inside Telegram without restarting the server**.

---

## 👑 Interactive Admin Panel (`/admin`)

The `/admin` panel offers a comprehensive control center:

| Setting | Description |
| :--- | :--- |
| **Provider Name** | Set provider tag (e.g., `OpenRouter`, `OpenAI`, `Groq`, `Custom`). |
| **Model Name** | Instant model switcher with presets (`openrouter/free`, `deepseek/deepseek-r1`, `anthropic/claude-3.5-sonnet`, `meta-llama/llama-3.3-70b-instruct`, `openai/gpt-4o-mini`) or custom model input. |
| **API URL** | Full endpoint URL (e.g., `https://openrouter.ai/api/v1/chat/completions`). |
| **API Key (Bearer Token)** | Securely update API keys. The input message containing your key is automatically deleted immediately for privacy. |
| **Enable Advanced Reasoning** | Toggle sending `{"reasoning": {"enabled": true}}` in the request payload (essential for DeepSeek R1 & reasoning models on OpenRouter). |
| **Quotas & Limits** | Configure `Chatbot Max Requests` (e.g. `50` or `0` for unlimited). Displays live `Used: X / Max: Y` counter and provides one-click counter reset. |
| **User Statistics** | View total registered patients, 24h active users, and total queries handled. |
| **Test AI Connection** | Performs a live ping test to the configured LLM endpoint and reports status, model confirmation, and latency in milliseconds. |
| **Broadcast Announcement** | Send rich markdown announcements to all registered bot users with real-time delivery progress. |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.10 or higher
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)
- An AI API Key (e.g., free key from [OpenRouter.ai](https://openrouter.ai/))

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/TelegramMediChat.git
   cd TelegramMediChat
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your preferred text editor:
   ```env
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ
   ADMIN_IDS=123456789,987654321
   AI_PROVIDER_NAME=OpenRouter
   AI_MODEL_NAME=openrouter/free
   AI_API_URL=https://openrouter.ai/api/v1/chat/completions
   AI_API_KEY=sk-or-v1-your-openrouter-key
   AI_ENABLE_REASONING=true
   CHATBOT_MAX_REQUESTS=50
   DB_PATH=medichat.db
   ```

5. **Run the Bot:**
   ```bash
   python bot.py
   ```

---

## 🐳 Production Server Deployment

### Method 1: Docker Compose (Recommended)

1. Ensure Docker and Docker Compose are installed on your server.
2. Edit `.env` with your credentials.
3. Start the container in detached mode:
   ```bash
   docker compose up -d --build
   ```
4. View real-time logs:
   ```bash
   docker compose logs -f
   ```
5. Stop or restart:
   ```bash
   docker compose restart
   docker compose down
   ```

### Method 2: Systemd Service (Linux Server)

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/medichat.service
   ```
2. Paste the following configuration (replace paths and user accordingly):
   ```ini
   [Unit]
   Description=TelegramMediChat Bot Service
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/TelegramMediChat
   ExecStart=/home/ubuntu/TelegramMediChat/venv/bin/python bot.py
   Restart=always
   RestartSec=5
   EnvironmentFile=/home/ubuntu/TelegramMediChat/.env

   [Install]
   WantedBy=multi-user.target
   ```
3. Enable and start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable medichat
   sudo systemctl start medichat
   sudo systemctl status medichat
   ```

---

## ⚙️ Environment Variables

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | String | *Required* | Telegram Bot API token from `@BotFather`. |
| `ADMIN_IDS` | String | `""` | Comma-separated list of Telegram Admin user IDs. |
| `AI_PROVIDER_NAME` | String | `OpenRouter` | Name of the AI provider. |
| `AI_MODEL_NAME` | String | `openrouter/free` | Default model identifier. |
| `AI_API_URL` | String | `https://openrouter.ai/api/v1/chat/completions` | Full chat completions API endpoint. |
| `AI_API_KEY` | String | `""` | Bearer API token for authentication. |
| `AI_ENABLE_REASONING` | Boolean | `true` | Enables `{"reasoning": {"enabled": true}}` payload. |
| `CHATBOT_MAX_REQUESTS`| Integer | `50` | Maximum requests quota limit (0 = Unlimited). |
| `DB_PATH` | String | `medichat.db` | Path to the SQLite database file. |

---

## ⌨️ Available Bot Commands

| Command | Description |
| :--- | :--- |
| `/start` | Launch or restart the bot and register user. |
| `/consult` | Start an interactive medical consultation. |
| `/profile` | View and edit your clinical health profile. |
| `/drugs` | Activate medication & interaction checker mode. |
| `/emergency` | Display red-flag emergency advice and hotline numbers. |
| `/tips` | Receive an evidence-based health & wellness tip. |
| `/reset` | Clear active conversation history memory. |
| `/status` | Check remaining consultation quota. |
| `/help` | Display usage instructions and command guide. |
| `/admin` | Open Admin Control Panel (Authorized admins only). |

---

## ⚠️ Safety & Clinical Disclaimer

> **IMPORTANT**: MediChat AI is an artificial intelligence assistant developed for informational and educational purposes. It does not provide definitive medical diagnoses, prescriptions, or clinical treatment plans. Users experiencing acute medical emergencies, severe pain, breathlessness, or signs of stroke must immediately contact local emergency medical services or visit the nearest emergency room.

---

<br/>

---

# 🇮🇷 راهنمای فارسی (Persian Documentation)

## 🩺 ربات هوشمند مشاوره پزشکی و دارویی تلگرام (TelegramMediChat)

**تلگرام مدی‌چت (TelegramMediChat)** یک ربات پیشرفته، مدرن و مبتنی بر هوش مصنوعی برای مشاوره پزشکی، بررسی علائم بیماری، تحلیل تداخلات دارویی و ارزیابی اورژانس‌های پزشکی است. این ربات با اتصال به ارائه‌دهندگان قدرتمند مانند **OpenRouter**، **OpenAI**، **DeepSeek**، **Anthropic** و سایر مدل‌های سازگار، پاسخ‌هایی دقیق، مستند و ساختاریافته به کاربران ارائه می‌دهد.

---

## 🌟 ویژگی‌های کلیدی

1. **مشاوره پزشکی و بالینی هوشمند**:
   - نگهداری سابقه مکالمه و حافظه چندمرحله‌ای برای درک کامل وضعیت بیمار.
   - تریاژ علائم و ساختاردهی پاسخ‌ها (تحلیل علائم، احتمالات بالینی، اقدامات خودمراقبتی، پرسش‌های لازم از پزشک و هشدارهای قرمز).
2. **پرونده سلامت اختصاصی کاربر (Health Profile)**:
   - امکان ثبت سن، جنسیت، وزن، حساسیت‌های دارویی/غذایی، بیماری‌های زمینه‌ای و داروهای مصرفی جاری.
   - تزریق خودکار پرونده بیمار به زمینه هوش مصنوعی برای مشاوره‌های دقیق‌تر و ایمن‌تر.
3. **بررسی تخصصی تداخلات دارویی (Drug Checker)**:
   - تحلیل تداخل دارو با دارو، دارو با غذا و مکمل‌ها همراه با هشدارهای منع مصرف.
4. **راهنمای تریاژ اورژانس (Emergency Guide)**:
   - راهنمای فوری علائم هشداردهنده خطرناک (سکته قلبی، علائم سکته مغزی FAST، تنگی نفس شدید، شوک آنافیلاکسی) و شماره‌های امداد اضطراری.
5. **پنل مدیریت پیشرفته درون ربات (`/admin`)**:
   - مدیریت کامل تمام پارامترهای هوش مصنوعی و سهمیه‌ها به صورت تعاملی در خود تلگرام.

---

## 👑 پنل مدیریت پیشرفته درون ربات (`/admin`)

ادمین‌های ربات (تعریف‌شده در متغیر `ADMIN_IDS`) می‌توانند بدون نیاز به ری‌استارت سرور، تمامی تنظیمات را زنده ویرایش کنند:

- 🏷️ **Provider Name**: نام ارائه‌دهنده (مانند `OpenRouter`، `OpenAI`، `Groq` و ...).
- 🧠 **Model Name**: تغییر مدل با دکمه‌های آماده (`openrouter/free`، `deepseek/deepseek-r1`، `anthropic/claude-3.5-sonnet`، `meta-llama/llama-3.3-70b-instruct`، `openai/gpt-4o-mini`) یا وارد کردن نام مدل دلخواه.
- 🌐 **API URL**: تغییر آدرس کامل اندپوینت (مثلاً `https://openrouter.ai/api/v1/chat/completions`).
- 🔑 **API Key (Bearer Token)**: ثبت توکن با قابلیت **حذف خودکار پیام ادمین** جهت امنیت و حفظ حریم خصوصی.
- ⚡ **Enable Advanced Reasoning**: فعال/غیرفعال‌سازی ارسال پارامتر `{"reasoning": {"enabled": true}}` (برای فعال‌سازی قدرت استدلال در مدل‌های DeepSeek R1 و مدل‌های OpenRouter).
- 📊 **Quotas & Limits**: تعیین سقف کل درخواست‌ها (مثلاً `50` یا `0` برای نامحدود)، مشاهده لحظه‌ای درخواست‌های استفاده‌شده (`Used: X / Max: Y`) و دکمه ریست صفر کردن شمارنده.
- 👥 **آمار کاربران**: مشاهده تعداد کل بیماران/کاربران، کاربران فعال ۲۴ ساعت گذشته و مجموع مشاوره‌های انجام‌شده.
- 🧪 **تست اتصال هوش مصنوعی (Ping Test)**: تست زنده برقراری ارتباط با مدل و نمایش پینگ (Latency) بر حسب میلی‌ثانیه.
- 📢 **ارسال پیام همگانی (Broadcast)**: ارسال اطلاعیه به تمام کاربران ثبت‌نام‌شده با نوار پیشرفت ارسال.

---

## 🚀 راهنمای راه‌اندازی و استقرار روی سرور

### روش اول: استقرار سریع با داکر (Docker Compose) - پیشنهادی

1. فایل `.env.example` را به `.env` کپی کنید:
   ```bash
   cp .env.example .env
   ```
2. اطلاعات ربات، توکن تلگرام و آی‌دی ادمین را در `.env` وارد کنید.
3. دستور زیر را برای بیلد و اجرای خودکار اجرا کنید:
   ```bash
   docker compose up -d --build
   ```
4. برای مشاهده لاگ‌ها:
   ```bash
   docker compose logs -f
   ```

---

### روش دوم: نصب مستقیم با پایتون

1. ساخت محیط مجازی و نصب پیش‌نیازها:
   ```bash
   python -m venv venv
   source venv/bin/activate  # در لینوکس
   pip install -r requirements.txt
   ```
2. تنظیم فایل `.env` و اجرای ربات:
   ```bash
   python bot.py
   ```

---

## ⚙️ جدول متغیرهای محیطی (`.env`)

| نام متغیر | نوع | توضیحات |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | الزامی | توکن دریافتی از BotFather تلگرام |
| `ADMIN_IDS` | اختیاری | شناسه عددی ادمین‌ها با کاما (مثال: `123456789,987654321`) |
| `AI_PROVIDER_NAME` | اختیاری | نام ارائه‌دهنده (پیش‌فرض: `OpenRouter`) |
| `AI_MODEL_NAME` | اختیاری | شناسه مدل (پیش‌فرض: `openrouter/free`) |
| `AI_API_URL` | اختیاری | اندپوینت API (پیش‌فرض: OpenRouter) |
| `AI_API_KEY` | اختیاری | کلید احراز هویت هوش مصنوعی (Bearer Token) |
| `AI_ENABLE_REASONING`| بولی | فعال بودن استدلال پیشرفته (`true`/`false`) |
| `CHATBOT_MAX_REQUESTS`| عددی | سقف مجاز درخواست‌ها جهت جلوگیری از هزینه ناخواسته |
| `DB_PATH` | متنی | مسیر پایگاه‌داده اس‌کیوال‌لایت (`medichat.db`) |

---

## ⌨️ دستورات ربات

- `/start` - شروع یا راه‌اندازی مجدد ربات
- `/consult` - شروع جلسه مشاوره پزشکی
- `/profile` - مشاهده و ویرایش پرونده سلامت
- `/drugs` - بخش بررسی داروها و تداخلات
- `/emergency` - راهنمای اورژانس‌های پزشکی
- `/tips` - دریافت نکته سلامت روز
- `/reset` - پاکسازی حافظه مکالمه و شروع مبحث جدید
- `/status` - بررسی وضعیت و سهمیه باقیمانده
- `/help` - راهنمای کامل استفاده از ربات
- `/admin` - ورود به پنل مدیریت (فقط برای ادمین‌ها)

---

## ⚠️ سلب مسئولیت پزشکی

> **تذکر مهم**: اطلاعات ارائه‌شده توسط این هوش مصنوعی صرفاً جنبه آموزشی و اطلاع‌رسانی دارد و به هیچ عنوان جایگزین تشخیص، تجویز یا درمان توسط پزشک متخصص نیست. در صورت بروز هرگونه شرایط حاد یا اورژانسی، فوراً با شماره‌های امدادی (۱۱۵) تماس بگیرید یا به نزدیک‌ترین مرکز درمانی مراجعه نمایید.
