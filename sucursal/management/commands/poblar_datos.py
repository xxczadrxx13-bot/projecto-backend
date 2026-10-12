import random
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from sucursal.models import Categoria, Producto

class Command(BaseCommand):
    help = "Genera datos masivos ficticios para Music Pro usando Faker y bulk_create"

    def add_arguments(self, parser):
        parser.add_argument('cantidad', type=int, help='Número de registros a generar (ej. 100, 1000, 100000, 1000000)')

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        fake = Faker('es_ES')

        self.stdout.write(self.style.WARNING(f"Iniciando generación de {cantidad:,} registros con Faker..."))
        tiempo_inicio = time.time()

        # Categorías base de Music Pro
        nombres_cat = ["Guitarras y Bajos", "Baterías y Percusión", "Teclados y Pianos", "Audio Profesional", "Accesorios y Cables", "DJ e Iluminación"]
        categorias = [Categoria.objects.get_or_create(nombre=n)[0] for n in nombres_cat]

        marcas = ["Fender", "Gibson", "Ibanez", "Yamaha", "Marshall", "Boss", "Shure", "Roland", "Korg", "Pioneer DJ", "Audio-Technica"]
        familias = ["Stratocaster", "Les Paul", "Custom Pro", "Studio Series", "V-Drums", "Digital Synth", "Reference Monitor", "Wireless Pack"]

        ultimo_id = Producto.objects.order_by('-id').values_list('id', flat=True).first() or 0
        lote = []
        batch_size = 5000  # Bloques óptimos para alta velocidad y bajo uso de RAM
        creados = 0

        for i in range(1, cantidad + 1):
            nuevo_sku = f"MP-{ultimo_id + i:07d}"
            nombre_prod = f"{random.choice(marcas)} {random.choice(familias)} {fake.word().capitalize()}"

            lote.append(
                Producto(
                    codigo=nuevo_sku,
                    nombre=nombre_prod,
                    categoria=random.choice(categorias),
                    precio=random.randint(15000, 3500000),
                    stock=random.randint(0, 150),
                    descripcion=fake.sentence(nb_words=12),
                    imagen="https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=500",
                    activo=random.choice([True, True, True, False])
                )
            )

            # Inserción en bloques
            if len(lote) >= batch_size:
                with transaction.atomic():
                    Producto.objects.bulk_create(lote)
                creados += len(lote)
                self.stdout.write(f"-> Insertados {creados:,} de {cantidad:,}...")
                lote = []

        # Insertar los restantes
        if lote:
            with transaction.atomic():
                Producto.objects.bulk_create(lote)
            creados += len(lote)

        tiempo_total = time.time() - tiempo_inicio
        self.stdout.write(self.style.SUCCESS(
            f"¡Éxito! Se crearon {creados:,} productos en {tiempo_total:.2f} segundos."
        ))