from rest_framework.test import APITestCase


class AnalyticsJobAPITests(APITestCase):
    def test_create_and_retrieve_job(self):
        create_resp = self.client.post('/v1/analytics/jobs', {'sql_query': 'SELECT 1'}, format='json')
        self.assertEqual(create_resp.status_code, 201)
        job_id = create_resp.data['id']

        get_resp = self.client.get(f'/v1/analytics/jobs/{job_id}')
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.data['status'], 'completed')
        self.assertTrue(get_resp.data['result_s3_uri'].startswith('s3://'))
