import re


def clean_mrz_line(line: str) -> str:
    line = line.upper().strip()

    # OCR often misreads the MRZ filler character "<"
    # as spaces or other characters.
    line = line.replace(" ", "")

    # Keep only characters that are valid in an MRZ.
    line = re.sub(r"[^A-Z0-9<]", "", line)

    return line


def find_mrz_lines(text: str):
    lines = [
        clean_mrz_line(line)
        for line in text.splitlines()
        if line.strip()
    ]

    candidates = [
        line for line in lines
        if len(line) >= 35
    ]

    for i in range(len(candidates) - 1):
        line1 = candidates[i]
        line2 = candidates[i + 1]

        if len(line1) >= 40 and len(line2) >= 40:
            return line1[:44], line2[:44]

    return None, None


def mrz_check_digit(value: str) -> str:
    weights = [7, 3, 1]
    total = 0

    for i, char in enumerate(value):
        if char == "<":
            number = 0
        elif char.isdigit():
            number = int(char)
        elif char.isalpha():
            number = ord(char) - ord("A") + 10
        else:
            number = 0

        total += number * weights[i % 3]

    return str(total % 10)


def verify_check_digit(value: str, check_digit: str) -> bool:
    if not check_digit or not check_digit.isdigit():
        return False

    return mrz_check_digit(value) == check_digit


def parse_passport_mrz(line1: str, line2: str):

    line1 = line1.ljust(44, "<")[:44]
    line2 = line2.ljust(44, "<")[:44]

    passport_number_raw = line2[0:9]
    passport_number_check = line2[9]

    nationality = line2[10:13]

    date_of_birth_raw = line2[13:19]
    date_of_birth_check = line2[19]

    sex = line2[20]

    expiry_date_raw = line2[21:27]
    expiry_date_check = line2[27]

    surname_and_names = line1[5:44]

    parts = surname_and_names.split("<<", 1)

    surname = parts[0].replace("<", " ").strip()

    if len(parts) > 1:
        given_names = parts[1].replace("<", " ").strip()
    else:
        given_names = ""

    passport_number = passport_number_raw.replace("<", "")

    check_digits = {
        "passport_number": verify_check_digit(
            passport_number_raw,
            passport_number_check
        ),
        "date_of_birth": verify_check_digit(
            date_of_birth_raw,
            date_of_birth_check
        ),
        "expiry_date": verify_check_digit(
            expiry_date_raw,
            expiry_date_check
        ),
    }

    valid = all(check_digits.values())

    return {
        "passport_number": passport_number,
        "surname": surname,
        "given_names": given_names,
        "nationality": nationality,
        "date_of_birth_raw": date_of_birth_raw,
        "sex": sex,
        "expiry_date_raw": expiry_date_raw,
        "check_digits": check_digits,
        "valid": valid,
        "raw_mrz": [line1, line2],
    }


def extract_mrz(text: str):

    line1, line2 = find_mrz_lines(text)

    if not line1 or not line2:
        return {
            "detected": False,
            "valid": False,
            "check_digits": {},
            "raw_mrz": [],
        }

    parsed = parse_passport_mrz(line1, line2)

    return {
        "detected": True,
        **parsed,
    }