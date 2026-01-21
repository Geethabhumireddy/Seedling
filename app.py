import streamlit as st
import json
from dotenv import load_dotenv
load_dotenv()

from github_utils import fetch_github_issue
from hf import analyze_issue_with_ai
from cache_utils import get_cached_analysis, cache_analysis

# Page configuration
st.set_page_config(
    page_title="Issue Analyzer - Seedlings Lab",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "input"
if "result" not in st.session_state:
    st.session_state.result = None
if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""
if "issue_number" not in st.session_state:
    st.session_state.issue_number = 0

# Unique Modern CSS with Seedlings Lab branding
st.markdown("""
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f4c3a 100%);
            min-height: 100vh;
        }
        
        .main { background: transparent !important; }
        
        /* Hero Header */
        .hero-container {
            background: linear-gradient(135deg, #1e293b 0%, #0f4c3a 100%);
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            text-align: center;
        }
        
        .hero-container h1 {
            font-size: 2.8em;
            font-weight: 800;
            background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .hero-container p {
            font-size: 1.1em;
            color: #cbd5e1;
            font-weight: 300;
            letter-spacing: 0.5px;
        }
        
        .brand-tag {
            display: inline-block;
            background: rgba(6, 182, 212, 0.2);
            color: #06b6d4;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            margin-top: 10px;
            border: 1px solid rgba(6, 182, 212, 0.4);
        }
        
        /* Input Section */
        .input-container {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(6, 182, 212, 0.2);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }
        
        .input-label {
            color: #cbd5e1;
            font-weight: 600;
            font-size: 0.95em;
            margin-bottom: 8px;
            display: block;
        }
        
        /* Analysis Results */
        .results-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .result-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(6, 182, 212, 0.3);
            border-radius: 12px;
            padding: 24px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .result-card:hover {
            border-color: rgba(6, 182, 212, 0.6);
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(6, 182, 212, 0.2);
        }
        
        .result-card.summary {
            grid-column: 1 / -1;
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.4);
        }
        
        .result-card h3 {
            color: #06b6d4;
            font-size: 1.1em;
            margin-bottom: 15px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .result-card p {
            color: #e2e8f0;
            line-height: 1.6;
            font-size: 0.95em;
        }
        
        /* Priority Circle */
        .priority-circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            font-weight: bold;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        
        .priority-1 { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
        .priority-2 { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); }
        .priority-3 { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
        .priority-4 { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
        .priority-5 { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); }
        
        .priority-num { font-size: 2.2em; line-height: 1; }
        .priority-text { font-size: 0.75em; opacity: 0.9; }
        
        /* Type Badge */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .badge-bug { background: rgba(239, 68, 68, 0.2); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.5); }
        .badge-feature { background: rgba(16, 185, 129, 0.2); color: #86efac; border: 1px solid rgba(16, 185, 129, 0.5); }
        .badge-documentation { background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.5); }
        .badge-question { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5); }
        .badge-other { background: rgba(107, 114, 128, 0.2); color: #d1d5db; border: 1px solid rgba(107, 114, 128, 0.5); }
        
        /* Labels */
        .labels-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .label-tag {
            background: rgba(6, 182, 212, 0.15);
            color: #06b6d4;
            padding: 6px 12px;
            border-radius: 14px;
            font-size: 0.85em;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }
        
        /* Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
        }
        
        /* Footer */
        .footer-container {
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid rgba(6, 182, 212, 0.2);
            text-align: center;
            color: #64748b;
        }
        
        .seedlings-logo {
            font-size: 1.2em;
            font-weight: 700;
            color: #06b6d4;
            margin-bottom: 5px;
        }
        
        .footer-text {
            font-size: 0.9em;
            color: #94a3b8;
            line-height: 1.6;
        }
        
        hr {
            border: none;
            border-top: 1px solid rgba(6, 182, 212, 0.2);
            margin: 20px 0;
        }
    </style>
""", unsafe_allow_html=True)

# PAGE 1: INPUT PAGE
if st.session_state.page == "input":
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h1>Issue Analyzer</h1>
            <p>Intelligent GitHub Issue Classification & Analysis</p>
            <div class="brand-tag">Powered by Seedlings Lab</div>
        </div>
    """, unsafe_allow_html=True)

    # Input Section
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown('<label class="input-label">GitHub Repository URL</label>', unsafe_allow_html=True)
        repo_url = st.text_input(
            "label",
            placeholder="https://github.com/facebook/react",
            label_visibility="collapsed"
        )

    with col2:
        st.markdown('<label class="input-label">Issue Number</label>', unsafe_allow_html=True)
        issue_number = st.number_input(
            "number",
            min_value=1,
            step=1,
            label_visibility="collapsed"
        )

    with col3:
        st.markdown('<label class="input-label">&nbsp;</label>', unsafe_allow_html=True)
        analyze_button = st.button("Analyze", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Handle Analysis
    if analyze_button:
        if not repo_url or not issue_number:
            st.error("Enter repository URL and issue number.")
        else:
            result = None
            # Check cache first
            cached_result = get_cached_analysis(repo_url, issue_number)
            if cached_result:
                result = cached_result
            else:
                with st.spinner("Fetching issue..."):
                    issue_data = fetch_github_issue(repo_url, issue_number)

                if "error" in issue_data:
                    st.error(f"Error: {issue_data['error']}")
                else:
                    with st.spinner("Analyzing with AI..."):
                        result = analyze_issue_with_ai(issue_data)
                    
                    if result and "error" not in result:
                        cache_analysis(repo_url, issue_number, result)

            if result and "error" not in result:
                st.session_state.result = result
                st.session_state.repo_url = repo_url
                st.session_state.issue_number = issue_number
                st.session_state.page = "results"
                st.rerun()

    # Footer
    st.markdown("""
        <div class="footer-container">
            <hr style='border: none; border-top: 1px solid rgba(6, 182, 212, 0.2);'>
            <div class="seedlings-logo">Seedlings Lab</div>
            <div class="footer-text">
                Intelligent Issue Analysis Platform<br>
                Powered by AI • Built with Purpose<br>
                <small>© 2026 Seedlings Lab. All rights reserved.</small>
            </div>
        </div>
    """, unsafe_allow_html=True)

# PAGE 2: RESULTS PAGE
elif st.session_state.page == "results":
    # Back Button at Top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Back to Input", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.result = None
            st.rerun()
    
    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h2 style='color: #06b6d4; margin: 0;'>Analysis Results</h2>
            </div>
        """, unsafe_allow_html=True)

    # Issue Information
    st.markdown(f"""
        <div class="result-card summary">
            <h3>Repository: {st.session_state.repo_url}</h3>
            <p style='margin: 5px 0 0 0; font-size: 0.9em;'>Issue #{st.session_state.issue_number}</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Display JSON Result
    st.markdown("""
        <div class="result-card">
            <h3>Analysis Output</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.json(st.session_state.result)

    # Action Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Back to Input", use_container_width=True, key="back_bottom"):
            st.session_state.page = "input"
            st.session_state.result = None
            st.rerun()
    with col2:
        if st.button("Copy JSON", use_container_width=True):
            st.success("JSON ready for copy!")
    with col3:
        if st.button("New Analysis", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.result = None
            st.rerun()

    # Footer
    st.markdown("""
        <div class="footer-container">
            <hr style='border: none; border-top: 1px solid rgba(6, 182, 212, 0.2);'>
            <div class="seedlings-logo">Seedlings Lab</div>
            <div class="footer-text">
                Intelligent Issue Analysis Platform<br>
                Powered by AI • Built with Purpose<br>
                <small>© 2026 Seedlings Lab. All rights reserved.</small>
            </div>
        </div>
    """, unsafe_allow_html=True)
