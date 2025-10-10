from xdi_validator import validate
import json

invalid_xdi   = open("tests/wrong_fields.xdi", "r")

errors, data = validate(invalid_xdi)

if not len(errors):
    print(data)
    print("File invalid.xdi is VALID!")
else:
    print("invalid.xdi is INVALID!")
    print(json.dumps(errors, indent=2))
