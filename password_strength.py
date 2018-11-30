import argparse
import re
from datetime import datetime
import os

DEFAULT_BLACK_LIST = ('123456', '123456789', '111111',
                      'password', 'qwerty', 'abc123', '12345678',
                      'password1', '1234567', '123123',)

def validate_date(input_string):
    try:
        datetime.strptime(input_string, "%d.%m.%y")
        return input_string.split('.')
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(input_string)
        raise argparse.ArgumentTypeError(msg)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Test your password reliability'
    )
    parser.add_argument('password', type=str, help='input password')
    parser.add_argument(
        '-fn', '--first_name',
        type=str,
        help='user first name',
        default=None
    )
    parser.add_argument(
        '-ln', '--last_name',
        type=str,
        help='user last name',
        default=None
    )
    parser.add_argument(
        '-bd', '--birthday',
        type=validate_date,
        help='user birthday in format dd.mm.yy',
        default=[]
    )
    parser.add_argument(
        '-c', '--company',
        type=str,
        default=None,
        help='company name or abbreviation'
    )
    parser.add_argument(
        '-e', '--email',
        type=str,
        help='user email',
        default=None
    )
    parser.add_argument(
        '-bl', '--black_list',
        type=str,
        default=None,
        help='path to text file with password black list'
    )
    return parser.parse_args()


def join_personal_info(data_list):
    personal_info = [element for element in data_list if element is not None]
    if len(personal_info):
        return personal_info


def count_number_of_symbols_types(password):
    number_of_types = sum([
        bool(re.search('\d', password)),
        bool(re.search('[a-z]', password)),
        bool(re.search('[A-Z]', password)),
        bool(re.search('[а-я]', password)),
        bool(re.search('[А-Я]', password)),
        bool(re.search('\W', password))
    ])
    return number_of_types


def check_entry_in_extended_black_list(password, filename_black_list):
    with open(filename_black_list, 'r') as file_object:
        str_data = file_object.read()
    black_list = str_data.split('\n')
    if password in black_list:
        return True
    return False


def check_entry_of_personal_info(password, personal_info):
    entry = False
    for word in personal_info:
        entry = bool(re.search(word.lower(), password.lower()))
    return entry


def get_password_strength(password, personal_info, filename_black_list,
                          min_strength=1, max_strength=10):
    password_strength = sum([
        1,
        int(len(password) > 8),
        int(len(password) > 12),
        count_number_of_symbols_types(password)
    ])
    if password in DEFAULT_BLACK_LIST:
        return 0
    password_strength += 1
    if filename_black_list is not None and \
            check_entry_in_extended_black_list(password, filename_black_list):
        return 0
    password_strength += 1
    if personal_info is not None:
        if check_entry_of_personal_info(password, personal_info):
            password_strength += -3
        else:
            password_strength += 1
    password_strength = max(password_strength, min_strength)
    password_strength = min(password_strength, max_strength)
    return password_strength


if __name__ == '__main__':
    args = parse_arguments()
    if args.black_list is not None and not os.path.exists(args.black_list):
        print("File with black list doesn't exist")
    personal_info = join_personal_info(
        [args.first_name,
         args.last_name,
         args.email,
         args.company] +
        args.birthday)
    password_strength = get_password_strength(
        args.password,
        personal_info,
        args.black_list
    )
    if password_strength == 0:
        exit("Пароль '{0}' находится в черном списке паролей.\n"
             "Таким паролем пользоваться нельзя!".format(args.password))
    print('Надежность пароля: {number}'.format(number=password_strength))
