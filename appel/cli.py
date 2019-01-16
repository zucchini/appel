# -*- coding: utf-8 -*-

"""Console script for appel."""
from .canvas import getUsersInCourse, getUsersForAssignment, setUserAssignmentScoresWithComments
from .policy import getPercentScore, getComments
from .spreadsheet import parseAllSpreadsheets
from collections import Counter
from pytz import timezone
from pydrive.auth import GoogleAuth

import sys
import click

OUTPUT_DATE_FORMAT = "%B %d, %Y %H:%M:%S"
TZ = timezone('US/Eastern')

@click.group()
def cli():
    pass

@cli.command()
@click.option('--canvas-token', help="Canvas token without the leading 2096~", prompt="Enter Canvas token without the leading 2096~", type=str)
@click.option('--course-id', help="Canvas course ID", prompt="Enter Canvas course ID", type=int)
@click.option('--assignment-id', help="Canvas assignment ID for grade entry", prompt="Enter Canvas assignment ID for grade entry", type=int)
@click.option('--spreadsheet-directory-id', help="Google Drive ID for directory containing attendance sheets", prompt="Enter Google Drive ID for directory containing attendance sheets", type=str)
@click.option('--dry-run', is_flag=True, help="Process and show grades without posting to Canvas.")
@click.option('-l', '--absence-limit', help="Number of absences after which deductions begin.", required=True, type=int)
@click.option('-d', '--deduction-per-absence', help="Percent deduction to be applied for each absence beyond limit", required=True, type=int)
def grade(canvas_token, course_id, assignment_id, spreadsheet_directory_id, dry_run, absence_limit, deduction_per_absence):
    """Grade student attendance."""

    # Setup Google Drive access
    click.echo("Connecting to Google Drive.")
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    click.echo("Connected to Google Drive successfully.\n")

    # Get the eligible users
    click.echo("Loading users with attendance requirements.")
    users = getUsersInCourse(canvas_token, course_id)
    users = getUsersForAssignment(users, canvas_token, assignment_id, course_id)
    clich.echo("%d users loaded successfully.\n" % len(users))

    # Get the spreadsheets
    click.echo("Loading attendance sheets.")
    attendance = parseAllSpreadsheets(spreadsheet_directory_id, gauth, users)
    click.echo("%d attendance sheets loaded successfully. Total %d attendance entries.\n" % (sum(1 for _ in attendance.values()), sum(sum(1 for k in x.values() if k is not None) for x in attendance.values())))

    # Show and enter grades
    grades = [(user, getPercentScore(attendance[user], absence_limit, deduction_per_absence), getComments(attendance[user])) for user in users]

    click.echo("Displaying grades:")
    for user, score, _ in grades:
        click.echo("Student: %s, score: %d" % (user.name, score))

    if not dry_run:
        click.echo("Entering grades on Canvas")
        setUserAssignmentScoresWithComments(canvas_token, course_id, assignment_id, grades)
        click.echo("Canvas grade entry complete.")

    click.echo("Goodbye!")

#@cli.command()
#@click.option('--text', 'output_format', flag_value='text', default=True)
#@click.option('--json', 'output_format', flag_value='json')
#@click.option('--csv', 'output_format', flag_value='csv')
#def list(output_format):
#    """List the students that require attendance."""
#
#    users = getUsersInCourse(token, course)
#
#    hasher = lambda x: hashlib.sha512(x.encode('ascii')).hexdigest()
#
#    map = {hasher(y.gtID): {'name': y.name, 'login': y.login} for y in users}
#
#    print(json.dumps(map, sort_keys=True, indent=4))
#
#@cli.command()
#def timedlab():
    # """Check Gradescope assignment for any submissions after attendance."""
    #
    # # Setup Google Drive access
    # print("Connecting to Google Drive.")
    # gauth = GoogleAuth()
    # gauth.LocalWebserverAuth()
    # print("Connected to Google Drive successfully.\n")
    #
    # # Get the eligible users
    # print("Loading users with attendance requirements.")
    # users = getUsersInCourse(canvas_token, course)
    # users = getUsersForAssignment(users, canvas_token, assignment, course)
    # print("%d users loaded successfully.\n" % len(users))
    #
    # # Get the spreadsheets
    # print("Loading attendance sheet.")
    # attendance = parseSingleSpreadsheet(spreadsheet_id, gauth, users)
    # print("Attendance sheet loaded successfully.\n")
    #
    # # Get their submission dates
    # print("Loading Gradescope submission information.")
    # submissions = getUserSubmissionTimes(users, gradescope_file)
    # print("Gradescope submission information loaded successfully.\n")
    #
    # # Run the comparison
    # print("Results:")
    # for user in users:
    #     checkout = attendance[user]
    #     submission_date = submissions[user]
    #
    #     if checkout is None and submission_date is None:
    #         #print("%s did not submit and did not check out. Absent?" % user.name)
    #         continue
    #
    #     if checkout is None and submission_date is not None:
    #         print("WARNING! %s submitted the assignment but did not check out." % user.name)
    #         continue
    #
    #     if submission_date is None and checkout is not None:
    #         print("WARNING! %s checked out but did not submit assignment." % user.name)
    #         continue
    #
    #     if checkout is not None and checkout.timestamp is None:
    #         print("WARNING! %s checked out but no timestamp was recorded, so a validation cannot be made." % user.name)
    #         continue
    #
    #     if submission_date > checkout.timestamp:
    #         print("WARNING! %s submitted assignment after checking out. Checkout: %s. Last submission: %s" % (user.name, checkout.timestamp.astimezone(TZ).strftime(OUTPUT_DATE_FORMAT), submission_date.astimezone(TZ).strftime(OUTPUT_DATE_FORMAT)))
    #         continue
    #
    # print("\nGoodbye!")

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
