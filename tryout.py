from app.models import Computed

val: Computed = Computed(fn=lambda x: x * x)

match val:
    case str():
        print('string type')
    case int():
        print('integer type')
    case dict():
        print('dictionary type')
    case float():
        print('float type')
    case Computed():
        print('computed type')


