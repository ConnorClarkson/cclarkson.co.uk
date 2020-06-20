import time
import boto3
from datetime import datetime, timezone
from boto3.dynamodb.conditions import Key, Attr
from flask_login import current_user, login_user, logout_user, login_required
from flask import redirect, url_for, render_template, request, flash, current_app
from werkzeug.urls import url_parse
from app.auth import bp
from app.auth.forms import LoginForm, ChangePasswordForm, EditEvent, NewEvent

CURRENT_USER = None


@current_app.login_manager.user_loader
def load_user(id):
    if CURRENT_USER and CURRENT_USER.id == id:
        return CURRENT_USER
    return None


class Cog_User:
    def __init__(self, is_active, is_authenticated, username, access_token, id_token, token_type):
        if 'admin' in username:
            self.id = 1
        else:
            self.id = 2
        self.is_active = is_active
        self.is_authenticated = is_authenticated
        self.username = username
        self.access_token = access_token
        self.id_token = id_token
        self.token_type = token_type

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def get_id(self):
        return self.id


@bp.route('/login', methods=['GET', 'POST'])
def login():
    global CURRENT_USER
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    l_form = LoginForm()
    c_form = ChangePasswordForm()
    client = boto3.client('cognito-idp', region_name=current_app.config['AWS_DEFAULT_REGION'],
                          aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'])
    # Login page logic
    if l_form.validate_on_submit():
        result = request.form.to_dict()
        try:
            tokens = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                          ClientId=current_app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'],
                                          AuthParameters={'USERNAME': result['username'],
                                                          'PASSWORD': result['password']})
            if 'ChallengeName' in tokens:
                if tokens['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                    c_form = ChangePasswordForm()
                    c_form.username.data = result['username']
                    return render_template('login.html', title='Sign In', type='Change', form=c_form)

            CURRENT_USER = Cog_User(is_active=True, is_authenticated=True, username=result['username'],
                                    access_token=tokens['AuthenticationResult']['AccessToken'],
                                    id_token=tokens['AuthenticationResult']['IdToken'],
                                    token_type=tokens['AuthenticationResult']['TokenType'])
            login_user(CURRENT_USER)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('auth.admin')
            return redirect(next_page)

        except client.exceptions.UserNotFoundException:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        except client.exceptions.PasswordResetRequiredException as PSRE:
            c_form.username.data = result['username']
            return render_template('login.html', title='Sign In', type='Change', form=c_form)
        except client.exceptions.NotAuthorizedException as NAE:
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash('Please try again.', 'error')
            return redirect(url_for('auth.login'))

    # Change password logic
    elif c_form.validate_on_submit():
        result = request.form.to_dict()
        if result['new_password'] != result['confirm_password']:
            flash('Invalid username or password', 'error')
            return render_template('login.html', title='Sign In', type='Change', form=c_form)
        try:
            access_token = None
            tokens = client.initiate_auth(AuthFlow='USER_PASSWORD_AUTH',
                                          ClientId=current_app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'],
                                          AuthParameters={'USERNAME': result['username'],
                                                          'PASSWORD': result['prev_password']})
            if 'ChallengeName' in tokens:
                if tokens['ChallengeName'] == 'NEW_PASSWORD_REQUIRED':
                    response = client.respond_to_auth_challenge(
                        ClientId=current_app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'],
                        ChallengeName=tokens['ChallengeName'],
                        Session=tokens['Session'],
                        ChallengeResponses={'NEW_PASSWORD': result['new_password'],
                                            'USERNAME': result['username']})
                    access_token = response['AuthenticationResult']['AccessToken']

            if access_token:
                CURRENT_USER = Cog_User(is_active=True, is_authenticated=True, username=result['username'],
                                        access_token=tokens['AuthenticationResult']['AccessToken'],
                                        id_token=tokens['AuthenticationResult']['IdToken'],
                                        token_type=tokens['AuthenticationResult']['TokenType'])
                login_user(CURRENT_USER)
                next_page = request.args.get('next')
                if not next_page or url_parse(next_page).netloc != '':
                    next_page = url_for('auth.admin')
                return redirect(next_page)
            else:
                flash('Contact Admin to change Password!', 'error')
                return render_template('login.html', title='Sign In', type='Change', form=c_form)
        except client.exceptions.InvalidPasswordException:
            flash('Invalid Password!', 'error')
            return render_template('login.html', title='Sign In', type='Change', form=c_form)
        except Exception as e:
            flash('Unable to update Password!', 'error')
            return render_template('login.html', title='Sign In', type='Change', form=c_form)

    return render_template('login.html', title='Sign In', type='Login', form=l_form)


TOTAL_ITEMS = 0


@bp.route('/admin')
@login_required
def admin():
    events = None
    response = current_app.config['DYNAMO_TABLE'].query(
        KeyConditionExpression=Key('event_id').eq(0))
    if len(response['Items']) > 0:
        events = response['Items']
        global TOTAL_ITEMS
        if events:
            TOTAL_ITEMS = len(events)
        else:
            TOTAL_ITEMS = 0
    return render_template('admin.html', events=events)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/new_event', methods=['POST', 'GET'])
@login_required
def new_event():
    if request.method == 'POST':

        result = request.form.to_dict()
        response = current_app.config['DYNAMO_TABLE'].query(
            KeyConditionExpression=Key('event_id').eq(0))
        on_the_door = True if 'on_the_door' in result else False
        sold_out = True if 'sold_out' in result else False

        if response and len(response['Items']) + 1 > int(result['id']):
            current_event_count = len(response) + 1
        else:
            current_event_count = result['id']

        date = datetime.strptime(result['date'], "%Y-%m-%d %H:%M")
        date.replace(tzinfo=timezone.utc)
        epoch_time = int((date - datetime(1970, 1, 1)).total_seconds())
        # TODO add error handling
        current_app.config['DYNAMO_TABLE'].put_item(Item={
            'event_id': 0,
            'timestamp': epoch_time,
            'id': int(current_event_count),
            'venue': result['venue'],
            'link': result['link'] if result['link'] != '' else 'None',
            'on_the_door': on_the_door,
            'sold_out': sold_out
        })
        flash("Successfully added new event!", 'success')
        return redirect(url_for('auth.admin'))
    else:
        edit_form = NewEvent()
        edit_form.id.data = TOTAL_ITEMS + 1
        edit_form.date.data = int(time.time())
        edit_form.venue.data = ''
        edit_form.link.data = ''
        return render_template('edit_events.html', form=edit_form, title="New Item")


@bp.route('/edit_event/<int:id>', methods=['POST', 'GET'])
@login_required
def edit_event(id):
    if request.method == 'POST':
        result = request.form.to_dict()
        on_the_door = True if 'on_the_door' in result else False
        sold_out = True if 'sold_out' in result else False

        orig_date = datetime(1970, 1, 1)
        date = datetime.strptime(result['date'], "%Y-%m-%d %H:%M")
        if '/' in result['orig_date']:
            orig_date = datetime.strptime(result['orig_date'], "%d/%m/%Y %H:%M")
        elif '-' in result['orig_date']:
            orig_date = datetime.strptime(result['orig_date'], "%Y-%m-%d %H:%M")

        epoch_time = int((date - datetime(1970, 1, 1)).total_seconds())
        original_epoch = int((orig_date - datetime(1970, 1, 1)).total_seconds())
        current_app.config['DYNAMO_TABLE'].delete_item(Key={
            'event_id': 0,
            'timestamp': original_epoch,
        },
            ConditionExpression="id = :val",
            ExpressionAttributeValues={
                ":val": int(result['id'])
            })
        if 'submit' in request.form and request.form['submit'] == "Save":
            current_app.config['DYNAMO_TABLE'].put_item(Item={
                'event_id': 0,
                'timestamp': epoch_time,
                'id': int(result['id']),
                'venue': result['venue'],
                'link': result['link'],
                'on_the_door': on_the_door,
                'sold_out': sold_out
            })
            flash(f"Successfully Updated event {result['venue']}!", 'success')
        else:
            flash(f"Successfully Deleted event {result['venue']}!", 'success')
        return redirect(url_for('auth.admin'))
    else:
        response = current_app.config['DYNAMO_TABLE'].query(
            KeyConditionExpression=Key('event_id').eq(0) & Key('timestamp').gt(0),
            FilterExpression=Attr('id').eq(str(id)))
        item = None

        if not response['Items']:
            response = current_app.config['DYNAMO_TABLE'].query(
                KeyConditionExpression=Key('event_id').eq(0) & Key('timestamp').gt(0))

        events = response['Items']
        for e in events:
            if int(e['id']) == id:
                item = e
                break

        if item:
            edit_form = EditEvent()
            edit_form.id.data = int(item['id'])
            edit_form.orig_date.data = item['timestamp']
            edit_form.date.data = item['timestamp']
            edit_form.venue.data = item['venue']
            edit_form.link.data = item['link']
            edit_form.on_the_door.data = item['on_the_door']
            edit_form.sold_out.data = item['sold_out']
            return render_template('edit_events.html', form=edit_form, title="Edit Item")
        else:
            flash("Unable to Edit", "error")
            return redirect(url_for('auth.admin'))
