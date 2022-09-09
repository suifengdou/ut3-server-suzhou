import inspect


def logging(obj, name, classlog, content):
    if inspect.isclass(classlog):
        record = classlog()
    else:
        return False
    record.obj = obj
    record.name = name
    record.content = content
    try:
        record.save()
    except Exception as e:
        return False
    return True


