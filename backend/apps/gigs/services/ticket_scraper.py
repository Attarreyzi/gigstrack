import requests
import json
import re
import datetime
import logging
from django.utils import timezone
from django.utils.text import slugify
from apps.venues.models import Venue
from apps.artists.models import Artist, Genre
from apps.gigs.models import Gigs, GigsLineup, GigsStatus

logger = logging.getLogger(__name__)

class TicketScraperService:
    """
    Scraper untuk menarik data acara konser dan Gigs nyata dari platform tiket lokal
    (seperti Megatix Indonesia dan agregator event).
    """

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    def fetch_megatix_events(self):
        """
        Menarik daftar event nyata dari Megatix Indonesia (Nuxt 3 SSR Payload).
        """
        url = 'https://megatix.co.id/events'
        try:
            r = requests.get(url, headers=self.HEADERS, timeout=12)
            if r.status_code != 200:
                logger.error(f"Megatix error HTTP {r.status_code}")
                return []

            match = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', r.text, re.DOTALL)
            if not match:
                return []

            data = json.loads(match.group(1))

            def resolve(val):
                if isinstance(val, int) and 0 <= val < len(data):
                    res = data[val]
                    if isinstance(res, (str, int, float, bool)):
                        return res
                    return str(res)
                return val

            parsed_events = []
            for item in data:
                if isinstance(item, dict) and 'slug' in item and 'venue_name' in item:
                    name = str(resolve(item.get('name', '')))
                    slug = str(resolve(item.get('slug', '')))
                    venue_name = str(resolve(item.get('venue_name', '')))
                    start_dt_raw = str(resolve(item.get('start_datetime', '')))
                    price_str = str(resolve(item.get('display_price', '0')))
                    cover = str(resolve(item.get('cover', '')))

                    if not name or not slug:
                        continue

                    # Ekstrak harga numerik (misal "Rp 150,000" -> 150000)
                    price_digits = re.sub(r'[^\d]', '', price_str.split('-')[0])
                    ticket_price = int(price_digits) if price_digits else 0

                    parsed_events.append({
                        'title': name,
                        'slug': slug,
                        'venue_name': venue_name or 'Panggung Konser Musik',
                        'start_datetime_raw': start_dt_raw,
                        'ticket_price': ticket_price,
                        'ticket_url': f"https://megatix.co.id/events/{slug}",
                        'poster_url': cover if cover.startswith('http') else f"https://megatix.co.id{cover}" if cover else "",
                        'source': 'megatix'
                    })

            return parsed_events
        except Exception as e:
            logger.error(f"Error scraping Megatix: {e}")
            return []
