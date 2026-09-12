def total(quantity):
    if type(quantity) is not int or quantity < 0:
        raise ValueError('quantity')
    return quantity * 10
