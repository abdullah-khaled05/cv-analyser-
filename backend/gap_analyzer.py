from datetime import date, datetime
from dateutil.relativedelta import relativedelta


# ============================================================
# DATE HELPERS
# ============================================================

def parse_date(date_string):
    """
    Convert a CV date into a Python date.

    Supported formats:
    - January 2025
    - Jan 2025
    - 01/2025
    - 2025-01
    - 2025
    - Present / Current / Now

    Year-only dates are internally represented as January,
    but the original precision is tracked separately.
    """

    if not date_string:
        return None

    date_string = date_string.strip().lower()

    if date_string in ["present", "current", "now"]:
        today = date.today()

        return date(
            today.year,
            today.month,
            1
        )

    formats = [
        "%B %Y",
        "%b %Y",
        "%m/%Y",
        "%Y-%m",
        "%Y",
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
    Calculate the number of complete months between dates.
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
# EDUCATION HELPERS
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
    Find an education record using keywords.
    """

    if isinstance(keywords, str):
        keywords = [keywords]

    for edu in education_periods:

        degree = (
            edu["degree"] or ""
        ).lower()

        for keyword in keywords:

            if keyword.lower() in degree:
                return edu

    return None


# ============================================================
# EDUCATION LEVEL DETECTION
# ============================================================

def get_matriculation(education):
    """
    Find Matriculation / SSC / O-Level education.
    """

    periods = get_education_periods(
        education
    )

    return find_degree(
        periods,
        [
            "matric",
            "ssc",
            "secondary school",
            "o-level",
            "o level"
        ]
    )


def get_intermediate(education):
    """
    Find Intermediate / HSSC / A-Level education.
    """

    periods = get_education_periods(
        education
    )

    return find_degree(
        periods,
        [
            "intermediate",
            "hssc",
            "higher secondary",
            "a-level",
            "a level",
            "fsc",
            "fa ",
            "ics",
            "icom"
        ]
    )


def get_bachelors(education):
    """
    Find Bachelor's degree.
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


def get_masters(education):
    """
    Find Master's degree.
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


# ============================================================
# EDUCATION GAPS
# ============================================================

def build_education_milestone(
    name,
    education
):
    """
    Build a standardized education milestone.
    """

    if not education:

        return {
            "status": "Not found",
            "degree": None,
            "institution": None,
            "start": None,
            "end": None
        }

    return {
        "status": "Found",
        "degree": education["degree"],
        "institution": education["institution"],

        "start": format_date(
            education["start"],
            education["start_original"]
        ),

        "end": format_date(
            education["end"],
            education["end_original"]
        )
    }


def calculate_education_gap(
    from_name,
    from_education,
    to_name,
    to_education
):
    """
    Calculate a gap between two specific education levels.

    Examples:
    Matriculation -> Intermediate
    Intermediate -> Bachelor's
    Bachelor's -> Master's
    """

    if not from_education or not to_education:

        return {
            "from_level": from_name,
            "to_level": to_name,
            "status": "Cannot assess",
            "duration_months": 0,
            "duration": "Not enough information"
        }

    previous_end = from_education["end"]
    next_start = to_education["start"]

    if not previous_end or not next_start:

        return {
            "from_level": from_name,
            "to_level": to_name,
            "status": "Cannot assess",
            "duration_months": 0,
            "duration": "Dates missing"
        }

    gap_months = months_between(
        previous_end,
        next_start
    )

    if gap_months > 0:

        return {
            "from_level": from_name,
            "to_level": to_name,

            "from": format_date(
                previous_end,
                from_education["end_original"]
            ),

            "to": format_date(
                next_start,
                to_education["start_original"]
            ),

            "status": "Gap detected",

            "duration_months":
                gap_months,

            "duration":
                format_duration(
                    gap_months
                )
        }

    return {
        "from_level": from_name,
        "to_level": to_name,
        "status": "No gap",
        "duration_months": 0,
        "duration": "0 months"
    }


def analyze_education_gaps(
    education
):
    """
    Explicitly analyze:

    Matriculation -> Intermediate
    Intermediate -> Bachelor's
    Bachelor's -> Master's
    """

    matriculation = get_matriculation(
        education
    )

    intermediate = get_intermediate(
        education
    )

    bachelors = get_bachelors(
        education
    )

    masters = get_masters(
        education
    )

    gaps = []

    gaps.append(
        calculate_education_gap(
            "Matriculation",
            matriculation,
            "Intermediate",
            intermediate
        )
    )

    gaps.append(
        calculate_education_gap(
            "Intermediate",
            intermediate,
            "Bachelor's",
            bachelors
        )
    )

    gaps.append(
        calculate_education_gap(
            "Bachelor's",
            bachelors,
            "Master's",
            masters
        )
    )

    return gaps


# ============================================================
# EMPLOYMENT OVERLAPS
# ============================================================

def detect_overlapping_jobs(jobs):
    """
    Detect periods where two jobs overlap.

    This is performed BEFORE merging employment periods
    so overlaps are not lost.
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

def merge_employment_periods(jobs):
    """
    Merge overlapping employment periods.

    This prevents overlapping jobs from being
    double-counted in total experience.
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
# EMPLOYMENT HELPERS
# ============================================================

def prepare_employment(
    cv_data,
    bachelors
):
    """
    Prepare employment records.

    Employment before Bachelor's is excluded when
    the Bachelor's completion date is precise.

    If Bachelor's is year-only, we avoid pretending
    that January is the actual graduation month.
    """

    jobs = []

    bachelors_graduation = (
        bachelors["end"]
        if bachelors
        else None
    )

    bachelors_year_only = (
        bachelors["end_year_only"]
        if bachelors
        else False
    )

    for experience in cv_data.experience:

        start = parse_date(
            experience.start_date
        )

        end = parse_date(
            experience.end_date
        )

        if not start:
            continue

        if not end:

            end = date.today().replace(
                day=1
            )

        if end <= start:
            continue

        excluded_before_bachelors = False
        clipped_to_bachelors = False
        bachelors_context = None

        # ----------------------------------------------------
        # Bachelor's handling
        # ----------------------------------------------------

        if bachelors_graduation:

            if not bachelors_year_only:

                # Job completely before Bachelor's
                if end <= bachelors_graduation:

                    excluded_before_bachelors = True

                # Job started before Bachelor's but
                # continued afterwards
                elif start < bachelors_graduation:

                    start = bachelors_graduation
                    clipped_to_bachelors = True

            else:

                # Bachelor's is year-only.
                # We cannot know the exact month.

                if end < bachelors_graduation:

                    excluded_before_bachelors = True

        if excluded_before_bachelors:
            continue

        # ----------------------------------------------------
        # Bachelor's context
        # ----------------------------------------------------

        if bachelors:

            if bachelors_year_only:

                if start.year < bachelors_graduation.year:

                    bachelors_context = (
                        "Started before Bachelor's "
                        "graduation year"
                    )

                elif start.year == bachelors_graduation.year:

                    bachelors_context = (
                        "Occurred during Bachelor's "
                        "graduation year"
                    )

                else:

                    bachelors_context = (
                        "After Bachelor's "
                        "graduation year"
                    )

            else:

                if clipped_to_bachelors:

                    bachelors_context = (
                        "Started before Bachelor's "
                        "graduation and continued after"
                    )

                else:

                    bachelors_context = (
                        "After Bachelor's graduation"
                    )

        jobs.append({

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
                bachelors_context
        })

    return jobs


# ============================================================
# POST-BACHELOR EMPLOYMENT GAPS
# ============================================================

def analyze_employment_gaps(
    jobs,
    bachelors
):
    """
    Identify:

    1. Bachelor's completion -> first employment
    2. Employment -> next employment

    This specifically satisfies the Phase 2
    post-Bachelor gap requirement.
    """

    gaps = []

    if not jobs:
        return gaps

    sorted_jobs = sorted(
        jobs,
        key=lambda x: x["start"]
    )

    # --------------------------------------------------------
    # Bachelor's -> First Job
    # --------------------------------------------------------

    if bachelors:

        bachelors_end = bachelors["end"]

        first_job = sorted_jobs[0]

        # Only perform exact Bachelor's -> job
        # calculation when Bachelor's has a precise month.

        if not bachelors["end_year_only"]:

            if first_job["start"] > bachelors_end:

                gap_months = months_between(
                    bachelors_end,
                    first_job["start"]
                )

                if gap_months > 0:

                    gaps.append({

                        "from":
                            format_date(
                                bachelors_end,
                                bachelors["end_original"]
                            ),

                        "to":
                            format_date(
                                first_job["start"],
                                first_job["start_original"]
                            ),

                        "duration_months":
                            gap_months,

                        "duration":
                            format_duration(
                                gap_months
                            ),

                        "context":
                            "Post-Bachelor gap before first employment"
                    })

    # --------------------------------------------------------
    # Job -> Next Job
    # --------------------------------------------------------

    merged_periods = merge_employment_periods(
        sorted_jobs
    )

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

    return gaps


# ============================================================
# MASTER'S RELATIONSHIP
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

        if job_start < masters_start:
            return "Overlaps Master's"

        return "During Master's"

    return "Unknown"


# ============================================================
# MAIN EXPERIENCE ANALYZER
# ============================================================

def analyze_experience(
    cv_data
):
    """
    Phase 2 analyzer.

    Checks:

    1. Post-Bachelor employment gaps
    2. Employment overlaps
    3. Educational gaps

    Also provides:
    - Education milestones
    - Master's employment context
    - Total professional experience
    """

    education = cv_data.education

    # ========================================================
    # EDUCATION
    # ========================================================

    matriculation = get_matriculation(
        education
    )

    intermediate = get_intermediate(
        education
    )

    bachelors = get_bachelors(
        education
    )

    masters = get_masters(
        education
    )

    education_gaps = analyze_education_gaps(
        education
    )

    education_timeline = {

        "matriculation":
            build_education_milestone(
                "Matriculation",
                matriculation
            ),

        "intermediate":
            build_education_milestone(
                "Intermediate",
                intermediate
            ),

        "bachelors":
            build_education_milestone(
                "Bachelor's",
                bachelors
            ),

        "masters":
            build_education_milestone(
                "Master's",
                masters
            )
    }

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

    # ========================================================
    # EMPLOYMENT
    # ========================================================

    jobs = prepare_employment(
        cv_data,
        bachelors
    )

    # ========================================================
    # NO EMPLOYMENT
    # ========================================================

    if not jobs:

        return {

            "education_timeline":
                education_timeline,

            "education_gaps":
                education_gaps,

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

    # ========================================================
    # EMPLOYMENT OVERLAPS
    # ========================================================

    overlaps = detect_overlapping_jobs(
        jobs
    )

    # ========================================================
    # EMPLOYMENT GAPS
    # ========================================================

    gaps = analyze_employment_gaps(
        jobs,
        bachelors
    )

    # ========================================================
    # MERGED EMPLOYMENT
    # ========================================================

    merged_periods = merge_employment_periods(
        jobs
    )

    # ========================================================
    # TOTAL EXPERIENCE
    # ========================================================

    total_experience_months = 0

    for period in merged_periods:

        total_experience_months += months_between(
            period["start"],
            period["end"]
        )

    # ========================================================
    # TOTAL GAP
    # ========================================================

    total_gap_months = sum(
        gap["duration_months"]
        for gap in gaps
    )

    # ========================================================
    # EMPLOYMENT TIMELINE
    # ========================================================

    employment_timeline = []

    for job in sorted(
        jobs,
        key=lambda x: x["start"]
    ):

        masters_context = (
            classify_job_relative_to_masters(
                job,
                masters
            )
        )

        employment_timeline.append({

            "company":
                job["company"],

            "position":
                job["position"],

            "start":
                format_date(
                    job["start"],
                    job["start_original"]
                ),

            "end":
                format_date(
                    job["end"],
                    job["end_original"]
                ),

            "bachelors_context":
                job["bachelors_context"],

            "masters_context":
                masters_context
        })

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        # ----------------------------------------------------
        # EDUCATION
        # ----------------------------------------------------

        "education_timeline":
            education_timeline,

        "education_gaps":
            education_gaps,

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

        # ----------------------------------------------------
        # EXPERIENCE
        # ----------------------------------------------------

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

        "employment_timeline":
            employment_timeline,

        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

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