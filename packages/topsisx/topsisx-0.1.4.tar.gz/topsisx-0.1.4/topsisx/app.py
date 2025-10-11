"""
TOPSISX Web Interface
Launch with: streamlit run app.py
Or after pip install: topsisx-app
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from topsisx.pipeline import DecisionPipeline
from topsisx.topsis import topsis
from topsisx.vikor import vikor
from topsisx.ahp import ahp
from topsisx.entropy import entropy_weights

# Page configuration
st.set_page_config(
    page_title="TOPSISX - Decision Making Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'data' not in st.session_state:
    st.session_state.data = None

def create_sample_data():
    """Create sample datasets for demonstration"""
    samples = {
        "Laptop Selection": pd.DataFrame({
            'Model': ['Laptop A', 'Laptop B', 'Laptop C', 'Laptop D'],
            'Price': [800, 1200, 1000, 900],
            'RAM_GB': [8, 16, 16, 8],
            'Battery_Hours': [6, 4, 8, 7],
            'Weight_KG': [2.0, 2.5, 1.8, 2.2]
        }),
        "Supplier Selection": pd.DataFrame({
            'Supplier': ['S1', 'S2', 'S3', 'S4', 'S5'],
            'Cost': [250, 200, 300, 275, 225],
            'Quality': [16, 16, 32, 32, 16],
            'Delivery_Time': [12, 8, 16, 8, 16],
            'Service_Rating': [5, 3, 4, 4, 2]
        }),
        "Investment Options": pd.DataFrame({
            'Option': ['Stock A', 'Stock B', 'Stock C', 'Bond X', 'Bond Y'],
            'Expected_Return': [12.5, 8.3, 15.2, 5.5, 6.0],
            'Risk_Level': [7, 4, 9, 2, 3],
            'Liquidity': [8, 9, 6, 7, 8],
            'Min_Investment': [1000, 500, 2000, 100, 200]
        })
    }
    return samples

def plot_results(result_df, method_name):
    """Create visualization of results"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Determine score column
    score_col = None
    if 'Topsis_Score' in result_df.columns:
        score_col = 'Topsis_Score'
    elif 'Q' in result_df.columns:
        score_col = 'Q'
    
    if score_col:
        # Bar chart of scores
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(result_df)))
        ax1.barh(range(len(result_df)), result_df[score_col], color=colors)
        ax1.set_yticks(range(len(result_df)))
        ax1.set_yticklabels([f"Alt {i+1}" for i in range(len(result_df))])
        ax1.set_xlabel('Score', fontsize=12)
        ax1.set_title(f'{method_name} Scores', fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()
    
    # Rank distribution
    rank_counts = result_df['Rank'].value_counts().sort_index()
    ax2.bar(rank_counts.index, rank_counts.values, color='skyblue', edgecolor='navy')
    ax2.set_xlabel('Rank', fontsize=12)
    ax2.set_ylabel('Count', fontsize=12)
    ax2.set_title('Rank Distribution', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    return fig

def get_download_link(df, filename, file_label):
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'
    return href

# Main UI
st.markdown('<h1 class="main-header">📊 TOPSISX Decision Making Tool</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-Criteria Decision Analysis Made Simple</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/decision.png", width=80)
    st.title("⚙️ Configuration")
    
    # Data input method
    st.subheader("1️⃣ Data Input")
    input_method = st.radio(
        "Choose input method:",
        ["Upload CSV", "Use Sample Data", "Manual Entry"],
        help="Select how you want to provide your decision data"
    )
    
    if input_method == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=['csv'],
            help="CSV should have alternatives as rows and criteria as columns"
        )
        
        if uploaded_file:
            try:
                st.session_state.data = pd.read_csv(uploaded_file)
                st.success(f"✅ Loaded {len(st.session_state.data)} rows")
            except Exception as e:
                st.error(f"Error loading file: {e}")
    
    elif input_method == "Use Sample Data":
        samples = create_sample_data()
        sample_choice = st.selectbox("Select sample dataset:", list(samples.keys()))
        st.session_state.data = samples[sample_choice]
        st.info(f"📋 Loaded: {sample_choice}")
    
    else:  # Manual Entry
        st.info("👉 Go to main panel to enter data manually")
    
    st.markdown("---")
    
    # Method selection
    st.subheader("2️⃣ Method Selection")
    
    weighting_method = st.selectbox(
        "Weighting Method:",
        ["Entropy", "Equal", "AHP"],
        help="How to calculate criteria importance"
    )
    
    ranking_method = st.selectbox(
        "Ranking Method:",
        ["TOPSIS", "VIKOR"],
        help="Algorithm for ranking alternatives"
    )
    
    # VIKOR parameter
    if ranking_method == "VIKOR":
        v_param = st.slider(
            "Strategy Weight (v)",
            0.0, 1.0, 0.5, 0.1,
            help="v=0: consensus, v=1: individual regret"
        )
    else:
        v_param = 0.5
    
    st.markdown("---")
    
    # About section
    with st.expander("ℹ️ About TOPSISX"):
        st.markdown("""
        **TOPSISX** is a comprehensive toolkit for Multi-Criteria Decision Making (MCDM).
        
        **Methods Supported:**
        - **TOPSIS**: Ranks based on distance from ideal solution
        - **VIKOR**: Finds compromise solutions
        - **AHP**: Pairwise comparison for weights
        - **Entropy**: Objective weight calculation
        
        **Version**: 0.1.3  
        **Author**: Suvit Kumar
        """)

# Main content area
if input_method == "Manual Entry":
    st.header("📝 Manual Data Entry")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        n_alternatives = st.number_input("Number of Alternatives", 2, 20, 3)
    with col2:
        n_criteria = st.number_input("Number of Criteria", 2, 10, 3)
    
    st.subheader("Enter your data:")
    
    # Create empty dataframe for manual entry
    criteria_names = [st.text_input(f"Criterion {i+1} name", f"C{i+1}", key=f"crit_{i}") 
                      for i in range(n_criteria)]
    
    data_dict = {}
    for i, name in enumerate(criteria_names):
        data_dict[name] = [st.number_input(
            f"Alt {j+1} - {name}", 
            value=0.0, 
            key=f"val_{i}_{j}"
        ) for j in range(n_alternatives)]
    
    if st.button("📥 Load Manual Data"):
        st.session_state.data = pd.DataFrame(data_dict)
        st.success("✅ Data loaded successfully!")

# Display and process data
if st.session_state.data is not None:
    df = st.session_state.data.copy()
    
    st.header("📋 Input Data")
    st.dataframe(df, use_container_width=True)
    
    # Identify numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.error("⚠️ Need at least 2 numeric criteria columns for analysis!")
    else:
        st.success(f"✅ Found {len(numeric_cols)} numeric criteria: {', '.join(numeric_cols)}")
        
        # Impact selection
        st.subheader("3️⃣ Define Impacts")
        st.info("📌 '+' means higher is better (benefit), '-' means lower is better (cost)")
        
        impacts = []
        cols = st.columns(min(4, len(numeric_cols)))
        for i, col_name in enumerate(numeric_cols):
            with cols[i % len(cols)]:
                impact = st.selectbox(
                    f"{col_name}",
                    ['+', '-'],
                    key=f"impact_{i}",
                    help=f"Impact direction for {col_name}"
                )
                impacts.append(impact)
        
        # AHP matrix input if needed
        pairwise_matrix = None
        if weighting_method == "AHP":
            st.subheader("4️⃣ AHP Pairwise Comparison")
            st.info("Enter how much more important row criterion is compared to column criterion (1-9 scale)")
            
            with st.expander("📖 AHP Scale Reference"):
                st.markdown("""
                - **1**: Equal importance
                - **3**: Moderate importance
                - **5**: Strong importance
                - **7**: Very strong importance
                - **9**: Extreme importance
                - **2, 4, 6, 8**: Intermediate values
                """)
            
            # Simple AHP matrix input
            ahp_data = []
            for i in range(len(numeric_cols)):
                row = []
                for j in range(len(numeric_cols)):
                    if i == j:
                        row.append(1.0)
                    elif i < j:
                        val = st.number_input(
                            f"{numeric_cols[i]} vs {numeric_cols[j]}",
                            1.0, 9.0, 1.0, 0.5,
                            key=f"ahp_{i}_{j}"
                        )
                        row.append(val)
                    else:
                        # Reciprocal
                        row.append(1.0 / ahp_data[j][i])
                ahp_data.append(row)
            
            pairwise_matrix = pd.DataFrame(ahp_data)
        
        # Run analysis button
        st.markdown("---")
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            with st.spinner("🔄 Processing..."):
                try:
                    # Create pipeline
                    pipeline = DecisionPipeline(
                        weights=weighting_method.lower(),
                        method=ranking_method.lower(),
                        verbose=False
                    )
                    
                    # Run analysis
                    if ranking_method == "VIKOR":
                        result = pipeline.run(
                            df,
                            impacts=impacts,
                            pairwise_matrix=pairwise_matrix,
                            v=v_param
                        )
                    else:
                        result = pipeline.run(
                            df,
                            impacts=impacts,
                            pairwise_matrix=pairwise_matrix
                        )
                    
                    st.session_state.results = result
                    st.success("✅ Analysis completed successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)

# Display results
if st.session_state.results is not None:
    result = st.session_state.results
    
    st.markdown("---")
    st.header("🏆 Results")
    
    # Results table
    st.subheader("📊 Ranking Table")
    st.dataframe(result, use_container_width=True)
    
    # Download button
    st.download_button(
        label="📥 Download Results (CSV)",
        data=result.to_csv(index=False),
        file_name=f"topsisx_results_{ranking_method.lower()}.csv",
        mime="text/csv"
    )
    
    # Visualization
    st.subheader("📈 Visualization")
    try:
        fig = plot_results(result, ranking_method)
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Could not generate visualization: {e}")
    
    # Top alternatives
    st.subheader("🥇 Top 3 Alternatives")
    top_3 = result.head(3)
    
    cols = st.columns(3)
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            medal = ["🥇", "🥈", "🥉"][i]
            st.markdown(f"### {medal} Rank {int(row['Rank'])}")
            
            # Display non-numeric columns (IDs)
            for col in result.columns:
                if col not in ['Rank', 'Topsis_Score', 'Q', 'S', 'R']:
                    st.metric(col, row[col])
    
    # Detailed statistics
    with st.expander("📊 Detailed Statistics"):
        st.write("**Summary Statistics:**")
        
        score_col = 'Topsis_Score' if 'Topsis_Score' in result.columns else 'Q'
        if score_col in result.columns:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Mean Score", f"{result[score_col].mean():.4f}")
            with col2:
                st.metric("Std Dev", f"{result[score_col].std():.4f}")
            with col3:
                st.metric("Min Score", f"{result[score_col].min():.4f}")
            with col4:
                st.metric("Max Score", f"{result[score_col].max():.4f}")

else:
    # Welcome screen
    if st.session_state.data is None:
        st.info("👈 Please upload data or select a sample dataset from the sidebar to begin")
        
        st.markdown("---")
        st.subheader("🚀 Quick Start Guide")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 1️⃣ Input Data")
            st.markdown("""
            - Upload CSV file
            - Use sample data
            - Enter manually
            """)
        
        with col2:
            st.markdown("### 2️⃣ Configure")
            st.markdown("""
            - Select methods
            - Define impacts
            - Set parameters
            """)
        
        with col3:
            st.markdown("### 3️⃣ Analyze")
            st.markdown("""
            - Run analysis
            - View results
            - Download report
            """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Made with ❤️ using <b>TOPSISX</b> | Version 0.1.3</p>
    <p>For support: <a href='https://github.com/SuvitKumar003/ranklib'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)