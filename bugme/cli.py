from argparse import ArgumentParser
from pathlib import Path
import sys
from shutil import make_archive

import app

DESCRIPTION = "bugme lightweight database"
PROG = "bugme"
VERSION = '0.1'


def get_multiline(prompt):
    lines = []
    print(prompt)
    print("Press Ctrl+D to end")
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break
    return '\n'.join(lines)
    

def in_progress(args):
    print("Functionality is not completed")
    print("Arguments passed are: ")
    print(args)


@app.require_app_instance
def export_instance(args, instance):
    filename = args.filename
    archive_format = args.archive_format
    # make_archive(filename, archive_format, base_dir = instance)
    in_progress(args)

    
@app.require_app_instance
def resolve_command(args, instance):
    defect_id =args.defect_id
    resolution = args.resolution
    if resolution is None:
        resolution = get_multiline("Resolution")
    app.resolve(defect_id, resolution, instance)
    

@app.require_app_instance
def comment_cmd(args, instance):
    defect_id = args.defect_id
    comment = args.comment

    if comment is None:
        comment = get_multiline("Comment: ")
    app.add_comment(defect_id, comment, instance)
    

@app.require_app_instance
def status_cmd(args, instance):
    defect_id = args.defect_id
    def update_status():
            app.update_status(defect_id, args.update, instance)
            sys.exit(0)

    if args.update is not None:
        update_status()
        
    status = app.get_status(defect_id, instance)
    print(status)

    
@app.require_app_instance
def new_defect(args, instance):
    if args.description is None:
        description = get_multiline("Enter the description: ")
    else:
        description = args.description

    if args.observed is None:
        observed = get_multiline("Observed behaviour: ")
    else:
        observed = args.observed

    if args.expected is None:
        expected = get_multiline("Expected behaviour: ")
    else:
        expected = args.expected

    did = app.create_new_defect(description, expected, observed, instance)
    print("Bug created with id: ",did)

    
@app.require_app_instance
def query_instance(args, instance):
    # TODO: Refactor the code to split the function into several functions
    # TODO: Refactor code to pretty print the results
    bugs = app.get_all_bugs(instance)
    if args.get:
        defect_id = args.get
        bug = app.get_bug(defect_id, instance)
        for key, value in bug.items():
            if key != 'comments':
                print(key, value, sep=':  ')
        print("Comments: ")
        for item in bug['comments']:
            print(item)
        sys.exit(0)
    if len(bugs) != 0:
        print("Found {x} items: ".format(x = len(bugs)))
        for item in bugs:
            print(item)
    else:
        print("No item found")


def create_app_instance(args):
    instance = app.get_app_instance()
    if instance is not None:
        print("Already part of an environment: {instance}".format(instance=instance))
    else:
        app.create_new_instance()
        

def check_instance(args):
    instance = app.get_app_instance()
    if instance is not None:
        print("Instance present at: {instance}".format(instance=instance))
    else:
        print("No instance exists in the current or any of the parent directories")


def get_parser():
    parser = ArgumentParser(description=DESCRIPTION, prog=PROG)
    parser.set_defaults(func=None)

    subcommands = parser.add_subparsers(help="Subcommands")

    create_instance = subcommands.add_parser("create", help="create a bugme db instance")
    create_instance.set_defaults(func=create_app_instance)

    check = subcommands.add_parser('check', help='check if the current folder is part of a bugme instance')
    check.set_defaults(func=check_instance)

    export = subcommands.add_parser('export', help='export the instance to an archive')
    export.add_argument('filename', help='name of the generated archive file')
    export.add_argument('--archive_format', default='zip', help='format of the archive')
    export.set_defaults(func=export_instance)

    query = subcommands.add_parser('query', help='query the bug database')
    query.add_argument('--get', help='get a particular defect by id')
    query.set_defaults(func=query_instance)

    add = subcommands.add_parser('add', help='create a new defect')
    add.add_argument('description', default=None, nargs='?')
    add.add_argument('observed', default=None, nargs='?')
    add.add_argument('expected', default=None, nargs='?')
    add.set_defaults(func=new_defect)

    resolve = subcommands.add_parser('resolve', help='close a defect with resolution')
    resolve.add_argument('defect_id', help='id of the defect that is to be resolved')
    resolve.add_argument('resolution', nargs='?', help='resolution for the defect')
    resolve.set_defaults(func=resolve_command)

    comment = subcommands.add_parser('comment', help ='add or modify comments to a defect')
    comment.add_argument('defect_id', help='id of the defect to comment')
    comment.add_argument('--comment', help='comment text', nargs='?')
    comment.set_defaults(func=comment_cmd)

    status = subcommands.add_parser('status', help='update the status of the bug')
    status.add_argument('defect_id', help='id of the defect for which status is required')
    status.add_argument('--update', help='update the status')
    status.set_defaults(func=status_cmd)

    parser.add_argument('--version', action='version',  version='%(prog)s {version}'.format(version=VERSION))

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    action = args.func
    if action is None:
        print("Arguments not given: ")
        parser.print_help()
    else:
        action(args)
