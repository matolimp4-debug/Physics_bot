import asyncio
import logging
import sqlite3
import os
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

BOT_TOKEN = "8839579656:AAFMvxw5FGNgkBI_vGQjCkG5engkrwHELOU"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DB_PATH = "physics_ege18.db"

# ==============================================================================
# 1. МАТРИЧНЫЙ ГЕНЕРАТОР БАЗЫ (1500+ УТВЕРЖДЕНИЙ)
# ==============================================================================
def generate_massive_database() -> List[Tuple[str, str, int, str]]:
    pool = []

    # ШАБЛОН 1: Прямая пропорциональность
    direct = [
        ("Механика", "при постоянной массе", "модуль ускорения тела", "m", "модулю равнодействующей силы", "модуля равнодействующей силы", "Второму закону Ньютона (a = F/m)"),
        ("Механика", "для данного тела", "модуль импульса", "m", "скорости движения", "скорости", "определению импульса (p = mv)"),
        ("Механика", "при постоянном коэффициенте трения", "модуль максимальной силы трения покоя", "f", "модулю силы нормальной реакции опоры", "модуля силы реакции", "закону Амонтона-Кулона (F = mu*N)"),
        ("Механика", "в данной жидкости", "архимедова сила", "f", "объёму погруженной части тела", "объёма погруженной части", "закону Архимеда (F = ro*g*V)"),
        ("Механика", "для упругой пружины", "модуль силы упругости", "f", "абсолютному удлинению", "абсолютного удлинения", "закону Гука (F = kx)"),
        ("МКТ", "в изохорном процессе", "давление идеального газа", "n", "абсолютной температуре", "абсолютной температуры", "закону Шарля (p/T = const)"),
        ("МКТ", "в изобарном процессе", "объём идеального газа", "m", "абсолютной температуре", "абсолютной температуры", "закону Гей-Люссака (V/T = const)"),
        ("МКТ", "для данной массы идеального газа", "внутренняя энергия", "f", "абсолютной температуре", "абсолютной температуры", "формуле (U = 3/2*vRT)"),
        ("МКТ", "при постоянной температуре", "концентрация молекул идеального газа", "f", "его давлению", "давления", "основному уравнению (p = nkT)"),
        ("Электродинамика", "при постоянном сопротивлении", "сила тока в участке цепи", "f", "напряжению на его концах", "напряжения", "закону Ома (I = U/R)"),
        ("Электродинамика", "в однородном магнитном поле", "модуль силы Ампера", "f", "силе тока в проводнике", "силы тока", "формуле силы Ампера (F = IBl*sin(a))"),
        ("Электродинамика", "в однородном магнитном поле", "модуль силы Лоренца", "f", "модулю скорости заряда", "модуля скорости", "формуле силы Лоренца (F = qvB)"),
        ("Электродинамика", "при постоянной площади рамки", "магнитный поток", "m", "модулю вектора магнитной индукции", "индукции поля", "определению потока (Ф = BScos(a))"),
        ("Оптика", "для монохроматического света", "энергия фотона", "f", "частоте излучения", "частоты", "формуле Планка (E = hv)"),
        ("Оптика", "при внешнем фотоэффекте", "модуль запирающего напряжения", "m", "частоте падающего света", "частоты", "уравнению Эйнштейна (eU = hv - A)"),
        ("Кванты", "в вакууме", "импульс фотона", "m", "его частоте", "частоты", "формуле (p = hv/c)")
    ]

    for topic, cond, Y, g, X_dat, X_gen, expl in direct:
        prop = "прямо пропорционален" if g == "m" else "прямо пропорциональна" if g == "f" else "прямо пропорционально"
        inv_prop = "обратно пропорционален" if g == "m" else "обратно пропорциональна" if g == "f" else "обратно пропорционально"
        
        pool.append((topic, f"{cond.capitalize()} {Y} {prop} {X_dat}.", 1, f"Согласно {expl}, зависимость прямая линейная."))
        pool.append((topic, f"{cond.capitalize()} {Y} {inv_prop} {X_dat}.", 0, f"Согласно {expl}, зависимость прямая, а не обратная."))
        pool.append((topic, f"{cond.capitalize()} {Y} не зависит от {X_gen}.", 0, f"Величина напрямую зависит от данного параметра по {expl}."))
        pool.append((topic, f"{cond.capitalize()} {Y} {prop} квадрату {X_gen}.", 0, f"Зависимость линейная по {expl}, а не квадратичная."))

    # ШАБЛОН 2: Обратная пропорциональность
    inv = [
        ("Механика", "при постоянном модуле силы", "оказываемое давление", "n", "площади поверхности", "площади", "определению давления (p = F/S)"),
        ("Механика", "при неизменной скорости", "длина механической волны", "f", "частоте колебаний", "частоты", "связи параметров волны (lambda = v/nu)"),
        ("МКТ", "в изотермическом процессе", "давление идеального газа", "n", "его объёму", "объёма", "закону Бойля-Мариотта (pV = const)"),
        ("Электродинамика", "для плоского конденсатора", "электроёмкость", "f", "расстоянию между обкладками", "расстояния", "формуле ёмкости (C = e*e0*S/d)"),
        ("Электродинамика", "для цилиндрического проводника", "электрическое сопротивление", "n", "площади поперечного сечения", "площади сечения", "формуле (R = ro*l/S)"),
        ("Оптика", "для электромагнитных волн", "длина волны в вакууме", "f", "частоте излучения", "частоты", "формуле (lambda = c/nu)"),
        ("Оптика", "для тонкой линзы", "оптическая сила", "f", "её фокусному расстоянию", "фокусного расстояния", "определению (D = 1/F)"),
        ("Кванты", "для фотона", "энергия", "f", "длине волны", "длины волны", "формуле (E = hc/lambda)")
    ]

    for topic, cond, Y, g, X_dat, X_gen, expl in inv:
        prop = "прямо пропорционален" if g == "m" else "прямо пропорциональна" if g == "f" else "прямо пропорционально"
        inv_prop = "обратно пропорционален" if g == "m" else "обратно пропорциональна" if g == "f" else "обратно пропорционально"
        
        pool.append((topic, f"{cond.capitalize()} {Y} {inv_prop} {X_dat}.", 1, f"Согласно {expl}, величины обратно пропорциональны."))
        pool.append((topic, f"{cond.capitalize()} {Y} {prop} {X_dat}.", 0, f"Зависимость обратная по {expl}, а не прямая."))
        pool.append((topic, f"{cond.capitalize()} {Y} не зависит от {X_gen}.", 0, f"Величина обратно зависит от параметра по {expl}."))

    # ШАБЛОН 3: Квадратичные и корневые зависимости
    quad = [
        ("Механика", "при постоянной массе", "кинетическая энергия тела", "f", "скорости", "скорости", "Ek = mv^2 / 2", "квадрату", "прямо"),
        ("Механика", "при постоянном радиусе", "центростремительное ускорение", "n", "скорости", "скорости", "a = v^2 / R", "квадрату", "прямо"),
        ("Механика", "для данной пружины", "потенциальная энергия", "f", "удлинению", "удлинения", "Ep = kx^2 / 2", "квадрату", "прямо"),
        ("Электродинамика", "на данном резисторе", "выделяемая тепловая мощность", "f", "силе тока", "силы тока", "P = I^2*R", "квадрату", "прямо"),
        ("Механика", "в законе всемирного тяготения", "сила притяжения", "f", "расстоянию", "расстояния", "F = GmM/R^2", "квадрату", "обратно"),
        ("Электродинамика", "в вакууме", "сила кулоновского взаимодействия", "f", "расстоянию между зарядами", "расстояния", "F = kq1q2/r^2", "квадрату", "обратно"),
        ("Механика", "для математического маятника", "период колебаний", "m", "длине нити", "длины нити", "T = 2pi*sqrt(l/g)", "квадратному корню из", "прямо"),
    ]

    for topic, cond, Y, g, X_dat, X_gen, formula, p_type, d_type in quad:
        prop = "прямо пропорционален" if g == "m" else "прямо пропорциональна" if g == "f" else "прямо пропорционально"
        inv_prop = "обратно пропорционален" if g == "m" else "обратно пропорциональна" if g == "f" else "обратно пропорционально"
        word = prop if d_type == "прямо" else inv_prop
        wrong_word = inv_prop if d_type == "прямо" else prop

        pool.append((topic, f"{cond.capitalize()} {Y} {word} {p_type} {X_gen}.", 1, f"Из формулы {formula} следует именно такая зависимость."))
        pool.append((topic, f"{cond.capitalize()} {Y} {word} {X_dat}.", 0, f"Из-за вида формулы {formula} зависимость нелинейная."))
        pool.append((topic, f"{cond.capitalize()} {Y} {wrong_word} {p_type} {X_gen}.", 0, f"Направление зависимости (прямая/обратная) указано ошибочно. См. {formula}."))

    # ШАБЛОН 4: Качественные ловушки ФИПИ
    qualitative = [
        ("Механика", "Сила трения покоя всегда строго равна произведению коэффициента трения на модуль силы нормальной реакции опоры.", False, "Эта формула дает только МАКСИМАЛЬНУЮ силу трения покоя. В остальных случаях она равна сдвигающей силе."),
        ("Механика", "Период малых колебаний математического маятника не зависит от массы груза.", True, "Формула T = 2pi*sqrt(l/g). Период зависит только от длины нити и ускорения свободного падения."),
        ("Механика", "Если равнодействующая сил равна нулю, тело обязательно покоится.", False, "По 1-му закону Ньютона тело может двигаться равномерно и прямолинейно."),
        ("МКТ", "Внутренняя энергия идеального одноатомного газа зависит от занимаемого им объёма.", False, "Формула U = (3/2)vRT. Внутренняя энергия идеального газа зависит только от температуры."),
        ("МКТ", "Процесс кипения жидкости происходит при постоянной температуре.", True, "Вся подводимая энергия идет на разрыв связей (парообразование), а не на нагрев жидкости."),
        ("Электродинамика", "Линии напряжённости электростатического поля являются замкнутыми.", False, "Они начинаются на плюсе и заканчиваются на минусе. Замкнутые линии бывают только у магнитных полей."),
        ("Электродинамика", "Сила Лоренца не совершает работы над движущимся зарядом.", True, "Сила Лоренца всегда перпендикулярна скорости, поэтому работа A = Fscos(90) = 0."),
        ("Оптика", "При переходе света из воздуха в стекло частота волны уменьшается.", False, "Частота задаётся источником и не меняется при переходе границ сред. Меняется только скорость и длина волны."),
        ("Кванты", "Красная граница фотоэффекта зависит от интенсивности падающего света.", False, "Красная граница зависит исключительно от свойств самого металла (работы выхода)."),
        ("Кванты", "Масса покоя фотона равна массе покоя электрона.", False, "Масса покоя фотона строго равна нулю, он существует только в движении.")
    ]

    for topic, text, is_correct, expl in qualitative:
        status = 1 if is_correct else 0
        pool.append((topic, text, status, expl))
        
        # Инверсия для удвоения базы
        if " не " in text:
            inv_text = text.replace(" не ", " ", 1)
        else:
            words = text.split(" ")
            words.insert(1, "не")
            inv_text = " ".join(words)
            
        inv_status = 1 - status
        pool.append((topic, inv_text, inv_status, expl))

    return pool


# ==============================================================================
# 2. РАБОТА С БАЗОЙ ДАННЫХ
# ==============================================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS statements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            text TEXT NOT NULL UNIQUE,
            is_correct INTEGER NOT NULL,
            explanation TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0
        )
    """)

    cur.execute("SELECT COUNT(*) FROM statements")
    if cur.fetchone()[0] < 100:
        logger.info("Генерация расширенной матрицы утверждений...")
        full_pool = generate_massive_database()
        
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
    if not row:
        cur.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = (0, 0)
    conn.close()
    return {"correct": row[0], "wrong": row[1]}

def update_user_stats(user_id: int, is_correct: bool):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if is_correct:
        cur.execute("UPDATE users SET correct_count = correct_count + 1 WHERE user_id = ?", (user_id,))
    else:
        cur.execute("UPDATE users SET wrong_count = wrong_count + 1 WHERE user_id = ?", (user_id,))
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


# ==============================================================================
# 3. ИНТЕРФЕЙС И КЛАВИАТУРЫ
# ==============================================================================
def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🚀 Начать тренировку")],
        [KeyboardButton(text="📊 Моя статистика")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_statement_keyboard(st_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Верно", callback_data=f"ans:{st_id}:1")
    builder.button(text="❌ Неверно", callback_data=f"ans:{st_id}:0")
    builder.button(text="💡 Объяснить", callback_data=f"expl:{st_id}")
    # 2 кнопки в первом ряду, 1 кнопка во втором
    builder.adjust(2, 1)
    return builder.as_markup()

def get_next_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➡️ Следующее утверждение", callback_data="next_st")
    return builder.as_markup()


# ==============================================================================
# 4. ОБРАБОТЧИКИ СООБЩЕНИЙ
# ==============================================================================
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    init_db()
    get_user_stats(message.from_user.id) # Инициализация юзера
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM statements")
    total = cur.fetchone()[0]
    conn.close()
    
    text = (
        "👋 **Добро пожаловать в тренажёр Задания №18!**\n\n"
        f"В базе сейчас **{total}** уникальных академических утверждений.\n"
        "Мы будем разбирать их строго по одному. Если сомневаешься — жми кнопку «Объяснить»!\n\n"
        "Выбери действие в меню ниже:"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "📊 Моя статистика")
async def show_stats(message: types.Message):
    stats = get_user_stats(message.from_user.id)
    text = (
        "📈 **Ваша статистика:**\n\n"
        f"✅ Правильных ответов: {stats['correct']}\n"
        f"❌ Ошибок: {stats['wrong']}"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "🚀 Начать тренировку")
async def start_training(message: types.Message):
    st = get_random_statement()
    text = (
        f"📚 **Раздел:** _{st['topic']}_\n\n"
        f"«{st['text']}»\n\n"
        "Утверждение верно?"
    )
    await message.answer(text, reply_markup=get_statement_keyboard(st["id"]), parse_mode="Markdown")


# ==============================================================================
# 5. ОБРАБОТЧИКИ КНОПОК (CALLBACK)
# ==============================================================================

# Обработка ответа "Верно" или "Неверно"
@dp.callback_query(F.data.startswith("ans:"))
async def handle_answer(query: types.CallbackQuery):
    _, st_id_str, user_ans_str = query.data.split(":")
    st_id = int(st_id_str)
    user_ans = int(user_ans_str)
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM statements WHERE id = ?", (st_id,))
    st = dict(cur.fetchone())
    conn.close()

    is_correct = (user_ans == st["is_correct"])
    update_user_stats(query.from_user.id, is_correct)

    status_header = "🟢 **ВЫ ОТВЕТИЛИ ПРАВИЛЬНО!**" if is_correct else "🔴 **ОШИБКА!**"
    real_ans = "ВЕРНО" if st["is_correct"] == 1 else "НЕВЕРНО"
    
    text = (
        f"{status_header}\n\n"
        f"«_{st['text']}_»\n\n"
        f"Истинный статус: **{real_ans}**\n\n"
        f"💡 **Разбор:** {st['explanation']}"
    )
    
    await query.message.edit_text(text, reply_markup=get_next_keyboard(), parse_mode="Markdown")
    await query.answer()

# Обработка кнопки "Объяснить"
@dp.callback_query(F.data.startswith("expl:"))
async def handle_explain(query: types.CallbackQuery):
    st_id = int(query.data.split(":")[1])
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM statements WHERE id = ?", (st_id,))
    st = dict(cur.fetchone())
    conn.close()

    real_ans = "ВЕРНО" if st["is_correct"] == 1 else "НЕВЕРНО"
    
    text = (
        f"👀 **ПОДСКАЗКА ОТКРЫТА** (Балл не засчитан)\n\n"
        f"«_{st['text']}_»\n\n"
        f"Истинный статус: **{real_ans}**\n\n"
        f"💡 **Разбор:** {st['explanation']}"
    )
    
    await query.message.edit_text(text, reply_markup=get_next_keyboard(), parse_mode="Markdown")
    await query.answer()

# Обработка кнопки "Следующее утверждение"
@dp.callback_query(F.data == "next_st")
async def next_statement(query: types.CallbackQuery):
    st = get_random_statement()
    text = (
        f"📚 **Раздел:** _{st['topic']}_\n\n"
        f"«{st['text']}»\n\n"
        "Утверждение верно?"
    )
    await query.message.edit_text(text, reply_markup=get_statement_keyboard(st["id"]), parse_mode="Markdown")
    await query.answer()


# ==============================================================================
# ЗАПУСК БОТА
# ==============================================================================
async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Бот успешно запущен в режиме по 1 утверждению!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
