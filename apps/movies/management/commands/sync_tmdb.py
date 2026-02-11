"""
Management command to sync movies from TMDb into the local database.

Usage:
    python manage.py sync_tmdb                    # default: 5 pages each
    python manage.py sync_tmdb --pages 10         # 10 pages each (~600 movies)
    python manage.py sync_tmdb --genres-only       # only sync genre list
"""
import time
from django.core.management.base import BaseCommand
from apps.movies.models import Genre
from apps.movies.services.tmdb_service import tmdb_service, TMDbService


class Command(BaseCommand):
    help = 'Sync movies from TMDb API into the local database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=5,
            help='Number of pages to fetch per category (default: 5, ~100 movies/category)',
        )
        parser.add_argument(
            '--genres-only',
            action='store_true',
            help='Only sync the genre list, skip movies',
        )

    def handle(self, *args, **options):
        pages = options['pages']
        genres_only = options['genres_only']

        self.stdout.write(self.style.MIGRATE_HEADING('🎬 TMDb Sync'))
        self.stdout.write('')

        # ── 1. Always sync genres first ──────────────────────────────
        self._sync_genres()

        if genres_only:
            self.stdout.write(self.style.SUCCESS('Done (genres only).'))
            return

        # ── 2. Sync movies from multiple TMDb endpoints ──────────────
        total = 0
        categories = [
            ('Trending (day)', lambda p: tmdb_service.get_trending_movies('day', p)),
            ('Popular',        lambda p: tmdb_service.get_popular_movies(p)),
            ('Top Rated',      lambda p: tmdb_service.get_top_rated_movies(p)),
            ('Trending (week)', lambda p: tmdb_service.get_trending_movies('week', p)),
        ]

        for label, fetcher in categories:
            count = self._sync_category(label, fetcher, pages)
            total += count

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'✅ Sync complete! {total} movie records upserted. '
            f'DB now has {Genre.objects.count()} genres and '
            f'{self._movie_count()} movies.'
        ))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_genres(self):
        """Fetch and upsert TMDb genre list."""
        genres_data = tmdb_service.get_genres()
        created = 0
        for g in genres_data:
            _, was_created = Genre.objects.update_or_create(
                tmdb_id=g['id'],
                defaults={'name': g['name']},
            )
            if was_created:
                created += 1

        self.stdout.write(
            f'  Genres: {len(genres_data)} synced ({created} new)'
        )

    def _sync_category(self, label, fetcher, pages):
        """Fetch `pages` pages from a TMDb endpoint and persist."""
        saved = 0
        for page in range(1, pages + 1):
            data = fetcher(page)
            if not data or 'results' not in data:
                self.stdout.write(
                    self.style.WARNING(f'  {label} page {page}: no data')
                )
                break

            count = TMDbService.persist_tmdb_movies(data['results'])
            saved += count

            # Be polite to the TMDb API
            time.sleep(0.25)

        self.stdout.write(f'  {label}: {saved} movies across {pages} pages')
        return saved

    @staticmethod
    def _movie_count():
        from apps.movies.models import Movie
        return Movie.objects.count()
