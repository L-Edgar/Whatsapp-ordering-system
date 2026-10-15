# whatsapp/admin.py
from django.contrib import admin
from .models import WhatsAppConfiguration

config = WhatsAppConfiguration.objects.get(business_id = 1)
config.access_token = "EAAT8SmkZA61ABSkZBdlXTSSHfCVhscjpiZAk7OOZCQTBZBZCSisLx2qACuTyZAZA3gQvjhKWU8NYsuY7Cx27XXCGwpsQKpnqFYTYTfikwYw8VJ9Rw6RCtJRqau54gmVjQohBgPeOwXhOGfReDWWjbI7S4ldKuwFm4PSSf7yOhc3cCCgjg4zQZCai0uqbsdxzdJwZDZD"
config.phone_number_id = "1382026141655741"
config.save()
@admin.register(WhatsAppConfiguration)
class WhatsAppConfigAdmin(admin.ModelAdmin):
    list_display = ["business", "phone_number_id", "is_active"]