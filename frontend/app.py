import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "https://cv-analyser-fawn.vercel.app"
st.set_page_config(
    page_title="CV Intelligence Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("CV Intelligence Analyzer")
st.write("Upload your CV to extract and analyze your information.")


uploaded_file = st.file_uploader(
    "Upload your CV",
    type=["pdf"]
)


if uploaded_file:

    if st.button("Analyze CV"):

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
                    }
                )

                if response.status_code != 200:
                    st.error(
                        f"Backend error: {response.text}"
                    )

                else:

                    result = response.json()

                    cv_data = result["data"]
                    experience_analysis = result[
                        "experience_analysis"
                    ]

                    st.success("CV analyzed successfully!")

                    # =====================================================
                    # EXPERIENCE SUMMARY
                    # =====================================================

                    st.header("Experience Summary")

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        st.metric(
                            "Total Experience",
                            experience_analysis[
                                "total_experience"
                            ]
                        )

                    with col2:
                        st.metric(
                            "Employment Gaps",
                            experience_analysis[
                                "number_of_gaps"
                            ]
                        )

                    with col3:
                        st.metric(
                            "Total Gap Duration",
                            experience_analysis[
                                "total_gap_duration"
                            ]
                        )

                    with col4:
                        st.metric(
                            "After Graduation",
                            experience_analysis[
                                "graduation_date"
                            ] or "Not found"
                        )

                    # =====================================================
                    # EMPLOYMENT GAP TABLE
                    # =====================================================

                    st.header("Employment Gap Analysis")

                    gaps = experience_analysis[
                        "employment_gaps"
                    ]

                    if gaps:

                        gap_rows = []

                        for index, gap in enumerate(
                            gaps,
                            start=1
                        ):

                            gap_rows.append({
                                "Gap": f"Gap {index}",
                                "From": gap["from"],
                                "To": gap["to"],
                                "Duration": gap["duration"]
                            })

                        gap_df = pd.DataFrame(gap_rows)

                        st.dataframe(
                            gap_df,
                            use_container_width=True,
                            hide_index=True
                        )

                    else:

                        st.success(
                            "No employment gaps detected."
                        )

                    # =====================================================
                    # PERSONAL INFORMATION
                    # =====================================================

                    st.header("Personal Information")

                    personal = cv_data["personal"]

                    personal_rows = [
                        {
                            "Field": "Name",
                            "Value": personal.get(
                                "name", ""
                            )
                        },
                        {
                            "Field": "Email",
                            "Value": personal.get(
                                "email", ""
                            )
                        },
                        {
                            "Field": "Phone",
                            "Value": personal.get(
                                "phone", ""
                            )
                        },
                        {
                            "Field": "Location",
                            "Value": personal.get(
                                "location", ""
                            )
                        },
                        {
                            "Field": "LinkedIn",
                            "Value": personal.get(
                                "linkedin", ""
                            )
                        },
                        {
                            "Field": "GitHub",
                            "Value": personal.get(
                                "github", ""
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

                    # =====================================================
                    # EDUCATION
                    # =====================================================

                    st.header("Education")

                    education_rows = []

                    for education in cv_data[
                        "education"
                    ]:

                        education_rows.append({
                            "Degree": education.get(
                                "degree", ""
                            ),
                            "Institution": education.get(
                                "institution", ""
                            ),
                            "Start Date": education.get(
                                "start_date", ""
                            ),
                            "End Date": education.get(
                                "end_date", ""
                            ),
                            "Grade": education.get(
                                "grade", ""
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

                    # =====================================================
                    # WORK EXPERIENCE
                    # =====================================================

                    st.header("Work Experience")

                    experience_rows = []

                    for experience in cv_data[
                        "experience"
                    ]:

                        experience_rows.append({
                            "Company": experience.get(
                                "company", ""
                            ),
                            "Position": experience.get(
                                "position", ""
                            ),
                            "Start Date": experience.get(
                                "start_date", ""
                            ),
                            "End Date": experience.get(
                                "end_date", ""
                            ),
                            "Description": " ".join(
                                experience.get(
                                    "description", []
                                )
                            )
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

                    # =====================================================
                    # SKILLS
                    # =====================================================

                    st.header("Skills")

                    skills = cv_data["skills"]

                    skills_rows = [
                        {
                            "Category": "Programming Languages",
                            "Skills": ", ".join(
                                skills.get(
                                    "programming_languages",
                                    []
                                )
                            )
                        },
                        {
                            "Category": "Frameworks",
                            "Skills": ", ".join(
                                skills.get(
                                    "frameworks",
                                    []
                                )
                            )
                        },
                        {
                            "Category": "Databases",
                            "Skills": ", ".join(
                                skills.get(
                                    "databases",
                                    []
                                )
                            )
                        },
                        {
                            "Category": "Cloud",
                            "Skills": ", ".join(
                                skills.get(
                                    "cloud",
                                    []
                                )
                            )
                        },
                        {
                            "Category": "AI / ML",
                            "Skills": ", ".join(
                                skills.get(
                                    "ai_ml",
                                    []
                                )
                            )
                        },
                        {
                            "Category": "Tools",
                            "Skills": ", ".join(
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

                    # =====================================================
                    # PROJECTS
                    # =====================================================

                    st.header("Projects")

                    project_rows = []

                    for project in cv_data[
                        "projects"
                    ]:

                        project_rows.append({
                            "Project": project.get(
                                "name", ""
                            ),
                            "Technologies": ", ".join(
                                project.get(
                                    "technologies",
                                    []
                                )
                            ),
                            "Description": project.get(
                                "description", ""
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

                    # =====================================================
                    # CERTIFICATIONS
                    # =====================================================

                    st.header("Certifications")

                    certification_rows = []

                    for certification in cv_data[
                        "certifications"
                    ]:

                        certification_rows.append({
                            "Certification": certification.get(
                                "name", ""
                            ),
                            "Issuer": certification.get(
                                "issuer", ""
                            ),
                            "Date": certification.get(
                                "date", ""
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

            except Exception as e:

                st.error(
                    f"Something went wrong: {str(e)}"
                )