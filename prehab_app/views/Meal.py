from django.db import transaction
from rest_framework.viewsets import GenericViewSet

from prehab.helpers.HttpException import HttpException
from prehab.helpers.HttpResponseHandler import HTTP
from prehab.helpers.SchemaValidator import SchemaValidator
from prehab_app.models import ConstraintType
from prehab_app.models.Meal import Meal
from prehab.permissions import Permission
from prehab_app.models.MealConstraintType import MealConstraintType
from prehab_app.serializers.Meal import MealSerializer


class MealViewSet(GenericViewSet):

    def list(self, request):
        try:
            queryset = self.paginate_queryset(Meal.objects.all())
            data = MealSerializer(queryset, many=True).data
        except HttpException as e:
            return HTTP.response(e.http_code, e.http_custom_message, e.http_detail)
        except Exception as e:
            return HTTP.response(400, 'Ocorreu um erro inesperado',
                                 'Unexpected Error. {}. {}.'.format(type(e).__name__, str(e)))

        return HTTP.response(200, '', data=data, paginator=self.paginator)

    @staticmethod
    def retrieve(request, pk=None):
        try:
            meal = Meal.objects.get(pk=pk)

        except Meal.DoesNotExist:
            return HTTP.response(404, 'Refeição não encontrada.', 'Meal with id {} not found.'.format(str(pk)))
        except ValueError:
            return HTTP.response(404, 'Url com formato inválido.', 'Invalid URL format. {}'.format(str(pk)))
        except HttpException as e:
            return HTTP.response(e.http_code, e.http_custom_message, e.http_detail)
        except Exception as e:
            return HTTP.response(400, 'Ocorreu um erro inesperado',
                                 'Unexpected Error. {}. {}.'.format(type(e).__name__, str(e)))

        data = MealSerializer(meal, many=False).data
        return HTTP.response(200, data=data)

    @staticmethod
    def create(request):
        try:
            if not Permission.verify(request, ['Admin']):
                raise HttpException(401,
                                    'Não tem permissões para aceder a este recurso.',
                                    'You don\'t have access to this resource.')

            data = request.data
            # 1. Check schema
            SchemaValidator.validate_obj_structure(data, 'meal/create.json')

            # 2. Check if meal type is available
            if not any(data['meal_type_id'] in meal_type for meal_type in Meal.meal_types):
                raise HttpException(400, 'Tipo de refeição não existe.', 'Meal Type does not exist.')

            with transaction.atomic():
                new_meal = Meal(
                    title=data['title'],
                    description=data.get('description', None),
                    multimedia_link=data.get('multimedia_link', None),
                    meal_type=data['meal_type_id']
                )
                new_meal.save()

                # Insert constraint types
                for constraint_type_id in data['constraint_types']:
                    constraint_type = ConstraintType.objects.get(pk=constraint_type_id)
                    meal_constraint_type = MealConstraintType(
                        meal=new_meal,
                        constraint_type=constraint_type
                    )
                    meal_constraint_type.save()

        except ConstraintType.DoesNotExist:
            return HTTP.response(404, 'Restrição alimentar not found.', 'Constraint not found.')
        except HttpException as e:
            return HTTP.response(e.http_code, e.http_custom_message, e.http_detail)
        except Exception as e:
            return HTTP.response(400, 'Ocorreu um erro inesperado',
                                 'Unexpected Error. {}. {}.'.format(type(e).__name__, str(e)))

        # Send Response
        data = {
            'meal_id': new_meal.id
        }
        return HTTP.response(201, 'Meal criada com sucesso.', data)

    @staticmethod
    def update(request, pk=None):
        return HTTP.response(405)

    @staticmethod
    def destroy(request, pk=None):
        return HTTP.response(405)
