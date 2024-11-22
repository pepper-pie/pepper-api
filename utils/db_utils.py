from django.db.models.expressions import Func

class Round(Func):
    # ref: https://stackoverflow.com/a/55905983/5132337
    function = 'ROUND'
    arity = 2
    arg_joiner = '::numeric, '