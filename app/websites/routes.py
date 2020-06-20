from flask import render_template
from app.websites import bp


@bp.route('/showcase', methods=['GET'])
def showcase():
    return render_template('websites.html')
