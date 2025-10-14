# LLM Service

[![PyPI version](https://img.shields.io/pypi/v/universal-llm-service.svg)](https://pypi.org/project/universal-llm-service/)
[![Build Status](https://github.com/DenisShahbazyan/LLM_Service/actions/workflows/publish.yml/badge.svg)](https://github.com/DenisShahbazyan/LLM_Service/actions)
[![Python Versions](https://img.shields.io/pypi/pyversions/universal-llm-service.svg)](https://pypi.org/project/universal-llm-service/)
[![License](https://img.shields.io/pypi/l/universal-llm-service.svg)](https://github.com/DenisShahbazyan/LLM_Service/blob/master/LICENSE)

(Актуальный README в github, обычно я забываю его обновить при релизе...)

# Библиотека для упрощенного использования LLM

Библиотека предоставляет упрощенный интерфейс для работы с различными LLM моделями, автоматический подсчет токенов и стоимости запросов, а также удобную интеграцию с существующими проектами. Создана на основе Langchain, являясь практичной оберткой для стандартизации взаимодействия с моделями.

## Основные возможности:
- Простой и понятный интерфейс для работы с LLM моделями
- Автоматический подсчет стоимости запросов
- Поддержка асинхронного API
- Мониторинг использования токенов
- Расчет затрат в USD с учетом текущего курса валюты по ЦБ РФ
- Тест соединения (работает так: пытается получить список моделей, если получает - возвращает True)
- Премодерация промпта (пока такую возможность дает только openai)

## Установка:
```sh
# Через uv
uv add "universal-llm-service[all]"

# Через pip
pip install "universal-llm-service[all]"

# Через poetry
poetry add "universal-llm-service[all]"

# Можно установить для конкретного провайдера
[anthropic]
[cerebras]
[deepseek]
[gigachat]
[gemini]
[openai]
[openrouter]
[xai]
```

## Использование:

### Перед началом нужно создать экземпляр модели, langchain - подобный:
Если в langchain мы создаем такой экземпляр:
```py
from langchain_openai import ChatOpenAI

gpt_4o_mini = ChatOpenAI(
    model='gpt-4o-mini',
    api_key='sk-proj-1234567890',
    temperature=0,
)
```

То здесь мы должны создавать такой:
```py
from llm.constructor import BaseLLM

gpt_4o_mini = BaseLLM(
    model='gpt-4o-mini',
    api_key='sk-proj-1234567890',
    temperature=0,
)
```

И его передаем при создании `LLMService`. Имена полей должны совпадать.



### Обычный диалог с LLM:
```py
import asyncio
from llm import LLMService

from llm_config import gpt_4o_mini


async def main():
    llm = await LLMService.create(gpt_4o_mini.to_dict())
    result = await llm.ainvoke(message='Сколько будет 2 + 2?')
    print(result)  # Ответ от llm
    print(llm.usage)  # Использование в токенах и деньгах
    print(llm.usd_rate)  # Курс доллара
    print(llm.chat_json)  # Весь чат в json


if __name__ == "__main__":
    asyncio.run(main())
```

### Структурированный вывод:
```py
import asyncio

from pydantic import BaseModel, Field

from llm_config import gpt_4o_mini
from llm import LLMService


class RelatedConceptOutput(BaseModel):
    """Новый термин и его сила связи с исходным термином."""

    title: str = Field(..., description='Название термина')
    length: int = Field(..., description='Сила связи')


class RelatedConceptListOutput(BaseModel):
    """Новые термины и их сила связи с исходным термином."""

    concepts: list[RelatedConceptOutput]


SYSTEM_PROMPT = (
    'Тебе дано понятие школьной программы: "Молекула". Сгенерируй ровно "5" понятий '
    'школьной программы, наиболее близких к этому понятию.'
)


async def main() -> None:
    llm = await LLMService.create(gpt_4o_mini.to_dict())
    structured_llm = await llm.with_structured_output(RelatedConceptListOutput)
    result = await structured_llm.ainvoke(message=SYSTEM_PROMPT)
    print(result)  # Ответ от llm
    print(structured_llm.usage)  # Использование в токенах и деньгах
    print(structured_llm.usd_rate)  # Курс доллара
    print(structured_llm.chat_json)  # Весь чат в json


if __name__ == '__main__':
    asyncio.run(main())
```

### Потоковый вывод:
```py
import asyncio


from example.llm_config import gpt_4o_mini  # noqa: F401
from llm.service import LLMService


async def main() -> None:
    llm = await LLMService.create(gpt_4o_mini.to_dict())
    stream = await llm.astream(message='Кратко расскажи что такое Python')
    async for chunk in stream:
        print(chunk, end='', flush=True)
    print('\n\n')
    print(stream.full_text)  # Полный текст стрима
    print(llm.usage)  # Использование в токенах и деньгах
    print(llm.usd_rate)  # Курс доллара
    print(llm.chat_json)  # Весь чат в json


if __name__ == '__main__':
    asyncio.run(main())
```

## Подробнее о возможностях:
- `llm.ainvoke` и `llm.stream` - методы принимают как отдельно системный промпт или сообщение, так и историю полность. Параметры принимаются как в стиле langchain так и в виде словарей. Перед отправкой любого сообщения в LLM отрабатывает класс подготовки контекста - PrepareChat:
Класс для подготовки чата в формате Langchain для модели.

1. Данный класс всегда отдает список сообщений в формате Langchain.
2. Если был отправлен только системный промпт, то после него добавляется пустое
    сообщение пользователя. Иначе некоторые модели не хотят работать с единственным
    системным промптом.


- `llm.usage.all_input_tokens` - общее количество отправленных токенов с момента инициализации
- `llm.usage.all_output_tokens`  - общее количество полученных токенов с момента инициализации
- `llm.usage.last_input_tokens` - количество отправленных токенов за последний вызов
- `llm.usage.last_output_tokens` - количество полученных токенов за последний вызов

---

- `llm.usage.all_input_spendings` - общие расходы в USD при отправке с момента инициализации
- `llm.usage.all_output_spendings` - общие расходы в USD при получении с момента инициализации
- `llm.usage.last_input_spendings` - расходы в USD при отправке за последний вызов
- `llm.usage.last_output_spendings` - расходы в USD при получении за последний вызов

---

- `llm.usd_rate` - курс валюты в USD.

## Запуск локально (для разработки):
Установка зависимостей
```sh
uv sync
```

Создать файл `.env` на основе шаблона `.env.template` и вписать ключи

Запуск примеров:
```sh
python -m example.simple  # Пример обычного общения с LLM
python -m example.structured  # Пример общения с LLM со структурированным выводом
python -m example.stream  # Пример общения с LLM в режиме стрима
```

# Список поддерживаемых моделей:
Все модели OpenRouter
| Модели                             | Обычный режим | Стриминговый режим           | Режим структурированного ответа |
|------------------------------------|---------------|------------------------------|---------------------------------|
| gpt-5                              | +             | Verified org only            | +                               |
| gpt-5-mini                         | +             | Verified org only            | +                               |
| gpt-5-nano                         | +             | +                            | +                               |
| gpt-5-chat-latest                  | +             | +                            | +                               |
| gpt-4.1                            | +             | +                            | +                               |
| gpt-4.1-mini                       | +             | +                            | +                               |
| gpt-4.1-nano                       | +             | +                            | +                               |
| gpt-4.5-preview                    | +             | +                            | +                               |
| gpt-4o-mini                        | +             | +                            | +                               |
| gpt-4o                             | +             | +                            | +                               |
| o3-2025-04-16                      | +             | +                            | +                               |
| o4-mini-2025-04-16                 | +             | +                            | +                               |
| GigaChat                           | +             | +                            | +                               |
| GigaChat-2                         | +             | +                            | +                               |
| GigaChat-Pro                       | +             | +                            | +                               |
| GigaChat-2-Pro                     | +             | +                            | +                               |
| GigaChat-Max                       | +             | +                            | +                               |
| GigaChat-2-Max                     | +             | +                            | +                               |
| claude-3-5-haiku-latest            | +             | +                            | +                               |
| claude-3-7-sonnet-latest           | +             | +                            | +                               |
| claude-opus-4-0                    | +             | +                            | +                               |
| claude-sonnet-4-0                  | +             | +                            | +                               |
| gemini-2.0-flash-001               | +             | +                            | +                               |
| gemini-2.5-flash                   | +             | +                            | +                               |
| gemini-2.5-pro-preview-06-05       | +             | +                            | +                               |
| grok-3-mini                        | +             | +                            | +                               |
| grok-3                             | +             | +                            | +                               |
| grok-3-fast                        | +             | +                            | +                               |
| deepseek-chat                      | +             | +                            | +                               |
| deepseek-reasoner                  | +             | +                            | +                               |
| gpt-oss-120b.                      | +             | +                            | -                               |
| qwen-3-32b                         | +             | +                            | +                               |
| llama-4-scout-17b-16e-instruct     | +             | +                            | +                               |
| llama-4-maverick-17b-128e-instruct | +             | +                            | +                               |
