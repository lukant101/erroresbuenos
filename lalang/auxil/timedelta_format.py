"""Exports function: timedelta_format."""


def timedelta_format(timedelta):
    """Input: timedelta (float) as seconds.

    Output: timedelta as string: {hours}:{minutes}:{seconds}.
    """
    timedelta = round(timedelta)
    if timedelta >= 3600:
        hour = timedelta // 3600
        carry_over = timedelta % 3600
        if carry_over >= 60:
            minute = carry_over // 60
            second = carry_over % 60
        else:
            second = carry_over
    elif timedelta >= 60:
        hour = 0
        minute = timedelta // 60
        second = timedelta % 60
    else:
        hour = 0
        minute = 0
        second = timedelta

    return f"{hour}:{minute}:{second}"


if __name__ == "__main__":
    timedelta = 7322
    print(timedelta_format(timedelta))
