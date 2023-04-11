def seconds(timeString):
    parts = timeString.split(":")
    total = 0
    weight = 1
    try:
        for i in range(len(parts)):
            total += float(parts[-(i+1)])*weight
            weight *= 60
        return total
    except:
        return False

def formatted(timeNum: float):
    minutes = int(timeNum // 60)
    sms = round(timeNum-minutes*60, 3)
    result = str(sms)
    if minutes:
        if sms < 10:
            result = str(minutes)+":0"+result

        else:
            result = str(minutes)+":"+result

    result = result+('0'*(3-len(result.split(".")[-1])))
    return result


def formatLeaderBoardPosition(position: int):
    suffix = "th"
    cases = {"1": "st",
                "2": "nd",
                "3": "rd",
                }
    if not ("0"+str(position))[-2] == "1":
        case = str(position)[-1]
        if case in cases.keys():
            suffix = cases[case]

    return str(position)+suffix


if __name__ == "__main__":
    tests = [
        "43",
        "60",
        "74",
        "43.5",
        "60.3",
        "74.9",
        "1:00",
        "1:02",
        "1:00.525",
        "15:33.120",
        "01:00",
        "01:00.3",
        "01:00.374",
        "1:09:32",
        "1:09:32.375"
    ]
    for test in tests:
        print(test, ", ", seconds(test))


    tests = [
        43,
        63.34,
    ]
    for test in tests:
        print(test, ", ", formatted(test))
