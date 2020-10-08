import json
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import FixingCommit, FixingFile, Repositories
from .serializers import FixingCommitSerializer, FixingFileSerializer, RepositorySerializer


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_repository(id: str, owner: str, name: str, url: str, default_branch: str, description: str,
                          issue_count: int,
                          releases_count: int, stars_count: int, watcher_count: int, primary_language: str,
                          created_at: str,
                          pushed_at: str):
        repository = Repositories(id=id, owner=owner, name=name, url=url, default_branch=default_branch,
                                  description=description, issue_count=issue_count, release_count=releases_count,
                                  star_count=stars_count, watcher_count=watcher_count,
                                  primary_language=primary_language,
                                  created_at=created_at, pushed_at=pushed_at)
        repository.save()
        return repository

    @staticmethod
    def create_fixing_commit(sha: str, msg: str, date: str, is_false_positive: bool, repository: Repositories):
        fixing_commit = FixingCommit(sha=sha, msg=msg, date=date, is_false_positive=is_false_positive,
                                     repository=repository)
        fixing_commit.save()
        return fixing_commit

    @staticmethod
    def create_fixing_file(filepath: str, is_false_positive: bool, bug_inducing_commit: str,
                           fixing_commit: FixingCommit):
        fixing_file = FixingFile(filepath=filepath, is_false_positive=is_false_positive,
                                 bug_inducing_commit=bug_inducing_commit, fixing_commit=fixing_commit)
        fixing_file.save()
        return fixing_file

    def setUp(self):
        # add test repositories
        self.repo1 = self.create_repository(id='MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ==', owner='jnv',
                                            name='ansible-role-unattended-upgrades',
                                            url='https://github.com/jnv/ansible-role-unattended-upgrades',
                                            default_branch='master',
                                            description='Setup unattended-upgrades on Debian-based systems',
                                            issue_count=37, releases_count=15, stars_count=201, watcher_count=10,
                                            primary_language='shell',
                                            created_at='2014-01-18T23:56:09Z', pushed_at='2020-08-18T12:28:29Z')

        self.repo2 = self.create_repository(id='MDEwOlJlcG9zaXRvcnkxNjAzNjY0Ng==', owner='jnv',
                                            name='ansible-role-debian-backports',
                                            url='https://github.com/jnv/ansible-role-debian-backports',
                                            default_branch='master',
                                            description='Setup backports repository for Debian and Ubuntu',
                                            issue_count=5, releases_count=6, stars_count=7, watcher_count=1,
                                            primary_language='shell',
                                            created_at='2014-01-15T16:46:51Z', pushed_at='2020-08-09T12:22:24Z')

        # add test fixing-commits
        self.fic1 = self.create_fixing_commit('123456789', 'Fixed issue #1', '06/10/2020 17:26', False, self.repo1)
        self.fic2 = self.create_fixing_commit('23456789', 'Fixed issue #2', '06/10/2020 17:27', False, self.repo1)
        self.fic3 = self.create_fixing_commit('3456789', 'Fixed issue #3', '06/10/2020 17:28', False, self.repo2)
        self.fic4 = self.create_fixing_commit('456789', 'Fixed issue #4', '06/10/2020 17:29', False, self.repo2)
        self.fic5 = self.create_fixing_commit('56789', 'Fixed issue #5', '06/10/2020 17:30', False, self.repo2)

        # add test fixing-files
        self.file1 = self.create_fixing_file('filename1.yaml', False, 'bic_123456789', self.fic1)
        self.file2 = self.create_fixing_file('filename2.yaml', False, 'bic_23456789', self.fic1)
        self.file3 = self.create_fixing_file('filename3.yaml', False, 'bic_3456789', self.fic1)
        self.file4 = self.create_fixing_file('filename1.yaml', False, 'bic_456789', self.fic2)
        self.file5 = self.create_fixing_file('filename4.yaml', False, 'bic_56789', self.fic2)
        self.file6 = self.create_fixing_file('filename5.yaml', False, 'bic_6789', self.fic3)

    def _post_teardown(self):
        Repositories.objects.all().delete()


class RepositoriesTest(BaseViewTest):

    def test_get_all_repositories(self):
        """
        This test ensures that all repositories added in the setUp method exist when we make a GET request to the \
        repositories/ endpoint
        """
        # get API response
        response = self.client.get(reverse('api:repositories-list'))

        # get data from db
        repositories = Repositories.objects.all()
        serializer = RepositorySerializer(repositories, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_repository(self):
        response = self.client.get(
            reverse('api:repositories-detail', kwargs={'pk': 'MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ=='}))
        repository = Repositories.objects.get(pk='MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ==')
        serializer = RepositorySerializer(repository)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_repository(self):
        response = self.client.get(reverse('api:repositories-detail', kwargs={'pk': 'WrOnGrEpOsItOrYsHa=='}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_repository(self):
        valid_payload = {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib'
        }

        repositories_before_create = RepositorySerializer(Repositories.objects.all(), many=True).data

        response = self.client.post(
            reverse('api:repositories-list'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        repositories_after_create = RepositorySerializer(Repositories.objects.all(), many=True).data

        self.assertGreater(len(repositories_after_create), len(repositories_before_create))

    def test_create_invalid_repository(self):
        invalid_payloads = [{
            # no id passed
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            # no owner passed
            'name': 'ansible-junos-stdlib',
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            # no name passed
            'url': 'https://github.com/Juniper/ansible-junos-stdlib',
        }, {
            'id': 'MDEwOlJlcG9zaXRvcnkxNjE4MzAxNQ==',
            'owner': 'Juniper',
            'name': 'ansible-junos-stdlib'
            # no url passed
        }]

        repositories_before_create = RepositorySerializer(Repositories.objects.all(), many=True).data

        for payload in invalid_payloads:
            response = self.client.post(
                reverse('api:repositories-list'),
                data=json.dumps(payload),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        repositories_after_create = RepositorySerializer(Repositories.objects.all(), many=True).data
        self.assertEqual(repositories_after_create, repositories_before_create)

    def test_create_repository_conflict(self):
        """
        Try to create a repository with the same ID of one already present in the database.
        :except: status.HTTP_409_CONFLICT
        """
        existing_payload = RepositorySerializer(self.repo1).data
        repositories_before_conflict = RepositorySerializer(Repositories.objects.all(), many=True).data

        # here the conflict
        response = self.client.post(
            reverse('api:repositories-list'),
            data=json.dumps(existing_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        repositories_after_conflict = RepositorySerializer(Repositories.objects.all(), many=True).data
        self.assertEqual(repositories_after_conflict, repositories_before_conflict)

    def test_delete_existing_repository(self):
        """
        Delete a repository from the database and compare the database before and after deleting.
        If the database differs, than the repository has been deleted
        """
        repositories_before_delete = Repositories.objects.all()
        serializer_before_delete = RepositorySerializer(repositories_before_delete, many=True).data

        response = self.client.delete(
            reverse('api:repositories-detail', kwargs={'pk': 'MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ=='})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        repositories_after_delete = Repositories.objects.all()
        serializer_after_delete = RepositorySerializer(repositories_after_delete, many=True).data

        self.assertLess(len(serializer_after_delete), len(serializer_before_delete))

    def test_delete_unexisting_repository(self):
        """
        Try to delete a repository that does not exist in the db.
        :except: HTTP_404_NOT_FOUND
        """
        response = self.client.delete(
            reverse('api:repositories-detail', kwargs={'pk': 'NoTPrEsEnT=='})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ================================== FIXING-COMMITS ==============================================================#
class FixingCommitsTest(BaseViewTest):

    def test_get_all_fixing_commits(self):
        """
        This test ensures that all fixing-commits added in the setUp method exist when we make a GET request to the \
        fixing-commits/ endpoint
        """
        # get API response
        response = self.client.get(reverse('api:fixing-commits-list'))

        # get data from db
        fixing_commits = FixingCommit.objects.all()
        serializer = FixingCommitSerializer(fixing_commits, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_valid_single_fixing_commit(self):
        response = self.client.get(reverse('api:fixing-commits-detail', kwargs={'pk': '123456789'}))
        fixing_commit = FixingCommit.objects.get(sha='123456789')
        serializer = FixingCommitSerializer(fixing_commit)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_invalid_single_fixing_commit(self):
        response = self.client.get(reverse('api:fixing-commits-detail', kwargs={'pk': '000000000'}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_valid_fixing_commits(self):
        repository = Repositories.objects.get(pk='MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ==')
        valid_payload = {
            'sha': '987654321',
            'msg': 'This is a new fixing-commit for testing!',
            'date': '06/10/2020 17:52',
            'repository': 'MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ=='
        }

        fixing_commits_before_create = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data

        response = self.client.post(
            reverse('api:fixing-commits-list'),
            data=json.dumps(valid_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        fixing_commits_after_create = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data
        self.assertGreater(len(fixing_commits_after_create), len(fixing_commits_before_create))

    def test_create_invalid_fixing_commit(self):
        invalid_payloads = [{
            # no sha passed
            'msg': 'This is a new fixing-commit for testing!',
            'date': '06/10/2020 17:52',
            'repository': 'MDEwOlJlcG9zaXRvcnkxNTk0MTM0NQ=='
        }, {
            'sha': '987654321',
            'msg': 'This is a new fixing-commit for testing!',
            'date': '06/10/2020 17:52'
            # no repository passed
        }, {
            'sha': '987654321',
            'msg': 'This is a new fixing-commit for testing!',
            'date': '06/10/2020 17:52',
            'repository': 'unexisting id'
        }]

        fixing_commits_before_create = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data

        for payload in invalid_payloads:
            response = self.client.post(
                reverse('api:fixing-commits-list'),
                data=json.dumps(payload),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        fixing_commits_after_create = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data
        self.assertEqual(fixing_commits_after_create, fixing_commits_before_create)

    def test_create_fixing_commit_conflict(self):
        """
        Try to create a fixing-commit with the same SHA of one already present in the database.
        :except: status.HTTP_409_CONFLICT
        """
        existing_payload = {'sha': '123456789'}
        fixing_commits_before_conflict = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data

        # here the conflict
        response = self.client.post(
            reverse('api:fixing-commits-list'),
            data=json.dumps(existing_payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        fixing_commits_after_conflict = FixingCommitSerializer(FixingCommit.objects.all(), many=True).data
        self.assertEqual(fixing_commits_after_conflict, fixing_commits_before_conflict)

    def test_patch_existing_fixing_commit(self):
        """
        Delete a repository from the database and compare the database before and after deleting.
        If the database differs, than the repository has been deleted
        """
        fixing_commit_before_patch = FixingCommit.objects.get(sha='123456789')
        serializer_before_patch = FixingCommitSerializer(fixing_commit_before_patch).data
        self.assertFalse(serializer_before_patch['is_false_positive'])

        response = self.client.patch(
            reverse('api:fixing-commits-detail', kwargs={'pk': '123456789'})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        fixing_commit_after_patch = FixingCommit.objects.get(sha='123456789')
        serializer_after_patch = FixingCommitSerializer(fixing_commit_after_patch).data
        self.assertTrue(serializer_after_patch['is_false_positive'])

    def test_patch_unexisting_fixing_commit(self):
        """
        Try to delete a repository that does not exist in the db.
        :except: HTTP_404_NOT_FOUND
        """
        response = self.client.patch(
            reverse('api:fixing-commits-detail', kwargs={'pk': 'ShANoTPrEsEnT'})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_existing_fixing_commit(self):
        """
        Delete a repository from the database and compare the database before and after deleting.
        If the database differs, than the repository has been deleted
        """
        fixing_commits_before_delete = FixingCommit.objects.all()
        serializer_before_delete = FixingCommitSerializer(fixing_commits_before_delete, many=True).data

        response = self.client.delete(
            reverse('api:fixing-commits-detail', kwargs={'pk': '123456789'})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        fixing_commits_after_delete = FixingCommit.objects.all()
        serializer_after_delete = FixingCommitSerializer(fixing_commits_after_delete, many=True).data

        self.assertLess(len(serializer_after_delete), len(serializer_before_delete))

    def test_delete_unexisting_fixing_commit(self):
        """
        Try to delete a repository that does not exist in the db.
        :except: HTTP_404_NOT_FOUND
        """
        response = self.client.delete(
            reverse('api:fixing-commits-detail', kwargs={'pk': 'ShANoTPrEsEnT'})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ================================== FIXING-FILES ==============================================================#
class FixingFilesTest(BaseViewTest):

    def test_get_all_fixing_files(self):
        """
        This test ensures that all fixing-files added in the setUp method exist when we make a GET request to the \
        fixing-files/ endpoint
        """
        # get API response
        response = self.client.get(reverse('api:fixing-files-list'))

        # get data from db
        fixing_files = FixingFile.objects.all()
        serializer = FixingFileSerializer(fixing_files, many=True)

        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fixing_commit_fixing_files(self):
        """
        This test ensures that the fixing-files belonging to a fixing-commit added in the setUp method exist when we \
        make a GET request to the fixing-files/ endpoint
        """
        # get API response
        response = self.client.get('%s?fixing_commit=%s' % (reverse('api:fixing-files-list'), self.fic1.sha))

        # get data from db
        fixing_files = FixingFile.objects.filter(fixing_commit=self.fic1.sha)
        serializer = FixingFileSerializer(fixing_files, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 3)

    def test_get_repository_commit_fixing_files(self):
        """
        This test ensures that the fixing-files belonging to a fixing-commit added in the setUp method exist when we \
        make a GET request to the fixing-files/ endpoint
        """
        # get API response
        response = self.client.get('%s?repository=%s' % (reverse('api:fixing-files-list'), self.repo1.id))

        # get data from db
        fixing_files = FixingFile.objects.filter(fixing_commit__repository=self.repo1.id)
        serializer = FixingFileSerializer(fixing_files, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 5)


    def test_get_fixing_files_invalid(self):
        """
        This test ensures that the passing both query parameters (fixing_commit and repository) to the GET request
        result in a HTTP_400_BAD_REQUEST
        """
        # get API response
        response = self.client.get('%s?fixing_commit=%s&repository=%s'
                                   % (reverse('api:fixing-files-list'), self.fic1.sha, self.repo1.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
