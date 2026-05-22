"""
VERA-RI: Verification Engine for Results & Accountability - Rhode Island
Type 4 Detection using WIDA ACCESS Speaking vs Writing + RICAS Achievement Data

Rhode Island context: WIDA ACCESS for ELLs, RICAS (Rhode Island Comprehensive Assessment
System), 4 performance levels (Not Meeting/Partially Meeting/Meeting/Exceeding Expectations).
66 LEAs, ~15,000 ELs (~11% of enrollment). Top: Providence 33% MLL (state takeover 2019-2024).
MLL (Multilingual Learner) population has doubled in recent years.
Providence state takeover 2019-2024 by RIDE. Smallest state, highest EL density.
Data: RIDE InfoWorks (infoworks.ride.ri.gov).

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_RI_BLUE = "#003DA5"
RI_GOLD = "#FFD700"
RI_DARK = "#002060"
RI_RED = "#CC0000"

# ============================================================================
# DATA: Rhode Island Districts with EL Populations
# ============================================================================

def load_districts():
    """
    Load RI LEAs with significant EL/MLL populations.
    Data modeled from RIDE InfoWorks (infoworks.ride.ri.gov).
    RICAS levels: Not Meeting, Partially Meeting, Meeting, Exceeding Expectations.
    66 LEAs, ~15,000 ELs (~11% of enrollment).
    Providence: 33% MLL (state takeover 2019-2024).
    MLL population has doubled in recent years.
    Rhode Island uses "MLL" (Multilingual Learner) terminology.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, ricas_ela_all, ricas_ela_el, ricas_ela_hispanic, ricas_ela_black, ricas_ela_white,
        #  ricas_math_all, ricas_math_el, top_el_languages)

        # Providence -- state takeover 2019-2024
        ("28", "Providence School District", 23500, 7755, 33.0,
         70.5, 28.5, 6.5, 15.2, 12.8, 52.5,
         22.8, 5.0, "Spanish, Portuguese, Haitian Creole, Arabic, Cape Verdean Creole"),

        # Core urban districts
        ("07", "Central Falls School District", 3200, 1440, 45.0,
         68.2, 24.2, 5.2, 12.8, 10.5, 48.5,
         18.5, 3.8, "Spanish, Portuguese, Guatemalan languages, Cape Verdean Creole"),
        ("30", "Pawtucket School District", 8800, 2640, 30.0,
         72.5, 30.2, 7.5, 16.5, 13.2, 54.2,
         25.2, 5.8, "Spanish, Portuguese, Cape Verdean Creole, Haitian Creole"),
        ("47", "Woonsocket School District", 5800, 1160, 20.0,
         71.8, 28.8, 6.8, 14.8, 12.2, 52.8,
         23.5, 5.2, "Spanish, French, Haitian Creole, Portuguese"),
        ("12", "Cranston School District", 10200, 1530, 15.0,
         80.5, 40.2, 11.5, 22.5, 18.2, 58.5,
         35.8, 9.5, "Spanish, Portuguese, Arabic, Italian"),

        # Suburban with growing EL
        ("14", "East Providence School District", 5200, 780, 15.0,
         78.2, 38.5, 10.8, 21.2, 17.5, 56.8,
         33.5, 8.8, "Spanish, Portuguese, Cape Verdean Creole"),
        ("46", "Warwick School District", 8500, 850, 10.0,
         82.5, 42.8, 12.8, 24.5, 19.8, 60.2,
         38.2, 10.5, "Spanish, Portuguese, Arabic"),
        ("44", "West Warwick School District", 3400, 340, 10.0,
         77.5, 36.8, 10.2, 20.5, 16.8, 55.5,
         32.2, 8.2, "Spanish, Portuguese, Arabic"),
        ("01", "Barrington School District", 3600, 180, 5.0,
         90.2, 58.5, 22.5, 36.8, 30.2, 66.5,
         54.2, 18.5, "Spanish, Chinese, Portuguese"),

        # Other LEAs
        ("24", "North Providence School District", 3200, 384, 12.0,
         79.8, 39.5, 11.2, 22.2, 18.0, 57.5,
         34.8, 9.2, "Spanish, Portuguese, Arabic, Italian"),
        ("06", "Burrillville School District", 2200, 110, 5.0,
         83.2, 44.5, 13.5, 24.8, 20.2, 59.5,
         39.5, 11.0, "Spanish, Portuguese, French"),
        ("48", "Westerly School District", 2800, 196, 7.0,
         84.5, 46.2, 14.2, 25.5, 21.5, 60.8,
         41.2, 11.8, "Spanish, Portuguese, Guatemalan languages"),
        ("22", "Newport School District", 2400, 360, 15.0,
         76.8, 35.8, 9.8, 19.8, 16.2, 55.2,
         31.5, 8.0, "Spanish, Portuguese, Haitian Creole, Cape Verdean Creole"),
        ("09", "Coventry School District", 4200, 210, 5.0,
         85.2, 48.2, 15.5, 27.2, 22.5, 61.8,
         43.5, 12.8, "Spanish, Portuguese, Arabic"),
        ("37", "South Kingstown School District", 3400, 170, 5.0,
         87.5, 52.5, 17.8, 30.5, 25.8, 63.5,
         47.8, 14.5, "Spanish, Chinese, Portuguese, Korean"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'ricas_ela_all', 'ricas_ela_el', 'ricas_ela_hispanic',
        'ricas_ela_black', 'ricas_ela_white',
        'ricas_math_all', 'ricas_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: ACCESS Domain Data
# ============================================================================

def load_access_data(districts_df):
    """
    Generate district ACCESS domain data modeled from RIDE InfoWorks ACCESS data.
    Rhode Island uses WIDA ACCESS. Exit criteria: composite 4.5+
    with domain minimums. RI uses "MLL" (Multilingual Learner) terminology.
    """
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 330 + (grade * 9)
                base_writing = 275 + (grade * 7)
                base_listening = 335 + (grade * 8)
                base_reading = 288 + (grade * 7)

                el_factor = d['ricas_ela_el'] / 16.0
                speaking_adj = int(11 * el_factor + d['el_percent'] * 0.28)
                writing_adj = int(-15 + (el_factor - 1) * 11)
                listening_adj = speaking_adj - 2
                reading_adj = writing_adj + 7

                if 'Cape Verdean Creole' in d['top_el_languages']:
                    speaking_adj += 3
                    writing_adj -= 4
                if 'Haitian Creole' in d['top_el_languages']:
                    speaking_adj += 4
                    writing_adj -= 3
                if 'Guatemalan languages' in d['top_el_languages']:
                    speaking_adj -= 3
                    writing_adj -= 7

                year_adj = 3 if year == 2025 else 0

                # Providence special: state takeover context, highest MLL %
                if d['district_id'] == '28':
                    speaking_adj += 2
                    writing_adj -= 6

                # Central Falls: highest EL%, smallest urban district
                if d['district_id'] == '07':
                    speaking_adj += 3
                    writing_adj -= 8

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(10, int(d['el_count'] / 6)),
                    'listening_avg': base_listening + listening_adj + year_adj,
                    'speaking_avg': base_speaking + speaking_adj + year_adj,
                    'reading_avg': base_reading + reading_adj + year_adj,
                    'writing_avg': base_writing + writing_adj + year_adj,
                    'composite_avg': int((base_speaking + speaking_adj +
                                          base_writing + writing_adj +
                                          base_listening + listening_adj +
                                          base_reading + reading_adj) / 4 + 12 + year_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: RICAS Achievement Data
# ============================================================================

def load_ricas_data(districts_df):
    """
    Generate RICAS data based on RIDE InfoWorks proficiency rates.
    RICAS has 4 performance levels: Not Meeting Expectations, Partially Meeting
    Expectations, Meeting Expectations, Exceeding Expectations.
    ELA and Math tested grades 3-8.
    """
    ricas_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['ricas_ela_all']
                    else:
                        base = d['ricas_math_all']

                    prof = max(8, min(85, base + (grade - 5) * -1.5))

                    if year == 2024:
                        prof = prof - 1.2

                    # 4-level distribution
                    exceeding = max(2, prof * 0.18)
                    meeting = max(5, prof - exceeding)
                    partial = max(10, (100 - prof) * 0.42)
                    not_meeting = max(5, 100 - meeting - exceeding - partial)

                    ricas_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'not_meeting_pct': round(not_meeting, 1),
                        'partial_pct': round(partial, 1),
                        'meeting_pct': round(meeting, 1),
                        'exceeding_pct': round(exceeding, 1),
                        'proficient_pct': round(meeting + exceeding, 1),
                    })

    return pd.DataFrame(ricas_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide ACCESS domain proficiency percentages by grade cluster.
    Source: RIDE InfoWorks (infoworks.ride.ri.gov) ACCESS data.
    ~15,000 ELs (~11%) across 66 LEAs.
    MLL population has doubled in recent years.
    Providence: 33% MLL, state takeover 2019-2024.
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 40, 'speaking': 36, 'reading': 22, 'writing': 16},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 46, 'speaking': 42, 'reading': 26, 'writing': 18},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 50, 'speaking': 44, 'reading': 30, 'writing': 21},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 53, 'speaking': 46, 'reading': 33, 'writing': 23},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 38, 'speaking': 34, 'reading': 20, 'writing': 14},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 44, 'speaking': 40, 'reading': 24, 'writing': 16},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 48, 'speaking': 42, 'reading': 28, 'writing': 19},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 51, 'speaking': 44, 'reading': 31, 'writing': 21},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.
    """
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'delta_normalized': delta_normalized,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("Rhode Island Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot LEAs", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("MLLs", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("Statewide MLL %", "~11%", help="~15,000 MLLs statewide; population has doubled")

    st.divider()

    st.subheader("Rhode Island Policy Context")
    st.markdown("""
    Rhode Island's **Multilingual Learner (MLL)** population has **doubled** in recent years,
    creating unprecedented demand for EL services in the nation's smallest state. **Providence**
    -- serving 33% MLL students -- was under **state takeover by RIDE from 2019-2024**, the
    most significant state intervention in RI history. **Central Falls** (45% MLL) is the
    most densely concentrated MLL district in the state. Rhode Island uses "MLL" (Multilingual
    Learner) terminology rather than "EL" (English Learner).
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**MLL Population Doubled**\nUnprecedented growth in multilingual learners statewide")
    with col2:
        st.warning("**Providence State Takeover**\nRIDE takeover 2019-2024, 33% MLL enrollment")
    with col3:
        st.info("**Central Falls 45% MLL**\nHighest MLL percentage in the state")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**WIDA ACCESS**\n4 domains, composite exit 4.5+ w/ domain mins")
    with col2:
        st.info("**RICAS**\n4 levels: Not Meeting to Exceeding Expectations")
    with col3:
        st.info("**RIDE InfoWorks**\n66 LEAs, infoworks.ride.ri.gov")

    st.divider()

    st.subheader("Key State Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Statewide MLL Count", "~15,000", help="~11% of total enrollment")
    with col2:
        st.metric("Total LEAs", "66")
    with col3:
        st.metric("ELP Assessment", "WIDA ACCESS")
    with col4:
        st.metric("Academic Assessment", "RICAS")

    st.divider()

    st.subheader("Top MLL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Spanish', 'Portuguese', 'Cape Verdean Creole', 'Haitian Creole',
                     'Arabic', 'Chinese', 'Guatemalan langs', 'French'],
        'Approx Share': [55, 10, 7, 6, 5, 3, 3, 2],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, '#C0C0C0'], [1, RI_BLUE]],
                      labels={'Approx Share': '% of MLL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top MLL Home Languages in Rhode Island")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot LEAs -- Highest MLL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'ricas_ela_all', 'ricas_ela_el', 'ricas_ela_black', 'ricas_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['LEA ID', 'District', 'Students', 'MLL Count', 'MLL %',
                       'ELA All %', 'ELA MLL %', 'ELA Black %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Multilingual Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, RI_BLUE]],
        labels={'el_count': 'MLLs', 'district_name': 'District', 'el_percent': 'MLL %'}
    )
    fig.update_layout(height=550, showlegend=False,
                      title="MLL Population by District (color = MLL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** RIDE InfoWorks (infoworks.ride.ri.gov). Rhode Island is a WIDA Consortium member.
    Domain proficiency percentages show the systemic oral-written delta: Speaking consistently
    outperforms Writing across all grade clusters. With the **MLL population doubling**
    and the **Providence state takeover** (2019-2024), these domain patterns have implications
    for how RIDE allocates resources post-takeover.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', RI_BLUE), ('speaking', RI_GOLD),
                           ('reading', '#888888'), ('writing', RI_RED)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 72])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[RI_RED if d > 18 else RI_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for Rhode Island:** The oral-written gap is compounded by the rapid
    doubling of the MLL population. Providence (33% MLL, post-state-takeover) and Central
    Falls (45% MLL) face acute pressure to serve students whose oral English develops faster
    than written English proficiency. The concentration of Portuguese and Creole speakers
    (Cape Verdean, Haitian) creates unique patterns -- these students may show strong oral
    skills due to Romance language cognates but struggle with English academic writing conventions.
    """)


def render_access_analysis(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures multilingual learners across four domains. Rhode Island has
    ~15,000 MLLs (~11% of enrollment) across 66 LEAs. Exit criteria: composite proficiency
    level **4.5+** with domain minimums. The MLL population has **doubled** in recent years.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="acc_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top MLL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.0f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[RI_BLUE, RI_GOLD, '#888888', RI_RED],
            text=[f"{s:.0f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.0f}")
        with col2:
            st.metric("Written Average", f"{written:.0f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.0f}",
                      delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.subheader("Exit Criteria Check (RI: composite 4.5+ w/ domain mins)")
        st.markdown("""
        Rhode Island exit criteria require a composite proficiency level of **4.5 or higher**
        with minimum domain scores. With the MLL population doubling, reclassification
        capacity is strained. Providence's post-state-takeover transition adds complexity
        to reclassification processes for its 7,700+ MLL students.
        """)
    else:
        st.warning("No data available for the selected filters.")


def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.

    In Rhode Island, the **doubling of the MLL population** and the **Providence state takeover**
    (2019-2024) create an urgent context for Type 4 detection. Central Falls (45% MLL) and
    Providence (33% MLL) are at highest risk for undetected Type 4 patterns.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.0f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=RI_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=RI_BLUE))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **Rhode Island-specific action:** Providence (post-state-takeover) and Central Falls
            should prioritize targeted writing interventions for MLL students flagged as Type 4.
            Portuguese and Creole speakers may show deceptively strong oral skills due to Romance
            language cognates while struggling with academic English writing. Coordinate with
            RIDE's MLL office to ensure post-takeover Providence receives adequate writing
            intervention resources. Consider bilingual writing workshops leveraging L1 literacy.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=RI_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=RI_BLUE, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="Scale Score", height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'delta_normalized', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Norm Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **RICAS ELA proficiency by subgroup** across pilot LEAs. Rhode Island faces significant
    gaps between white students and MLL/Hispanic/Black students. The **Providence state
    takeover** (2019-2024) was driven in part by these persistent gaps. With the MLL
    population doubling, the gap challenge has intensified statewide.
    """)

    st.divider()

    fig = go.Figure()
    sorted_df = districts_df.sort_values('ricas_ela_all', ascending=True)
    for col, name, color in [
        ('ricas_ela_white', 'White', '#666666'),
        ('ricas_ela_all', 'All Students', RI_BLUE),
        ('ricas_ela_hispanic', 'Hispanic', '#E8540A'),
        ('ricas_ela_black', 'Black', RI_RED),
        ('ricas_ela_el', 'MLLs', RI_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="RICAS ELA Proficiency by Subgroup -- RIDE InfoWorks",
        barmode='group', xaxis_title="% Meeting or Exceeding Expectations", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gap Magnitude: White - Black / White - MLL")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wb_gap'] = districts_df_copy['ricas_ela_white'] - districts_df_copy['ricas_ela_black']
    districts_df_copy['wh_gap'] = districts_df_copy['ricas_ela_white'] - districts_df_copy['ricas_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['ricas_ela_white'] - districts_df_copy['ricas_ela_el']

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_wb = districts_df_copy['wb_gap'].mean()
        st.metric("Avg White-Black Gap", f"{avg_wb:.1f} pts", delta="Critical", delta_color="inverse")
    with col2:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="Critical", delta_color="inverse")
    with col3:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-MLL Gap", f"{avg_we:.1f} pts", delta="Critical", delta_color="inverse")

    st.error(f"**Average White-MLL gap: {avg_we:.0f} pts.** The doubling of the MLL population "
             f"has intensified this gap. Providence (33% MLL, post-state-takeover) and Central "
             f"Falls (45% MLL) bear the heaviest burden with the most limited per-pupil resources.")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('wb_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['wb_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[RI_RED if g > 35 else RI_GOLD for g in gap_sorted['wb_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['wb_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-Black ELA Gap by District (pts)", height=550,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("MLL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='ricas_ela_all', y='ricas_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, RI_BLUE]],
        hover_name='district_name',
        labels={'ricas_ela_all': 'All Students ELA %', 'ricas_ela_el': 'MLL ELA %',
                'el_count': 'MLL Count', 'el_percent': 'MLL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=80, y1=80,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="MLL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("""
    ---
    **Rhode Island context:** The scatter plot starkly illustrates the MLL achievement gap
    across all LEAs. Providence and Central Falls -- the two highest MLL% districts --
    show the lowest overall proficiency AND the largest MLL gaps. The Providence state
    takeover (2019-2024) was intended to address these systemic failures, but the doubling
    of the MLL population has outpaced intervention capacity.
    """)


def render_ricas(ricas_df, districts_df):
    st.header("RICAS Assessment Analysis")
    st.markdown("""
    **Rhode Island Comprehensive Assessment System (RICAS)** -- 4 performance levels:
    Not Meeting Expectations, Partially Meeting Expectations, Meeting Expectations,
    Exceeding Expectations. ELA and Math: grades 3-8.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="ricas_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="ricas_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="ricas_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="ricas_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = ricas_df[
        (ricas_df['district_id'] == district_id) &
        (ricas_df['grade'] == grade) &
        (ricas_df['subject'] == subject) &
        (ricas_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Not Meeting", f"{row['not_meeting_pct']:.1f}%")
        with col2:
            st.metric("Partially Meeting", f"{row['partial_pct']:.1f}%")
        with col3:
            st.metric("Meeting", f"{row['meeting_pct']:.1f}%")
        with col4:
            st.metric("Exceeding", f"{row['exceeding_pct']:.1f}%")

        levels = ['Not Meeting', 'Partially Meeting', 'Meeting', 'Exceeding']
        values = [row['not_meeting_pct'], row['partial_pct'],
                  row['meeting_pct'], row['exceeding_pct']]
        colors = [RI_RED, '#E8540A', RI_GOLD, RI_BLUE]
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"RICAS {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Combined Proficiency (Meeting + Exceeding)",
                  f"{row['proficient_pct']:.1f}%",
                  help="Meeting Expectations + Exceeding Expectations")

        st.subheader(f"RICAS {subject} Across Grades -- {district} ({year})")
        cross = ricas_df[
            (ricas_df['district_id'] == district_id) &
            (ricas_df['subject'] == subject) &
            (ricas_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            col_map = {'Not Meeting': 'not_meeting_pct', 'Partially Meeting': 'partial_pct',
                       'Meeting': 'meeting_pct', 'Exceeding': 'exceeding_pct'}
            for level, color in zip(levels, colors):
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_map[level]],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"RICAS {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(access_df, ricas_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-RI analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ACCESS CSV",
            access_df.to_csv(index=False),
            "vera_ri_access.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("RICAS Data")
        st.dataframe(ricas_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download RICAS CSV",
            ricas_df.to_csv(index=False),
            "vera_ri_ricas.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_ri_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_ri_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-RI | Rhode Island Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {RI_BLUE}; }}
        .stButton > button {{ background-color: {RI_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {RI_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    ricas_df = load_ricas_data(districts_df)
    domain_df = load_statewide_domain_data()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {RI_BLUE}; margin: 0;">VERA-RI</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Rhode Island Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "RICAS Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - RIDE InfoWorks ACCESS Data
    - RIDE InfoWorks Portal
    - RICAS Assessment
    - RI Dept of Education

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points (normalized)

    **RI Exit Criteria:**
    - Composite 4.5+ w/ domain mins

    **Key Context:**
    - ~15,000 MLLs (~11%)
    - 66 LEAs
    - **MLL population doubled**
    - **Providence state takeover**
    - Providence 7,755 MLLs (33%)
    - Central Falls 1,440 MLLs (45%)
    - Spanish dominant (55%)
    - Portuguese/Creole communities
    - RI uses "MLL" terminology

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "ACCESS Analysis":
        render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(access_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "RICAS Analysis":
        render_ricas(ricas_df, districts_df)
    elif page == "Export Data":
        render_export(access_df, ricas_df, districts_df, domain_df)


if __name__ == "__main__":
    main()
