from django.shortcuts import render, redirect
from medico.models import DadosMedico, Especialidades, DatasAbertas, is_medico
from django.http import HttpResponse
from datetime import datetime
from paciente.models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    if request.method == 'GET':
        medico_filtrar = request.GET.get('medico')
        especialidades_filtrar = request.GET.getlist('especialidades')
        # Obtém todos os objetos DadosMedico do banco de dados
        medicos = DadosMedico.objects.all()
        
        # Filtra os médicos pelo nome se 'medico_filtrar' estiver presente
        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)
        # Filtra os médicos pelas especialidades selecionadas se 'especialidades_filtrar' estiver presente
        if especialidades_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidades_filtrar)
            
        especialidades = Especialidades.objects.all()
        
        return render(request, 'home.html', {'medicos': medicos, 'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    
@login_required
def escolher_horario(request, id_dados_medicos):
    if request.method == 'GET':
        # Obtém o objeto DadosMedico com base no id_dados_medicos fornecido na URL
        medico = DadosMedico.objects.get(id=id_dados_medicos)
        
        # Filtra datas disponíveis que pertencem ao mesmo usuário do médico e que ainda não foram agendadas
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
        
        # Renderiza o template 'escolher_horario.html', passando os dados do médico e as datas disponíveis para o contexto do template
        return render(request, 'escolher_horario.html', {'medico': medico, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})

@login_required
def agendar_horario(request, id_data_aberta):
    if request.method == 'GET':
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        
        horario_agendado = Consulta(
            paciente=request.user,
            data_aberta=data_aberta
        )
        
        horario_agendado.save()
        
        data_aberta.agendado = True
        data_aberta.save()
        
        messages.add_message(request, constants.SUCCESS, 'Consulta agendada com sucesso!')
        return redirect('/pacientes/minhas_consultas/')
    
@login_required    
def minhas_consultas(request):
    data = request.GET.get('data')
    especialidade_escolhida = request.GET.get('especialidade')
    
    minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())

#tenho que compara  aespecialidade do medico da consulta com a especialidade escolhida
    if especialidade_escolhida:
        minhas_consultas = minhas_consultas.filter(data_aberta__user__dadosmedico__especialidade__id=especialidade_escolhida)
        
    if data:
        minhas_consultas = minhas_consultas.filter(data_aberta__data__gte=data)
    
    
    especialidades = Especialidades.objects.all()
    
    return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'especialidades': especialidades, 'is_medico': is_medico(request.user)})

@login_required
def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        dado_medico = DadosMedico.objects.get(user=consulta.data_aberta.user)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'documentos': documentos})
    
@login_required
def cancelar_consulta(request, id_consulta):
    consulta = Consulta.objects.get(id=id_consulta)
    
    if request.user != consulta.paciente:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/pacientes/consulta/{id_consulta}')
    consulta.status = 'C'
    consulta.save()
    messages.add_message(request, constants.SUCCESS, 'Consulta cancelada com sucesso!')
    return redirect(f'/pacientes/consulta/{id_consulta}')