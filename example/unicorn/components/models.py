from django.shortcuts import redirect
from django.utils.functional import cached_property

from django_unicorn.components import HashUpdate, LocationUpdate, UnicornView
from django_unicorn.db import DbModel
from django_unicorn.decorators import db_model
from example.coffee.models import Flavor


class ModelsView(UnicornView):
    flavors = Flavor.objects.none()

    # Demonstrates how to use an instantiated model; class attributes get stored on
    # the class, so django-unicorn handles clearing this with `_resettable_attributes_cache`
    # in components.py
    class_flavor: Flavor = Flavor()

    def __init__(self, **kwargs):
        # Demonstrates how to use an instance variable on the class
        self.instance_flavor = Flavor()

        # super() `has` to be called at the end
        super().__init__(**kwargs)

    def hydrate(self):
        # Using `hydrate` is the best way to make sure that QuerySets
        # are re-queried every time the component is loaded
        self.flavors = Flavor.objects.all().order_by("-id")[:2]

    def add_instance_flavor(self):
        self.instance_flavor.save()
        id = self.instance_flavor.id
        self.reset()

        # return HashUpdate(f"#createdId={id}")
        return LocationUpdate(redirect(f"/models?createdId={id}"), title="new title")

    def add_class_flavor(self):
        self.class_flavor.save()
        id = self.class_flavor.id
        self.reset()

        # Note: this can cause inputs to appear to be cached
        return redirect(f"/models?createdId={id}")

    @db_model
    def delete(self, model):
        model.delete()

    @cached_property
    def available_flavors(self):
        flavors = Flavor.objects.all()

        if self.instance_flavor and self.instance_flavor.pk:
            return flavors.exclude(pk=self.instance_flavor.pk)

        return flavors

    class Meta:
        db_models = [DbModel("flavor", Flavor)]
