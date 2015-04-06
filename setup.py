from __future__ import print_function
from datetime import datetime
import subprocess
import fileinput
import json
import os


GITHUB_URL = 'https://api.github.com/user/repos'
DIR_PATH = ''

TYPE = {
    'START_DATE': 'When would you like to start logs? [YYYY-MM-DD] : ',
    'END_DATE': 'When would you like to end logs? [YYYY-MM-DD] : ',
    'HANDLE': 'What is your github handle: ',
    'NAME': 'Enter a name for your repository: ',
    'PRIVATE': 'Would you like it private or public: ',
    'TIME': 'What time would you like to be reminded?\nEnter time in a digital'
            ' format E.G. 13:45 : ',
    'BAD_GITHUB_CRED': 'Bad credentials',
}


def set_dir_path(repository_name):
    global DIR_PATH
    DIR_PATH = '{}/{}'.format(os.getcwd(), repository_name)


def get(key, invalid=True):
    value = raw_input(TYPE[key])
    while invalid(value):
        value = raw_input(TYPE[key])
    return value


def validate_private(value):
    value = value.lower()
    print(value)
    return value != 'private' and value != 'public'


def date(date):
    return datetime.strptime(date, '%Y-%m-%d')


def validate_date(d):
    try:
        date(d)
        return False
    except ValueError:
        return True


def time(time):
    return datetime.strptime(time, '%H:%M')


def validate_time(t):
    try:
        time(t)
        return False
    except ValueError:
        return True


def cron_job(minutes, hours, start_date, end_date, repository_name):
    cron_path = '{}/logjob.sh'.format(os.path.dirname(os.path.realpath
                                                      (__file__)))

    for line in fileinput.input(cron_path, inplace=True):
        print(line.replace('REPOSITORY_PATH', DIR_PATH).replace(
              'END_DATE', str(end_date)).replace(
              'START_DATE', str(start_date)), end='')

    timing_sequence = '{} {} * * 1-5'.format(minutes, hours)
    subprocess.check_call(['chmod', '+x', cron_path])
    cron = '"{} {}"'.format(timing_sequence, cron_path)

    # FIX THIS
    # c1 = ['crontab', '-l']
    # c2 = ['{', 'cat', ';', 'echo', cron, ';', '}']
    # c3 = ['crontab', '-']

    # p1 = subprocess.Popen(c1, shell=True, stdout=subprocess.PIPE)
    # p2 = subprocess.Popen(c2, shell=True, stdin=p1.stdout,
    #                       stdout=subprocess.PIPE)
    # p3 = subprocess.Popen(c3, shell=True, stdin=p2.stdout)
    # p3.communicate()

    cmd = 'crontab -l | {{ cat; echo {}; }} | crontab -'.format(cron)
    subprocess.check_call(cmd, shell=True)


def make_repo(handle, name, private):
    if private == 'private':
        private = True

    data = {
        'name': name,
        'private': private,
        'description': 'Internship daily log diary.'
    }
    cmd = ['curl', '-u', handle, '-d', json.dumps(data), GITHUB_URL]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout = json.loads(p.communicate()[0])

    if TYPE['BAD_GITHUB_CRED'] in stdout:
        print('Repository creation failed, please try again.')
        exit(0)

    cmd = ['git', 'clone', stdout['ssh_url']]
    subprocess.check_call(cmd)


def main():
    handle = raw_input(TYPE['HANDLE'])
    repo_name = raw_input(TYPE['NAME'])
    private = get('PRIVATE', validate_private)

    set_dir_path(repo_name)
    make_repo(handle, repo_name, private)

    start_date = date(get('START_DATE', validate_date))
    end_date = date(get('END_DATE', validate_date))
    hours, minutes = get('TIME', validate_time).split(':')

    cron_job(minutes, hours, start_date, end_date, repo_name)

    print('And you\'re done.')
    print('Goodbye')


if __name__ == '__main__':
    main()

# TODO: validate datetime correctly, fails on an enter press
# TODO: check git repo creation properly
# TODO: move the script to external location?
