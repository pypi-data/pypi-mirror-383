import math
from beeseeder.bee_logger import bee_log
from beeseeder.utils import ModelItem
import anthropic
from django.conf import settings
import json
import requests
import time
from tqdm import tqdm
from typing import Optional
from django.apps import apps


def download_json_data(data_url: str) -> dict | None:
    try:
        response = requests.get(data_url)
        if response.status_code == 200:
            return response.json()
        else:
            bee_log("Error downloading json data", response.text)
            return None
    except Exception as e:
        bee_log("Error downloading json data", e)
        return None

class DataSeeder:
    def __init__(self, seed_data: list[dict]=None, url: Optional[str] = None) -> None:
        if not seed_data and url:
            seed_data = download_json_data(url)
            
        self.seed_data = seed_data
        self.seeded_instances = {}
        
    
    def seed_dependent_model(self, model, model_data_list:list[dict]):
     
        errors = []
        success_count= 0
        for model_data in model_data_list:
            many_to_many_fields = {}
            
            #replace relational relationship ids with their instances
            for name, value in model_data.items():
                field = model._meta.get_field(name)
                if field.is_relation and field.concrete:
                    field_type = field.get_internal_type()
                    if field_type == "ManyToManyField":
                        field_instances = [self.seeded_instances[instance_id] for instance_id in value if instance_id in self.seeded_instances]
                        many_to_many_fields[name] = field_instances
                    else:
                        field_instance = self.seeded_instances.get(value)
                        model_data[name] = field_instance
            
            try:
                seed_id = model_data.pop("id")
                popped_relationships = [model_data.pop(name) for name in many_to_many_fields.keys()]
                
                instance = model.objects.create(**model_data)
                
                for key, value in many_to_many_fields.items():
                    getattr(instance, key).set(value)
                        
                self.seeded_instances[seed_id] = instance
                success_count += 1
            except Exception as e:
                bee_log(f"Error seeding model {model.__name__}: {e}")
                errors.append(e)
                continue
                
        print(f"Populated {model.__name__} model with {success_count} records, completed with {len(errors)} errors")
    
    def seed_independent_model(self, model, model_data_list: list[dict]):
        # print('seeding independent model', model.__name__, model_data_list)
        
        errors = []
        success_count= 0
        for model_data in model_data_list:
            seed_id =model_data.pop("id")
            try:
                instance = model.objects.create(**model_data)
                self.seeded_instances[seed_id] = instance
                success_count += 1
            except Exception as e:
                bee_log(f"Error seeding model {model.__name__}: {e}")
                errors.append(e)
                continue
        
        print(f"Populated {model.__name__} model with {success_count} records, completed with {len(errors)} errors")

    
        
        
    def is_dependent_model(self, model):
        return any(field.is_relation and field.concrete for field in model._meta.get_fields())
    
    def seed(self):
        dependent_models = []
        independent_models = []
        
        
        for model_key, model_data in self.seed_data.items():
            app_label, model_name = model_key.split(".")#example: accounts.UserAccount
            try:
                model = apps.get_model(app_label, model_name)
            except LookupError:
                bee_log(f"Model {app_label}.{model_name} not found.")
                continue
            
            
            if self.is_dependent_model(model):
                dependent_models.append({
                    "model": model,
                    "model_data_list": model_data
                })
            else:
                independent_models.append({
                    "model": model,
                    "model_data_list": model_data
                })


        for independent_model in independent_models:
            self.seed_independent_model(independent_model["model"], independent_model["model_data_list"])
            
        for dependent_model in dependent_models:
            self.seed_dependent_model(dependent_model["model"], dependent_model["model_data_list"])
        
        bee_log("Database seeding completed ")
        print(json.dumps(self.seeded_instances, indent=4, default=str))

class DataGenerator:
    def __init__(self, model_items: list[ModelItem]) -> None:
        BEESEEDER_API_KEY = getattr(settings, "BEESEEDER_API_KEY", None)
        self.base_api_url = getattr(settings, "BEESEEDER_API_URL", "https://beeseeder.up.railway.app")

        self.model_items = model_items
        self.api_key = BEESEEDER_API_KEY
        
    def generate(self): 
        input_data = [model_item.model_schema for model_item in self.model_items]
       
        json_data = json.dumps(input_data, default=str)
        
        bee_log("Generating synthetic data using agentic methods...")
        headers = {
            "x-api-key": self.api_key
        }
        response = requests.post( f"{self.base_api_url}/generator/generate/", json={
            "tables": json.loads(json_data),
            "framework": "django",
            "record_per_table_count": 50
        }, headers=headers)
        
        
        if response.status_code == 200:
            response_data = response.json()
            job_id = response_data.get('data', {}).get("job_id")
            
            bee_log(f'Data generation initiated successfully, job_id: {response_data.get("data", {}).get("job_id")}')
            with tqdm(total=100, desc='Data generation progress', unit='%') as pbar:
                last_progress = 0
                while True:
                    response = requests.get(f"{self.base_api_url}/generator/job/poll/{job_id}", headers=headers)
                    if response.status_code == 200:
                        response_data = response.json()
                        job_status = response_data.get('status')
                        progress = abs(int(response_data.get('progress')))
                        
                        if progress > last_progress:
                            pbar.update(progress - last_progress)
                            last_progress = progress
                            
                        if job_status == 'completed':
                            pbar.update(100 - last_progress)
                            data_url = response_data.get('job', {}).get('result_url')
                            job_data = download_json_data(data_url)
                            return True, job_data
                        elif job_status == 'failed':
                            bee_log('Data generation failed')
                            return False, None
                        else:
                            time.sleep(10)
                    else:
                        bee_log("Error getting job status", response.text)
                        return False, None

        else:
            bee_log("Error generating data", response.text)
            return False, None
        
        

 
    
 
        
        
                
                