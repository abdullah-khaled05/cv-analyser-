
import streamlit as st
import requests
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "https://cv-analyser-fawn.vercel.app"

st.set_page_config(
    page_title="CV Intelligence Analyzer",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("CV Intelligence Analyzer")

st.write(
    "Upload your CV to extract, analyze, and understand "
    "your education and professional experience."
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your CV",
    type=["pdf"]
)


# ============================================================
# ANALYZE CV
# ============================================================

if uploaded_file:

    if st.button("Analyze CV", type="primary"):

        with st.spinner("Analyzing CV..."):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/analyze",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file,
                            "application/pdf"
                        )
                    },
                    timeout=120
                )

                # ====================================================
                # BACKEND ERROR
                # ====================================================

                if response.status_code != 200:

                    st.error(
                        f"Backend error: {response.text}"
                    )

                else:

                    result = response.json()

                    cv_data = result.get(
                        "data",
                        {}
                    )

                    experience_analysis = result.get(
                        "experience_analysis",
                        {}
                    )

                    st.success(
                        "CV analyzed successfully!"
                    )


                    # ====================================================
                    # EXPERIENCE SUMMARY
                    # ====================================================

                    st.header("Experience Summary")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "Total Experience",
                            experience_analysis.get(
                                "total_experience",
                                "0 months"
                            )
                        )

                    with col2:

                        st.metric(
                            "Employment Gaps",
                            experience_analysis.get(
                                "number_of_gaps",
                                0
                            )
                        )

                    with col3:

                        st.metric(
                            "Total Gap Duration",
                            experience_analysis.get(
                                "total_gap_duration",
                                "0 months"
                            )
                        )

                    with col4:

                        st.metric(
                            "Employment Overlaps",
                            experience_analysis.get(
                                "number_of_overlaps",
                                0
                            )
                        )


                    # ====================================================
                    # EDUCATION MILESTONES
                    # ====================================================

                    st.header("Education Milestones")

                    col1, col2 = st.columns(2)

                    with col1:

                        bachelors = experience_analysis.get(
                            "bachelors_graduation"
                        )

                        st.metric(
                            "Bachelor's Graduation",
                            bachelors
                            if bachelors
                            else "Not found"
                        )

                    with col2:

                        masters = experience_analysis.get(
                            "masters_graduation"
                        )

                        st.metric(
                            "Master's Graduation",
                            masters
                            if masters
                            else "Not found"
                        )


                    # ====================================================
                    # EMPLOYMENT TIMELINE
                    # ====================================================

                    st.header("Employment Timeline")

                    timeline = experience_analysis.get(
                        "employment_timeline",
                        []
                    )

                    if timeline:

                        timeline_rows = []

                        for index, job in enumerate(
                            timeline,
                            start=1
                        ):

                            timeline_rows.append({

                                "Job":
                                    f"Job {index}",

                                "Company":
                                    job.get(
                                        "company",
                                        ""
                                    ),

                                "Position":
                                    job.get(
                                        "position",
                                        ""
                                    ),

                                "Start":
                                    job.get(
                                        "start",
                                        ""
                                    ),

                                "End":
                                    job.get(
                                        "end",
                                        ""
                                    ),

                                "Bachelor's Context":
                                    job.get(
                                        "bachelors_context",
                                        ""
                                    ),

                                "Master's Context":
                                    job.get(
                                        "masters_context",
                                        ""
                                    )
                            })

                        timeline_df = pd.DataFrame(
                            timeline_rows
                        )

                        st.dataframe(
                            timeline_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No employment timeline found."
                        )


                    # ====================================================
                    # EMPLOYMENT GAP ANALYSIS
                    # ====================================================

                    st.header("Employment Gap Analysis")

                    gaps = experience_analysis.get(
                        "employment_gaps",
                        []
                    )

                    if gaps:

                        gap_rows = []

                        for index, gap in enumerate(
                            gaps,
                            start=1
                        ):

                            gap_rows.append({

                                "Gap":
                                    f"Gap {index}",

                                "From":
                                    gap.get(
                                        "from",
                                        ""
                                    ),

                                "To":
                                    gap.get(
                                        "to",
                                        ""
                                    ),

                                "Duration":
                                    gap.get(
                                        "duration",
                                        ""
                                    ),

                                "Duration (Months)":
                                    gap.get(
                                        "duration_months",
                                        0
                                    ),

                                "Context":
                                    gap.get(
                                        "context",
                                        ""
                                    )
                            })

                        gap_df = pd.DataFrame(
                            gap_rows
                        )

                        st.dataframe(
                            gap_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.success(
                            "No employment gaps detected."
                        )


                    # ====================================================
                    # EMPLOYMENT OVERLAPS
                    # ====================================================

                    st.header("Employment Overlap Analysis")

                    overlaps = experience_analysis.get(
                        "employment_overlaps",
                        []
                    )

                    if overlaps:

                        overlap_rows = []

                        for index, overlap in enumerate(
                            overlaps,
                            start=1
                        ):

                            job1 = overlap.get(
                                "job_1",
                                {}
                            )

                            job2 = overlap.get(
                                "job_2",
                                {}
                            )

                            overlap_rows.append({

                                "Overlap":
                                    f"Overlap {index}",

                                "Job 1":
                                    (
                                        f"{job1.get('position', '')} "
                                        f"at {job1.get('company', '')}"
                                    ),

                                "Job 2":
                                    (
                                        f"{job2.get('position', '')} "
                                        f"at {job2.get('company', '')}"
                                    ),

                                "From":
                                    overlap.get(
                                        "from",
                                        ""
                                    ),

                                "To":
                                    overlap.get(
                                        "to",
                                        ""
                                    ),

                                "Duration":
                                    overlap.get(
                                        "duration",
                                        ""
                                    ),

                                "Duration (Months)":
                                    overlap.get(
                                        "duration_months",
                                        0
                                    )
                            })

                        overlap_df = pd.DataFrame(
                            overlap_rows
                        )

                        st.dataframe(
                            overlap_df,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.info(
                            "Overlapping employment periods are "
                            "reported separately but are counted "
                            "only once toward total professional experience."
                        )

                    else:

                        st.success(
                            "No overlapping employment periods detected."
                        )


                    # ====================================================
                    # EDUCATION GAPS
                    # ====================================================

                    st.header("Education Gap Analysis")

                    education_gaps = experience_analysis.get(
                        "education_gaps",
                        []
                    )

                    if education_gaps:

                        education_gap_rows = []

                        for index, gap in enumerate(
                            education_gaps,
                            start=1
                        ):

                            education_gap_rows.append({

                                "Gap":
                                    f"Gap {index}",

                                "From Degree":
                                    gap.get(
                                        "from_degree",
                                        ""
                                    ),

                                "To Degree":
                                    gap.get(
                                        "to_degree",
                                        ""
                                    ),

                                "From":
                                    gap.get(
                                        "from",
                                        ""
                                    ),

                                "To":
                                    gap.get(
                                        "to",
                                        ""
                                    ),

                                "Duration":
                                    gap.get(
                                        "duration",
                                        ""
                                    ),

                                "Duration (Months)":
                                    gap.get(
                                        "duration_months",
                                        0
                                    )
                            })

                        education_gap_df = pd.DataFrame(
                            education_gap_rows
                        )

                        st.dataframe(
                            education_gap_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.success(
                            "No education gaps detected."
                        )


                    # ====================================================
                    # PERSONAL INFORMATION
                    # ====================================================

                    st.header("Personal Information")

                    personal = cv_data.get(
                        "personal",
                        {}
                    )

                    personal_rows = [

                        {
                            "Field": "Name",
                            "Value": personal.get(
                                "name",
                                ""
                            )
                        },

                        {
                            "Field": "Email",
                            "Value": personal.get(
                                "email",
                                ""
                            )
                        },

                        {
                            "Field": "Phone",
                            "Value": personal.get(
                                "phone",
                                ""
                            )
                        },

                        {
                            "Field": "Location",
                            "Value": personal.get(
                                "location",
                                ""
                            )
                        },

                        {
                            "Field": "LinkedIn",
                            "Value": personal.get(
                                "linkedin",
                                ""
                            )
                        },

                        {
                            "Field": "GitHub",
                            "Value": personal.get(
                                "github",
                                ""
                            )
                        }
                    ]

                    personal_df = pd.DataFrame(
                        personal_rows
                    )

                    st.dataframe(
                        personal_df,
                        use_container_width=True,
                        hide_index=True
                    )


                    # ====================================================
                    # EDUCATION
                    # ====================================================

                    st.header("Education")

                    education_rows = []

                    for education in cv_data.get(
                        "education",
                        []
                    ):

                        education_rows.append({

                            "Degree":
                                education.get(
                                    "degree",
                                    ""
                                ),

                            "Institution":
                                education.get(
                                    "institution",
                                    ""
                                ),

                            "Start Date":
                                education.get(
                                    "start_date",
                                    ""
                                ),

                            "End Date":
                                education.get(
                                    "end_date",
                                    ""
                                ),

                            "Grade":
                                education.get(
                                    "grade",
                                    ""
                                )
                        })

                    if education_rows:

                        education_df = pd.DataFrame(
                            education_rows
                        )

                        st.dataframe(
                            education_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No education information found."
                        )


                    # ====================================================
                    # WORK EXPERIENCE
                    # ====================================================

                    st.header("Extracted Work Experience")

                    experience_rows = []

                    for experience in cv_data.get(
                        "experience",
                        []
                    ):

                        description = experience.get(
                            "description",
                            []
                        )

                        if isinstance(
                            description,
                            list
                        ):

                            description = " ".join(
                                description
                            )

                        experience_rows.append({

                            "Company":
                                experience.get(
                                    "company",
                                    ""
                                ),

                            "Position":
                                experience.get(
                                    "position",
                                    ""
                                ),

                            "Start Date":
                                experience.get(
                                    "start_date",
                                    ""
                                ),

                            "End Date":
                                experience.get(
                                    "end_date",
                                    ""
                                ),

                            "Description":
                                description
                        })

                    if experience_rows:

                        experience_df = pd.DataFrame(
                            experience_rows
                        )

                        st.dataframe(
                            experience_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No work experience found."
                        )


                    # ====================================================
                    # SKILLS
                    # ====================================================

                    st.header("Skills")

                    skills = cv_data.get(
                        "skills",
                        {}
                    )

                    skills_rows = [

                        {
                            "Category":
                                "Programming Languages",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "programming_languages",
                                        []
                                    )
                                )
                        },

                        {
                            "Category":
                                "Frameworks",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "frameworks",
                                        []
                                    )
                                )
                        },

                        {
                            "Category":
                                "Databases",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "databases",
                                        []
                                    )
                                )
                        },

                        {
                            "Category":
                                "Cloud",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "cloud",
                                        []
                                    )
                                )
                        },

                        {
                            "Category":
                                "AI / ML",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "ai_ml",
                                        []
                                    )
                                )
                        },

                        {
                            "Category":
                                "Tools",

                            "Skills":
                                ", ".join(
                                    skills.get(
                                        "tools",
                                        []
                                    )
                                )
                        }
                    ]

                    skills_df = pd.DataFrame(
                        skills_rows
                    )

                    st.dataframe(
                        skills_df,
                        use_container_width=True,
                        hide_index=True
                    )


                    # ====================================================
                    # PROJECTS
                    # ====================================================

                    st.header("Projects")

                    project_rows = []

                    for project in cv_data.get(
                        "projects",
                        []
                    ):

                        technologies = project.get(
                            "technologies",
                            []
                        )

                        if isinstance(
                            technologies,
                            list
                        ):

                            technologies = ", ".join(
                                technologies
                            )

                        project_rows.append({

                            "Project":
                                project.get(
                                    "name",
                                    ""
                                ),

                            "Technologies":
                                technologies,

                            "Description":
                                project.get(
                                    "description",
                                    ""
                                )
                        })

                    if project_rows:

                        projects_df = pd.DataFrame(
                            project_rows
                        )

                        st.dataframe(
                            projects_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No projects found."
                        )


                    # ====================================================
                    # CERTIFICATIONS
                    # ====================================================

                    st.header("Certifications")

                    certification_rows = []

                    for certification in cv_data.get(
                        "certifications",
                        []
                    ):

                        certification_rows.append({

                            "Certification":
                                certification.get(
                                    "name",
                                    ""
                                ),

                            "Issuer":
                                certification.get(
                                    "issuer",
                                    ""
                                ),

                            "Date":
                                certification.get(
                                    "date",
                                    ""
                                )
                        })

                    if certification_rows:

                        certifications_df = pd.DataFrame(
                            certification_rows
                        )

                        st.dataframe(
                            certifications_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.info(
                            "No certifications found."
                        )


            # ============================================================
            # ERROR HANDLING
            # ============================================================

            except requests.exceptions.Timeout:

                st.error(
                    "The backend took too long to respond. "
                    "Please try again."
                )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the backend. "
                    "Please check that the Vercel backend is running."
                )

            except ValueError:

                st.error(
                    "The backend returned an invalid response. "
                    "Please check the API response."
                )

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )
