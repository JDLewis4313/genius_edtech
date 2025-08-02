from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def elements_api(request):
    return Response({'message': 'Elements API placeholder'})

@api_view(['GET'])
def element_detail_api(request, pk):
    return Response({'message': f'Detail for element {pk}'})
