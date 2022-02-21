import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIClient
from model_bakery import baker
import random

from students.models import Student, Course


def random_list_for_students(students_set, qty=10):
    students_id_set = [student.id for student in students_set]
    students_random_list = [random.choice(students_id_set) for i in range(random.randint(1, qty))]
    return students_random_list


def get_random_course_id(courses):
    courses_id_set = [course.id for course in courses]
    random_id = random.choice(courses_id_set)
    return random_id


def get_course_url_filtered_by(courses, param):
    if param == 'name':
        expected_name_set = [course.name for course in courses]
        random_param = random.choice(expected_name_set)
        queryset = Course.objects.prefetch_related('students').filter(name=random_param)
    else:
        random_param = get_random_course_id(courses)
        queryset = Course.objects.prefetch_related('students').filter(id=random_param)

    courses = []
    for course in queryset:
        students = [student.id for student in course.students.all()]
        courses.append({'id': course.id, 'name': course.name, 'students': students})
    url = f'{reverse("courses-list")}?{param}={random_param}'
    return courses, url


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.prepare(Student, *args, **kwargs)

    return factory


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


def insert_data_to_db(course_factory, student_factory, c_num=10, st_num=10):
    students_set = student_factory(_quantity=st_num)
    courses = course_factory(_quantity=c_num, students=students_set)
    return courses, students_set


@pytest.mark.django_db
def test_get_first_course(client, student_factory, course_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory, c_num=1, st_num=10)

    assert len(courses) == 1

    course = courses[0]
    students = [student.id for student in course.students.all()]
    course_input_data = {'id': course.id, 'name': course.name, 'students': students}
    url = f'{reverse("courses-list")}{course.id}/'
    resp = client.get(url)

    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()

    assert type(resp_json) is dict

    assert resp_json == course_input_data


@pytest.mark.django_db
def test_get_course_list(client, student_factory, course_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory, c_num=1, st_num=10)
    url = reverse("courses-list")
    resp = client.get(url)

    assert resp.status_code == HTTP_200_OK

    resp_json = resp.json()

    assert len(resp_json) == len(courses)

    result_ids_set = [result['id'] for result in resp_json]
    expected_ids_set = [course.id for course in courses]

    assert result_ids_set == expected_ids_set


@pytest.mark.django_db
def test_filter_name(client, student_factory, course_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory)
    courses, url = get_course_url_filtered_by(courses, 'name')
    request = client.get(url)

    assert request.status_code == HTTP_200_OK

    assert courses == request.json()


@pytest.mark.django_db
def test_filter_id(client, student_factory, course_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory)
    courses, url = get_course_url_filtered_by(courses, 'id')
    request = client.get(url)

    assert request.status_code == HTTP_200_OK

    assert courses == request.json()


@pytest.mark.django_db
def test_create_new(client):
    students_set = baker.make(Student, _quantity=10)
    students_random_list = random_list_for_students(students_set, qty=10)
    name_data = 'test_course'
    data = {'name': name_data, 'students': students_random_list}
    url = reverse("courses-list")
    request = client.post(url, data)

    assert request.status_code == 201

    url_check = f'{reverse("courses-list")}?name={name_data}'
    request_check = client.get(url_check)

    assert request_check.status_code == 200

    assert len(request_check.json()) == 1

    assert request.json() == request_check.json()[0]





@pytest.mark.django_db
def test_put(client, student_factory, course_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory)
    students_random_list = random_list_for_students(students_set, qty=10)
    random_id = get_random_course_id(courses)
    url = f'{reverse("courses-list")}{random_id}/'
    name_data = 'random_data'
    data = {'name': name_data, 'students': students_random_list}

    data_before = client.get(url)
    assert data_before.status_code == 200


    request = client.put(url, data)
    assert request.status_code == 200

    url_after = f'{reverse("courses-list")}?name={name_data}'
    data_after = client.get(url_after)
    assert data_after.status_code == 200

    assert len(data_after.json()) == 1

    assert data_after.json()[0] == request.json()

    assert data_after.json()[0] != data_before.json()


@pytest.mark.django_db
def test_delete(client, course_factory, student_factory):
    courses, students_set = insert_data_to_db(course_factory, student_factory)
    random_course_id = get_random_course_id(courses)
    url = reverse("courses-list")
    url2 = f'{url}{random_course_id}/'
    request = client.delete(url2)

    assert request.status_code == 204

    request_after = client.get(url2)

    assert request_after.status_code == 404

    request_data = client.get(url).json()
    courses_id_after_delete = [request['id'] for request in request_data]

    assert random_course_id not in courses_id_after_delete
