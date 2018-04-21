import string
import random

from rest_framework.viewsets import GenericViewSet

from prehab.helpers.HttpException import HttpException
from prehab.helpers.HttpResponseHandler import HTTP
from prehab.helpers.SchemaValidator import SchemaValidator
from prehab_app.models import Role
from prehab_app.models.Doctor import Doctor
from prehab_app.models.User import User
from prehab_app.serializers.Doctor import DoctorSerializer


class DoctorViewSet(GenericViewSet):

    def list(self, request):
        try:
            # In case it's an Admin and Doctors(need confirmation[security reasons]) -> Retrieve ALL doctors info
            if request.ROLE_ID == 1 and request.ROLE_ID == 2:
                queryset = self.paginate_queryset(Doctor.objects.all())
            else:
                raise HttpException(400, 'Some error occurred')
        except HttpException as e:
            return HTTP.response(e.http_code, e.http_detail)
        except Exception as e:
            return HTTP.response(400, 'Some error occurred')

        data = DoctorSerializer(queryset, many=True).data

        return HTTP.response(200, '', data=data, paginator=self.paginator)

    @staticmethod
    def retrieve(request, pk=None):
        try:
            doctor = Doctor.objects.get(id=pk)
            # In case it's not Admin -> fails
            if request.ROLE_ID != 1:
                raise HttpException(401, 'You don\t have permission to access this Doctor Information')

            data = DoctorSerializer(doctor, many=False).data

        except Doctor.DoesNotExist:
            return HTTP.response(404, 'Doctor with id {} does not exist'.format(str(pk)))
        except HttpException as e:
            return HTTP.response(e.http_code, e.http_detail)
        except Exception as e:
            return HTTP.response(400, 'Some error occurred')

        return HTTP.response(200, '', data)

    @staticmethod
    def create(request):
        try:
            # 1. Check schema
            SchemaValidator.validate_obj_structure(request.data, 'doctor/create.json')

            # 2. Add new User
            new_user = User(
                name=request.data['name'] if 'name' in request.data else None,
                username=request.data['username'],
                email=request.data['email'],
                phone=request.data['phone'] if 'phone' in request.data else None,
                password=request.data['password'],
                role=Role.objects.doctor_role().get(),
                activation_code=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)),
                is_active=True,
            )
            new_user.save()

            # 3 Create new Doctor
            doctor = Doctor(
                id=new_user,
                department=request.data['department'] if 'department' in request.data else None
            )
            doctor.save()

        except HttpException as e:
            return HTTP.response(e.http_code, e.http_detail)
        except Exception as e:
            return HTTP.response(400, str(e))

        return HTTP.response(200, 'New doctor account created sucessfully')

    @staticmethod
    def update(request, pk=None):
        return HTTP.response(405, '')

    @staticmethod
    def destroy(request, pk=None):
        return HTTP.response(405, '')