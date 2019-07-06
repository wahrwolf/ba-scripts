def parse_floats_from_dict(data):
    for k, v in data.items():
        try:
            v = float(v)
        except ValueError as err:
            print(err)
            pass
        finally:
            yield k, v

