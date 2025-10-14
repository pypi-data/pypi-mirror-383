# from dataclasses import dataclass, field
# from typing import List, Optional

# # import marshmallow_dataclass
# # import marshmallow.validate


# @dataclass
# class Building:
#     # field metadata is used to instantiate the marshmallow field
#     height: float = field(metadata={"validate": marshmallow.validate.Range(min=0)})
#     name: str = field(default="anonymous")


# @dataclass
# class City:
#     name: Optional[str]
#     buildings: List[Building] = field(default_factory=list)


# city_schema = marshmallow_dataclass.class_schema(City)()

# city = city_schema.load(
#     {"name": "Paris", "buildings": [{"name": "Eiffel Tower", "height": 324}]}
# )
# # => City(name='Paris', buildings=[Building(height=324.0, name='Eiffel Tower')])

# city_dict = city_schema.dump(city)
# # => {'name': 'Paris', 'buildings': [{'name': 'Eiffel Tower', 'height': 324.0}]}