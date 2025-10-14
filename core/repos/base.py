
class BaseRepository:
    model = None

    def __init__(self, model=None):
        if model:
            self.model = model
        if self.model is None:
            raise ValueError("Repository must have a model")

    def get_all(self, **filters):
        return self.model.objects.filter(**filters)

    def get_by_id(self, pk):
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs):
        instance = self.model.objects.create(**kwargs)
        return instance

    def update(self, pk, **kwargs):
        obj = self.get_by_id(pk)
        if not obj:
            return None
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()
        return obj

    def delete(self, pk):
        obj = self.get_by_id(pk)
        if not obj:
            return False
        obj.delete()
        return True
