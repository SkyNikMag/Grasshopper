from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Athlet
from .forms import AthletForm
from django.db.models import Q, Max
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login
from .forms import RegisterForm
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
from .forms import CompetitionLoginForm
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Avg
from django.db.models import F
from django.http import Http404



@login_required
def athlet_list(request):
    # Отображаем только спортсменов, принадлежащих вошедшему пользователю
    athlets = Athlet.objects.filter(user=request.user)
    # Получаем уникальные значения для фильтров, если они применимы
    teams = athlets.values_list('team', flat=True).distinct().order_by('team')
    regions = athlets.values_list('region', flat=True).distinct().order_by('region')

    # Получение значения поиска
    search_query = request.GET.get('search', '')

    if search_query:
        athlets = athlets.filter(
            Q(name__icontains=search_query.strip()) | Q(team__icontains=search_query.strip())
        )

    # Apply filters based on user input (if any)
    team_filter = request.GET.get('team')
    region_filter = request.GET.get('region')
    gender_filter = request.GET.get('gender')
    age_filter = request.GET.get('age')
    order_by = request.GET.get('order_by')

    # Filter the queryset based on the selected filters
    if team_filter:
        athlets = athlets.filter(team=team_filter)
    if region_filter:
        athlets = athlets.filter(region=region_filter)
    if gender_filter:
        # Фильтруем по значению из базы, которое является 'MN' для мужчин и 'WN' для женщин
        athlets = athlets.filter(gender=gender_filter)
    if age_filter == 'under_24':
        athlets = athlets.filter(date_birthday__gt='2000-01-01')  # Adjust date based on age calculation logic
    elif age_filter == 'over_24':
        athlets = athlets.filter(date_birthday__lt='2000-01-01')  # Adjust date based on age calculation logic

    if order_by:
        athlets = athlets.order_by(order_by)

    # Check if any results match the filters/search
    no_results = not athlets.exists()

    return render(request, 'grasshopper/athlet/list.html', {
        'athlets': athlets,
        'teams': teams,
        'regions': regions,
        'no_results': no_results,
    })


def athlet_detail(request, id):
    athlet = get_object_or_404(Athlet, id=id)

    return render(request,
                  'grasshopper/athlet/detail.html',
                  {'athlet': athlet})

@login_required
def athlet_add(request):
    if request.method == 'POST':
        form = AthletForm(request.POST)
        if form.is_valid():
            athlete = form.save(commit=False)
            athlete.user = request.user  # Привязка к текущему пользователю
            athlete.save()
            return redirect('grasshopper:athlet_list')
    else:
        form = AthletForm()
    return render(request, 'grasshopper/athlet/add.html', {'form': form})


def athlet_change(request, id):
    athlet = get_object_or_404(Athlet, pk=id)


    if request.method == "POST":
        # Create a form instance with the POST data, bound to the existing athlet instance
        form = AthletForm(request.POST, instance=athlet)

        if form.is_valid():
            form.save()  # This will save the changes to the existing athlete
            return redirect('grasshopper:athlet_list')
    else:
        # Initialize the form with the current athlete data
        form = AthletForm(instance=athlet)

    return render(request, 'grasshopper/athlet/change.html', {'form': form})

def athlet_delete(request, id):
    athlet = get_object_or_404(Athlet, id=id)

    if request.method == "POST":
        # Если форма была отправлена, удалите спортсмена и перенаправьте его в список
        athlet.delete()
        return redirect('grasshopper:athlet_list')

    # Render the confirmation page
    return render(request, 'grasshopper/athlet/delete_confirm.html', {'athlet': athlet})

@login_required
def results_view(request):
    if request.method == "POST":
        # Обработка сохранения результатов
        for athlete_id, result_list in request.POST.lists():
            if athlete_id.startswith("results_"):
                athlete_id = int(athlete_id.split("_")[1])
                new_results = [int(r) for r in result_list if r.isdigit()]

                try:
                    athlete = Athlet.objects.get(id=athlete_id)
                    existing_results = json.loads(athlete.results) if athlete.results else []

                    # Получаем количество существующих результатов
                    existing_count = len(existing_results)

                    # Добавляем только новые результаты
                    new_results_to_add = new_results[existing_count:]  # Все новые результаты, которые еще не сохранены

                    if new_results_to_add:
                        # Обновляем результаты, добавляя только новые
                        updated_results = existing_results + new_results_to_add
                        athlete.results = json.dumps(updated_results)

                        # Считаем и сохраняем средний результат
                        if updated_results:
                            athlete.average_result = round(sum(updated_results) / len(updated_results), 2)
                            athlete.total_result = sum(updated_results)
                        else:
                            athlete.average_result = None
                            athlete.total_result = 0

                        athlete.save()

                except Athlet.DoesNotExist:
                    continue

        return JsonResponse({"message": "Результаты сохранены"})

    # Обработка GET-запроса для отображения страницы с фильтрацией данных
    results_type = request.GET.get("type", "all")
    print("Получен тип результата:", results_type)

    # Получение базового набора данных для текущего пользователя
    athletes_queryset = Athlet.objects.filter(user=request.user)

    # Фильтрация по имени или команде
    search_query = request.GET.get('search', '').strip()
    if search_query:
        athletes_queryset = athletes_queryset.filter(
            Q(name__icontains=search_query) | Q(team__icontains=search_query)
        )

    # Дополнительные фильтры
    team_filter = request.GET.get('team')
    region_filter = request.GET.get('region')
    gender_filter = request.GET.get('gender')
    age_filter = request.GET.get('age')

    if team_filter:
        athletes_queryset = athletes_queryset.filter(team=team_filter)
    if region_filter:
        athletes_queryset = athletes_queryset.filter(region=region_filter)
    if gender_filter:
        athletes_queryset = athletes_queryset.filter(gender=gender_filter)
    if age_filter == 'under_24':
        athletes_queryset = athletes_queryset.filter(date_birthday__gt='2000-01-01')
    elif age_filter == 'over_24':
        athletes_queryset = athletes_queryset.filter(date_birthday__lt='2000-01-01')

    athletes = list(athletes_queryset)

    # Расчет среднего результата для каждого спортсмена и количества результатов
    for athlete in athletes:
        athlete.decoded_results = json.loads(athlete.results) if athlete.results else []
        athlete.result_count = len(athlete.decoded_results)  # Количество результатов

    # Сортировка спортсменов: сначала по количеству результатов (по убыванию), затем по среднему результату (по возрастанию)
    athletes = sorted(athletes, key=lambda x: (-x.result_count, x.average_result))

    # Фильтрация по типу результата
    if results_type == "semifinal":
        # 50% лучших спортсменов по среднему результату
        semifinalists = athletes[:len(athletes) // 2]

        # Если у полуфиналистов есть дополнительные результаты, добавляем их и пересчитываем средний результат
        for athlete in semifinalists:
            athlete.decoded_results = json.loads(athlete.results) if athlete.results else []
            athlete.average_result = round(sum(athlete.decoded_results) / len(athlete.decoded_results), 2)

        # Сортируем полуфиналистов по количеству результатов и среднему результату
        athletes = sorted(semifinalists, key=lambda x: (-x.result_count, x.average_result))

    elif results_type == "final":
        # Полуфиналисты: первые 50%
        semifinalists = athletes[:len(athletes) // 2]
        # Из полуфиналистов выбираем 50% для финала
        finalists = semifinalists[:len(semifinalists) // 2]

        # Обновляем результаты и пересчитываем средний результат для финалистов
        for athlete in finalists:
            athlete.decoded_results = json.loads(athlete.results) if athlete.results else []
            athlete.average_result = round(sum(athlete.decoded_results) / len(athlete.decoded_results), 2)

        # Сортируем финалистов по количеству результатов и среднему результату
        athletes = sorted(finalists, key=lambda x: (-x.result_count, x.average_result))

    # Сортировка для всех других типов (если не полуфинал или финал)
    if results_type == "all":
        athletes = sorted(athletes, key=lambda x: (-x.result_count, x.average_result))

    print("Results type:", results_type)

    # Получаем уникальные команды и регионы для фильтров
    teams = athletes_queryset.values_list('team', flat=True).distinct().order_by('team')
    regions = athletes_queryset.values_list('region', flat=True).distinct().order_by('region')

    # Отправка в шаблон отфильтрованных данных
    return render(request, 'grasshopper/athlet/results.html', {
        "athletes": athletes,  # итоговый отфильтрованный список спортсменов
        'teams': teams,
        'regions': regions,
    })




def competition_login(request):
    if request.method == "POST":
        competition_id = request.POST.get("competition")  # Получаем ID выбранного соревнования
        password = request.POST.get("password")

        # Проверяем, что поле 'competition' не пустое
        if not competition_id:
            messages.error(request, "Пожалуйста, выберите соревнование.")
            return redirect('grasshopper:competition_login')  # Перенаправляем обратно на страницу входа

        try:
            # Получаем выбранного пользователя
            user = User.objects.get(id=competition_id)

            # Проверяем правильность пароля
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)  # Логиним пользователя
                return redirect("grasshopper:athlet_list")  # Перенаправление на основную страницу после входа
            else:
                messages.error(request, "Неверный пароль.")
        except User.DoesNotExist:
            messages.error(request, "Пользователь не найден.")

        # Если аутентификация не прошла или произошла ошибка, рендерим страницу с ошибками
        return render(request, "grasshopper/login.html", {'users': User.objects.all()})

    # Для GET-запроса выводим форму входа с пользователями
    else:
        users = User.objects.all()  # Получаем всех пользователей
        return render(request, "grasshopper/login.html", {'users': users})


def competition_register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        username = request.POST.get("username")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")
        if password != password_confirm:
            messages.error(request, "Пароли не совпадают. Пожалуйста, введите их заново.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Пользователь с таким именем уже существует")
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, "Регистрация прошла успешно. Пожалуйста, войдите.")
            return redirect("grasshopper:competition_login")
    else:
        form = RegisterForm()
    return render(request, "grasshopper/register.html", {'form': form})

# def register(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.set_password(form.cleaned_data['password'])  # Установите пароль
#             user.save()
#             login(request, user)  # Автоматически войти после регистрации
#             return redirect('grasshopper:athlet_list')  # Перенаправить на страницу с данными спортсменов
#     else:
#         form = RegisterForm()
#     return render(request, 'grasshopper/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('grasshopper:competition_login')  # Перенаправляем на страницу входа после выхода

#
# def printable_athlete_list(request):
#     # Получаем тип результата из GET-параметров (по умолчанию "all")
#     results_type = request.GET.get("type", "all")
#
#     # Получаем базовый набор данных для текущего пользователя
#     athletes_queryset = Athlet.objects.filter(user=request.user)
#
#     athletes = list(athletes_queryset)
#
#     # Обработка и сортировка спортсменов в зависимости от результатов
#     for athlete in athletes:
#         athlete.decoded_results = json.loads(athlete.results) if athlete.results else []
#         athlete.result_count = len(athlete.decoded_results)
#         athlete.average_result = (
#             round(sum(athlete.decoded_results) / len(athlete.decoded_results), 2)
#             if athlete.decoded_results else 0
#         )
#
#     # Сортировка и фильтрация для полуфинала и финала
#     if results_type == "semifinal":
#         semifinalists = athletes[:len(athletes) // 2]
#         for athlete in semifinalists:
#             athlete.result_type = "semifinal"
#         athletes = semifinalists
#     elif results_type == "final":
#         semifinalists = athletes[:len(athletes) // 2]
#         finalists = semifinalists[:len(semifinalists) // 2]
#         for athlete in finalists:
#             athlete.result_type = "final"
#         athletes = finalists
#     else:
#         for athlete in athletes:
#             athlete.result_type = "all"
#
#     # Добавление ранжирования: финалисты, полуфиналисты, остальные
#     athletes.sort(key=lambda x: (
#         {"final": 0, "semifinal": 1, "all": 2}[x.result_type],
#         -x.result_count,
#         x.average_result
#     ))
#
#     max_jumps = max(
#         len(athlete.decoded_results) for athlete in athletes if athlete.results
#     )
#
#     return render(request, 'grasshopper/athlet/printable_athlete_list.html', {
#         'athletes': athletes,
#         'max_jumps': max(max_jumps, 5)
#     })
def print_protocol(request):
    protocol_type = request.GET.get('protocol_type')
    results_type = request.GET.get("type", "all")

    # Query athletes
    athletes_queryset = Athlet.objects.all()

    # Determine default template
    template = 'grasshopper/athlet/printable_athlete_list.html'

    protocol_labels = {
        'male': 'Мужчины',
        'female': 'Женщины',
        'junior_male': 'Юниоры',
        'junior_female': 'Юниорки',
        'team': 'команды',  # You can add more mappings if needed
    }



    # Filter by protocol type
    if protocol_type == 'male':
        athletes_queryset = athletes_queryset.filter(gender='MN')
    elif protocol_type == 'female':
        athletes_queryset = athletes_queryset.filter(gender='WN')
    elif protocol_type == 'junior_male':
        athletes_queryset = athletes_queryset.filter(
            gender='MN', date_birthday__gte=timezone.now() - timedelta(days=24 * 365)
        )
    elif protocol_type == 'junior_female':
        athletes_queryset = athletes_queryset.filter(
            gender='WN', date_birthday__gte=timezone.now() - timedelta(days=24 * 365)
        )
    elif protocol_type == 'team':
        template = 'grasshopper/athlet/print_team_list.html'

    protocol_label = protocol_labels.get(protocol_type, 'Общий зачет')

    # Decode results and calculate stats for each athlete
    athletes = list(athletes_queryset)
    for athlete in athletes:
        athlete.decoded_results = json.loads(athlete.results) if athlete.results else []
        athlete.result_count = len(athlete.decoded_results)

    # Apply minimum result count limitation only for team protocols
    if protocol_type == 'team':
        # Calculate min_result_count and limit displayed results
        min_result_count = min((athlete.result_count for athlete in athletes), default=0)
        max_jumps_range = range(min_result_count)

        # Limit results and calculate team-specific total using only displayed results
        for athlete in athletes:
            athlete.padded_results = athlete.decoded_results[:min_result_count]
            athlete.total_result = sum(athlete.padded_results)
    else:
        # Display all results for non-team protocols
        max_jumps = max((athlete.result_count for athlete in athletes), default=5)
        for athlete in athletes:
            athlete.padded_results = athlete.decoded_results + [''] * (max_jumps - athlete.result_count)
            athlete.total_result = sum(athlete.decoded_results)  # Full sum for non-team protocols
        max_jumps_range = range(max_jumps)

    # Sort athletes based on total count and average
    athletes.sort(key=lambda x: (-x.result_count, x.total_result))

    # Filter results by stages
    if results_type == "semifinal":
        athletes = athletes[:len(athletes) // 2]
    elif results_type == "final":
        athletes = athletes[:len(athletes) // 4]

    # Group by team and calculate total results for team protocol
    if protocol_type == 'team':
        teams = {}
        for athlete in athletes:
            team_name = athlete.team
            if team_name not in teams:
                teams[team_name] = {
                    'team': team_name,
                    'athletes': [],
                    'total_result': 0
                }
            teams[team_name]['athletes'].append(athlete)
            teams[team_name]['total_result'] += athlete.total_result  # Sum only displayed results

        # Sort teams by total result
        sorted_teams = sorted(teams.values(), key=lambda x: x['total_result'])

        # Assign ranks to teams
        for rank, team in enumerate(sorted_teams, start=1):
            team['rank'] = rank

        return render(request, template, {
            'teams': sorted_teams,
            'max_jumps_range': max_jumps_range,
        })
    else:
        # Render non-team protocols with all results
        return render(request, template, {
            'athletes': athletes,
            'max_jumps_range': max_jumps_range,
            'protocol_type': protocol_label,
        })
