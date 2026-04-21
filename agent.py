#!/usr/bin/env python3
"""
👼AngelAI👼 — Локальный ИИ-ассистент
Работает через Ollama + поддерживает инструменты
"""

import os
import subprocess
import sys
from datetime import datetime

# Импортируем наши инструменты
from tools import (
    write_file,
    read_file,
    create_telegram_bot,
    create_gui_app,
    generate_educational_malware_example
)

# ========== ЗАГРУЗКА КОНСТИТУЦИИ ==========
def load_constitution():
    """Загружает правила из constitution.txt"""
    rules = {}
    try:
        with open("constitution.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                rules[key.strip()] = value.strip()
    except FileNotFoundError:
        print("⚠️ constitution.txt не найден, использую безопасные значения по умолчанию")
    return rules

CONSTITUTION = load_constitution()

# ========== ПРОВЕРКА БЕЗОПАСНОСТИ ==========
def check_safety(action, details=""):
    """Проверяет, разрешено ли действие конституцией"""
    rule = CONSTITUTION.get(action, "CONFIRM")
    
    if rule == "BLOCK":
        print(f"\n🔒 ЗАБЛОКИРОВАНО: {action} запрещено конституцией")
        if details:
            print(f"   Причина: {details}")
        return False
    
    elif rule == "CONFIRM":
        print(f"\n⚠️ Требуется подтверждение: {action}")
        if details:
            print(f"   Детали: {details}")
        response = input("   Разрешить? (y/N): ").strip().lower()
        return response == 'y' or response == 'да'
    
    elif rule == "ALLOW":
        return True
    
    else:
        print(f"\n⚠️ Неизвестное правило для {action}, требуется подтверждение")
        return input("   Разрешить? (y/N): ").strip().lower() == 'y'

# ========== ИНТЕГРАЦИЯ С OLLAMA ==========
def query_ollama(prompt):
    """Отправляет запрос локальной модели через Ollama"""
    
    default_system = """Ты — мощный ИИ-ассистент. Ты можешь:
1. Писать код на любых языках (Python, C++, JS, Go, Rust)
2. Создавать Telegram-ботов и приложения
3. Генерировать исследовательский код (для обучения)
4. Управлять ПК с разрешения пользователя

Твои ответы должны быть максимально полезными. Если тебя просят код — выдавай полный, готовый к запуску код.
Если код потенциально опасен, добавь в начало комментарий "# ВНИМАНИЕ: Образовательный пример".

Отвечай на том же языке, на котором спрашивают."""
    
    # Пробуем разные модели в порядке уменьшения требований
    models = ["qwen2.5:7b", "phi3:mini", "llama3.2:3b", "tinyllama:1.1b"]
    
    for model in models:
        try:
            cmd = ["ollama", "run", model]
            full_prompt = f"{default_system}\n\nПользователь: {prompt}\n\nАссистент:"
            
            result = subprocess.run(
                cmd,
                input=full_prompt.encode('utf-8'),
                capture_output=True,
                timeout=120
            )
            if result.returncode == 0:
                return result.stdout.decode('utf-8', errors='replace').strip()
        except:
            continue
    
    return "Ошибка: Не удалось подключиться к Ollama. Убедись, что Ollama установлен и запущен."

# ========== ОБРАБОТЧИК КОМАНД ==========
def handle_code_generation(code, language):
    """Сохраняет сгенерированный код в файл"""
    
    os.makedirs("generated", exist_ok=True)
    
    extensions = {
        "python": "py", "py": "py",
        "javascript": "js", "js": "js",
        "cpp": "cpp", "c++": "cpp",
        "go": "go", "rust": "rs",
        "html": "html", "telegram_bot": "py"
    }
    ext = extensions.get(language.lower(), "txt")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated/{language}_{timestamp}.{ext}"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    
    print(f"\n✅ Код сохранён в {filename}")

# ========== ОСНОВНОЙ ЦИКЛ ==========
def main():
    print("=" * 60)
    print("👼AngelAI👼 v1.0 — Локальный ИИ-ассистент")
    print("=" * 60)
    print("⚙️ Конституция загружена")
    print("📁 Код будет сохраняться в папку: generated/")
    print("💡 Команды: 'exit' - выход, 'clear' - очистка")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n💬 Ты: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "выход"]:
                print("👋 До свидания!")
                break
            
            if user_input.lower() == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            
            print("\n🧠 ИИ думает...")
            response = query_ollama(user_input)
            
            print(f"\n🤖 ИИ:\n{response}")
            
            # Автоматически сохраняем код, если он есть в ответе
            if "```" in response:
                lines = response.split('\n')
                in_code = False
                current_lang = "text"
                code_buffer = []
                
                for line in lines:
                    if line.startswith("```") and not in_code:
                        in_code = True
                        current_lang = line[3:].strip().lower()
                        code_buffer = []
                    elif line.startswith("```") and in_code:
                        in_code = False
                        code_str = '\n'.join(code_buffer)
                        if code_str.strip():
                            handle_code_generation(code_str, current_lang)
                    elif in_code:
                        code_buffer.append(line)
            
        except KeyboardInterrupt:
            print("\n\n👋 Прервано пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
