from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def parse_date(date_string):
    """
    Convert common CV date formats into a Python date.
    """

    if not date_string:
        return None

    date_string = date_string.strip().lower()

    # Handle current employment
    if date_string in ["present", "current", "now"]:
        today = date.today()
        return date(today.year, today.month, 1)

    formats = [
        "%B %Y",       # January 2025
        "%b %Y",       # Jan 2025
        "%m/%Y",       # 01/2025
        "%Y-%m",       # 2025-01
        "%Y",          # 2025
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_string, fmt)
            return date(parsed.year, parsed.month, 1)
        except ValueError:
            continue

    return None


def months_between(start, end):
    """
    Calculate the number of months between two dates.
    """

    if end <= start:
        return 0

    difference = relativedelta(end, start)

    return difference.years * 12 + difference.months


def format_duration(months):
    """
    Convert months into a readable duration.
    """

    years = months // 12
    remaining_months = months % 12

    if years > 0 and remaining_months > 0:
        return f"{years} years {remaining_months} months"

    if years > 0:
        return f"{years} years"

    return f"{remaining_months} months"


def get_graduation_date(education):
    """
    Find the latest education end date.

    This is used as the graduation date.
    """

    dates = []

    for edu in education:

        parsed = parse_date(edu.end_date)

        if parsed:
            dates.append(parsed)

    if not dates:
        return None

    return max(dates)


def merge_employment_periods(jobs):
    """
    Merge overlapping employment periods.

    Example:

    Job A: Jan 2023 - Dec 2023
    Job B: Jun 2023 - Mar 2024

    Becomes:

    Jan 2023 - Mar 2024
    """

    if not jobs:
        return []

    jobs = sorted(jobs, key=lambda x: x["start"])

    merged = []

    current_start = jobs[0]["start"]
    current_end = jobs[0]["end"]

    for job in jobs[1:]:

        start = job["start"]
        end = job["end"]

        # Overlapping or directly connected employment
        if start <= current_end:

            if end > current_end:
                current_end = end

        else:

            merged.append(
                {
                    "start": current_start,
                    "end": current_end
                }
            )

            current_start = start
            current_end = end

    merged.append(
        {
            "start": current_start,
            "end": current_end
        }
    )

    return merged


def analyze_experience(cv_data):
    """
    Analyze employment gaps and total professional experience.

    Rules:

    1. Only employment after graduation counts.
    2. Employment gaps do not count toward experience.
    3. Overlapping jobs are counted only once.
    4. Current employment is supported.
    """

    graduation_date = get_graduation_date(
        cv_data.education
    )

    jobs = []

    # -----------------------------------------
    # Extract valid employment periods
    # -----------------------------------------

    for experience in cv_data.experience:

        start = parse_date(experience.start_date)
        end = parse_date(experience.end_date)

        if not start:
            continue

        # If no end date, assume current employment
        if not end:
            end = date.today().replace(day=1)

        # Ignore invalid dates
        if end <= start:
            continue

        # -----------------------------------------
        # Remove experience before graduation
        # -----------------------------------------

        if graduation_date:

            # Entire job happened before graduation
            if end <= graduation_date:
                continue

            # Job started before graduation
            # but continued after graduation
            if start < graduation_date:
                start = graduation_date

        jobs.append(
            {
                "company": experience.company,
                "position": experience.position,
                "start": start,
                "end": end
            }
        )

    if not jobs:

        return {
            "graduation_date": (
                graduation_date.strftime("%B %Y")
                if graduation_date
                else None
            ),
            "total_experience": "0 months",
            "total_experience_months": 0,
            "employment_gaps": [],
            "total_gap_duration": "0 months",
            "total_gap_months": 0,
            "number_of_gaps": 0
        }

    # -----------------------------------------
    # Merge overlapping employment
    # -----------------------------------------

    merged_periods = merge_employment_periods(jobs)

    # -----------------------------------------
    # Calculate gaps
    # -----------------------------------------

    gaps = []

    for i in range(1, len(merged_periods)):

        previous_end = merged_periods[i - 1]["end"]
        next_start = merged_periods[i]["start"]

        gap_months = months_between(
            previous_end,
            next_start
        )

        if gap_months > 0:

            gaps.append(
                {
                    "from": previous_end.strftime("%B %Y"),
                    "to": next_start.strftime("%B %Y"),
                    "duration_months": gap_months,
                    "duration": format_duration(gap_months)
                }
            )

    # -----------------------------------------
    # Calculate total experience
    # -----------------------------------------

    total_experience_months = 0

    for period in merged_periods:

        total_experience_months += months_between(
            period["start"],
            period["end"]
        )

    # -----------------------------------------
    # Calculate total gap duration
    # -----------------------------------------

    total_gap_months = sum(
        gap["duration_months"]
        for gap in gaps
    )

    return {
        "graduation_date": (
            graduation_date.strftime("%B %Y")
            if graduation_date
            else None
        ),

        "total_experience": format_duration(
            total_experience_months
        ),

        "total_experience_months": (
            total_experience_months
        ),

        "employment_gaps": gaps,

        "total_gap_duration": format_duration(
            total_gap_months
        ),

        "total_gap_months": total_gap_months,

        "number_of_gaps": len(gaps)
    }