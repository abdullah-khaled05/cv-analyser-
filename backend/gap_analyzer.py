from datetime import date, datetime
from dateutil.relativedelta import relativedelta


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(date_string):
    """
    Convert a CV date into a Python date.

    Important:
    - Month + year -> exact month
    - Year only -> January is used internally, but the
      precision is tracked separately where necessary.
    - Present/current/now -> current month
    """

    if not date_string:
        return None

    date_string = date_string.strip().lower()

    # Current employment
    if date_string in ["present", "current", "now"]:

        today = date.today()

        return date(
            today.year,
            today.month,
            1
        )

    formats = [
        "%B %Y",       # January 2025
        "%b %Y",       # Jan 2025
        "%m/%Y",       # 01/2025
        "%Y-%m",       # 2025-01
        "%Y",          # 2025
    ]

    for fmt in formats:

        try:

            parsed = datetime.strptime(
                date_string,
                fmt
            )

            return date(
                parsed.year,
                parsed.month,
                1
            )

        except ValueError:
            continue

    return None


def is_year_only(date_string):
    """
    Check whether a date contains only a year.

    Examples:

    2025 -> True
    2024 -> True
    January 2025 -> False
    Aug 2024 -> False
    """

    if not date_string:
        return False

    value = date_string.strip()

    return (
        len(value) == 4
        and value.isdigit()
    )


def format_date(date_value, original_string=None):
    """
    Format dates for output.

    If the original value only contained a year,
    return only the year.

    Otherwise return Month Year.
    """

    if not date_value:
        return None

    if original_string and is_year_only(
        original_string
    ):
        return str(date_value.year)

    return date_value.strftime(
        "%B %Y"
    )


def months_between(start, end):
    """
    Calculate the number of months between two dates.
    """

    if not start or not end:
        return 0

    if end <= start:
        return 0

    difference = relativedelta(
        end,
        start
    )

    return (
        difference.years * 12
        + difference.months
    )


def format_duration(months):
    """
    Convert months into readable duration.
    """

    years = months // 12

    remaining_months = months % 12

    if years > 0 and remaining_months > 0:

        return (
            f"{years} years "
            f"{remaining_months} months"
        )

    if years > 0:

        return f"{years} years"

    return f"{remaining_months} months"


# ============================================================
# EDUCATION
# ============================================================

def get_education_periods(education):
    """
    Extract valid education periods.
    """

    periods = []

    for edu in education:

        start = parse_date(
            edu.start_date
        )

        end = parse_date(
            edu.end_date
        )

        if not start or not end:
            continue

        periods.append({

            "degree": edu.degree,

            "institution": edu.institution,

            "start": start,

            "end": end,

            "start_original": edu.start_date,

            "end_original": edu.end_date,

            "start_year_only":
                is_year_only(
                    edu.start_date
                ),

            "end_year_only":
                is_year_only(
                    edu.end_date
                )
        })

    return sorted(
        periods,
        key=lambda x: x["start"]
    )


def find_degree(
    education_periods,
    keywords
):
    """
    Find a degree using keywords.
    """

    if isinstance(
        keywords,
        str
    ):
        keywords = [keywords]

    for edu in education_periods:

        degree = (
            edu["degree"] or ""
        ).lower()

        for keyword in keywords:

            if keyword.lower() in degree:

                return edu

    return None


def get_bachelors_graduation(
    education
):
    """
    Find Bachelor's graduation record.
    """

    periods = get_education_periods(
        education
    )

    return find_degree(
        periods,
        [
            "bachelor",
            "b.s",
            "bsc",
            "b.sc",
            "bs ",
            "btech",
            "b.tech"
        ]
    )


def get_masters_graduation(
    education
):
    """
    Find Master's graduation record.
    """

    periods = get_education_periods(
        education
    )

    return find_degree(
        periods,
        [
            "master",
            "m.s",
            "msc",
            "m.sc",
            "ms ",
            "mtech",
            "m.tech"
        ]
    )


def analyze_education_gaps(
    education
):
    """
    Find gaps between education programs.
    """

    periods = get_education_periods(
        education
    )

    gaps = []

    for i in range(
        1,
        len(periods)
    ):

        previous = periods[i - 1]

        current = periods[i]

        gap_months = months_between(
            previous["end"],
            current["start"]
        )

        if gap_months > 0:

            gaps.append({

                "from_degree":
                    previous["degree"],

                "to_degree":
                    current["degree"],

                "from":
                    format_date(
                        previous["end"],
                        previous[
                            "end_original"
                        ]
                    ),

                "to":
                    format_date(
                        current["start"],
                        current[
                            "start_original"
                        ]
                    ),

                "duration_months":
                    gap_months,

                "duration":
                    format_duration(
                        gap_months
                    )
            })

    return gaps


# ============================================================
# EMPLOYMENT CLASSIFICATION
# ============================================================

def classify_job_relative_to_masters(
    job,
    masters
):
    """
    Determine whether employment is:

    - Before Master's
    - During Master's
    - After Master's
    - Overlaps Master's
    """

    if not masters:
        return "Master's not found"

    job_start = job["start"]
    job_end = job["end"]

    masters_start = masters["start"]
    masters_end = masters["end"]

    # Completely before Master's
    if job_end <= masters_start:

        return "Before Master's"

    # Completely after Master's
    if job_start >= masters_end:

        return "After Master's"

    # Job overlaps Master's
    if (
        job_start < masters_end
        and job_end > masters_start
    ):

        # Started before Master's
        if job_start < masters_start:

            return "Overlaps Master's"

        # Started during Master's
        return "During Master's"

    return "Unknown"


# ============================================================
# EMPLOYMENT OVERLAPS
# ============================================================

def detect_overlapping_jobs(
    jobs
):
    """
    Detect periods where two jobs overlap.
    """

    overlaps = []

    for i in range(
        len(jobs)
    ):

        for j in range(
            i + 1,
            len(jobs)
        ):

            job1 = jobs[i]

            job2 = jobs[j]

            overlap_start = max(
                job1["start"],
                job2["start"]
            )

            overlap_end = min(
                job1["end"],
                job2["end"]
            )

            if overlap_start < overlap_end:

                overlap_months = months_between(
                    overlap_start,
                    overlap_end
                )

                overlaps.append({

                    "job_1": {
                        "company":
                            job1["company"],

                        "position":
                            job1["position"]
                    },

                    "job_2": {
                        "company":
                            job2["company"],

                        "position":
                            job2["position"]
                    },

                    "from":
                        overlap_start.strftime(
                            "%B %Y"
                        ),

                    "to":
                        overlap_end.strftime(
                            "%B %Y"
                        ),

                    "duration_months":
                        overlap_months,

                    "duration":
                        format_duration(
                            overlap_months
                        )
                })

    return overlaps


# ============================================================
# MERGE EMPLOYMENT PERIODS
# ============================================================

def merge_employment_periods(
    jobs
):
    """
    Merge overlapping employment periods.

    This prevents double-counting experience.
    """

    if not jobs:
        return []

    jobs = sorted(
        jobs,
        key=lambda x: x["start"]
    )

    merged = []

    current_start = jobs[0]["start"]

    current_end = jobs[0]["end"]

    for job in jobs[1:]:

        start = job["start"]

        end = job["end"]

        if start <= current_end:

            if end > current_end:

                current_end = end

        else:

            merged.append({

                "start":
                    current_start,

                "end":
                    current_end
            })

            current_start = start

            current_end = end

    merged.append({

        "start":
            current_start,

        "end":
            current_end
    })

    return merged


# ============================================================
# MAIN EXPERIENCE ANALYZER
# ============================================================

def analyze_experience(
    cv_data
):
    """
    Analyze:

    1. Bachelor's graduation
    2. Master's graduation
    3. Employment gaps
    4. Employment overlaps
    5. Education gaps
    6. Jobs relative to Master's
    7. Total professional experience

    Important:

    Employment before Bachelor's is excluded
    when the Bachelor's graduation date is precise.

    If Bachelor's graduation is only a year,
    the analyzer avoids pretending that the
    exact graduation month is known.
    """

    education = cv_data.education

    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    bachelors = get_bachelors_graduation(
        education
    )

    masters = get_masters_graduation(
        education
    )

    education_gaps = analyze_education_gaps(
        education
    )

    bachelors_graduation = (
        bachelors["end"]
        if bachelors
        else None
    )

    masters_graduation = (
        masters["end"]
        if masters
        else None
    )

    bachelors_year_only = (
        bachelors["end_year_only"]
        if bachelors
        else False
    )

    # --------------------------------------------------------
    # Extract employment
    # --------------------------------------------------------

    jobs = []

    for experience in cv_data.experience:

        start = parse_date(
            experience.start_date
        )

        end = parse_date(
            experience.end_date
        )

        if not start:
            continue

        # Current job
        if not end:

            end = date.today().replace(
                day=1
            )

        if end <= start:
            continue

        # ----------------------------------------------------
        # Bachelor's handling
        # ----------------------------------------------------

        excluded_before_bachelors = False

        clipped_to_bachelors = False

        if bachelors_graduation:

            # If Bachelor's date is precise,
            # we can safely exclude jobs that
            # ended before graduation.

            if not bachelors_year_only:

                if end <= bachelors_graduation:

                    excluded_before_bachelors = True

                elif start < bachelors_graduation:

                    start = bachelors_graduation

                    clipped_to_bachelors = True

            else:

                # Bachelor's is year-only.
                #
                # We do NOT know the exact month.
                #
                # Therefore we keep the job and
                # report the uncertainty instead
                # of deleting potentially valid work.

                if end < bachelors_graduation:

                    excluded_before_bachelors = True

        if excluded_before_bachelors:

            continue

        job = {

            "company":
                experience.company,

            "position":
                experience.position,

            "start":
                start,

            "end":
                end,

            "start_original":
                experience.start_date,

            "end_original":
                experience.end_date,

            "bachelors_context":
                None,

            "masters_context":
                None
        }

        # ----------------------------------------------------
        # Bachelor's relationship
        # ----------------------------------------------------

        if bachelors:

            if bachelors_year_only:

                if (
                    start.year
                    < bachelors_graduation.year
                ):

                    job[
                        "bachelors_context"
                    ] = (
                        "Started before "
                        "Bachelor's graduation year"
                    )

                elif (
                    start.year
                    == bachelors_graduation.year
                ):

                    job[
                        "bachelors_context"
                    ] = (
                        "Occurred during "
                        "Bachelor's graduation year"
                    )

                else:

                    job[
                        "bachelors_context"
                    ] = (
                        "After Bachelor's graduation year"
                    )

            else:

                if clipped_to_bachelors:

                    job[
                        "bachelors_context"
                    ] = (
                        "Started before Bachelor's "
                        "graduation and continued after"
                    )

                else:

                    job[
                        "bachelors_context"
                    ] = (
                        "After Bachelor's graduation"
                    )

        # ----------------------------------------------------
        # Master's relationship
        # ----------------------------------------------------

        job[
            "masters_context"
        ] = classify_job_relative_to_masters(
            job,
            masters
        )

        jobs.append(job)

    # --------------------------------------------------------
    # No employment
    # --------------------------------------------------------

    if not jobs:

        return {

            "bachelors_graduation":
                format_date(
                    bachelors_graduation,
                    bachelors[
                        "end_original"
                    ]
                    if bachelors
                    else None
                ),

            "masters_graduation":
                format_date(
                    masters_graduation,
                    masters[
                        "end_original"
                    ]
                    if masters
                    else None
                ),

            "total_experience":
                "0 months",

            "total_experience_months":
                0,

            "employment_gaps":
                [],

            "employment_overlaps":
                [],

            "education_gaps":
                education_gaps,

            "employment_timeline":
                [],

            "total_gap_duration":
                "0 months",

            "total_gap_months":
                0,

            "number_of_gaps":
                0,

            "number_of_overlaps":
                0
        }

    # --------------------------------------------------------
    # Detect overlaps
    # --------------------------------------------------------

    overlaps = detect_overlapping_jobs(
        jobs
    )

    # --------------------------------------------------------
    # Merge employment
    # --------------------------------------------------------

    merged_periods = merge_employment_periods(
        jobs
    )

    # --------------------------------------------------------
    # Employment gaps
    # --------------------------------------------------------

    gaps = []

    for i in range(
        1,
        len(merged_periods)
    ):

        previous_end = merged_periods[
            i - 1
        ]["end"]

        next_start = merged_periods[
            i
        ]["start"]

        gap_months = months_between(
            previous_end,
            next_start
        )

        if gap_months > 0:

            gaps.append({

                "from":
                    previous_end.strftime(
                        "%B %Y"
                    ),

                "to":
                    next_start.strftime(
                        "%B %Y"
                    ),

                "duration_months":
                    gap_months,

                "duration":
                    format_duration(
                        gap_months
                    ),

                "context":
                    "Employment gap"
            })

    # --------------------------------------------------------
    # Total experience
    # --------------------------------------------------------

    total_experience_months = 0

    for period in merged_periods:

        total_experience_months += months_between(
            period["start"],
            period["end"]
        )

    # --------------------------------------------------------
    # Total gap duration
    # --------------------------------------------------------

    total_gap_months = sum(

        gap["duration_months"]

        for gap in gaps
    )

    # --------------------------------------------------------
    # Employment timeline
    # --------------------------------------------------------

    employment_timeline = []

    for job in jobs:

        employment_timeline.append({

            "company":
                job["company"],

            "position":
                job["position"],

            "start":
                job["start"].strftime(
                    "%B %Y"
                ),

            "end":
                job["end"].strftime(
                    "%B %Y"
                ),

            "bachelors_context":
                job["bachelors_context"],

            "masters_context":
                job["masters_context"]
        })

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    return {

        "bachelors_graduation":
            format_date(
                bachelors_graduation,
                bachelors[
                    "end_original"
                ]
                if bachelors
                else None
            ),

        "masters_graduation":
            format_date(
                masters_graduation,
                masters[
                    "end_original"
                ]
                if masters
                else None
            ),

        "total_experience":
            format_duration(
                total_experience_months
            ),

        "total_experience_months":
            total_experience_months,

        "employment_gaps":
            gaps,

        "employment_overlaps":
            overlaps,

        "education_gaps":
            education_gaps,

        "employment_timeline":
            employment_timeline,

        "total_gap_duration":
            format_duration(
                total_gap_months
            ),

        "total_gap_months":
            total_gap_months,

        "number_of_gaps":
            len(gaps),

        "number_of_overlaps":
            len(overlaps)
    }