from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.messages import constants
from django.contrib import messages

from .models import Categoria, Flashcard, Desafio, FlashcardDesafio


def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user)

        categoria_filtro = request.GET.get('categoria')
        dificuldade_filtro = request.GET.get('dificuldade')

        if categoria_filtro:
            flashcards = flashcards.filter(categoria__id=categoria_filtro)

        if dificuldade_filtro:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtro)

        return render(
            request,
            'novo_flashcard.html',
            {
                'categorias': categorias,
                'dificuldades': dificuldades,
                'flashcards': flashcards,
            }

        )
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(
                request,
                constants.ERROR,
                'Preencha os campos de pergunta e resposta'
            )
            return redirect('novo_flashcard')

        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
        )

        flashcard.save()

        messages.add_message(
            request, constants.SUCCESS, 'Flashcard criado com suceso!!'
        )

        return redirect('novo_flashcard')


def deletar_flashcard(request, id):
    # validar a segurança
    flashcard = Flashcard.objects.get(id=id)
    flashcard.delete()
    messages.add_message(
        request,
        constants.SUCCESS,
        'Flashcard deletado com sucesso!!'
    )

    return redirect('novo_flashcard')


def iniciar_desafio(request):
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES

        return render(
            request,
            'iniciar_desafio.html',
            {
                'categorias': categorias,
                'dificuldades': dificuldades
            },
        )

    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categorias')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade,
        )

        desafio.save()

        desafio.categoria.add(*categorias)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio')

        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )

            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/listar_desafio')


def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)
    # TODO: desenvolver os status
    # TODO: desenvolver os filtros
    return render(
        request,
        'listar_desafio.html',
        {
            'desafios': desafios,
        },
    )


def desafio(request, id):
    desafio = Desafio.objects.get(id=id)

    if not desafio.user == request.user:
        raise Http404()

    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        errados = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()

        return render(
            request,
            'desafio.html',
            {
                'desafio': desafio,
                'acertos': acertos,
                'errados': errados,
                'faltantes': faltantes,
             }
        )


def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}/')