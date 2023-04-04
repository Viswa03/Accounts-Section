# import requests
# from rest_framework.response import Response

# from .dynamic import dynamic_link


# def get_hostname(request) :
#     print(request.get_host())
#     return request.get_host().split(':')[0].lower()

# def get_tenant(request):
#     hostname=get_hostname(request)
#     subdomain=hostname.split('.')[0]
#     services='apigateway'
#     dynamic=dynamic_link(services,'apigateway/user/tenant'+ '/' + str(subdomain))
#     response=requests.get(dynamic).json()
#     print(response)
#     return response
#     # return User.objects.filter(tenant_company=subdomain)