from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages

from apostilas.models import Apostila, ViewApostilas


# Create your views here.
def add_apostila(request):
    if request.method == 'GET':
        apostilas = Apostila.objects.filter(usuario=request.user)
        visualizacoes = ViewApostilas.objects.filter(apostila__user=request.user).count()
        return render(
            request,
            'add_apostila.html',
            {
                'apostilas': apostilas,
                'visualizacoes' : visualizacoes,
            }
        )

    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        arquivo = request.POST.get('arquivo')

        apostila = Apostila(usuario=request.user, titulo=titulo, arquivo=arquivo)
        apostila.save()

        messages.add_message(
            request,
            constants.messages.SUCCESS,
            'Apostila cadastrada com sucesso!'
        )

        return redirect('/apostila/add_apostila/')


def apostila(request, id):
    apostila = Apostila.objects.get(id=id)

    views_unicas = ViewApostilas.objects.filter(apostila=apostila).values('ip').distinct().count()
    views_totais = ViewApostilas.objects.filter(apostila=apostila).count()

    view = ViewApostilas(
        ip = request.META['REMOTE_ADDR'],
        apostila = apostila
    )

    view.save()

    return render(
        request,
        'apostilas.html',
        {
            'apostila': apostila,
            'views_unicas': views_unicas,
            'views_totais': views_totais,
        }
    )
