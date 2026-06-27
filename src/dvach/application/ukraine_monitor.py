import asyncio
from typing import List
from loguru import logger
from datetime import datetime
from ..domain.entities import Thread
from ..domain.interfaces import I2chClient
from ..shared.utils import strip_html

class UkraineMonitor:
    KEYWORDS = [
        # География и города
        'украин', 'киев', 'курск', 'донецк', 'луганск', 'херсон', 'запорож', 'харьков', 
        'одесс', 'крым', 'белгород', 'бахмут', 'авдеевка', 'покровск', 'суджа', 'купянск',
        'волчанск', 'часов яр', 'угледар', 'львов', 'днепр', 'николаев',
        # Персоналии
        'зеля', 'зеленск', 'залужн', 'сырск', 'буданов', 'ермак', 'путин', 'трамп', 'байден',
        'кулеба', 'безуглая', 'подоляк', 'арестович', 'шольц', 'макрон', 'орбан', 'фицо',
        # Военные термины и техника
        'всу', 'сво', 'фронт', 'наступ', 'орешник', 'дрон', 'бпла', 'пво', 'ракета', 
        'тцк', 'мобилиз', 'переговор', 'абрамс', 'леопард', 'f-16', 'химарс', 'плен', 'обмен',
        'патриот', 'patriot', 'кинжал', 'искандер', 'storm shadow', 'scalp', 'taurus', 'atacms',
        'герань', 'ланцет', 'солнцепек', 'арта', 'снаряд', 'фортификац', 'минные поля',
        # Политика и международка
        'нато', 'nato', 'ес', 'евросоюз', 'оон', 'магатэ', 'саммит', 'мирный план', 
        'заморозка', 'корейский сценарий', 'эскалация', 'демилитаризация', 'денацификация',
        # Экономика и ресурсы
        'санкции', 'потолок цен', 'газ', 'нефть', 'энергетика', 'блэкаут', 'свет', 'генератор',
        'зерновая сделка', 'порты', 'инфраструктура',
        # Сленг и специфические темы
        'хрюк', 'свин', 'порох', 'ватник', 'хохл', 'укроп', '404', 'сало', 'тарас', 'мыкола',
        'бандера', 'шухевич', 'майдан', 'рада', 'тцк-шники', 'мясной штурм'
    ]
    BOARDS = ['po', 'news']

    def __init__(self, client: I2chClient, interval: int = 3600):
        self.client = client
        self.interval = interval
        self._running = False

    async def get_hourly_report(self) -> str:
        all_threads: List[Thread] = []
        for board in self.BOARDS:
            try:
                threads = await self.client.get_threads(board)
                # Filter by keywords
                relevant = [
                    t for t in threads 
                    if any(k in (t.subject or '').lower() or k in t.op_post.comment.lower() 
                          for k in self.KEYWORDS)
                ]
                all_threads.extend(relevant)
            except Exception as e:
                logger.error(f"Error fetching /{board}/: {e}")

        # Sort by post count to get the "loudest" ones
        top_threads = sorted(all_threads, key=lambda x: x.posts_count, reverse=True)[:5]
        
        if not top_threads:
            return "За последний час острых тем по Украине не найдено."

        report = f"\n{'='*20} СВОДКА ПО УКРАИНЕ ({datetime.now().strftime('%H:%M')}) {'='*20}\n"
        for i, t in enumerate(top_threads, 1):
            content = strip_html(t.op_post.comment).replace('\n', ' ')[:200]
            report += f"{i}. [/{t.board_code}/] ID: {t.id} | Постов: {t.posts_count}\n"
            report += f"   Тема: {t.subject if t.subject else 'Без темы'}\n"
            report += f"   Суть: {content}...\n"
            report += f"   Ссылка: https://2ch.org/{t.board_code}/res/{t.id}.html\n"
            report += f"{'-'*60}\n"
        
        return report

    async def start(self):
        self._running = True
        logger.info(f"Ukraine Hourly Monitor started. Interval: {self.interval}s")
        
        while self._running:
            report = await self.get_hourly_report()
            print(report)
            
            # Save to file for history
            with open("ukraine_digest.log", "a", encoding="utf-8") as f:
                f.write(report + "\n")
                
            logger.info("Next update in 1 hour...")
            await asyncio.sleep(self.interval)

    def stop(self):
        self._running = False
