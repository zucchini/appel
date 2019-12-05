GRADE_SPLITTER = " ----------------------------------- "

def getPercentScore(attendance):
    attended = sum(1 for x in attendance.values() if x is not None)

    scale = float(attended) / (len(attendance) - 1)

    return int(100 * min(scale, 1))

def getComments(attendance):
    comments = []

    for date in sorted(attendance.keys()):
        entry = attendance[date]
        if entry is None:
            comments.append("%s: ABSENT" % date)
        else:
            comments.append("%s: PRESENT - %s - Notes: %s" % (date, entry.location, entry.notes))

    return GRADE_SPLITTER.join(comments)
