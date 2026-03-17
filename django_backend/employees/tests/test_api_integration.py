import base64
from unittest.mock import patch

import cv2
import numpy as np
from django.conf import settings
from django.test import TestCase
from django.test import override_settings

from employees.models import Employee, FaceEmbedding


TEST_MIDDLEWARE = [
    item
    for item in settings.MIDDLEWARE
    if item != 'whitenoise.middleware.WhiteNoiseMiddleware'
]


@override_settings(MIDDLEWARE=TEST_MIDDLEWARE)
class ApiIntegrationTests(TestCase):
    def setUp(self):
        self.client.defaults['CONTENT_TYPE'] = 'application/json'

    def _image_b64(self):
        frame = np.zeros((64, 64, 3), dtype=np.uint8)
        ok, encoded = cv2.imencode('.jpg', frame)
        self.assertTrue(ok)
        return base64.b64encode(encoded.tobytes()).decode('utf-8')

    def _create_employee_with_embedding(self, emp_id='001', name='Alice', vector=None):
        if vector is None:
            vector = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        employee = Employee.objects.create(emp_id=emp_id, name=name, is_active=True)
        emb = FaceEmbedding(employee=employee)
        emb.set_embedding(vector)
        emb.save()
        return employee

    @patch('employees.views.get_engine')
    def test_register_employee_image_success(self, mock_get_engine):
        mock_engine = mock_get_engine.return_value
        mock_engine.detect_and_embed.return_value = np.array([0.1, 0.2, 0.3], dtype=np.float32)

        response = self.client.post(
            '/api/register-employee-image/',
            data={
                'name': 'Novo Funcionario',
                'image_base64': self._image_b64(),
                'threshold': 0.40,
            },
            content_type='application/json',
            HTTP_X_ADMIN_PASSWORD='Admin123',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['employee']['name'], 'Novo Funcionario')
        self.assertTrue(Employee.objects.filter(name='Novo Funcionario').exists())
        self.assertEqual(FaceEmbedding.objects.count(), 1)

    def test_register_employee_image_invalid_admin_password(self):
        response = self.client.post(
            '/api/register-employee-image/',
            data={
                'name': 'Sem Permissao',
                'image_base64': self._image_b64(),
            },
            content_type='application/json',
            HTTP_X_ADMIN_PASSWORD='Errada',
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['error_code'], 'invalid_admin_password')

    @patch('employees.views.get_engine')
    def test_register_employee_image_duplicate_face(self, mock_get_engine):
        duplicate_vector = np.array([0.3, 0.2, 0.1], dtype=np.float32)
        self._create_employee_with_embedding(emp_id='001', name='Funcionario Existente', vector=duplicate_vector)

        mock_engine = mock_get_engine.return_value
        mock_engine.detect_and_embed.return_value = duplicate_vector

        response = self.client.post(
            '/api/register-employee-image/',
            data={
                'name': 'Duplicado',
                'image_base64': self._image_b64(),
                'threshold': 0.40,
            },
            content_type='application/json',
            HTTP_X_ADMIN_PASSWORD='Admin123',
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(data['error_code'], 'duplicate_face')
        self.assertEqual(data['employee']['name'], 'Funcionario Existente')

    @patch('employees.views.get_engine')
    def test_recognize_image_success(self, mock_get_engine):
        known_vector = np.array([0.9, 0.1, 0.1], dtype=np.float32)
        employee = self._create_employee_with_embedding(emp_id='123', name='Funcionario Reconhecido', vector=known_vector)

        mock_engine = mock_get_engine.return_value
        mock_engine.detect_and_embed.return_value = known_vector

        response = self.client.post(
            '/api/recognize-image/',
            data={
                'image_base64': self._image_b64(),
                'threshold': 0.40,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['recognized'])
        self.assertEqual(data['employee']['id'], employee.id)

    def test_register_log_invalid_mode_returns_400(self):
        Employee.objects.create(emp_id='777', name='Funcionario Log', is_active=True)

        response = self.client.post(
            '/api/register-log/',
            data={
                'emp_id': '777',
                'mode': 'invalido',
                'confidence': 0.55,
            },
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('mode', data)
