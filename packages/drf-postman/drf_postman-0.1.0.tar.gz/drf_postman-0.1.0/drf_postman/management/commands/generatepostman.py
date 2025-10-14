from django.core.management.base import BaseCommand, CommandError

from drf_postman.generator import PostmanCollectionGenerator
from drf_postman.config import get_config

class Command(BaseCommand):
    help = 'Generate Postman v2.1 collection from Django REST Framework routes.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            '-o',
            type=str,
            default='postman_collection.json',
            help='Output file path for the Postman collection (default: postman_collection.json)'
        )

        parser.add_argument(
            '--name',
            '-n',
            type=str,
            default=None,
            help='Collection name (default: from settings or "API Collection")'
        )
        
        parser.add_argument(
            '--base-url',
            '-b',
            type=str,
            default=None,
            help='Base URL for the API (default: from settings or "{{base_url}}")'
        )

    def handle(self, *args, **options):
        # Get config
        config = get_config()
        collection_name = options['name'] or config.get('COLLECTION_NAME')
        output_path = options['output'] or config.get('OUTPUT_PATH')
        base_url = options['base_url'] or config.get('BASE_URL')

        self.stdout.write(self.style.MIGRATE_HEADING('Generating Postman Collection'))

        try:
            # Generate collection
            generator = PostmanCollectionGenerator(
                collection_name=collection_name,
                base_url=base_url
            )

            self.stdout.write('Analyzing DRF routes...')

            generator.save_to_file(output_path)

            self.stdout.write(
                self.style.SUCCESS(f'Postman collection generated successfully: {output_path}')
            )
            self.stdout.write(f'   Collection name: {collection_name}')
            self.stdout.write(f'   Base URL: {base_url}')
        except Exception as e:
            raise CommandError(f'Failed to generate Postman collection: {str(e)}')