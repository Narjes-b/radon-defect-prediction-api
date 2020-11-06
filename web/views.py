import io
import json
import pandas as pd
from apis.models import MetricsFile, PredictiveModel, Repository, Task
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.http import require_GET, require_POST
from github import Github, GithubException

from backend.miner import BackendRepositoryMiner
from backend.predictor import BackendTrainer


@require_GET
def get_github_repository(request):
    access_token = request.headers.get('token')
    full_name_or_id = request.GET['full_name_or_id']

    try:
        g = Github(login_or_token=access_token)
        repo = g.get_repo(full_name_or_id)

        content = {
            'id': repo.id,
            'full_name': repo.full_name,
            'url': repo.html_url,
            'default_branch': repo.default_branch,
            'description': repo.description,
            'created_at': repo.created_at.strftime("%Y-%d-%m %H:%M:%S"),
            'star_count': repo.stargazers_count,
        }
        return HttpResponse(content=json.dumps(content), content_type='application/json', status=200)
    except GithubException as e:
        print(e)
        return HttpResponse(status=400)


def repository_dump_metrics(request, pk: str):
    repository = get_object_or_404(Repository, pk=pk)
    metrics = MetricsFile.objects.get(repository=repository, language='ansible')
    df = pd.read_csv(io.BytesIO(metrics.file))

    filename = f'{repository.full_name}_ansible_metrics.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    df.to_csv(path_or_buf=response, index=False)

    return response


def repository_dump_model(request, pk: str):
    repository = get_object_or_404(Repository, pk=pk)
    model = PredictiveModel.objects.get(repository=repository, language='ansible')
    b_model = model.file

    filename = f'{repository.full_name}_ansible_model.joblib'
    response = HttpResponse(b_model, content_type='application/octet-streamapplication/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


def repository_home(request, pk):
    repository = get_object_or_404(Repository, pk=pk)
    return render(request=request, context={'repository': repository}, template_name='repository_home.html', status=200)


def repository_fixing_commits(request, pk):
    repository = get_object_or_404(Repository, pk=pk)
    return render(request=request, context={'repository': repository}, template_name='repository_fixing_commits.html',
                  status=200)


def repository_fixing_files(request, pk):
    repository = get_object_or_404(Repository, pk=pk)
    return render(request=request, context={'repository': repository}, template_name='repository_fixing_files.html',
                  status=200)


@require_POST
def repository_mine(request, pk):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    task_id, task_state = BackendRepositoryMiner(
        repo_id=pk,
        language=body.get('language'),
        labels=body.get('labels'),
        regex=body.get('regex')).mine()

    if task_state == Task.ACCEPTED:
        return HttpResponse(status=202, content=task_id)
    else:
        return HttpResponse(status=500)


def repository_train_settings(request, pk):
    repository = get_object_or_404(Repository, pk=pk)
    return render(request=request, context={'repository': repository}, template_name='repository_train_settings.html',
                  status=200)


def repository_train_start(request, pk):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    task_id, task_state = BackendTrainer(
        repo_id=pk,
        language=body.get('language'),
        classifiers=body.get('classifiers'),
        balancers=body.get('balancers'),
        normalizers=body.get('normalizers'),
        selectors=body.get('selectors')).train()

    if task_state == Task.ACCEPTED:
        return HttpResponse(status=202, content=task_id)
    else:
        return HttpResponse(status=500)
