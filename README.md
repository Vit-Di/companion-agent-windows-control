# 🎛️ Win-Agent (Server Side)

**[UA]** Серверна частина системи керування Windows-комп'ютерами через Bitfocus Companion.  
**[EN]** The server-side agent for controlling Windows PCs via Bitfocus Companion.

---

## 🇺🇦 Опис (Українська)

Це репозиторій **Агента** — програми, яка має бути запущена на кожному Windows-комп'ютері, яким ви плануєте керувати. Вона приймає команди від модуля Companion і виконує їх (запуск програм, емуляція клавіатури, системні команди).

Для повноцінної роботи вам також знадобиться клієнтський модуль для Companion:  
👉 **[Завантажити Модуль (Bitfocus Companion Module)](https://github.com/Vit-Di/companion-module-vitdi-win-agent/tree/main)**

### 🛠️ Інструкція зі встановлення

#### Крок 1: Встановлення Агента (Ви знаходитесь тут)
*Це потрібно зробити на комп'ютерах, якими ви будете керувати.*

1.  Перейдіть у вкладку **Releases** (праворуч на цій сторінці).
2.  Завантажте архів **Win-Agent.zip**.
3.  Розпакуйте папку `Win-Agent` у постійне місце (наприклад, на диск `C:\Win-Agent`).
4.  **Запуск:**
    * Двічі натисніть **`start.bat`**, щоб запустити сервіс.
    * Щоб зупинити, використовуйте **`stop.bat`**.
5.  *(Рекомендовано)* Щоб агент запускався автоматично, створіть ярлик для `start.bat` і помістіть його в папку автозавантаження (`Win+R` -> `shell:startup`).

#### Крок 2: Встановлення Модуля 
*(Виконуйте цей крок, якщо модуль ще не відображається у списку Companion)*

1.  Завантажте репозиторій (**Source code** або Release).👉 **[Завантажити Модуль (Bitfocus Companion Module)](https://github.com/Vit-Di/companion-module-vitdi-win-agent/tree/main)**

2.  Розпакуйте архів у будь-яку зручну папку (наприклад, `Documents\CompanionModules`).
3.  Відкрийте інтерфейс **Bitfocus Companion**.
4.  Натисніть на шестерню **Settings** (Налаштування) угорі праворуч.
5.  Перейдіть на вкладку **Developer Modules**.
6.  У рядку **"Base path for local developer modules"** натисніть кнопку папки 📂.
7.  Виберіть папку, куди ви розпакували цей модуль.
8.  Натисніть **Reload** або перезапустіть Companion. Модуль з'явиться у пошуку під назвою **"Windows Control Agent"**.

#### Крок 3: Налаштування
1.  Додайте модуль у Companion.
2.  Введіть **IP-адреси** ваших ПК, де вже запущено Агента.
3.  Порт за замовчуванням: `8001`.
4.  Збережіть. Статус має стати `OK`.

Перейдіть за посиланням вище (на репозиторій модуля) та дотримуйтесь інструкцій там, щоб підключити Companion до цього агента.

### ⚠️ Важлива примітка
* **Порт:** Агент використовує порт **8001**. Переконайтеся, що він не заблокований брандмауером.
* **Утиліти:** Для роботи системних команд (гучність, сон) у папці агента обов'язково має бути файл `nircmd.exe` (входить до складу Release-версії).

---

## 🇺🇸 Description (English)

This is the **Agent** repository — the application that must run on every target Windows PC. It listens for commands from Bitfocus Companion and executes them (app launch, keystrokes, system power, etc.).

To use this, you also need the Companion Module:  
👉 **[Get the Companion Module here](https://github.com/Vit-Di/companion-module-vitdi-win-agent/tree/main)**

### 🛠️ Installation Guide

#### Step 1: Install the Agent (You are here)
*Perform this on the target computers.*

1.  Go to the **Releases** section (right side of this page).
2.  Download **Win-Agent.zip**.
3.  Extract the folder to a permanent location (e.g., `C:\Win-Agent`).
4.  **Run:**
    * Double-click **`start.bat`** to start the service.
    * Use **`stop.bat`** to stop it.
5.  *(Recommended)* For auto-start, create a shortcut of `start.bat` and place it in the Startup folder (`Win + R` -> type `shell:startup`).

#### Step 2: Install the Module 
*(Perform this step if the module is not yet displayed in Companion)*

1.  Download repository (**Source code** or Release). 👉 **[Get the Companion Module here](https://github.com/Vit-Di/companion-module-vitdi-win-agent/tree/main)**

2.  Extract it to any folder (e.g., `Documents\CompanionModules`).
3.  Open the **Bitfocus Companion** interface.
4.  Click on **Settings** (gear icon ⚙️) in the top right.
5.  Go to the **Developer Modules** tab.
6.  In the **"Base path for local developer modules"** field, click the folder icon 📂.
7.  Select the folder where you extracted this module.
8.  Click **Reload** (or restart Companion). Search for **"Windows Control Agent"** to add it.

#### Step 3: Configuration
1.  Add the module to your Companion surface.
2.  Enter the **IP Addresses** of your target PCs (where the Agent is running).
3.  Default Port: `8001`.
4.  Save. The status should turn **OK**.



### ⚠️ Important Note
* **Port:** The agent listens on port **8001**. Ensure it is allowed through your firewall.
* **Dependencies:** `nircmd.exe` must be present in the agent folder (included in the Release zip).

### 🛡️ Troubleshooting / Якщо виникає помилка при запуску

**[EN]** If you see a "Security Warning" window when running `start.bat`:
1. Uncheck the box **"Always ask before opening this file"**.
2. Click **Run**.

**[UA]** Якщо при запуску `start.bat` з'являється вікно "Попередження системи безпеки":
1. Зніміть галочку **"Завжди запитувати перед відкриттям цього файлу"**.
2. Натисніть кнопку **Виконати**.
