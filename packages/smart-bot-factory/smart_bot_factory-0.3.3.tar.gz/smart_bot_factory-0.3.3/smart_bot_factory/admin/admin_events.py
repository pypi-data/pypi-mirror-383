# Обработчики для создания админских событий

import logging
from datetime import datetime, time, timezone
from dateutil.relativedelta import relativedelta
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from ..aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
import pytz

logger = logging.getLogger(__name__)

# Московская временная зона
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# Импортируем состояния
from ..core.states import AdminStates

# Создаем роутер для админских событий
admin_events_router = Router()

def setup_admin_events_handlers(dp):
    """Настройка обработчиков админских событий"""
    dp.include_router(admin_events_router)

@admin_events_router.message(Command(commands=["создать_событие", "create_event"]))
async def create_event_start(message: Message, state: FSMContext):
    """Начало создания события"""
    from ..handlers.handlers import get_global_var
    admin_manager = get_global_var('admin_manager')
    
    if not admin_manager.is_admin(message.from_user.id):
        return
    
    await state.set_state(AdminStates.create_event_name)
    
    await message.answer(
        "📝 **Создание нового события**\n\n"
        "Введите название события:\n"
        "_(Название поможет вам идентифицировать событие для редактирования или удаления)_",
        parse_mode='Markdown'
    )

@admin_events_router.message(AdminStates.create_event_name)
async def process_event_name(message: Message, state: FSMContext):
    """Обработка названия события"""
    from ..handlers.handlers import get_global_var
    
    event_name = message.text.strip()
    
    if not event_name:
        await message.answer("❌ Название не может быть пустым. Попробуйте еще раз:")
        return
    
    # Проверяем уникальность названия (только среди активных событий)
    supabase_client = get_global_var('supabase_client')
    name_exists = await supabase_client.check_event_name_exists(event_name)
    
    if name_exists:
        await message.answer(
            f"⚠️ **Событие с названием «{event_name}» уже существует и находится в статусе ожидания!**\n\n"
            f"Пожалуйста, выберите другое название или дождитесь выполнения/отмены существующего события.\n\n"
            f"💡 _Вы можете использовать это же название после завершения или отмены текущего события._",
            parse_mode='Markdown'
        )
        return
    
    # Сохраняем название
    await state.update_data(event_name=event_name)
    await state.set_state(AdminStates.create_event_date)
    
    # Показываем календарь для выбора даты
    calendar = SimpleCalendar(locale='ru', today_btn='Сегодня', cancel_btn='Отмена')
    # Ограничиваем выбор датами от вчера до +12 месяцев (чтобы сегодня был доступен)
    calendar.set_dates_range(datetime.now() + relativedelta(days=-1), datetime.now() + relativedelta(months=+12))
    calendar_markup = await calendar.start_calendar()
    
    await message.answer(
        f"✅ Название события: **{event_name}**\n\n"
        "📅 Выберите дату отправки:",
        reply_markup=calendar_markup,
        parse_mode='Markdown'
    )

@admin_events_router.callback_query(SimpleCalendarCallback.filter(), AdminStates.create_event_date)
async def process_event_date(callback_query: CallbackQuery, callback_data: dict, state: FSMContext):
    """Обработка выбора даты"""
    calendar = SimpleCalendar(locale='ru', cancel_btn='Отмена', today_btn='Сегодня')
    
    # Ограничиваем выбор датами от вчера до +12 месяцев (чтобы сегодня был доступен)
    calendar.set_dates_range(datetime.now() + relativedelta(days=-1), datetime.now() + relativedelta(months=+12))
    selected, date = await calendar.process_selection(callback_query, callback_data)
    
    if selected == 'cancel':
        # Нажата кнопка "Отмена"
        await state.clear()
        await callback_query.message.edit_text(
            "❌ Создание события отменено",
            parse_mode='Markdown'
        )
    elif selected:
        # Дата выбрана успешно (True или обычный выбор)
        await state.update_data(event_date=date.strftime('%Y-%m-%d'))
        await state.set_state(AdminStates.create_event_time)
        
        await callback_query.message.edit_text(
            f"✅ Дата: **{date.strftime('%d.%m.%Y')}**\n\n"
            "⏰ Введите время отправки в формате ЧЧ:ММ\n"
            "_(Например: 14:30)_",
            parse_mode='Markdown'
        )
    # Если selected is False/None - это навигация по календарю, ничего не делаем
    # Календарь сам обновится при навигации

@admin_events_router.message(AdminStates.create_event_time)
async def process_event_time(message: Message, state: FSMContext):
    """Обработка времени события"""
    time_str = message.text.strip()
    
    # Валидация формата времени
    try:
        event_time = datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        await message.answer(
            "❌ Неверный формат времени. Используйте формат HH:MM\n"
            "_(Например: 14:30)_",
            parse_mode='Markdown'
        )
        return
    
    # Сохраняем время
    await state.update_data(event_time=time_str)
    await state.set_state(AdminStates.create_event_segment)
    
    # Получаем все доступные сегменты
    from ..handlers.handlers import get_global_var
    supabase_client = get_global_var('supabase_client')
    
    segments = await supabase_client.get_all_segments()
    
    # Создаем клавиатуру с сегментами
    keyboard = []
    
    # Большая кнопка "Отправить всем" на два столбца
    keyboard.append([
        InlineKeyboardButton(text="📢 Отправить всем", callback_data="segment:all")
    ])
    
    # Кнопки сегментов (по 2 в ряд)
    if segments:
        for i in range(0, len(segments), 2):
            row = []
            row.append(InlineKeyboardButton(
                text=f"👥 {segments[i]}", 
                callback_data=f"segment:{segments[i]}"
            ))
            if i + 1 < len(segments):
                row.append(InlineKeyboardButton(
                    text=f"👥 {segments[i+1]}", 
                    callback_data=f"segment:{segments[i+1]}"
                ))
            keyboard.append(row)
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    data = await state.get_data()
    await message.answer(
        f"✅ Время: **{time_str}**\n\n"
        f"👥 Выберите сегмент пользователей для отправки:\n"
        f"_(Найдено сегментов: {len(segments)})_",
        reply_markup=markup,
        parse_mode='Markdown'
    )

@admin_events_router.callback_query(F.data.startswith("segment:"), AdminStates.create_event_segment)
async def process_event_segment(callback_query: CallbackQuery, state: FSMContext):
    """Обработка выбора сегмента"""
    segment_data = callback_query.data.split(":", 1)[1]
    
    # segment_data = "all" или название сегмента
    segment_name = None if segment_data == "all" else segment_data
    segment_display = "Все пользователи" if segment_data == "all" else segment_data
    
    # Сохраняем сегмент
    await state.update_data(segment=segment_name, segment_display=segment_display)
    await state.set_state(AdminStates.create_event_message)
    
    await callback_query.message.edit_text(
        f"✅ Сегмент: **{segment_display}**\n\n"
        "💬 **Введите сообщение для пользователей**\n\n"
        "📸 _Вы можете прикрепить к сообщению **фото или видео** — они будут отправлены пользователям в том же порядке_\n\n"
        "📄 _Если нужно добавить **PDF или другие документы**, вы сможете это сделать на следующем шаге_",
        parse_mode='Markdown'
    )

@admin_events_router.message(AdminStates.create_event_message)
async def process_event_message(message: Message, state: FSMContext):
    """Обработка сообщения для пользователей"""
    event_message = message.text or message.caption or ""
    
    if not event_message.strip():
        await message.answer("❌ Сообщение не может быть пустым. Попробуйте еще раз:")
        return
    
    # Сохраняем сообщение и media_group_id если есть
    data_to_update = {'event_message': event_message}
    
    # Если это часть альбома (media group), сохраняем ID группы
    if message.media_group_id:
        data_to_update['media_group_id'] = message.media_group_id
        data_to_update['waiting_for_album'] = True
        logger.info(f"Обнаружен альбом с ID: {message.media_group_id}")
    
    await state.update_data(**data_to_update)
    
    # Если есть фото в сообщении, сохраняем его
    files = []
    if message.photo:
        import os
        from ..handlers.handlers import get_global_var
        bot = get_global_var('bot')
        
        # Создаем временную папку если её нет
        temp_dir = "temp_event_files"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Скачиваем фото
        photo = message.photo[-1]  # Берем самое большое фото
        file = await bot.get_file(photo.file_id)
        file_path = os.path.join(temp_dir, f"{photo.file_id}.jpg")
        await bot.download_file(file.file_path, file_path)
        
        files.append({
            'type': 'photo',
            'file_path': file_path,
            'name': f"{photo.file_id}.jpg",
            'stage': 'with_message',
            'has_caption': bool(message.caption)  # Первое фото с текстом
        })
        logger.info(f"Фото сохранено: {file_path} (with_message)")
    
    await state.update_data(files=files)
    
    # Если это НЕ альбом, переходим к добавлению файлов
    if not message.media_group_id:
        await state.set_state(AdminStates.create_event_files)
        
        # Кнопки для добавления файлов или пропуска
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить без файлов", callback_data="files:skip")]
        ])
        
        await message.answer(
            "✅ **Сообщение сохранено!**\n\n"
            "📎 **Дополнительные файлы**\n\n"
            "Теперь вы можете отправить:\n"
            "📄 PDF документы\n"
            "📁 Файлы любых форматов\n"
            "🎥 Дополнительные видео\n"
            "🖼 Дополнительные фото\n\n"
            "💡 _Можно отправить несколько файлов по очереди_\n\n"
            "Или нажмите кнопку, если дополнительных файлов нет:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    # Если альбом - ничего не делаем, остальные фото обработаются отдельным handler

@admin_events_router.message(AdminStates.create_event_message, F.photo)
async def process_album_photos(message: Message, state: FSMContext):
    """Обработка остальных фото из альбома"""
    import os
    from ..handlers.handlers import get_global_var
    
    data = await state.get_data()
    
    # Проверяем что это альбом и мы ждем остальные фото
    if not data.get('waiting_for_album'):
        return
    
    # Проверяем что это тот же альбом
    if message.media_group_id != data.get('media_group_id'):
        return
    
    bot = get_global_var('bot')
    files = data.get('files', [])
    
    # Создаем временную папку если её нет
    temp_dir = "temp_event_files"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Скачиваем фото
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = os.path.join(temp_dir, f"{photo.file_id}.jpg")
    await bot.download_file(file.file_path, file_path)
    
    files.append({
        'type': 'photo',
        'file_path': file_path,
        'name': f"{photo.file_id}.jpg",
        'stage': 'with_message',
        'has_caption': False  # Остальные фото без текста
    })
    
    await state.update_data(files=files)
    logger.info(f"Фото из альбома сохранено: {file_path} (with_message, всего: {len(files)})")
    
    # Автоматически переходим к следующему этапу через 2 секунды после последнего фото
    import asyncio
    await asyncio.sleep(2)
    
    # Проверяем что все еще ждем альбом (не было новых фото)
    data = await state.get_data()
    if data.get('waiting_for_album') and data.get('media_group_id') == message.media_group_id:
        # Все фото получены, переходим к добавлению доп файлов
        await state.update_data(waiting_for_album=False)
        await state.set_state(AdminStates.create_event_files)
        
        files_count = len(data.get('files', []))
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Продолжить", callback_data="files:skip")]
        ])
        
        await message.answer(
            f"✅ **Сообщение и {files_count} фото сохранены!**\n\n"
            "📎 **Дополнительные файлы**\n\n"
            "Теперь вы можете отправить:\n"
            "📄 PDF документы\n"
            "📁 Файлы любых форматов\n"
            "🎥 Дополнительные видео\n\n"
            "💡 _Можно отправить несколько файлов по очереди_\n\n"
            "Или нажмите кнопку, если дополнительных файлов нет:",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )

@admin_events_router.callback_query(F.data == "album:done", AdminStates.create_event_message)
async def finish_album_collection(callback_query: CallbackQuery, state: FSMContext):
    """Завершение сбора фото из альбома"""
    await state.update_data(waiting_for_album=False)
    await state.set_state(AdminStates.create_event_files)
    
    data = await state.get_data()
    files_count = len(data.get('files', []))
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Продолжить", callback_data="files:skip")]
    ])
    
    await callback_query.message.edit_text(
        f"✅ **Сообщение и {files_count} фото сохранены!**\n\n"
        "📎 **Дополнительные файлы**\n\n"
        "Теперь вы можете отправить:\n"
        "📄 PDF документы\n"
        "📁 Файлы любых форматов\n"
        "🎥 Дополнительные видео\n\n"
        "💡 _Эти файлы будут отправлены после сообщения_\n\n"
        "Или нажмите кнопку, если дополнительных файлов нет:",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@admin_events_router.message(AdminStates.create_event_files, F.document | F.photo | F.video)
async def process_event_files(message: Message, state: FSMContext):
    """Обработка файлов для события"""
    import os
    from ..handlers.handlers import get_global_var
    
    data = await state.get_data()
    files = data.get('files', [])
    bot = get_global_var('bot')
    
    # Создаем временную папку если её нет
    temp_dir = "temp_event_files"
    os.makedirs(temp_dir, exist_ok=True)
    
    # Скачиваем и добавляем файл в список
    if message.document:
        file = await bot.get_file(message.document.file_id)
        file_path = os.path.join(temp_dir, f"{message.document.file_id}_{message.document.file_name}")
        await bot.download_file(file.file_path, file_path)
        
        files.append({
            'type': 'document',
            'file_path': file_path,
            'name': message.document.file_name,
            'stage': 'after_message'
        })
        logger.info(f"Документ сохранен: {file_path} (after_message)")
        
    elif message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_path = os.path.join(temp_dir, f"{photo.file_id}.jpg")
        await bot.download_file(file.file_path, file_path)
        
        files.append({
            'type': 'photo',
            'file_path': file_path,
            'name': f"{photo.file_id}.jpg",
            'stage': 'after_message'
        })
        logger.info(f"Фото сохранено: {file_path} (after_message)")
        
    elif message.video:
        file = await bot.get_file(message.video.file_id)
        file_path = os.path.join(temp_dir, f"{message.video.file_id}.mp4")
        await bot.download_file(file.file_path, file_path)
        
        files.append({
            'type': 'video',
            'file_path': file_path,
            'name': f"{message.video.file_id}.mp4",
            'stage': 'after_message'
        })
        logger.info(f"Видео сохранено: {file_path} (after_message)")
    
    await state.update_data(files=files)
    
    # Кнопка для завершения добавления файлов
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить добавление файлов", callback_data="files:done")]
    ])
    
    await message.answer(
        f"✅ Файл добавлен (всего: {len(files)})\n\n"
        "Отправьте еще файлы или нажмите кнопку для завершения:",
        reply_markup=keyboard
    )

@admin_events_router.callback_query(F.data.startswith("files:"), AdminStates.create_event_files)
async def process_files_action(callback_query: CallbackQuery, state: FSMContext):
    """Обработка действий с файлами"""
    action = callback_query.data.split(":", 1)[1]
    
    data = await state.get_data()
    files = data.get('files', [])
    
    if action == "skip":
        files = []
        await state.update_data(files=files)
    
    # Переход к подтверждению
    await state.set_state(AdminStates.create_event_confirm)
    
    # Формируем дату и время для отображения (московское время)
    event_date = data.get('event_date')
    event_time = data.get('event_time')
    naive_datetime = datetime.strptime(f"{event_date} {event_time}", '%Y-%m-%d %H:%M')
    moscow_datetime = MOSCOW_TZ.localize(naive_datetime)
    
    # Сначала отправляем превью сообщения
    from aiogram.types import FSInputFile, InputMediaPhoto, InputMediaVideo
    
    # Анализируем файлы
    files_with_msg = [f for f in files if f.get('stage') == 'with_message']
    files_after = [f for f in files if f.get('stage') == 'after_message']
    
    # 1. Отправляем сообщение с прикрепленными файлами
    if files_with_msg:
        media_group = []
        first_file = True
        
        for file_info in files_with_msg:
            if file_info['type'] == 'photo':
                media = InputMediaPhoto(
                    media=FSInputFile(file_info['file_path']),
                    caption=data.get('event_message') if first_file else None,
                    parse_mode='Markdown' if first_file else None
                )
                media_group.append(media)
            elif file_info['type'] == 'video':
                media = InputMediaVideo(
                    media=FSInputFile(file_info['file_path']),
                    caption=data.get('event_message') if first_file else None,
                    parse_mode='Markdown' if first_file else None
                )
                media_group.append(media)
            first_file = False
        
        if media_group:
            await callback_query.message.answer_media_group(media_group)
    else:
        # Только текст
        await callback_query.message.answer(
            data.get('event_message'),
            parse_mode='Markdown'
        )
    
    # 2. Отправляем дополнительные файлы
    for file_info in files_after:
        if file_info['type'] == 'document':
            await callback_query.message.answer_document(
                FSInputFile(file_info['file_path'])
            )
        elif file_info['type'] == 'photo':
            await callback_query.message.answer_photo(
                FSInputFile(file_info['file_path'])
            )
        elif file_info['type'] == 'video':
            await callback_query.message.answer_video(
                FSInputFile(file_info['file_path'])
            )
    
    # 3. Отправляем сообщение с подтверждением
    summary = (
        f"📋 **Подтверждение создания события**\n\n"
        f"📝 Название: **{data.get('event_name')}**\n"
        f"📅 Дата и время: **{moscow_datetime.strftime('%d.%m.%Y %H:%M')} (МСК)**\n"
        f"👥 Сегмент: **{data.get('segment_display')}**\n"
        f"📎 Файлов: **{len(files)}**\n\n"
        f"⬆️ _Сообщение выше будет отправлено {data.get('segment_display', 'всем пользователям')}_\n\n"
        "Подтвердите создание события:"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Создать", callback_data="confirm:yes"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="confirm:no")
        ]
    ])
    
    await callback_query.message.edit_text(
        summary,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@admin_events_router.callback_query(F.data.startswith("confirm:"), AdminStates.create_event_confirm)
async def process_event_confirmation(callback_query: CallbackQuery, state: FSMContext):
    """Обработка подтверждения создания события"""
    action = callback_query.data.split(":", 1)[1]
    
    if action == "no":
        await state.clear()
        await callback_query.message.edit_text(
            "❌ Создание события отменено",
            parse_mode='Markdown'
        )
        return
    
    # Создаем событие
    data = await state.get_data()
    
    from ..handlers.handlers import get_global_var
    supabase_client = get_global_var('supabase_client')
    
    # Формируем datetime для планирования
    event_date = data.get('event_date')
    event_time = data.get('event_time')
    
    # Создаем naive datetime из введенного московского времени
    naive_datetime = datetime.strptime(f"{event_date} {event_time}", '%Y-%m-%d %H:%M')
    
    # Привязываем к московской временной зоне
    moscow_datetime = MOSCOW_TZ.localize(naive_datetime)
    
    # Конвертируем в UTC для сохранения в БД
    utc_datetime = moscow_datetime.astimezone(pytz.UTC)
    
    logger.info(f"⏰ Время события: Москва={moscow_datetime.strftime('%d.%m.%Y %H:%M %Z')}, UTC={utc_datetime.strftime('%d.%m.%Y %H:%M %Z')}")
    
    # Загружаем файлы в Supabase Storage
    import os
    event_name = data.get('event_name')
    files = data.get('files', [])
    uploaded_files = []
    
    try:
        for file_info in files:
            # Читаем локальный файл
            with open(file_info['file_path'], 'rb') as f:
                file_bytes = f.read()
            
            # Загружаем в Storage
            storage_info = await supabase_client.upload_event_file(
                event_name=event_name,
                file_data=file_bytes,
                file_name=file_info['name']
            )
            
            # Сохраняем только метаданные (БЕЗ file_id и локального пути)
            uploaded_files.append({
                'type': file_info['type'],
                'name': file_info['name'],
                'storage_path': storage_info['storage_path'],
                'stage': file_info['stage'],
                'has_caption': file_info.get('has_caption', False)
            })
            
            # Удаляем временный локальный файл
            try:
                os.remove(file_info['file_path'])
                logger.info(f"🗑️ Удален временный файл: {file_info['file_path']}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось удалить временный файл: {e}")
        
        logger.info(f"✅ Загружено {len(uploaded_files)} файлов в Storage для события '{event_name}'")
        
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки файлов в Storage: {e}")
        # Если ошибка - пытаемся удалить уже загруженные файлы
        try:
            await supabase_client.delete_event_files(event_name)
        except:
            pass
        raise
    
    # Подготавливаем данные события с метаданными файлов
    event_data = {
        'segment': data.get('segment'),
        'message': data.get('event_message'),
        'files': uploaded_files  # ← Сохраняем только метаданные
    }
    
    try:
        # Сохраняем в БД (в UTC)
        event_id = await supabase_client.save_admin_event(
            event_name=event_name,
            event_data=event_data,
            scheduled_datetime=utc_datetime
        )
        
        await callback_query.message.edit_text(
            f"✅ **Событие успешно создано!**\n\n"
            f"📝 Название: `{data.get('event_name')}`\n"
            f"📅 Запланировано на: **{moscow_datetime.strftime('%d.%m.%Y %H:%M')} (МСК)**\n"
            f"👥 Сегмент: **{data.get('segment_display')}**\n\n"
            f"💡 _Нажмите на название для копирования_",
            parse_mode='Markdown'
        )
        
        # Очищаем состояние
        await state.clear()
        await state.set_state(AdminStates.admin_mode)
        
    except Exception as e:
        logger.error(f"Ошибка создания события: {e}")
        await callback_query.message.edit_text(
            f"❌ Ошибка создания события:\n`{str(e)}`",
            parse_mode='Markdown'
        )
        await state.clear()
        await state.set_state(AdminStates.admin_mode)

@admin_events_router.message(Command(commands=["список_событий", "list_events"]))
async def list_events_command(message: Message, state: FSMContext):
    """Просмотр всех запланированных событий"""
    from ..handlers.handlers import get_global_var
    admin_manager = get_global_var('admin_manager')
    supabase_client = get_global_var('supabase_client')
    
    if not admin_manager.is_admin(message.from_user.id):
        return
    
    try:
        # Получаем все pending события (незавершенные и неотмененные)
        events = await supabase_client.get_admin_events(status='pending')
        
        if not events:
            await message.answer(
                "📋 **Нет активных событий**\n\n"
                "Используйте `/create_event` для создания нового события",
                parse_mode='Markdown'
            )
            return
        
        # Формируем список событий в красивом формате
        text_parts = [
            f"📋 **Активные события** ({len(events)})\n"
        ]
        
        for idx, event in enumerate(events, 1):
            event_name = event['event_type']
            
            # Конвертируем UTC в московское время для отображения
            utc_time = datetime.fromisoformat(event['scheduled_at'].replace('Z', '+00:00'))
            moscow_time = utc_time.astimezone(MOSCOW_TZ)
            
            # Красивый формат с эмодзи и структурой
            text_parts.append(
                f"📌 **{idx}.** `{event_name}`\n"
                f"    🕐 {moscow_time.strftime('%d.%m.%Y в %H:%M')} МСК\n"
            )
        
        text_parts.append(
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💡 _Нажмите на название для копирования_\n"
            f"🗑️ Удалить: `/delete_event название`"
        )
        
        await message.answer(
            "\n".join(text_parts),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка получения событий: {e}")
        await message.answer(
            f"❌ Ошибка получения событий:\n`{str(e)}`",
            parse_mode='Markdown'
        )


@admin_events_router.message(Command(commands=["удалить_событие", "delete_event"]))
async def delete_event_command(message: Message, state: FSMContext):
    """Удаление события по названию"""
    from ..handlers.handlers import get_global_var
    admin_manager = get_global_var('admin_manager')
    supabase_client = get_global_var('supabase_client')
    
    if not admin_manager.is_admin(message.from_user.id):
        return
    
    # Парсим название из команды
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer(
            "❌ Укажите название события:\n"
            "`/delete_event название`\n\n"
            "Используйте /list_events для просмотра списка событий",
            parse_mode='Markdown'
        )
        return
    
    event_name = parts[1].strip()
    
    try:
        # Удаляем по названию (только pending события)
        response = supabase_client.client.table('scheduled_events').update({
            'status': 'cancelled'
        }).eq('event_type', event_name).eq(
            'event_category', 'admin_event'
        ).eq('status', 'pending').execute()
        
        if response.data:
            await message.answer(
                f"✅ Событие `{event_name}` успешно отменено",
                parse_mode='Markdown'
            )
            logger.info(f"Отменено событие с названием '{event_name}'")
        else:
            await message.answer(
                f"❌ Активное событие с названием `{event_name}` не найдено\n\n"
                f"Используйте /list_events для просмотра списка активных событий",
                parse_mode='Markdown'
            )
        
    except Exception as e:
        logger.error(f"Ошибка удаления события: {e}")
        await message.answer(
            f"❌ Ошибка удаления события:\n`{str(e)}`",
            parse_mode='Markdown'
        )

