# ══════════════════════════════════════════════════
# WINE QC DASHBOARD — DIRECTORY
# ══════════════════════════════════════════════════
# Structure:
# [1] Imports                    ~ line 15
# [2] Data Loading               ~ line 30
# [3] Outline(Sidebar & Filters) ~ line 65
# [4] Page 1 — Executive Summary  ~ line 125
# [5] Page 2 — Parameter Profiles ~ line 217
# [6] Page 3 — SPC Analysis       ~ line 352
# [7] Page 4 — Quality Drivers    ~ line 570
# [8] Page 5 — Red vs White       ~ line 768
# ══════════════════════════════════════════════════

# ══════════════════════════════════════════
# ---- IMPORTS -----
# ══════════════════════════════════════════
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')


# ══════════════════════════════════════════
# ---- DATA LOADING -----
# ══════════════════════════════════════════
@st.cache_data
def load_data():
    # Build path relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, '..', 'data', 'processed', 'wine_combined.csv')
    spc_path = os.path.join(base_dir, '..', 'data', 'processed', 'spc_summary.csv')
    
    df = pd.read_csv(data_path)
    spc = pd.read_csv(spc_path)
    return df, spc

df, spc_summary = load_data()

# ── PARAMETERS LIST ──
params = ['fixed acidity', 'volatile acidity', 'citric acid',
          'residual sugar', 'chlorides', 'free sulfur dioxide',
          'total sulfur dioxide', 'density', 'pH',
          'sulphates', 'alcohol']

# ── SPEC LIMITS ──
spec_limits = {
    'volatile acidity':    {'LSL': 0.08, 'USL': 1.2},
    'pH':                  {'LSL': 2.9,  'USL': 4.0},
    'sulphates':           {'LSL': 0.25, 'USL': 1.5},
    'alcohol':             {'LSL': 8.5,  'USL': 15.0},
    'free sulfur dioxide': {'LSL': 10.0, 'USL': 60.0},
    'chlorides':           {'LSL': 0.005,'USL': 0.20},
}

# ── COLOR MAP ──
color_map = {'Red': 'crimson', 'White': 'palegoldenrod'}

# ══════════════════════════════════════════
# ---- PAGE OUTLINE -----
# ══════════════════════════════════════════

# ── PAGE CONFIGURATION ──
st.set_page_config(
    page_title="Wine Quality Control Dashboard",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── SIDEBAR ──
st.sidebar.image("https://img.icons8.com/emoji/96/wine-glass-emoji.png", width=80)
st.sidebar.title("🍷 Wine Quality Control Dashboard")
st.sidebar.markdown("---")
st.sidebar.markdown("### Filters")

wine_filter = st.sidebar.multiselect(
    "Wine Type",
    options=['Red', 'White'],
    default=['Red', 'White']
)

tier_filter = st.sidebar.multiselect(
    "Quality Tier",
    options=['Low', 'Medium', 'High'],
    default=['Low', 'Medium', 'High']
)

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "A Quality Control analysis of 6,500 wine batches "
    "using Statistical Process Control, "
    "Cpk analysis and regulatory standards."
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Dataset:** [UCI Wine Quality](https://archive.ics.uci.edu/dataset/186/wine+quality)"
)
st.sidebar.markdown(
    "**Standards:** OIV Annex C | EU Reg 606/2009"
)

# ── APPLY FILTERS ──
filtered = df[
    (df['wine_type'].isin(wine_filter)) &
    (df['quality_tier'].isin(tier_filter))
]

# ── PAGES ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary",
    "🔬 Parameter Profiles",
    "📈 SPC Analysis",
    "🎯 Quality Drivers",
    "⚗️ Red vs White"
])

# ══════════════════════════════════════════
# PAGE 1 — EXECUTIVE SUMMARY
# ══════════════════════════════════════════
with tab1:
    # ── PROBLEM STATEMENT ──
    st.title("🍷 Wine Quality Control Dashboard")
    st.markdown("---")
    
    st.markdown("### A Data Science Approach to Quality Control")
    st.markdown(
        "**What makes a good wine — and can chemistry tell us before we taste it?**"
    )
    st.markdown(
        "This dashboard applies Quality Control (QC) frameworks "
        "to red & white wine samples. "
        "It answers the following questions: "
        "**is this process in control, are parameters "
        "within spec and what does a failing batch look like chemically?**"
    )
    
    st.markdown("---")

    # ── KPI CARDS ──
    st.subheader("📌 Key Quality Metrics")
    k1, k2, k3, k4 = st.columns(4)

    total = len(filtered)
    pass_pct = round(
        len(filtered[filtered['qc_status'] == 'Pass']) / total * 100, 1) if total > 0 else 0

    # Always calculate both wine type averages from full dataset
    avg_red = round(df[df['wine_type'] == 'Red']['quality'].mean(), 2)
    avg_white = round(df[df['wine_type'] == 'White']['quality'].mean(), 2)

    # Show selected wine type avg dynamically
    if len(wine_filter) == 1:
        selected_wtype = wine_filter[0]
        other_wtype = 'White' if selected_wtype == 'Red' else 'Red'
        selected_avg = avg_red if selected_wtype == 'Red' else avg_white
        other_avg = avg_white if selected_wtype == 'Red' else avg_red
        delta_label = f"{round(selected_avg - other_avg, 2):+.2f} vs {other_wtype}"
        quality_label = f"Avg Quality — {selected_wtype}"
    else:
        selected_avg = round(filtered['quality'].mean(), 2) if total > 0 else 0
        delta_label = f"{round(avg_red - avg_white, 2):+.2f} Red vs White"
        quality_label = "Avg Quality — Both"

    critical_params = len(spc_summary[spc_summary['Verdict'] == '🚨 Out of Control'])

    with k1:
        st.metric("Total Batches Analysed", f"{total:,}")
    with k2:
        st.metric("QC Pass Rate", f"{pass_pct}%",
                  delta=f"{pass_pct - 50:.1f}% vs 50% baseline")
    with k3:
        st.metric(quality_label, selected_avg, delta=delta_label)
    with k4:
        st.metric("Critical Parameters", critical_params,
                  delta="Require immediate action",
                  delta_color="inverse")

    st.markdown("---")

    # ── ROW 1: QUALITY DISTRIBUTION + PASS FAIL ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Quality Score Distribution")
        fig = px.histogram(filtered, x='quality', color='wine_type',
                           nbins=7,
                           color_discrete_map=color_map,
                           labels={'quality': 'Quality Score',
                                   'wine_type': 'Wine Type'},
                           opacity=1.0)
        fig.update_layout(
            paper_bgcolor='#E8E8E8',
            plot_bgcolor="#E0DFDF",
            yaxis_title='Number of Samples',
            legend_title='Wine Type',
            xaxis=dict(tickmode='linear', dtick=1),
            yaxis=dict(gridcolor="#FFFCFC"),
            bargap=0.1,
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("QC Pass / Fail by Wine Type")
        
        status_counts = filtered.groupby(
            ['wine_type', 'qc_status']).size().reset_index(name='count')
        fig2 = px.sunburst(status_counts,
                           path=['wine_type', 'qc_status'],
                           values='count',
                           color='wine_type',
                           color_discrete_map=color_map)
        fig2.update_traces(root_color='#E8E8E8', marker=dict(line=dict(color="#D8D6D6", width=2)))  # dark border between segments)
        fig2.update_layout(paper_bgcolor='#E8E8E8', height=350)
        st.plotly_chart(fig2, use_container_width=True)

        st.caption(
            "    **Pass** = Quality score ≥ 6 |  **Fail** = Quality score < 6 "
        )

    st.markdown("---")

    # ── ROW 2: PARAMETER STATUS TABLE ──
    st.subheader("📋 Parameter Health Summary")
    st.markdown("*Based on OIV/EU Regulation 606/2009 spec limits — Food Industry Cpk threshold ≥ 1.0*")
    st.caption(
    "✅ **In Control** — Cpk ≥ 1.0 AND OOS < 1% | "
    "⚠️ **Monitor** — Cpk < 1.0 OR OOS 1–5% | "
    "🚨 **Out of Control** — Cpk < 0.67 OR OOS > 5% "
    )

    # Colour verdict column
    def colour_verdict(val):
        if '🚨' in str(val):
            return 'background-color: #f8d7da'
        elif '⚠️' in str(val):
            return 'background-color: #fff3cd'
        elif '✅' in str(val):
            return 'background-color: #d4edda'
        return ''

    styled = spc_summary.style.map(
        colour_verdict, subset=['Verdict']
    )
    st.dataframe(styled, use_container_width=True, height=430)


# ══════════════════════════════════════════
# PAGE 2 PARAMETER PROFILES
# ══════════════════════════════════════════
with tab2:
    st.title("🔬 Parameter Profiles")
    st.markdown("*Comprehensive Analysis of 11 physicochemical parameters across the wine types and quality tiers*")
    st.markdown("Use the **parameter selector** to drill into any variable and **the heatmap** "
    "to explore which parameters are most strongly linked to one another & quality scores.")
    st.markdown("---")

    # ── PARAMETER SELECTOR ──
    selected_param = st.selectbox(
        "Select Parameter to Explore",
        options=params,
        index=0
    )

    st.markdown("---")

    # ── ROW 1: BOX PLOT + VIOLIN PLOT ──
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"{selected_param.title()} — Red vs White")
        fig = px.box(filtered,
                     x='wine_type',
                     y=selected_param,
                     color='wine_type',
                     color_discrete_map=color_map,
                     points=False,
                     labels={'wine_type': 'Wine Type',
                             selected_param: selected_param.title()})

        # Add spec limit lines if parameter has defined limits
        if selected_param in spec_limits:
            fig.add_hline(y=spec_limits[selected_param]['USL'],
                         line_dash='dot', line_color='orange',
                         annotation_text=f"USL: {spec_limits[selected_param]['USL']}")
            fig.add_hline(y=spec_limits[selected_param]['LSL'],
                         line_dash='dot', line_color='orange',
                         annotation_text=f"LSL: {spec_limits[selected_param]['LSL']}")

        # Add sensory threshold for volatile acidity
        if selected_param == 'volatile acidity':
            fig.add_hline(y=0.7, line_dash='dashdot',
                         line_color='purple',
                         annotation_text='⚠️ Sensory threshold: 0.7 g/L')

        fig.update_layout(
            paper_bgcolor='#E8E8E8',
            plot_bgcolor='white',
            showlegend=False,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader(f"{selected_param.title()} — By Quality Tier")
        fig2 = px.box(filtered,
                      x='quality_tier',
                      y=selected_param,
                      color='wine_type',
                      color_discrete_map=color_map,
                      points=False,
                      category_orders={'quality_tier': ['Low', 'Medium', 'High']},
                      labels={'quality_tier': 'Quality Tier',
                              selected_param: selected_param.title(),
                              'wine_type': 'Wine Type'})
        fig2.update_layout(
            paper_bgcolor='#E8E8E8',
            plot_bgcolor='white',
            legend_title='Wine Type',
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── ROW 2: DISTRIBUTION HISTOGRAM ──
    st.subheader(f"{selected_param.title()} — Full Distribution")
    fig3 = px.histogram(filtered,
                        x=selected_param,
                        color='wine_type',
                        nbins=40,
                        color_discrete_map=color_map,
                        opacity=0.7,
                        labels={selected_param: selected_param.title(),
                                'wine_type': 'Wine Type'})

    # Add spec limits if available
    if selected_param in spec_limits:
        fig3.add_vline(x=spec_limits[selected_param]['USL'],
                      line_dash='dot', line_color='orange',
                      annotation_text=f"USL: {spec_limits[selected_param]['USL']}")
        fig3.add_vline(x=spec_limits[selected_param]['LSL'],
                      line_dash='dot', line_color='orange',
                      annotation_text=f"LSL: {spec_limits[selected_param]['LSL']}")

    fig3.update_layout(
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        yaxis_title='Number of Samples',
        legend_title='Wine Type',
        height=350
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── ROW 3: CORRELATION HEATMAP ──
    st.subheader("Correlation Heatmap")
    st.markdown("*How do parameters relate to each other and to quality score?*")

    st.markdown(
        "Each cell shows the relationship between two parameters, "
        "ranging from **-1.0** (-ve relationship) to **+1.0** (+ve relationship). "
        "**Darker cells = stronger relationships.** "
    )
    st.caption(
        "💡 To explore how parameters affect quality scores specifically, see the Quality Drivers page."
    )
    st.markdown("---")

    heatmap_wine = st.radio(
        "Select Wine Type",
        options=['Red', 'White'],
        horizontal=True
    )

    corr_data = filtered[filtered['wine_type'] == heatmap_wine][params + ['quality']].corr()

    fig4, ax = plt.subplots(figsize=(12, 8))
    cmap = 'Reds' if heatmap_wine == 'Red' else 'YlOrBr'

    st.info("**Alcohol** is the leading driver for quality of both red and white wines")
    sns.heatmap(corr_data,
                annot=True,
                fmt='.2f',
                cmap=cmap,
                ax=ax,
                annot_kws={'size': 8},
                linewidths=0.5)
    ax.set_title(f'{heatmap_wine} Wine — Correlation Matrix', fontsize=14)
    fig4.patch.set_facecolor('#E8E8E8')
    st.pyplot(fig4)
    plt.close()

    


# ══════════════════════════════════════════
#  PAGE 3 SPC ANALYSIS
# ══════════════════════════════════════════
with tab3:
    st.title("📈 SPC Analysis")
    st.markdown("*Statistical Process Control — Are these wine production processes in control?*")
    st.markdown("---")

    # ── CONTROL CHART SECTION ──
    st.subheader("🎛️ I-MR Control Charts")
    st.markdown("*Points beyond ±3σ are flagged as Out of Control (OOC). Orange dotted lines show OIV/EU spec limits.*")

    col1, col2 = st.columns(2)
    with col1:
        chart_param = st.selectbox(
            "Select Parameter",
            options=list(spec_limits.keys()),
            index=0
        )
    with col2:
        chart_wine = st.radio(
            "Wine Type",
            options=['Red', 'White'],
            horizontal=True
        )

    # Build control chart
    subset = df[df['wine_type'] == chart_wine][chart_param].reset_index(drop=True)
    mean = subset.mean()
    std = subset.std()
    ucl = mean + 3*std
    lcl = mean - 3*std
    ooc = (subset > ucl) | (subset < lcl)
    ooc_count = ooc.sum()
    ooc_pct = round(ooc_count/len(subset)*100, 1)

    fig = go.Figure()

    # In control points
    fig.add_trace(go.Scatter(
        x=subset[~ooc].index,
        y=subset[~ooc].values,
        mode='markers',
        name='In Control',
        marker=dict(color='steelblue', size=4, opacity=0.5)
    ))

    # OOC points
    fig.add_trace(go.Scatter(
        x=subset[ooc].index,
        y=subset[ooc].values,
        mode='markers',
        name='Out of Control',
        marker=dict(color='red', size=6, symbol='x')
    ))

    # Lines
    fig.add_hline(y=mean, line_dash='solid', line_color='green',
                  annotation_text=f'Mean: {mean:.3f}')
    fig.add_hline(y=ucl, line_dash='dash', line_color='red',
                  annotation_text=f'UCL: {ucl:.3f}')
    fig.add_hline(y=lcl, line_dash='dash', line_color='red',
                  annotation_text=f'LCL: {lcl:.3f}')
    fig.add_hline(y=spec_limits[chart_param]['USL'],
                  line_dash='dot', line_color='orange',
                  annotation_text=f"USL: {spec_limits[chart_param]['USL']}")
    fig.add_hline(y=spec_limits[chart_param]['LSL'],
                  line_dash='dot', line_color='orange',
                  annotation_text=f"LSL: {spec_limits[chart_param]['LSL']}")

    # Three zone system for volatile acidity
    if chart_param == 'volatile acidity':
        fig.add_hline(y=0.7, line_dash='dashdot', line_color='purple',
                      annotation_text='⚠️ Sensory threshold: 0.7 g/L',
                      annotation_position='top right')
        fig.add_hrect(y0=spec_limits[chart_param]['LSL'], y1=0.7,
                      fillcolor='green', opacity=0.05,
                      annotation_text='Ideal zone',
                      annotation_position='right')
        fig.add_hrect(y0=0.7, y1=spec_limits[chart_param]['USL'],
                      fillcolor='orange', opacity=0.05,
                      annotation_text='Warning zone',
                      annotation_position='right')
        fig.add_hrect(y0=spec_limits[chart_param]['USL'],
                      y1=subset.max()+0.1,
                      fillcolor='red', opacity=0.05,
                      annotation_text='Out of spec zone',
                      annotation_position='right')

    fig.update_layout(
        title=f'Control Chart — {chart_param.title()} ({chart_wine} Wine) | '
              f'OOC: {ooc_count} points ({ooc_pct}%)',
        xaxis_title='Sample Index',
        yaxis_title=chart_param.title(),
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        height=450,
        legend=dict(orientation='h', y=-0.2),
        yaxis=dict(gridcolor='#F0F0F0'),
        xaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── CPK BAR CHART ──
    st.subheader("⚙️ Process Capability (Cpk)")
    st.markdown("*Threshold: Cpk ≥ 1.0 = Capable | 0.67–1.0 = Marginal | < 0.67 = Incapable*")

    d2 = 1.128

    cpk_results = []
    for param, spec in spec_limits.items():
        for wtype in ['Red', 'White']:
            s = df[df['wine_type'] == wtype][param].dropna().reset_index(drop=True)
            mean_v = s.mean()
            sigma = s.diff().abs().dropna().mean() / d2
            cpu = (spec['USL'] - mean_v) / (3 * sigma)
            cpl = (mean_v - spec['LSL']) / (3 * sigma)
            cpk = round(min(cpu, cpl), 3)
            status = (' Capable' if cpk >= 1.0
                      else ' Marginal' if cpk >= 0.67
                      else ' Incapable')
            cpk_results.append({
                'Parameter': param,
                'Wine Type': wtype,
                'Cpk': cpk,
                'Status': status
            })

    cpk_df = pd.DataFrame(cpk_results)
    cpk_df = cpk_df.sort_values('Cpk', ascending=False)  #see
    cpk_df['Parameter & Wine'] = cpk_df['Parameter'] + ' (' + cpk_df['Wine Type'] + ')'

    # PLOT SECTION
    fig2 = px.bar(cpk_df,
                  x='Parameter & Wine',
                  y='Cpk',
                  color='Status',
                  title='Process Capability (Cpk) — OIV & EU Reg 606/2009',
                  color_discrete_map={
                      ' Capable':   'seagreen',
                      ' Marginal': 'orange',
                      ' Incapable':'crimson'
                  },
                  text='Cpk',
                  labels={'Parameter & Wine': '',
                          'Cpk': 'Cpk Value'})

    fig2.add_hline(y=1.0, line_dash='dash', line_color='black',
                   annotation_text='Capable (1.0)',
                   annotation_position='top right')
    fig2.add_hline(y=0.67, line_dash='dot', line_color='grey',
                   annotation_text='Marginal (0.67)',
                   annotation_position='top right')

    fig2.update_traces(textposition='outside', textfont_size=9)
    fig2.update_layout(
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        height=500,
        xaxis_tickangle=-35,
        legend_title='Status',
        margin=dict(r=150, b=120, t=80),
        yaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig2, use_container_width=True)

    # CALLOUT SECTION 
    cap_count = len(cpk_df[cpk_df['Status'].str.contains('Capable')])
    mar_count = len(cpk_df[cpk_df['Status'].str.contains('Marginal')])
    inc_count = len(cpk_df[cpk_df['Status'].str.contains('Incapable')])

    st.markdown(
        f"**Summary:** {cap_count} capable ✅ | "
        f"{mar_count} marginal ⚠️ | "
        f"{inc_count} incapable ❌ across both wine types"
        )
    st.warning(
    "🚨 **Key finding:** Free sulphur dioxide is incapable in both wine types "
    "(Red Cpk: 0.234, White Cpk: 0.591) — representing the main "
    "process control failure in this dataset. One in three red wine batches "
    "falls below the minimum preservation threshold."
    )   

    st.markdown("---")

    # ── OOS FREQUENCY CHART ──
    st.subheader("🚨 Out-of-Spec (OOS) Frequency")
    st.markdown("*How many batches fall outside OIV/EU spec limits per parameter?*")

    oos_results = []
    for param, spec in spec_limits.items():
        for wtype in ['Red', 'White']:
            s = df[df['wine_type'] == wtype][param]
            oos_total = ((s < spec['LSL']) | (s > spec['USL'])).sum()
            oos_pct = round(oos_total / len(s) * 100, 1)
            oos_results.append({
                'Parameter': param,
                'Wine Type': wtype,
                'OOS %': oos_pct,
                'OOS Count': int(oos_total),
                'Total Samples': len(s)
            })

    oos_df = pd.DataFrame(oos_results)

        # Compute total OOS per parameter (across both wine types)
    param_order = (
        oos_df.groupby('Parameter')['OOS %']
        .mean()   # you can also use .max() if you want worst-case emphasis
        .sort_values(ascending=False)
        .index.to_list()
    )

    # Convert Parameter to ordered categorical
    oos_df['Parameter'] = pd.Categorical(
        oos_df['Parameter'],
        categories=param_order,
        ordered=True
    )
    oos_df = oos_df.sort_values('Parameter')

    # PLOT

    fig3 = px.bar(oos_df,
              x='Parameter',
              y='OOS %',
              color='Wine Type',
              barmode='group',
              color_discrete_map=color_map,
              text='OOS %',
              title='Out-of-Spec Frequency based on OIV/EU Standards',
              labels={'OOS %': 'OOS Rate (%)', 'Parameter': ''},
              custom_data=['OOS Count', 'Total Samples', 'Wine Type'])
    
        # Critical threshold line at 5%
    fig3.add_hline(y=5.0,
                line_dash='dash',
                line_color='red',
                line_width=1.5,
                annotation_text='🚨 Critical threshold (5%)',
                annotation_position='top right',
                annotation_font_color='red')

    # Hover template with OOS count
    fig3.update_traces(
        textposition='outside',
        textfont_size=9,
        hovertemplate=(
            "<b>%{customdata[2]} Wine — %{x}</b><br>"
            "OOS Rate: %{y}%<br>"
            "OOS Count: %{customdata[0]} batches<br>"
            "Total Samples: %{customdata[1]}<br>"
            "<extra></extra>"
        )
    )
    fig3.update_layout(
    paper_bgcolor='#E8E8E8',
    plot_bgcolor='white',
    height=500,
    xaxis_tickangle=-30,
    legend_title='Wine Type',
    margin=dict(r=150, b=120, t=80),
    yaxis=dict(gridcolor='#F0F0F0'),
    xaxis=dict(gridcolor='#F0F0F0')
    )

    st.plotly_chart(fig3, use_container_width=True)

        # ── TWO CLEAN CHEMISTRY NOTES ──
    col_note1, col_note2 = st.columns(2)

    with col_note1:
        st.info(
             "⚗️ **Chemistry Note:** Red wine's higher free SO₂ OOS rate (33.1%) reflects "
            "its lower SO₂ requirements due to tannin antioxidant protection, "
            "not a process failure."
            "\n\nThis highlights a limitation of applying uniform spec limits across both wine types.\n\n"
        )

    with col_note2:
        st.warning(
            "⚠️ **High OOS** rates for Free SO₂ are common but this often indicates " \
            "inconsistent SO₂ addition protocols during production." 
            "\n\n This is the main process control challenge in this dataset "
            "and corrective action is needed regardless of wine type."
        )

    st.markdown("---")

    # ── PHASE 3 SUMMARY TABLE ──
    st.subheader("📋 SPC Summary Table")
    st.markdown("*Overall Verdict: Process Stability, Capability, & Specification Compliance*")

    def colour_verdict(val):
        if '🚨' in str(val) or 'Incapable' in str(val):
            return 'background-color: #f8d7da'
        elif '⚠️' in str(val) or 'Marginal' in str(val):
            return 'background-color: #fff3cd'
        elif '✅' in str(val) or 'Capable' in str(val):
            return 'background-color: #d4edda'
        return ''
    

    # Formatting copy of New DF
    spc_display = spc_summary.copy()

    styled_spc = spc_display.style\
        .applymap(colour_verdict, subset=['Verdict', 'Cpk Status'])\
        .format({'OOC %': '{:.1f}', 'Cpk': '{:.3f}', 'OOS %': '{:.1f}'})

    st.dataframe(styled_spc, use_container_width=True, height=430, hide_index=True)

    with st.expander("ℹ️ How are verdicts assigned?", expanded=False):
        st.markdown("""
        📊 **How verdicts are assigned:**
        Each parameter is evaluated on two criteria simultaneously:
        **process capability (Cpk)** measures how consistently the process
        stays within spec limits, while **Out-of-Spec rate (OOS %)** measures
        how many batches actually failed those limits.
        A parameter only needs to fail **one** of the two criteria to receive
        the worse verdict.
        
        | Verdict | Cpk | OOS % | Meaning |
        |---|---|---|---|
        | ✅ In Control | ≥ 1.0 | ≤ 1% | Process is capable and compliant |
        | ⚠️ Monitor | < 1.0 | 1–5% | Process is borderline — monitor closely |
        | 🚨 Out of Control | < 0.67 | > 5% | Process is failing — corrective action needed |
        """)

# ══════════════════════════════════════════
# PAGE 4 — QUALITY DRIVERS
# ══════════════════════════════════════════
with tab4:
    st.title("🎯 Quality Drivers")
    st.markdown("**What chemical parameters drive wine quality up or down? \n"
                " What does the chemical profile look like for low and high quality wines?**")
    st.markdown("---")

    # ── ROW 1: CORRELATION BAR CHARTS ──
    st.subheader("📊 Quality Driver Correlation Analysis")
    st.markdown("*Correlation of each parameter against quality score. Red = negative driver, Blue = positive driver.*")

    col1, col2 = st.columns(2)

    for col, wtype in zip([col1, col2], ['Red', 'White']):
        with col:
            st.markdown(f"**{wtype} Wine**")
            corr = df[df['wine_type'] == wtype][params + ['quality']].corr()['quality'].drop('quality').sort_values()
            bar_colors = ['crimson' if x < 0 else 'steelblue' for x in corr.values]

            fig = go.Figure(go.Bar(
                x=corr.values,
                y=corr.index,
                orientation='h',
                marker_color=bar_colors,
                text=[f'{v:.2f}' for v in corr.values],
                textposition='outside'
            ))
            fig.add_vline(x=0, line_color='black', line_width=0.8)
            fig.update_layout(
                paper_bgcolor='#E8E8E8',
                plot_bgcolor='white',
                height=400,
                xaxis=dict(range=[-0.6, 0.6], gridcolor='#F0F0F0'),
                yaxis=dict(gridcolor='#F0F0F0'),
                margin=dict(l=150, r=80)
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ── ROW 2: SCATTER PLOTS ──
    st.subheader("🔍 Parameter vs Quality Score")
    st.markdown("*Explore the relationship between any parameter and its quality score*")

    col1, col2 = st.columns(2)
    with col1:
        scatter_param = st.selectbox(
            "Select Parameter",
            options=params,
            index=params.index('alcohol')
        )
    with col2:
        scatter_wine = st.multiselect(
            "Wine Type",
            options=['Red', 'White'],
            default=['Red', 'White']
        )

    scatter_data = df[df['wine_type'].isin(scatter_wine)]

    fig2 = px.scatter(scatter_data,
                      x=scatter_param,
                      y='quality',
                      color='wine_type',
                      trendline='ols',
                      color_discrete_map=color_map,
                      opacity=0.4,
                      labels={scatter_param: scatter_param.title(),
                              'quality': 'Quality Score',
                              'wine_type': 'Wine Type'})
    fig2.update_layout(
        paper_bgcolor="#D1CFCF",
        plot_bgcolor='white',
        height=400,
        legend_title='Wine Type',
        yaxis=dict(gridcolor='#F0F0F0'),
        xaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ── ROW 3: LOW VS HIGH QUALITY PROFILE ──
    st.subheader("⚗️ Low vs High Quality — Chemical Profile")
    st.markdown("*Comparison of Average parameter values for Low (≤5) vs High (≥8) quality wines*")

    profile_wine = st.radio(
        "Select Wine Type",
        options=['Red', 'White'],
        horizontal=True,
        key='profile_radio'
    )

    top_params = ['volatile acidity', 'alcohol', 'sulphates',
                  'citric acid', 'pH', 'chlorides']

    profile_data = df[
        (df['wine_type'] == profile_wine) &
        (df['quality_tier'].isin(['Low', 'High']))
    ]

    means = profile_data.groupby('quality_tier')[top_params].mean().reset_index()
    melted = means.melt(id_vars='quality_tier',
                        var_name='Parameter',
                        value_name='Mean Value')
    melted = melted.sort_values('Mean Value', ascending=False)  #see
    

    fig3 = px.bar(melted,
                  x='Parameter',
                  y='Mean Value',
                  color='quality_tier',
                  barmode='group',
                  color_discrete_map={'Low': 'tomato', 'High': 'seagreen'},
                  text_auto='.2f',
                  title=f'{profile_wine} Wine — Low vs High Quality Chemical Profile',
                  labels={'Mean Value': 'Mean Value',
                          'quality_tier': 'Quality Tier'})
    fig3.update_layout(
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        height=400,
        xaxis_tickangle=-30,
        legend_title='Quality Tier',
        yaxis=dict(gridcolor='#F0F0F0'),
        xaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── ROW 4: ROOT CAUSE TABLE ──
    st.subheader("🔎 Root Cause Analysis Summary")
    st.caption("Process status cross-referenced with quality impact per parameter")
# -------------------------------------------------------------------
    st.markdown("""
        ### Key Insight
        White wines show higher instability in alcohol and sulfur dioxide parameters, 
        while red wines remain largely within acceptable control limits.
    """)

    root_causes = {
        'volatile acidity': 'Indicates microbial spoilage risk',
        'pH':              'Indicates acid imbalance due to grape variety or fermentation',
        'sulphates':       'Might indicate Inconsistent SO₂ addition protocol',
        'alcohol':          'Signals incomplete fermentation',
        'free sulfur dioxide': 'Might indicate inconsistent SO₂ addition. Signals preservation risk',
        'chlorides':        'Indicates terroir variation due to water source or soil salinity',
    }
    
    rca_rows = []
    for param, spec in spec_limits.items():
        for wtype in ['Red', 'White']:
            subset = df[df['wine_type'] == wtype]
            oos_count = ((subset[param] < spec['LSL']) |
                        (subset[param] > spec['USL'])).sum()
            oos_pct = round(oos_count / len(subset) * 100, 1)

            in_spec = subset[
                (subset[param] >= spec['LSL']) &
                (subset[param] <= spec['USL'])
            ]['quality'].mean()
            out_spec = subset[
                (subset[param] < spec['LSL']) |
                (subset[param] > spec['USL'])
            ]['quality'].mean()
            delta = round(out_spec - in_spec, 3) if oos_count > 0 else 0.0

            quality_risk = ('🚨 High' if delta < -0.5
                        else '⚠️ Medium' if delta < 0
                        else '✅ Low')

            spc_row = spc_summary[
                (spc_summary['Parameter'] == param) &
                (spc_summary['Wine Type'] == wtype)
            ]
        
            verdict = spc_row['Verdict'].values[0] if len(spc_row) > 0 else 'N/A'

            rca_rows.append({
                'Wine Type':     wtype,
                'Parameter':     param,
                'Process Status':   verdict,
                'Out-Of-Spec %':         oos_pct,
                'Deviation': delta,
                'Quality Risk':  quality_risk,
                'Likely Cause':    root_causes[param]
            })

    rca_df = pd.DataFrame(rca_rows)
    
    # ── CHEMISTRY NOTES ──
    st.markdown("#### 🔬 Chemistry Note")

    title = "## Root Causes of Quality Drop or Spoilage in Parameters"
    formatted_text = "\n\n".join([f"**{k}**: {v}" for k, v in root_causes.items()])

    st.info(f"{title}\n\n{formatted_text}")

    # ── SUMMARY TABLE (BRIEF) ──
    st.markdown("#### 📋 Summary View")

    summary_df = rca_df[
    ['Wine Type', 'Parameter', 'Process Status', 'Quality Risk']
    ]

    def colour_verdict(val):
        if '🚨' in str(val):
            return 'background-color: #f8d7da'
        elif '⚠️' in str(val):
            return 'background-color: #fff3cd'
        elif '✅' in str(val):
            return 'background-color: #d4edda'
        return ''

    styled_summary = summary_df.style.applymap(
        colour_verdict, subset=['Process Status', 'Quality Risk']
    )
    st.dataframe(styled_summary, use_container_width=True) #height=430)

    # ── DETAILED VIEW (HIDDEN) ──
    with st.expander("See detailed metrics"):
        def colour_rca(val):
            if '🚨' in str(val):
                return 'background-color: #f8d7da'
            elif '⚠️' in str(val):
                return 'background-color: #fff3cd'
            elif '✅' in str(val):
                return 'background-color: #d4edda'
            return ''

        styled_rca = rca_df.style.applymap(
            colour_rca, subset=['Process Status', 'Quality Risk']
        )
        st.dataframe(styled_rca, use_container_width=True)

# ══════════════════════════════════════════
# PAGE 5 — RED VS WHITE WINE COMPARISON
# ══════════════════════════════════════════
with tab5:
    st.title("⚗️ Red Wine vs White Wine")
    st.markdown("*Red and white wine are chemically distinct products requiring separate quality standards, this section compares them*")
    st.markdown("---")


    # ── ROW 1: SIDE BY SIDE BAR CHART ──
    st.subheader("🍷 Average Parameter Values — Red vs White")
    st.markdown("*How do the chemical profiles of red and white wine differ on average?*")

    # Calculate means per wine type
    avg_params = df.groupby('wine_type')[params].mean().reset_index()
    melted_avg = avg_params.melt(id_vars='wine_type',
                                var_name='Parameter',
                                value_name='Mean Value')

    # Parameter selector for focus
    selected_params = st.multiselect(
        "Select Parameters to Display",
        options=params,
        default=['volatile acidity', 'alcohol', 'pH',
                'sulphates', 'chlorides', 'citric acid', 'residual sugar']
    )

    filtered_avg = melted_avg[melted_avg['Parameter'].isin(selected_params)]

    fig = px.bar(filtered_avg,
                x='Parameter',
                y='Mean Value',
                color='wine_type',
                barmode='group',
                color_discrete_map=color_map,
                text_auto='.3f',
                title='Average Chemical Profile — Red vs White Wine',
                labels={'Mean Value': 'Mean Value',
                        'Parameter': '',
                        'wine_type': 'Wine Type'})

    fig.update_layout(
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        height=450,
        xaxis_tickangle=-30,
        legend_title='Wine Type',
        yaxis=dict(gridcolor='#F0F0F0'),
        xaxis=dict(gridcolor='#F0F0F0')
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── ROW 2: SO2 BINDING RATIO ──
    st.subheader("🧪 SO₂ Binding Ratio by Quality Tier")
    st.markdown("*Free SO₂ / Total SO₂ — measures active preservation efficiency. Higher ratio = better protected wine.*")

    col1, col2 = st.columns([2, 1])

    with col1:
        fig2 = px.box(filtered,
                      x='quality_tier',
                      y='SO2_binding_ratio',
                      color='wine_type',
                      category_orders={'quality_tier': ['Low', 'Medium', 'High']},
                      color_discrete_map=color_map,
                      points=False,
                      labels={'SO2_binding_ratio': 'Free SO₂ / Total SO₂',
                              'quality_tier': 'Quality Tier',
                              'wine_type': 'Wine Type'})
        fig2.add_annotation(
            text="Higher ratio = more active SO₂ preservation",
            xref="paper", yref="paper",
            x=0.5, y=1.08,
            showarrow=False,
            font=dict(size=11, color="grey")
        )
        fig2.update_layout(
            paper_bgcolor='#E8E8E8',
            plot_bgcolor='white',
            legend_title='Wine Type',
            height=400,
            yaxis=dict(gridcolor='#F0F0F0'),
            xaxis=dict(gridcolor='#F0F0F0')
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("#### 🔬 Chemistry Note")
        st.info(
            "SO₂ exists in two forms in wine:\n\n"
            "**Free SO₂** — active, unbound, providing actual antimicrobial "
            "and antioxidant protection.\n\n"
            "**Bound SO₂** — chemically attached to sugars and aldehydes, "
            "providing no protective function.\n\n"
            "White wine has higher total SO₂ but more binding occurs due to "
            "higher residual sugar — making the ratio a more meaningful "
            "quality metric than total SO₂ alone."
        )

    st.markdown("---")

    # ── ROW 3: SIDE BY SIDE CPK COMPARISON ──
    st.subheader("⚙️ Process Capability Comparison — Red vs White")
    st.markdown("*Using the same parameters & limits, which type of wine performs better within standards?*")

    d2 = 1.128
    cpk_compare = []

    for param, spec in spec_limits.items():
        for wtype in ['Red', 'White']:
            s = df[df['wine_type'] == wtype][param].dropna().reset_index(drop=True)
            mean_v = s.mean()
            sigma = s.diff().abs().dropna().mean() / d2
            cpu = (spec['USL'] - mean_v) / (3 * sigma)
            cpl = (mean_v - spec['LSL']) / (3 * sigma)
            cpk = round(min(cpu, cpl), 3)
            status = ('✅ Capable' if cpk >= 1.0
                      else '⚠️ Marginal' if cpk >= 0.67
                      else '❌ Incapable')
            cpk_compare.append({
                'Parameter': param,
                'Wine Type': wtype,
                'Cpk': cpk,
                'Status': status
            })

    cpk_compare_df = pd.DataFrame(cpk_compare)

    fig3 = px.bar(cpk_compare_df,
                  x='Parameter',
                  y='Cpk',
                  color='Wine Type',
                  barmode='group',
                  color_discrete_map=color_map,
                  text='Cpk',
                  facet_col='Wine Type',
                  title='Cpk Comparison — Red vs White Wine',
                  labels={'Cpk': 'Cpk Value', 'Parameter': ''})

    fig3.add_hline(y=1.0, line_dash='dash', line_color='black',
                   annotation_text='Capable (1.0)',
                   annotation_position='top left')
    fig3.add_hline(y=0.67, line_dash='dot', line_color='grey',
                   annotation_text='Marginal (0.67)',
                   annotation_position='top left')

    fig3.update_traces(textposition='outside', textfont_size=9)
    fig3.update_layout(
        paper_bgcolor='#E8E8E8',
        plot_bgcolor='white',
        height=500,
        xaxis_tickangle=-30,
        xaxis2_tickangle=-30,
        showlegend=False,
        margin=dict(r=150, b=120, t=80),
        yaxis=dict(gridcolor='#F0F0F0')
    )
    fig3.for_each_annotation(lambda a: a.update(
        text=a.text.replace('Wine Type=', ''),
        font=dict(size=13)
    ))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")

    # ── ROW 4: STATISTICAL SUMMARY TABLE ──
    st.subheader("📋 Statistical Summary — Red vs White")
    st.markdown("*Mean and standard deviation of all parameters by wine type*")

    summary_stats = df.groupby('wine_type')[params].agg(['mean', 'std']).round(3)
    summary_stats.columns = [f'{col[0]} ({col[1]})' for col in summary_stats.columns]
    st.dataframe(summary_stats, use_container_width=True)
