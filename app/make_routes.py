
from flask import render_template, request


def define_routes(config, module):
    def routes():
        # request.form()

        if request.method == "GET":
            returned_value =module("GET")
            return render_template(config['Template'], returned_value=returned_value)
        elif request.method == "POST":
            returned_colour = request.form.get('color_picker')
            returned_value = module("POST", returned_colour)
            return render_template(config['Template'], color=returned_colour, returned_value=returned_value)

        return render_template(config['Template'])
    return routes
