from flask import jsonify

def success_response(data=None, message="Success", status_code=200):
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(errors, message="Error", status_code=400):
    return jsonify({"message": message, "errors": errors}), status_code
