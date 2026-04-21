#!/usr/bin/env python3
"""
👼AngelAI👼 — Веб-интерфейс с историей чата
Запуск: python app.py
Потом открой в браузере: http://localhost:5000
"""

import subprocess
import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'my_ai_agent_secret_key_2026'

# Папка для сохранения историй
HISTORY_DIR = "chat_histories"
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs("generated", exist_ok=True)

# ========== ЗАГРУЗКА КОНСТИТУЦИИ ==========
def load_constitution():
    rules = {}
    try:
        with open("constitution.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                rules[key.strip()] = value.strip()
    except:
        rules = {}
    return rules

CONSTITUTION = load_constitution()

# ========== ПРОВЕРКА БЕЗОПАСНОСТИ ==========
def check_safety(action, details=""):
    rule = CONSTITUTION.get(action, "CONFIRM")
    if rule == "BLOCK":
        return {"allowed": False, "reason": f"Действие '{action}' запрещено конституцией"}
    elif rule == "CONFIRM":
        return {"allowed": True, "requires_confirmation": True, "action": action, "details": details}
    else:
        return {"allowed": True, "requires_confirmation": False}

# ========== ЗАПРОС К OLLAMA ==========
def query_ollama(prompt, conversation_history=None):
    """Отправляет запрос локальной модели через Ollama с учётом истории"""
    
    system_prompt = """Ты — мощный ИИ-ассистент. Ты можешь:
1. Писать код на любых языках (Python, C++, JS, Go, Rust)
2. Создавать Telegram-ботов и приложения
3. Генерировать исследовательский код (для обучения)
4. Управлять ПК с разрешения пользователя

Твои ответы должны быть максимально полезными. Если тебя просят код — выдавай полный, готовый к запуску код.
Отвечай на том же языке, на котором спрашивают."""
    
    # Формируем промпт с историей
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        for msg in conversation_history[-10:]:  # последние 10 сообщений для контекста
            messages.append(msg)
    messages.append({"role": "user", "content": prompt})
    
    # Пробуем разные модели
    models = ["qwen2.5:7b", "phi3:mini", "llama3.2:3b", "tinyllama:1.1b"]
    
    for model in models:
        try:
            # Создаём временный файл с промптом
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                full_prompt = f"{system_prompt}\n\n"
                if conversation_history:
                    for msg in conversation_history[-6:]:
                        full_prompt += f"{msg['role']}: {msg['content']}\n"
                full_prompt += f"user: {prompt}\n\nassistant:"
                f.write(full_prompt)
                temp_file = f.name
            
            cmd = ["ollama", "run", model]
            result = subprocess.run(
                cmd,
                input=full_prompt.encode('utf-8'),
                capture_output=True,
                timeout=180
            )
            os.unlink(temp_file)
            
            if result.returncode == 0:
                response = result.stdout.decode('utf-8', errors='replace').strip()
                # Обрезаем возможные повторения
                if len(response) > 5000:
                    response = response[:5000] + "\n\n...[ответ сокращён]..."
                return response
        except Exception as e:
            continue
    
    return "❌ Ошибка: Не удалось подключиться к Ollama. Убедись, что Ollama установлен и запущен (`ollama serve`)."

# ========== СОХРАНЕНИЕ ИСТОРИИ ==========
def save_conversation(session_id, messages):
    """Сохраняет историю чата"""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({
            "session_id": session_id,
            "messages": messages,
            "updated_at": datetime.now().isoformat()
        }, f, ensure_ascii=False, indent=2)

def load_conversation(session_id):
    """Загружает историю чата"""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])
    return []

def get_all_sessions():
    """Возвращает список всех сессий"""
    sessions = []
    for filename in os.listdir(HISTORY_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(HISTORY_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append({
                    "id": data["session_id"],
                    "updated_at": data.get("updated_at", ""),
                    "preview": data["messages"][0]["content"][:50] if data["messages"] else "Новый чат"
                })
    return sorted(sessions, key=lambda x: x["updated_at"], reverse=True)

# ========== СОХРАНЕНИЕ КОДА ==========
def save_generated_code(code, language):
    """Сохраняет сгенерированный код"""
    extensions = {
        "python": "py", "javascript": "js", "cpp": "cpp",
        "html": "html", "telegram_bot": "py"
    }
    ext = extensions.get(language.lower(), "txt")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"generated/code_{timestamp}.{ext}"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename

# ========== ВЕБ-МАРШРУТЫ ==========
@app.route('/')
def index():
    """Главная страница с чатом"""
    session_id = request.args.get('session', None)
    return render_template('chat.html', session_id=session_id)

@app.route('/api/chat', methods=['POST'])
def chat():
    """API для отправки сообщений"""
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    history = data.get('history', [])
    
    if not message:
        return jsonify({"error": "Сообщение пустое"}), 400
    
    # Добавляем сообщение пользователя в историю
    history.append({"role": "user", "content": message})
    
    # Получаем ответ от ИИ
    response = query_ollama(message, history[:-1])
    
    # Добавляем ответ в историю
    history.append({"role": "assistant", "content": response})
    
    # Сохраняем историю
    save_conversation(session_id, history)
    
    # Проверяем, есть ли код в ответе для сохранения
    saved_file = None
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
                    saved_file = save_generated_code(code_str, current_lang)
            elif in_code:
                code_buffer.append(line)
    
    return jsonify({
        "response": response,
        "history": history,
        "saved_file": saved_file
    })

@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """Список всех чатов"""
    return jsonify(get_all_sessions())

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Загружает конкретную сессию"""
    history = load_conversation(session_id)
    return jsonify({"history": history})

@app.route('/api/session/new', methods=['POST'])
def new_session():
    """Создаёт новую сессию"""
    from uuid import uuid4
    session_id = str(uuid4())[:8]
    save_conversation(session_id, [])
    return jsonify({"session_id": session_id})

@app.route('/api/session/delete/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """Удаляет сессию"""
    filepath = os.path.join(HISTORY_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
    return jsonify({"success": True})

if __name__ == '__main__':
    print("=" * 60)
    print("🤖 MY AI AGENT — ВЕБ-ИНТЕРФЕЙС")
    print("=" * 60)
    print("🌐 Открой в браузере: http://localhost:5000")
    print("💾 Истории чатов сохраняются автоматически")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
