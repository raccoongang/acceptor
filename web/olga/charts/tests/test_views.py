"""
Tests for charts views.
"""

import json
from datetime import datetime

from mock import patch

from django.test import TestCase

from olga.analytics.models import InstallationStatistics
from olga.charts.views import (
    get_data_created_datetime_scope,
    GraphsView,
    MapView
)

# pylint: disable=invalid-name


class TestMapView(TestCase):
    """
    Tests for map view, that contains world map statistics functionality.
    """

    def setUp(self):
        """
        Set up common response.
        """
        self.response = self.client.get('/map/')

    def test_map_url(self):
        """
        Verify that map url resolves to map view.
        """
        self.assertEqual(self.response.resolver_match.func.__name__, MapView.__name__)

    def test_map_view_status_code(self):
        """
        Verify that map view returns status 200 (ok) after get request to map url.
        """
        self.assertEqual(self.response .status_code, 200)

    def test_map_view_html(self):
        """
        Verify that map view uses correct html-template after get request to map url.
        """
        self.assertTemplateUsed(self.response, 'charts/worldmap.html')

    def test_top_country(self):
        """
        Verify that get_statistics_top_country method returns top country if tabular format countries list exists.

        Actually before using get_statistics_top_country method server sorts tabular format countries list
        in descending order, that means first element is top value.
        """
        tabular_format_countries_list = [['Canada', 66, '20'], ['United States', 33, '10']]

        result = InstallationStatistics.get_statistics_top_country(tabular_format_countries_list)

        self.assertEqual('Canada', result)


@patch('olga.analytics.models.InstallationStatistics.objects.aggregate')
class TestViewsHelpFunctions(TestCase):
    """
    Tests for charts help functions.
    """

    def test_update_datetime_if_data_exists(self, mock_installation_statistics_model_objects_aggregate):
        """
        Verify that get_first_and_last_datetime_of_update_data method returns first and last objects datetime.
        """
        mock_min_datetime_of_update_data = datetime(2017, 6, 1, 14, 56, 18)
        mock_max_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_installation_statistics_model_objects_aggregate.return_value = {
            'data_created_datetime__min': mock_min_datetime_of_update_data,
            'data_created_datetime__max': mock_max_datetime_of_update_data
        }

        result = get_data_created_datetime_scope()

        self.assertEqual(
            (mock_min_datetime_of_update_data, mock_max_datetime_of_update_data), result
        )

    @patch('olga.charts.views.datetime')
    def test_update_datetime_if_no_data(
            self, mock_datetime, mock_installation_statistics_model_objects_aggregate
    ):
        """
        Verify that get_first_and_last_datetime_of_update_data method returns `datetime.now` if no objects.
        """
        mock_first_datetime_of_update_data = mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_datetime.now.return_value = mock_first_datetime_of_update_data

        mock_installation_statistics_model_objects_aggregate.return_value = {
            'data_created_datetime__min': None,
            'data_created_datetime__max': None
        }

        result = get_data_created_datetime_scope()

        self.assertEqual(
            (mock_first_datetime_of_update_data, mock_last_datetime_of_update_data), result
        )


class TestGraphsView(TestCase):
    """
    Tests for map view, that contains graphs statistics functionality.
    """

    def setUp(self):
        """
        Set up common response.
        """
        self.response = self.client.get('/')

    def test_graphs_url(self):
        """
        Verify that graphs url resolves to graphs view.
        """
        self.assertEqual(self.response.resolver_match.func.__name__, GraphsView.__name__)

    def test_graphs_view_status_code(self):
        """
        Verify that graphs view returns status 200 (ok) after get request to graphs url.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_graphs_view_html(self):
        """
        Verify that graphs view uses correct html-template after get request to graphs url.
        """
        self.assertTemplateUsed(self.response, 'charts/graphs.html')

    @patch('olga.charts.views.get_data_created_datetime_scope')
    @patch('olga.analytics.models.InstallationStatistics.timeline')
    @patch('olga.analytics.models.InstallationStatistics.data_per_period')
    @patch('olga.analytics.models.InstallationStatistics.overall_counts')
    def test_map_view_context_fields_values(
            self,
            mock_installation_statistics_model_overall_counts,
            mock_installation_statistics_model_data_per_period,
            mock_installation_statistics_model_timeline,
            mock_get_data_created_datetime_scope
    ):  # pylint: disable=too-many-locals
        """
        Verify that graphs view render correct context fields values.
        """
        mock_timeline = ['2017-05-14', '2017-05-15', '2017-05-16']
        mock_students, mock_courses, mock_instances = [4124, 5122, 6412], [110, 211, 167], [30, 20, 25]
        mock_instances_count, mock_courses_count, mock_students_count, mock_certificates_count = 6412, 167, 25, 0
        mock_first_datetime_of_update_data = datetime(2017, 6, 1, 14, 56, 18)
        mock_last_datetime_of_update_data = datetime(2017, 7, 2, 23, 12, 8)

        mock_installation_statistics_model_timeline.return_value = mock_timeline

        mock_installation_statistics_model_data_per_period.return_value = mock_students, mock_courses, mock_instances

        mock_installation_statistics_model_overall_counts.return_value = {
            "instances_count": 6412,
            "courses_count": 167,
            "students_count": 25,
            "generated_certificates_count": 0,
        }

        mock_get_data_created_datetime_scope.return_value = \
            mock_first_datetime_of_update_data, mock_last_datetime_of_update_data

        response = self.client.get('/')

        self.assertEqual(json.loads(response.context['timeline']), mock_timeline)
        self.assertEqual(json.loads(response.context['students']), mock_students)
        self.assertEqual(json.loads(response.context['courses']), mock_courses)
        self.assertEqual(json.loads(response.context['instances']), mock_instances)
        self.assertEqual(response.context['instances_count'], mock_instances_count)
        self.assertEqual(response.context['students_count'], mock_students_count)
        self.assertEqual(response.context['courses_count'], mock_courses_count)
        self.assertEqual(response.context['generated_certificates_count'], mock_certificates_count)
        self.assertEqual(response.context['first_datetime_of_update_data'], mock_first_datetime_of_update_data)
        self.assertEqual(response.context['last_datetime_of_update_data'], mock_last_datetime_of_update_data)
