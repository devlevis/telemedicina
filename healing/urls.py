from django.contrib import admin
#funções de criar url padrão(do site)
from django.urls import path, include
#importando arquivo settings de healing
from django.conf import settings
#função de criar url para arquivos de media:
from django.conf.urls.static import static
from django.shortcuts import redirect


urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('medicos/', include('medico.urls')),
    path('pacientes/', include('paciente.urls')),
    path('', lambda request: redirect('/usuarios/login'))
    #Assim eu crio url para media:
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
