import random

from django.core.management.base import BaseCommand

from data.models import ValueEntry, IndexedValueEntry
from data.utils import Timer


FUNCS = {
    'random': lambda: random.random(),
    'normal': lambda: random.gauss(0.5, 0.15),
}


class Command(BaseCommand):
    help = 'Load sample data for Value and IndexedValue models'

    batch_size = 10_000  # how many to load at once - count might be millions

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1_000_000,
            help='Number of records to create'
        )

        parser.add_argument(
            '--value',
            action='store_true',
            help='Whether to create Value records'
        )

        parser.add_argument(
            '--indexed_value',
            action='store_true',
            help='Whether to create IndexedValue records'
        )

        parser.add_argument(
            '--func',
            type=str,
            default='random',
            help='Function to generate values'
        )

    def handle(self, *args, **options):
        count = options['count']
        value = options['value']
        indexed_value = options['indexed_value']
        func_name = options['func']
        func = FUNCS[func_name]

        if not value and not indexed_value:
            self.stdout.write('No value records to create. Exiting.')
            return
        
        random.seed(42)
        
        i = 0
        while i < count:
            self.stdout.write(
                self.style.ERROR(f'Creating records {i:,} to {min(i + self.batch_size, count):,}...')
            )
            values = [func() for _ in range(self.batch_size)]

            if value:
                with Timer('Value bulk create') as timer:
                    ValueEntry.objects.bulk_create([ValueEntry(value=v) for v in values])
                self.stdout.write(self.style.SUCCESS(f'Created Value records in {timer.duration:.2f} seconds'))
            
            if indexed_value:
                with Timer('IndexedValue bulk create') as timer:
                    IndexedValueEntry.objects.bulk_create([IndexedValueEntry(value=v) for v in values])
                self.stdout.write(self.style.SUCCESS(f'Created IndexedValue records in {timer.duration:.2f} seconds'))
    
            i += self.batch_size
                
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count:,} Value and/or IndexedValue records')
        )
