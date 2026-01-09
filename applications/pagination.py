from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """Base pagination class with customizable response format."""
    page_size = 20
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data, key='items'):
        return Response({
            'success': True,
            'data': {
                key: data,
                'pagination': {
                    'currentPage': self.page.number,
                    'totalPages': self.page.paginator.num_pages,
                    'totalItems': self.page.paginator.count,
                    'limit': self.get_page_size(self.request)
                }
            }
        })


class ApplicantPagination(StandardResultsSetPagination):
    """Pagination for applicant list endpoints."""
    
    def get_paginated_response(self, data):
        return super().get_paginated_response(data, key='applicants')


class MemberPagination(StandardResultsSetPagination):
    """Pagination for member list endpoints."""
    
    def get_paginated_response(self, data):
        return super().get_paginated_response(data, key='members')


class ActivityLogPagination(StandardResultsSetPagination):
    """Pagination for activity log endpoints."""
    
    def get_paginated_response(self, data):
        return super().get_paginated_response(data, key='activities')
