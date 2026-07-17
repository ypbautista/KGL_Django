from django.contrib import admin
from .models import (
    JugendlichePerson,
    Bezugsperson,
    Fragebogen,
    FragebogenFall,
    Einladung,
    FragebogenAntwort,
    FragebogenAbschnitt,
    FrageVorlage,
    AbschnittFrage,
    AbschnittAntwort,
    FrageAntwort
)

admin.site.register(JugendlichePerson)
admin.site.register(Bezugsperson)
admin.site.register(Fragebogen)
admin.site.register(FragebogenFall)
admin.site.register(Einladung)
admin.site.register(FragebogenAntwort)
admin.site.register(FragebogenAbschnitt)
admin.site.register(FrageVorlage)
admin.site.register(AbschnittFrage)
admin.site.register(AbschnittAntwort)
admin.site.register(FrageAntwort)


original_get_app_list = admin.AdminSite.get_app_list

def custom_get_app_list(self, request, app_label=None):
    app_list = original_get_app_list(self, request, app_label)
    
    target_app = None
    other_apps = []
    
    for app in app_list:
        if app['app_label'] == 'fragebogen':
            target_app = app
        else:
            other_apps.append(app)
            
    if not target_app:
        return app_list

    person_models = []
    blueprint_models = []
    logic_models = []
    answer_models = []
    
    for model in target_app['models']:
        name = model['object_name']
        
        if name in ['JugendlichePerson', 'Bezugsperson']:
            person_models.append(model)

        elif name in ['Fragebogen', 'FragebogenAbschnitt', 'FrageVorlage', 'AbschnittFrage']:
            blueprint_models.append(model)

        elif name in ['FragebogenFall', 'Einladung']:
            logic_models.append(model)

        elif name in ['FragebogenAntwort', 'AbschnittAntwort', 'FrageAntwort']:
            answer_models.append(model)

    reordered_sections = []
    
    if person_models:
        reordered_sections.append({
            'name': '1. Stammdaten (Personen)',
            'app_label': 'fb_people',
            'models': person_models,
            'has_module_perms': target_app['has_module_perms'],
            'app_url': target_app['app_url'],
        })
        
    if blueprint_models:
        reordered_sections.append({
            'name': '2. Fragebogen-Konfiguration',
            'app_label': 'fb_templates',
            'models': blueprint_models,
            'has_module_perms': target_app['has_module_perms'],
            'app_url': target_app['app_url'],
        })
        
    if logic_models:
        reordered_sections.append({
            'name': '3. Diagnostische Fälle & Links',
            'app_label': 'fb_workflow',
            'models': logic_models,
            'has_module_perms': target_app['has_module_perms'],
            'app_url': target_app['app_url'],
        })
        
    if answer_models:
        reordered_sections.append({
            'name': '4. Ausgefüllte Antworten (Rohdaten)',
            'app_label': 'fb_vault',
            'models': answer_models,
            'has_module_perms': target_app['has_module_perms'],
            'app_url': target_app['app_url'],
        })

    return other_apps + reordered_sections

admin.AdminSite.get_app_list = custom_get_app_list