from rest_framework import viewsets, mixins


class ListRetriveViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):

    pass
