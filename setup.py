from __future__ import print_function
from datetime import datetime
import subprocess
import fileinput
import json
import os
from urllib2 import urlopen, Request, HTTPError


GITHUB_URL = 'https://api.github.com/user/repos'
CRON_SCRIPT_FILE = 'logjob.sh'
GITHUB_ACCESS_TOKEN_URL = 'https://github.com/settings/applications'

TYPE = {
    'START_DATE': 'When would you like to start logs? [YYYY-MM-DD] : ',
    'END_DATE': 'When would you like to end logs? [YYYY-MM-DD] : ',
    'HANDLE': 'What is your github handle: ',
    'NAME': 'Enter a name for your repository: ',
    'PRIVATE': 'Would you like it private or public: ',
    'TIME': 'What time would you like to be reminded?\nEnter time in a digital'
            + ' format E.G. 13:45 : ',
    'BAD_GITHUB_CRED': 'Bad credentials',
    'ACCESS_TOKEN': 'If you have Github 2Factor enabled please enter your '
                    + 'access token now. See {}. If not just press enter.\n'
                    .format(GITHUB_ACCESS_TOKEN_URL) + 'Github access token: ',
}


def get_and_validate(key, invalidator, formattor):
    value = raw_input(TYPE[key])
    while invalidator(value):
        value = raw_input(TYPE[key])
    return formattor(value)


def private_formattor(value):
    return value == 'private'


def validate_private(value):
    value = value.lower()
    return value != 'private' and value != 'public'


def date_formattor(date):
    return datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d')


def validate_date(d):
    try:
        date_formattor(d)
        return False
    except ValueError:
        return True


def time_formattor(time):
    time = datetime.strptime(time, '%H:%M')
    return time.hour, time.minute


def validate_time(t):
    try:
        time_formattor(t)
        return False
    except ValueError:
        return True


def cron_job(minutes, hours, start_date, end_date, dir_path, repository_name):
    cron_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             CRON_SCRIPT_FILE)

    for line in fileinput.input(cron_path, inplace=True):
        print(line.replace('REPOSITORY_PATH', dir_path).replace(
              'END_DATE', str(end_date)).replace(
              'CRON_SCRIPT_FILE', CRON_SCRIPT_FILE).replace(
              'START_DATE', str(start_date)), end='')

    timing_sequence = '{} {} * * 1-5'.format(minutes, hours)
    subprocess.check_call(['chmod', '+x', cron_path])
    cron = '"{} {}"'.format(timing_sequence, cron_path)

    cmd = 'crontab -l | {{ cat; echo {}; }} | crontab -'.format(cron)
    subprocess.check_call(cmd, shell=True)


def make_repo(handle, name, private, access_token):
    data = {
        'name': name,
        'login': handle,
        'private': private,
        'description': 'Internship daily log diary.'
    }

    request = Request(GITHUB_URL, json.dumps(data))

    if access_token is not None:
        auth_token = 'token {}'.format(access_token)
        request.add_header("Authorization", auth_token)

    try:
        response = urlopen(request)
    except HTTPError, error:
        print(error.read())
        exit(0)

    response_data = json.loads(response.read())
    cmd = ['git', 'clone', response_data['ssh_url']]
    subprocess.check_call(cmd)


def main():
    handle = raw_input(TYPE['HANDLE'])
    repo_name = raw_input(TYPE['NAME'])
    access_token = raw_input(TYPE['ACCESS_TOKEN'])
    private = get_and_validate('PRIVATE', validate_private, private_formattor)

    make_repo(handle, repo_name, private, access_token)

    start_date = get_and_validate('START_DATE', validate_date, date_formattor)
    end_date = get_and_validate('END_DATE', validate_date, date_formattor)
    hours, minutes = get_and_validate('TIME', validate_time, time_formattor)

    dir_path = os.path.join(os.getcwd(), repo_name)
    cron_job(minutes, hours, start_date, end_date, dir_path, repo_name)

    print('And you\'re done.')
    print('Goodbye')


if __name__ == '__main__':
    main()
