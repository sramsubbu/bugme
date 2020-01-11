from argparse import ArgumentParser
from pathlib import Path
import sys

from app_config import APP_PATH
import app

def get_parser():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers()

    initor = subparsers.add_parser('init', help='initialise a bugme instance')
    initor.set_defaults(func=initialise)

    chcker = subparsers.add_parser('check', help='check if the current folder is part of a bugme instance')
    chcker.set_defaults(func=check_instance)

    creator = subparsers.add_parser('create',help='Create a new defect')
    creator.add_argument('-f','--file', help='defect argument file [for bulk creation')
    creator.add_argument('--description', help='description of the defect')
    creator.add_argument('--values', help='the description, expected and observed behaviour values as comma separated values')
    creator.set_defaults(func=create_new_defect)
    
    getter = subparsers.add_parser('get', help='get the details of a defect')
    getter.add_argument('defect_id', help='the id of the defect to be fetched')
    getter.set_defaults(func=get_defect)
    
    updater = subparsers.add_parser('update', help='update a defect with new information')
    updater.add_argument('defect_id', help='the id of the defect to be updated')
    updater.add_argument('--status', help='new status to be updated')
    updater.add_argument('--comment',help='add a comment to the defect')
    updater.add_argument('--resolve', help='resolve the defect')
    updater.set_defaults(func=update_defect)
    
    reporter = subparsers.add_parser('report', help='generate a report based on the query')
    reporter.set_defaults(func=in_progress)

    return parser



def initialise(args):
    if APP_PATH is not None:
        print("Cannot initialise instance")
        print(f"An instance already exists at {APP_PATH}")
        sys.exit(1)

    cwd = Path.cwd()
    app.App.create_new_instance(cwd)


def _check_instance():
    if APP_PATH is None:
        print("No app instance found in the current directory (or in any of the parent directories)")
        sys.exit(1)
    return


def check_instance(args):
    print("Running check...")
    _check_instance()
    print("Valid app instance")
    

def create_new_defect(args, app_instance):
    if args.file is not None:
        print("This feature is still not implemented")
        return

    if args.values is not None:
        description, expected, observed = args.values.split(',')

    elif args.description is not None:
        description, expected, observed  = args.description, '', ''

    else:
        description = input("Description: ")
        expected_behaviour = input("Expected behaviour: ")
        observed_behaviour = input("Observerd behaviour: ")

    app_instance.create_new_defect(description, expected_behaviour, observed_behaviour)


def get_defect(args, app_instance):
    defect_id = args.defect_id
    
    try:
        defect = app_instance.get_defect(defect_id)
    except ValueError:
        print(f"no defect with defect id '{defect_id}'")
        sys.exit(1)

    comments = defect.pop('comments')
    for name, value in defect.items():
        print(name.replace('_', ' ').title(), value, sep=':\t')

    print("\nComments: ")
    for comment in comments:
        print(comment['created_date'],comment['comment'],sep=':\t')


def update_defect(args, app_instance):
    defect_id = args.defect_id

    if args.status is None and args.comment is None and args.resolve is None:
       print("Update what? ")
       sys.exit(1)

    if args.comment:
        app_instance.add_comment(defect_id, args.comment)

    elif args.status:
        app_instance.update_status(defect_id, args.status)

    elif args.resolve:
        app_instance.resolve_defect(defect_id, args.resolve)
    
    return  
        

def in_progress(args, app_instance):
    print("option is not implemented yet")
    


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    _check_instance()
    app_instance = app.App(APP_PATH)
    args.func(args, app_instance)
    
