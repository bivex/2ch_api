import asyncio
from datetime import datetime, timedelta
from typing import List
from dvach.infrastructure.client import DvachClient
from dvach.application.ukraine_monitor import UkraineMonitor
from dvach.shared.utils import strip_html

async def get_top_of_two_days():
    client = DvachClient()
    monitor = UkraineMonitor(client) # Reuse keywords from monitor
    
    # We'll check po and news
    boards = ['po', 'news']
    two_days_ago = datetime.now() - timedelta(days=2)
    
    all_relevant_threads = []
    
    print(f"\nSearching for top Ukraine-related threads from the last 48 hours...")
    
    for board in boards:
        try:
            threads = await client.get_threads(board)
            for t in threads:
                # Filter by age (must be created within last 48 hours)
                if t.op_post.timestamp < two_days_ago:
                    continue
                
                # Filter by keywords
                text = (t.subject or '').lower() + ' ' + t.op_post.comment.lower()
                if any(k in text for k in monitor.KEYWORDS):
                    all_relevant_threads.append(t)
        except Exception as e:
            print(f"Error fetching /{board}/: {e}")

    # Sort by post count (engagement)
    top_threads = sorted(all_relevant_threads, key=lambda x: x.posts_count, reverse=True)[:10]

    if not top_threads:
        print("No threads matching criteria found.")
        return

    print(f"\n{'='*25} TOP 10 UKRAINE TRENDS (LAST 48H) {'='*25}")
    for i, t in enumerate(top_threads, 1):
        content = strip_html(t.op_post.comment).replace('\n', ' ')
        # Format for readability
        if len(content) > 300:
            content = content[:297] + "..."
            
        print(f"{i}. [/{t.board_code}/] ID: {t.id} | 🔥 {t.posts_count} posts")
        print(f"   Created: {t.op_post.timestamp}")
        print(f"   Subject: {t.subject if t.subject else 'No subject'}")
        print(f"   Content: {content}")
        print(f"   Link: https://2ch.org/{t.board_code}/res/{t.id}.html")
        print("-" * 80)

    await client.close()

if __name__ == '__main__':
    asyncio.run(get_top_of_two_days())
