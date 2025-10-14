from django.core.management.base import BaseCommand
from django.apps import apps
from beeseeder.data_generator import DataGenerator, DataSeeder
from beeseeder.bee_logger import bee_log
from beeseeder.utils import ModelItem
from beeseeder.services import order_models_by_dependency
from django.conf import settings


SEED_APPS = getattr(settings, "SEED_APPS", [])


ASCII_ART = r"""
   ____  U _____ uU _____ u 
U | __")u\| ___"|/\| ___"|/ 
 \|  _ \/ |  _|"   |  _|"   
  | |_) | | |___   | |___   
  |____/  |_____|  |_____|  
 _|| \\_  <<   >>  <<   >>  
(__) (__)(__) (__)(__) (__)                            
"""


class Command(BaseCommand):
    def handle(self, *args, **options) -> str | None:
        print(ASCII_ART)
        
        BEESEEDER_API_KEY = getattr(settings, "BEESEEDER_API_KEY", None)

        if not BEESEEDER_API_KEY:
            bee_log("Oops, could not find a BEESEEDER_API_KEY in settings")
            return
        
        bee_log('Relax while i seed the database for you ill BEEEE back soon..')
        bee_log("Collecting your models")
        model_items = []
        all_models = apps.get_models()
        for model in all_models:
            if model._meta.app_label  in SEED_APPS:       
                model_item = ModelItem(model, record_count=50)
                model_items.append(model_item)
                
        bee_log(f"Collected {len(model_items)} models")
        
        
        ordered_model_items = order_models_by_dependency(model_items)
            
        generator = DataGenerator(ordered_model_items)
        success, job_data = generator.generate()
        if success:
            seeder = DataSeeder(seed_data=job_data)
            seeder.seed()
        else:
            bee_log("Data generation failed")
            
        
        # seeder = DataSeeder(url="https://res.cloudinary.com/dzya6c7nh/raw/upload/v1759582826/beeseeder/json/result/9aeb029a-e39d-4b75-b500-e74fc168f573.json")
        # seeder.seed()
        
        