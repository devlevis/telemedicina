from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedico, is_medico, DatasAbertas
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
# Importação para manipular datas
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento 
from django.contrib.auth.decorators import login_required

@login_required
def cadastro_medico(request):
    # Verifica se o usuário já é médico
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já é médico!')
        return redirect('/medicos/abrir_horario')
    
    if request.method == 'GET':
        # Obtém todas as especialidades para exibição no formulário
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico': is_medico(request.user)})
    elif request.method == 'POST':
        # Coleta dados do formulário
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')
        
        # Cria um novo objeto DadosMedico com as informações fornecidas
        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            especialidade_id=especialidade,
            descricao=descricao,
            valor_consulta=valor_consulta,
            user=request.user
        )
        
        # Salva os dados do médico no banco de dados
        dados_medico.save()
        
        # Adiciona uma mensagem de sucesso
        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso!')
        return redirect('/medicos/abrir_horario')
    
@login_required
def abrir_horario(request):
    # Verifica se o usuário é um médico
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horário')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        # Obtém os dados do médico e as datas abertas
        dados_medicos = DadosMedico.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'datas_abertas': datas_abertas, 'is_medico': is_medico(request.user)})
    elif request.method == 'POST':
        # Coleta a data e formata
        data = request.POST.get('data')
        data_fomatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')
        
        # Verifica se a data é válida
        if data_fomatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data não pode ser anterior que a data atual')
            return redirect('/medicos/abrir_horario')
        
        # Verifica se já existe um horário cadastrado para essa data
        if DatasAbertas.objects.filter(data=data, user=request.user).exists():
            messages.add_message(request, constants.ERROR, 'Já existe um horário cadastrado para essa data!')
            return redirect('/medicos/abrir_horario')
        
        # Cria um novo objeto DatasAbertas e salva no banco de dados
        horario_abrir = DatasAbertas(
            data=data,
            user=request.user
        )
        
        horario_abrir.save()
        
        # Adiciona uma mensagem de sucesso
        messages.add_message(request, constants.SUCCESS, 'Horário cadastrado com sucesso!')
        return redirect('/medicos/abrir_horario')
    
@login_required
def consultas_medico(request):
    # Verifica se o usuário é um médico
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horário')
        return redirect('/usuarios/sair')
    
    # Obtém a data atual, sem a hora.
    hoje = datetime.now().date()
    
    # Filtra as consultas para o médico logado que são agendadas para o dia atual.
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user) \
                                     .filter(data_aberta__data__gte=hoje) \
                                     .filter(data_aberta__data__lt=hoje + timedelta(days=1))
    
    # Filtra todas as consultas que não estão agendadas para o dia atual.
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)
    
    # Renderiza a página 'consultas_medico.html' com as consultas do dia e as restantes
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

@login_required
def consulta_area_medico(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horário')
        return redirect('/usuarios/sair')
    
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos})
    if request.method == 'POST':
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')
        
        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada!')
            return redirect(f'/medicos/consulta_area_medico/{consulta.id}')
        elif consulta.status == 'F':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada!')
            return redirect(f'/medicos/consulta_area_medico/{consulta.id}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()
        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso!')
        return redirect(f'/medicos/consulta_area_medico/{consulta.id}')
    
@login_required
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir horário')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/abrir_horario/')

    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

@login_required
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos!')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    
    if not documento:
        messages.add_message(request, constants.ERROR, 'Preencha o campo documento!')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
    
    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso.')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

from django.db.models import Count

@login_required
def dashboard(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem abrir a dashboard')
        return redirect('/usuarios/sair')
    
    # Obtém as consultas do usuário logado que estão dentro de um intervalo de 7 dias no passado até 1 dia no futuro
    consultas = Consulta.objects.filter(data_aberta__user=request.user)\
    .filter(data_aberta__data__range=[datetime.now().date() - timedelta(days=7), datetime.now().date() + timedelta(days=1)])\
    .annotate().values('data_aberta__data').annotate(quantidade=Count('id'))# Seleciona apenas a data das consultas e conta o numero de consultas para cada data
    
    # Cria uma lista de datas formatadas como strings (ex: "13-07-2024")
    datas = [i['data_aberta__data'].strftime("%d-%m-%Y") for i in consultas]
    # Cria uma lista com as quantidades de consultas correspondentes a cada data
    quantidade = [i['quantidade'] for i in consultas]
    
    # Renderiza o template 'dashboard.html' passando as listas de datas e quantidades como contexto
    return render(request, 'dashboard.html', {'datas': datas, 'quantidade': quantidade})