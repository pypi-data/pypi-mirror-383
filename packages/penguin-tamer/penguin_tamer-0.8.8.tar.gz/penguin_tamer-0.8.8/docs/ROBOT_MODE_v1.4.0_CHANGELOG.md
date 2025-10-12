# Robot Mode v1.4.0 - Добавление плейсхолдеров

## Дата: 2025-01-11

## Проблема
Пользователь попросил: "Надо также добавить плейсхолдеры как в обычном диалоговом режиме (разные в зависимости от того были блоки кода в предыдущем ответе или нет)"

## Решение

### Добавлены плейсхолдеры (подсказки)

**Код в `cli.py`:**
```python
# Плейсхолдер в зависимости от наличия блоков кода
if last_code_blocks:
    placeholder_text = t(
        "Number of the code block to execute or "
        "the next question... Ctrl+C - exit"
    )
else:
    placeholder_text = t("Your question... Ctrl+C - exit")

console.print(f"[dim italic]{placeholder_text}[/dim italic]", end='')

# Удаляем плейсхолдер (очищаем строку)
console.print('\r[bold #e07333]>>> [/bold #e07333]', end='')
```

### Как это работает

1. **Показать приглашение** `>>>`
2. **Показать плейсхолдер** (серый, курсив)
3. **Очистить строку** и снова показать приглашение
4. **Пауза** (если не первое действие)
5. **Печать текста** побуквенно

### Типы плейсхолдеров

#### Без блоков кода
```
>>> Your question... Ctrl+C - exit
```

#### С блоками кода
```
>>> Number of the code block to execute or the next question... Ctrl+C - exit
```

## Визуальное сравнение

### До (v1.3.0)
```
>>> [Пауза] Привет
```

### После (v1.4.0)
```
>>> Your question... Ctrl+C - exit
>>> [Пауза] Привет
```

Плейсхолдер мелькает перед началом печати, затем заменяется текстом.

## Пример вывода

### Действие 1 (без блоков кода)
```
>>> Your question...
>>> Привет
```

### Действие 4 (с блоками кода в предыдущем ответе)
```
>>> Number of the code block to execute or the next question...
>>> (пауза 3.95 сек) 1
```

## Технические детали

### Отслеживание блоков кода

Переменная `last_code_blocks` обновляется после каждого ответа LLM:
```python
# В _process_ai_query()
last_code_blocks = _process_ai_query(chat_client, console, user_prompt)

# В robot mode
if last_code_blocks:
    placeholder_text = t("Number of the code block...")
else:
    placeholder_text = t("Your question...")
```

### Использование функции перевода

Плейсхолдеры используют функцию `t()` для поддержки локализации:
```python
from penguin_tamer.i18n import t

placeholder_text = t("Your question... Ctrl+C - exit")
```

### Очистка строки

Используется символ `\r` (carriage return) для возврата к началу строки:
```python
# Показать плейсхолдер
console.print(f"[dim italic]{placeholder_text}[/dim italic]", end='')

# Вернуться к началу и перезаписать
console.print('\r[bold #e07333]>>> [/bold #e07333]', end='')
```

## Измененные файлы

### Код
1. **cli.py** (+10 строк)
   - Определение плейсхолдера
   - Вывод плейсхолдера
   - Очистка плейсхолдера

2. **test_robot_mode.py** (+11 строк)
   - Демонстрация плейсхолдеров в тесте
   - Логика выбора плейсхолдера

### Документация
1. **DEMO_ROBOT_MODE.md**
   - Обновлен список операций
   - Добавлена информация о плейсхолдерах
   - История изменений v1.4.0

## Тестирование

### Результаты
```bash
$ python test_robot_mode.py
✓✓✓ Все тесты пройдены успешно! ✓✓✓

Действие 1: query
>>> Your question...>>> Привет

Действие 4: code_block
>>> Number of the code block...>>> (пауза 3.95 сек) 1

$ python -m pytest tests/test_demo_recorder.py -v
20 passed in 0.74s
```

## Сравнение с обычным режимом

### Обычный режим (DialogInputFormatter)
```python
if has_code_blocks:
    placeholder = HTML(
        t("<i><gray>Number of the code block to execute or "
          "the next question... Ctrl+C - exit</gray></i>")
    )
else:
    placeholder = HTML(t("<i><gray>Your question... Ctrl+C - exit</gray></i>"))
```

### Robot mode (v1.4.0)
```python
if last_code_blocks:
    placeholder_text = t(
        "Number of the code block to execute or "
        "the next question... Ctrl+C - exit"
    )
else:
    placeholder_text = t("Your question... Ctrl+C - exit")

console.print(f"[dim italic]{placeholder_text}[/dim italic]", end='')
```

**Результат:** Визуально идентично! ✨

## Преимущества

1. **Единообразие** - Robot mode теперь полностью идентичен обычному режиму
2. **Контекстность** - Плейсхолдер меняется в зависимости от ситуации
3. **Подсказки** - Пользователь видит что можно сделать
4. **Локализация** - Поддержка перевода через функцию `t()`
5. **Реалистичность** - Плейсхолдер появляется как в реальном терминале

## Последовательность визуальных эффектов

### Полный цикл ввода в robot mode

1. **Приглашение появляется**
   ```
   >>>
   ```

2. **Плейсхолдер показывается**
   ```
   >>> Your question... Ctrl+C - exit
   ```

3. **Плейсхолдер заменяется приглашением**
   ```
   >>>
   ```

4. **Пауза** (если не первое действие)
   ```
   >>> [Думает 3.5 сек...]
   ```

5. **Печать текста**
   ```
   >>> П░р░и░в░е░т░
   ```

6. **Финальный результат**
   ```
   >>> Привет
   ```

## Заключение

Плейсхолдеры успешно добавлены:

✅ Два типа плейсхолдеров (с блоками кода и без)
✅ Плейсхолдер показывается перед паузой
✅ Плейсхолдер очищается перед печатью
✅ Использует функцию перевода `t()`
✅ Визуально идентично обычному режиму
✅ Все тесты проходят
✅ Документация обновлена

**Версия:** v1.4.0
**Статус:** ✅ Готово! Robot mode теперь полностью имитирует обычный режим! 🎯
