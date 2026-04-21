"""
Инструменты для ИИ-агента
Каждый инструмент проверяется через конституцию
"""

import os
import subprocess
import platform

# ========== ФАЙЛОВЫЕ ОПЕРАЦИИ ==========
def is_system_file(path):
    """Проверяет, является ли файл системным"""
    system_paths = [
        "C:\\Windows", "/System", "/boot",
        "/usr/bin", "/bin", "/sbin"
    ]
    path_lower = path.lower()
    return any(sp in path_lower for sp in system_paths)

def write_file(path, content):
    """Безопасная запись файла"""
    try:
        if is_system_file(path):
            print(f"🔒 Блокировано: попытка записи в системный файл {path}")
            return False
        
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Файл сохранён: {path}")
        return True
    except Exception as e:
        print(f"❌ Ошибка записи: {e}")
        return False

def read_file(path):
    """Чтение файла"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Ошибка чтения: {e}"

# ========== СОЗДАНИЕ ПРИЛОЖЕНИЙ ==========
def create_telegram_bot(token="YOUR_TOKEN_HERE"):
    """Генерирует код Telegram-бота"""
    return f'''
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = "{token}"

async def start(update: Update, context):
    await update.message.reply_text("Привет! Я бот 🤖")

async def echo(update: Update, context):
    await update.message.reply_text(f"Ты сказал: {{update.message.text}}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
'''

def create_gui_app(app_type="calculator"):
    """Генерирует GUI приложение"""
    if app_type == "calculator":
        return '''
import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        result = eval(entry.get())
        label_result.config(text=f"Результат: {result}")
    except:
        messagebox.showerror("Ошибка", "Неверное выражение")

root = tk.Tk()
root.title("Калькулятор")
root.geometry("300x200")

entry = tk.Entry(root, width=30)
entry.pack(pady=10)

btn = tk.Button(root, text="Вычислить", command=calculate)
btn.pack()

label_result = tk.Label(root, text="Результат: ")
label_result.pack(pady=10)

root.mainloop()
'''
    return "# GUI приложение готово"

# ========== УПРАВЛЕНИЕ ПК ==========
def shutdown_pc_with_timer(seconds=60):
    """Выключение ПК с таймером"""
    system = platform.system()
    
    if system == "Windows":
        cmd = f"shutdown /s /t {seconds}"
    elif system in ["Linux", "Darwin"]:
        cmd = f"shutdown -h +{seconds//60}"
    else:
        return f"❌ Неподдерживаемая ОС: {system}"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        return f"✅ ПК выключится через {seconds} секунд"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def cancel_shutdown():
    """Отмена выключения"""
    system = platform.system()
    if system == "Windows":
        try:
            subprocess.run("shutdown /a", shell=True, check=True)
            return "✅ Выключение отменено"
        except:
            return "❌ Не удалось отменить выключение"
    return "❌ Отмена доступна только в Windows"

# ========== ИССЛЕДОВАТЕЛЬСКИЙ КОД ==========
def generate_educational_malware_example():
    """Генерирует пример кода для образовательных целей"""
    return '''
# ============================================================
# ОБРАЗОВАТЕЛЬНЫЙ ПРИМЕР: Демонстрация принципов работы
# ============================================================
# ВНИМАНИЕ: Этот код предназначен ТОЛЬКО для изолированной среды
# ============================================================

def demonstrate_infection_principle():
    print("=== Демонстрация принципа ===")
    print("В реальном коде здесь было бы:")
    print("1. Поиск файлов")
    print("2. Копирование кода")
    print("3. Но в целях безопасности этот пример НИЧЕГО не изменяет")

if __name__ == "__main__":
    print("🔬 ОБРАЗОВАТЕЛЬНЫЙ ПРИМЕР - НЕ ВРЕДОНОСНЫЙ")
    demonstrate_infection_principle()
'''
