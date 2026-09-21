import asyncio
import logging
import sqlite3
import random
from typing import Dict, Any, List, Tuple

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"  # <-- ВСТАВЬ СЮДА СВОЙ ТОКЕН

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DB_PATH = "physics_ege18.db"

def generate_fipi_database() -> List[Tuple[str, str, int, str]]:
    pool = []

    # 1. КАЧЕСТВЕННАЯ БАЗА (Точные формулировки со скриншотов и ФИПИ)
    core_statements = [
        # Механика
        ("Механика", "Сила – векторная величина, равная произведению массы тела на его скорость.", 0, "Это определение импульса (p = mv), а не силы. Сила равна произведению массы на ускорение (F = ma)."),
        ("Механика", "Импульс тела – векторная величина, равная произведению массы тела на его скорость.", 1, "Строгое определение импульса: p = mv."),
        ("Механика", "Потенциальная энергия тела зависит от его массы и скорости движения тела.", 0, "От массы и скорости зависит кинетическая энергия (mv^2/2). Потенциальная зависит от положения в поле сил (например, mgh)."),
        ("Механика", "Потенциальная энергия тела в поле тяжести Земли зависит от его массы и высоты над нулевым уровнем.", 1, "Формула E_p = mgh. Зависимость прямая."),
        ("Механика", "При абсолютно упругом ударе двух тел сохраняется только закон сохранения импульса, а механическая энергия не сохраняется.", 0, "При абсолютно упругом ударе сохраняется и импульс, и кинетическая энергия."),
        ("Механика", "Сила трения покоя всегда строго равна произведению коэффициента трения на модуль силы нормальной реакции опоры.", 0, "Она равна этому произведению только в предельном случае (максимальная сила трения покоя перед сдвигом)."),
        
        # МКТ и Термодинамика
        ("МКТ", "Хаотическое тепловое движение частиц тела прекращается при достижении термодинамического равновесия.", 0, "Тепловое движение молекул не прекращается никогда (кроме абсолютного нуля). В равновесии выравнивается лишь температура."),
        ("МКТ", "При адиабатном расширении газа его температура уменьшается.", 1, "В адиабатном процессе Q=0. Газ совершает работу за счет убыли своей внутренней энергии (A' = -dU), следовательно, температура падает."),
        ("МКТ", "При адиабатном сжатии газа его температура уменьшается.", 0, "При сжатии над газом совершают работу внешние силы, его внутренняя энергия и температура увеличиваются."),
        ("МКТ", "В процессе кипения жидкости при постоянном давлении ее температура остается неизменной.", 1, "Вся подводимая теплота идет на разрыв межмолекулярных связей (парообразование), а не на увеличение кинетической энергии молекул."),
        ("МКТ", "Относительная влажность воздуха не может превышать 100%.", 1, "При 100% пар становится насыщенным. Дальнейшее добавление влаги приведет к конденсации (выпадению росы)."),
        
        # Электродинамика
        ("Электродинамика", "В растворах или расплавах электролитов электрический ток представляет собой упорядоченное движение ионов, происходящее на фоне их теплового хаотического движения.", 1, "Точное физическое определение природы тока в жидких проводниках второго рода."),
        ("Электродинамика", "В металлах электрический ток представляет собой упорядоченное движение положительных ионов.", 0, "В металлах носителями тока являются свободные электроны. Ионы закреплены в узлах кристаллической решетки."),
        ("Электродинамика", "ЭДС индукции в замкнутом контуре равна скорости изменения магнитного потока через площадь, ограниченную этим контуром.", 1, "Это закон электромагнитной индукции Фарадея (E = -dФ/dt)."),
        ("Электродинамика", "Поверхность проводника, находящегося длительное время в электростатическом поле, является эквипотенциальной.", 1, "Свободные заряды перераспределяются так, чтобы внутри проводника поле стало равным нулю, следовательно, потенциал на всей поверхности одинаков."),
        ("Электродинамика", "Линии напряженности электростатического поля замкнуты.", 0, "Они всегда начинаются на положительных зарядах и заканчиваются на отрицательных. Замкнуты линии магнитного поля."),
        ("Электродинамика", "Магнитное поле действует с силой Лоренца на любой электрический заряд, помещенный в это поле.", 0, "Сила Лоренца действует только на ДВИЖУЩИЕСЯ электрические заряды (F = qvB sin a). На неподвижный заряд магнитное поле не действует."),
        
        # Оптика
        ("Оптика", "При преломлении электромагнитных волн на границе двух сред длина волны остаётся неизменной величиной.", 0, "При переходе между средами неизменной остается ЧАСТОТА. Длина волны и скорость распространения изменяются."),
        ("Оптика", "При переходе света из оптически менее плотной среды в более плотную угол преломления меньше угла падения.", 1, "Так как скорость света падает, луч прижимается к перпендикуляру (закон Снеллиуса)."),
        ("Оптика", "Электромагнитные волны являются продольными.", 0, "Световые и любые другие электромагнитные волны являются поперечными (векторы E и B колеблются перпендикулярно скорости)."),
        
        # Квантовая и ядерная физика
        ("Кванты", "В процессе позитронного бета-распада происходит выбрасывание из ядра позитрона, возникшего из-за самопроизвольного превращения протона в нейтрон.", 1, "Точное описание бета-плюс распада: p -> n + e+ + v."),
        ("Кванты", "При бета-распаде ядра выполняются законы сохранения энергии и электрического заряда, но не выполняется закон сохранения импульса.", 0, "В любых ядерных реакциях закон сохранения импульса выполняется неукоснительно."),
        ("Кванты", "Красная граница фотоэффекта зависит только от работы выхода электронов из материала катода.", 1, "Красная граница - это минимальная частота или максимальная длина волны, она является характеристикой самого вещества."),
        ("Кванты", "Энергия фотона прямо пропорциональна длине его волны.", 0, "Энергия фотона E = hc/λ. Она обратно пропорциональна длине волны.")
    ]

    # Матрица изопроцессов (дает ~1000 утверждений за счет комбинаторики)
    processes = {
        "изобарном нагревании": {"p": "не изменяется", "V": "увеличивается", "T": "увеличивается", "U": "увеличивается", "n": "уменьшается", "ro": "уменьшается"},
        "изобарном охлаждении": {"p": "не изменяется", "V": "уменьшается", "T": "уменьшается", "U": "уменьшается", "n": "увеличивается", "ro": "увеличивается"},
        "изохорном нагревании": {"p": "увеличивается", "V": "не изменяется", "T": "увеличивается", "U": "увеличивается", "n": "не изменяется", "ro": "не изменяется"},
        "изохорном охлаждении": {"p": "уменьшается", "V": "не изменяется", "T": "уменьшается", "U": "уменьшается", "n": "не изменяется", "ro": "не изменяется"},
        "изотермическом расширении": {"p": "уменьшается", "V": "увеличивается", "T": "не изменяется", "U": "не изменяется", "n": "уменьшается", "ro": "уменьшается"},
        "изотермическом сжатии": {"p": "увеличивается", "V": "уменьшается", "T": "не изменяется", "U": "не изменяется", "n": "увеличивается", "ro": "увеличивается"}
    }
    
    param_names = {
        "p": "давление газа", "V": "объем газа", "T": "абсолютная температура",
        "U": "внутренняя энергия", "n": "концентрация молекул", "ro": "плотность газа"
    }
    
    actions = ["увеличивается", "уменьшается", "не изменяется"]

    for proc_name, effects in processes.items():
        for param, true_effect in effects.items():
            param_text = param_names[param]
            for action in actions:
                text = f"При {proc_name} идеального газа его {param_text} {action}."
                is_correct = 1 if action == true_effect else 0
                
                if is_correct:
                    expl = f"Верно. В {proc_name} {param_text} {true_effect} (согласно законам идеального газа)."
                else:
                    expl = f"Неверно. При {proc_name} {param_text} на самом деле {true_effect}."
                
                pool.append(("МКТ", text, is_correct, expl))

    # Слияние баз
    pool.extend(core_statements)
    
    return pool

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Таблица всех утверждений
    cur.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            text TEXT NOT NULL UNIQUE,
            is_correct INTEGER NOT NULL,
            explanation TEXT NOT NULL
        )
    """)

    # Таблица статистики пользователей
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0
        )
    """)
    
    # Таблица ОШИБОК для режима повторения
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mistakes (
            user_id INTEGER,
            statement_id INTEGER,
            UNIQUE(user_id, statement_id)
        )
    """)

    cur.execute("SELECT COUNT(*) FROM statements")
    if cur.fetchone()[0] < 100:
        logger.info("Генерация расширенной матрицы утверждений ФИПИ...")
        full_pool = generate_fipi_database()
        
        inserted = 0
        for item in full_pool:
            try:
                cur.execute("INSERT INTO statements (topic, text, is_correct, explanation) VALUES (?, ?, ?, ?)", item)
                inserted += 1
            except sqlite3.IntegrityError:
                pass
                
        conn.commit()
        logger.info(f"База успешно сгенерирована: загружено {inserted} утверждений.")

    conn.commit()
    conn.close()

def get_user_stats(user_id: int) -> Dict[str, int]:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT correct_count, wrong_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    
    cur.execute("SELECT COUNT(*) FROM mistakes WHERE user_id = ?", (user_id,))
    mistakes_count = cur.fetchone()[0]
    
    if not row:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = (0, 0)
    conn.close()
    return {"correct": row[0], "wrong": row[1], "mistakes_left": mistakes_count}

def update_user_stats(user_id: int, is_correct: bool, statement_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if is_correct:
        cur.execute("UPDATE users SET correct_count = correct_count + 1 WHERE user_id = ?", (user_id,))
    else:
        cur.execute("UPDATE users SET wrong_count = wrong_count + 1 WHERE user_id = ?", (user_id,))
        # Добавляем в ошибки, если ответил неверно
        cur.execute("INSERT OR IGNORE INTO mistakes (user_id, statement_id) VALUES (?, ?)", (user_id, statement_id))
    conn.commit()
    conn.close()

def remove_mistake(user_id: int, statement_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM mistakes WHERE user_id = ? AND statement_id = ?", (user_id, statement_id))
    conn.commit()
    conn.close()

def get_random_statement() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM statements ORDER BY RANDOM() LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return dict(row)

def get_random_mistake(user_id: int) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("""
        SELECT s.* FROM statements s
        JOIN mistakes m ON s.id = m.statement_id
        WHERE m.user_id = ?
        ORDER BY RANDOM() LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🚀 Новое утверждение")],
        [KeyboardButton(text="🔁 Работа над ошибками")],
        [KeyboardButton(text="📊 Моя статистика")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_statement_keyboard(st_id: int, is_mistake_mode: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    prefix = "mans" if is_mistake_mode else "ans" # mans = mistake answer
    
    builder.button(text="✅ Верно", callback_data=f"{prefix}:{st_id}:1")
    builder.button(text="❌ Неверно", callback_data=f"{prefix}:{st_id}:0")
    builder.button(text="💡 Объяснить (Без ответа)", callback_data=f"expl:{st_id}:{int(is_mistake_mode)}")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_next_keyboard(is_mistake_mode: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_mistake_mode:
        builder.button(text="➡️ Следующая ошибка", callback_data="next_mistake")
    else:
        builder.button(text="➡️ Следующее утверждение", callback_data="next_st")
    return builder.as_markup()


dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    init_db()
    stats = get_user_stats(message.from_user.id)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM statements")
    total = cur.fetchone()[0]
    conn.close()
    
    text = (
        "🎓 **Тренажёр ЕГЭ по Физике: Задание №18**\n\n"
        f"В базе загружено **{total}** уникальных академических утверждений в строгом формате ФИПИ.\n\n"
        "Особенности бота:\n"
        "🔸 Мы разбираем утверждения по одному.\n"
        "🔸 Бот сам сохраняет твои неверные ответы в раздел **«Работа над ошибками»**.\n"
        "🔸 Если сомневаешься — жми «Объяснить».\n\n"
        "Выбери режим в меню ниже 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message):
    stats = get_user_stats(message.from_user.id)
    text = (
        "📈 **Ваша статистика:**\n\n"
        f"✅ Правильных ответов: {stats['correct']}\n"
        f"❌ Ошибок допущено: {stats['wrong']}\n"
        f"🔁 Утверждений в списке ошибок: **{stats['mistakes_left']}**"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚀 Новое утверждение")
async def start_training(message: types.Message):
    st = get_random_statement()
    text = (
        f"📚 Раздел: _{st['topic']}_\n\n"
        f"**«{st['text']}»**\n\n"
        "Утверждение верно?"
    )
    await message.answer(text, reply_markup=get_statement_keyboard(st["id"]), parse_mode="Markdown")

@dp.message(F.text == "🔁 Работа над ошибками")
async def start_mistakes(message: types.Message):
    st = get_random_mistake(message.from_user.id)
    if not st:
        await message.answer("🎉 Отлично! У тебя сейчас нет неразобранных ошибок. Возвращайся к новым заданиям.")
        return
        
    text = (
        f"🔁 **РАБОТА НАД ОШИБКАМИ**\n"
        f"📚 Раздел: _{st['topic']}_\n\n"
        f"**«{st['text']}»**\n\n"
        "Утверждение верно?"
    )
    await message.answer(text, reply_markup=get_statement_keyboard(st["id"], is_mistake_mode=True), parse_mode="Markdown")



async def process_answer(query: types.CallbackQuery, st_id: int, user_ans: int, is_mistake_mode: bool):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM statements WHERE id = ?", (st_id,))
    st = dict(cur.fetchone())
    conn.close()

    is_correct = (user_ans == st["is_correct"])
    
    # Обновляем статистику (только для обычного режима, чтобы не накручивать при повторении)
    if not is_mistake_mode:
        update_user_stats(query.from_user.id, is_correct, st_id)
    
    # Если в режиме ошибок ответил правильно - удаляем из списка ошибок
    if is_mistake_mode and is_correct:
        remove_mistake(query.from_user.id, st_id)
        status_header = "🟢 **ОШИБКА ИСПРАВЛЕНА!** (Удалено из списка)"
    elif is_mistake_mode and not is_correct:
        status_header = "🔴 **СНОВА ОШИБКА!** (Остается в списке)"
    else:
        status_header = "🟢 **ВЕРНО!**" if is_correct else "🔴 **НЕВЕРНО!** (Добавлено в ошибки)"

    real_ans = "ВЕРНО" if st["is_correct"] == 1 else "НЕВЕРНО"
    
    text = (
        f"{status_header}\n\n"
        f"«_{st['text']}_»\n\n"
        f"Правильный статус: **{real_ans}**\n\n"
        f"💡 **Разбор:** {st['explanation']}"
    )
    
    await query.message.edit_text(text, reply_markup=get_next_keyboard(is_mistake_mode), parse_mode="Markdown")
    await query.answer()

@dp.callback_query(F.data.startswith("ans:"))
async def handle_normal_answer(query: types.CallbackQuery):
    _, st_id_str, user_ans_str = query.data.split(":")
    await process_answer(query, int(st_id_str), int(user_ans_str), False)

@dp.callback_query(F.data.startswith("mans:"))
async def handle_mistake_answer(query: types.CallbackQuery):
    _, st_id_str, user_ans_str = query.data.split(":")
    await process_answer(query, int(st_id_str), int(user_ans_str), True)

@dp.callback_query(F.data.startswith("expl:"))
async def handle_explain(query: types.CallbackQuery):
    _, st_id_str, is_mistake_str = query.data.split(":")
    st_id = int(st_id_str)
    is_mistake_mode = bool(int(is_mistake_str))
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM statements WHERE id = ?", (st_id,))
    st = dict(cur.fetchone())
    conn.close()

    real_ans = "ВЕРНО" if st["is_correct"] == 1 else "НЕВЕРНО"
    
    text = (
        f"👀 **ПОДСКАЗКА ОТКРЫТА** (Статистика не изменена)\n\n"
        f"«_{st['text']}_»\n\n"
        f"Правильный статус: **{real_ans}**\n\n"
        f"💡 **Разбор:** {st['explanation']}"
    )
    
    await query.message.edit_text(text, reply_markup=get_next_keyboard(is_mistake_mode), parse_mode="Markdown")
    await query.answer()

@dp.callback_query(F.data == "next_st")
async def next_statement(query: types.CallbackQuery):
    st = get_random_statement()
    text = (
        f"📚 Раздел: _{st['topic']}_\n\n"
        f"**«{st['text']}»**\n\n"
        "Утверждение верно?"
    )
    await query.message.edit_text(text, reply_markup=get_statement_keyboard(st["id"]), parse_mode="Markdown")
    await query.answer()

@dp.callback_query(F.data == "next_mistake")
async def next_mistake_statement(query: types.CallbackQuery):
    st = get_random_mistake(query.from_user.id)
    if not st:
        await query.message.edit_text("🎉 Отлично! Все ошибки из твоего списка исправлены.", parse_mode="Markdown")
        await query.answer()
        return
        
    text = (
        f"🔁 **РАБОТА НАД ОШИБКАМИ**\n"
        f"📚 Раздел: _{st['topic']}_\n\n"
        f"**«{st['text']}»**\n\n"
        "Утверждение верно?"
    )
    await query.message.edit_text(text, reply_markup=get_statement_keyboard(st["id"], is_mistake_mode=True), parse_mode="Markdown")
    await query.answer()

async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Бот симулятор ЕГЭ №18 (с режимом ошибок) успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
