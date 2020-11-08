# Generated by Django 3.1.3 on 2020-11-08 12:26

from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.CharField(max_length=40, primary_key=True, serialize=False, unique=True)),
                ('full_name', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=200)),
                ('default_branch', models.CharField(blank=True, default='master', max_length=100)),
                ('description', models.TextField(blank=True, default='')),
                ('issue_count', models.IntegerField(blank=True, default=0)),
                ('release_count', models.IntegerField(blank=True, default=0)),
                ('star_count', models.IntegerField(blank=True, default=0)),
                ('watcher_count', models.IntegerField(blank=True, default=0)),
                ('primary_language', models.CharField(blank=True, default='', max_length=50)),
                ('created_at', models.CharField(blank=True, default='', max_length=30)),
                ('pushed_at', models.CharField(blank=True, default='', max_length=30)),
                ('indicators', djongo.models.fields.JSONField(default={})),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('state', models.CharField(choices=[('pending', 'pending'), ('accepted', 'accepted'), ('running', 'running'), ('completed', 'completed'), ('error', 'error')], default='pending', editable=False, max_length=10)),
                ('name', models.CharField(choices=[('none', 'none'), ('extract-metrics', 'extract-metrics'), ('mine-fixing-commits', 'mine-fixing-commits'), ('mine-fixed-files', 'mine-fixed-files'), ('mine-failure-prone-files', 'mine-failure-prone-files'), ('scoring', 'scoring'), ('train', 'train')], default='none', max_length=50)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.repository')),
            ],
        ),
        migrations.CreateModel(
            name='PredictiveModel',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.BinaryField()),
                ('language', models.CharField(max_length=50)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.repository')),
            ],
        ),
        migrations.CreateModel(
            name='MetricsFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('file', models.BinaryField()),
                ('language', models.CharField(max_length=50)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.repository')),
            ],
        ),
        migrations.CreateModel(
            name='FixingCommit',
            fields=[
                ('sha', models.CharField(editable=False, max_length=50, primary_key=True, serialize=False, unique=True)),
                ('msg', models.TextField(blank=True, default='')),
                ('date', models.CharField(blank=True, default='', max_length=30)),
                ('is_false_positive', models.BooleanField(blank=True, default=False)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.repository')),
            ],
        ),
        migrations.CreateModel(
            name='FixedFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('is_false_positive', models.BooleanField(blank=True, default=False)),
                ('filepath', models.CharField(editable=False, max_length=300)),
                ('bug_inducing_commit', models.CharField(editable=False, max_length=50)),
                ('fixing_commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.fixingcommit')),
            ],
        ),
        migrations.CreateModel(
            name='FailureProneFile',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('filepath', models.CharField(editable=False, max_length=300)),
                ('commit', models.CharField(editable=False, max_length=50)),
                ('fixing_commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apis.fixingcommit')),
            ],
        ),
    ]
