def read_command_line():
    from argparse import ArgumentParser as AP
    from canvas_selector import choose_options
    parser = AP()
    parser.add_argument('-c', '--course', help="Canvas courseID",
                        default=None)
    parser.add_argument('-s', '--semester', help='semester id, e.g. "2241"',
                        default=None)

    args = parser.parse_args()
    args.assignment = True

    return choose_options(args)


def mark_ungraded(sub, ass):
    """Given a submission for an assignment, mark that submission, and update the grade on canvas
    
    Args:
        sub: canvasapi.submission.Submission
        ass: canvasapi.assignment.Assignment
        
    Returns:
        mark: the numerical grade (integer) awarded to the submission
    """
    from .test_exercises import studentTest
    from canvas_selector import update_grade, nameFile
    if len(sub.attachments) > 0:
        downname = nameFile(sub)
        mark = int(ass.points_possible) * studentTest(downname)
        sub.mark_read()
        if sub.grade:
            if mark > int(sub.grade):
                update_grade(sub, mark)
        else:
            update_grade(sub, mark)
        return mark


def clear_testsrc():
    """check if testsrc is installed, and if so, use pip to
    uninstall it"""
    from importlib.util import find_spec
    installed = find_spec('testsrc') is not None
    if installed:
        import subprocess
        import sys
        subprocess.check_call(
            [sys.executable, "-m", "pip", "uninstall", "-y", "testsrc"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT)
    return


def mark_submissions(ass):
    """Given a Canvas assignment, download all ungraded submissions, and grade them"""
    from canvas_selector import get_submissions
    from tqdm import tqdm

    marks = []
    ungraded = get_submissions(ass)
    for sub in tqdm(ungraded, desc=f"Grading     {ass.name}", ascii=True):
        marks.append(mark_ungraded(sub, ass))
    num_zeros = sum(x == 0 for x in marks)
    print(f"{num_zeros} out of {len(marks)} students scored zero")


def update_grade(sub, newgrade):
    sub.edit(submission={'posted_grade': str(newgrade)})


def main():
    from canvas_selector import cleanup
    args = read_command_line()

    for ass in args.asses:
        mark_submissions(ass)
        clear_testsrc()
        cleanup(ass.id)


if __name__ == '__main__':
    main()
