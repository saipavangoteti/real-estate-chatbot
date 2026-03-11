import streamlit as st
import pandas as pd
import os
import io
from datetime import datetime

# ── Page config must be first ─────────────────────────────────────────────────
st.set_page_config(
    page_title="LuxeEstate AI",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from config import (
    GROQ_API_KEY, APP_TITLE, COMPANY_NAME, AGENT_NAME,
    COMPANY_PHONE, COMPANY_EMAIL, PROPERTIES_CSV, LEADS_CSV,
)
from utils.data_manager import (
    load_properties, load_leads, format_price, update_lead_status,
)

# ── Inject custom CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.main-header h1 {
    font-family: 'Playfair Display', serif;
    color: #e8d5b0;
    font-size: 2rem;
    margin: 0;
}

.main-header p {
    color: #a8b2c8;
    margin: 0;
    font-size: 0.9rem;
}

.chat-container {
    background: #f8f9fc;
    border-radius: 16px;
    padding: 1.5rem;
    min-height: 450px;
    max-height: 550px;
    overflow-y: auto;
    border: 1px solid #e2e8f0;
}

.user-bubble {
    background: linear-gradient(135deg, #0f3460, #1a1a2e);
    color: white;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    margin: 0.5rem 0 0.5rem auto;
    max-width: 75%;
    width: fit-content;
    font-size: 0.93rem;
    line-height: 1.5;
    float: right;
    clear: both;
}

.bot-bubble {
    background: white;
    color: #1a1a2e;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    margin: 0.5rem auto 0.5rem 0;
    max-width: 78%;
    width: fit-content;
    font-size: 0.93rem;
    line-height: 1.5;
    float: left;
    clear: both;
    border: 1px solid #e2e8f0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.bot-avatar {
    display: inline-block;
    background: linear-gradient(135deg, #e8d5b0, #c9a96e);
    color: #1a1a2e;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    text-align: center;
    line-height: 28px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-right: 6px;
    vertical-align: middle;
}

.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    border: 1px solid #e2e8f0;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.metric-card .metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0f3460;
}

.metric-card .metric-label {
    font-size: 0.8rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.property-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border: 1px solid #e2e8f0;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}

.property-card:hover {
    box-shadow: 0 4px 16px rgba(15,52,96,0.12);
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-available { background: #d1fae5; color: #065f46; }
.badge-sold      { background: #fee2e2; color: #991b1b; }
.badge-pending   { background: #fef3c7; color: #92400e; }

.quick-btn {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.82rem;
    cursor: pointer;
    margin: 0.2rem;
    color: #0f3460;
    transition: all 0.2s;
}
.quick-btn:hover { background: #0f3460; color: white; border-color: #0f3460; }

.stTextInput > div > div > input {
    border-radius: 25px !important;
    border: 2px solid #e2e8f0 !important;
    padding: 0.6rem 1.2rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #0f3460 !important;
    box-shadow: 0 0 0 3px rgba(15,52,96,0.1) !important;
}

div[data-testid="stSidebar"] {
    background: #1a1a2e;
}

div[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

.clearfix::after { content: ""; display: table; clear: both; }

.typing-indicator {
    display: flex;
    gap: 4px;
    padding: 10px 14px;
    background: white;
    border-radius: 18px;
    width: fit-content;
    border: 1px solid #e2e8f0;
}

.typing-dot {
    width: 8px; height: 8px;
    background: #a0aec0;
    border-radius: 50%;
    animation: typing 1.2s infinite;
}

@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); }
    30% { transform: translateY(-8px); }
}
</style>
""", unsafe_allow_html=True)


# ── Initialize Session State ──────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "agent_error" not in st.session_state:
    st.session_state.agent_error = None
if "pending_input" not in st.session_state:
    st.session_state.pending_input = ""


# ── Load / Init Agent ─────────────────────────────────────────────────────────
def init_agent():
    if st.session_state.agent is None:
        api_key = st.session_state.get("groq_key_input") or GROQ_API_KEY
        if not api_key:
            return False
        try:
            os.environ["GROQ_API_KEY"] = api_key
            from chatbot import build_agent
            st.session_state.agent = build_agent()
            st.session_state.agent_error = None
            return True
        except Exception as e:
            st.session_state.agent_error = str(e)
            return False
    return True


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding: 1rem 0;'>
        <div style='font-size:2.5rem'>🏠</div>
        <div style='font-family: Playfair Display, serif; font-size:1.3rem; color:#e8d5b0; font-weight:700;'>{APP_TITLE}</div>
        <div style='font-size:0.78rem; color:#94a3b8; margin-top:4px;'>{COMPANY_NAME}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["💬 Chat", "🏘️ Properties", "📋 Leads", "⚙️ Settings"],
        label_visibility="collapsed",
    )

    st.markdown("---")

    # API Key input
    st.markdown("<small style='color:#94a3b8'>GROQ API KEY</small>", unsafe_allow_html=True)
    api_input = st.text_input(
        "Groq API Key",
        value=GROQ_API_KEY,
        type="password",
        key="groq_key_input",
        label_visibility="collapsed",
        placeholder="gsk_...",
    )
    if api_input and api_input != GROQ_API_KEY:
        st.session_state.agent = None  # force re-init

    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:0.78rem; color:#94a3b8; line-height:1.8;'>
        📞 {COMPANY_PHONE}<br>
        📧 {COMPANY_EMAIL}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CHAT
# ═══════════════════════════════════════════════════════════════════════════════
if "💬 Chat" in page:

    st.markdown(f"""
    <div class='main-header'>
        <div style='font-size:2.5rem'>🏠</div>
        <div>
            <h1>{APP_TITLE}</h1>
            <p>Powered by Groq · LangChain · {AGENT_NAME} is ready to assist you</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Init agent
    agent_ready = init_agent()

    if not agent_ready:
        st.warning("⚠️ Please add your **Groq API Key** in the sidebar to activate the chatbot.")
        if st.session_state.agent_error:
            st.error(f"Error: {st.session_state.agent_error}")
        st.stop()

    # Quick action chips
    st.markdown("**Quick Actions:**")
    cols = st.columns(6)
    quick_actions = [
        ("🏠 Show Properties", "Show me all available properties"),
        ("🔍 Search 2BHK", "Search for 2BHK apartments under 60 lakhs"),
        ("📅 Site Visit", "I want to schedule a site visit"),
        ("📞 Consultation", "Book a consultation call"),
        ("💰 EMI Calculator", "Help me calculate EMI for 50 lakhs loan"),
        ("📍 Locations", "What locations do you have properties in?"),
    ]
    for i, (label, action) in enumerate(quick_actions):
        with cols[i]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                st.session_state.pending_input = action

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat display
    chat_html = "<div class='chat-container'>"
    if not st.session_state.chat_history:
        chat_html += f"""
        <div style='text-align:center; padding:3rem 1rem; color:#94a3b8;'>
            <div style='font-size:3rem; margin-bottom:1rem'>🏡</div>
            <div style='font-family:Playfair Display,serif; font-size:1.2rem; color:#0f3460; margin-bottom:0.5rem'>
                Hello! I'm {AGENT_NAME}
            </div>
            <div style='font-size:0.9rem'>
                Your AI Real Estate Assistant. Ask me anything about properties,<br>
                site visits, consultations, EMI calculations and more!
            </div>
        </div>
        """
    else:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                chat_html += f"<div class='user-bubble'>{msg['content']}</div>"
            else:
                safe = msg["content"].replace("\n", "<br>")
                chat_html += f"""
                <div class='bot-bubble'>
                    <span class='bot-avatar'>A</span>
                    {safe}
                </div>
                """
    chat_html += "<div class='clearfix'></div></div>"
    st.markdown(chat_html, unsafe_allow_html=True)

    # Input row
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Message",
            value=st.session_state.pending_input,
            placeholder=f"Ask {AGENT_NAME} anything about real estate...",
            key="chat_input",
            label_visibility="collapsed",
        )
    with col_btn:
        send_clicked = st.button("Send ➤", use_container_width=True, type="primary")

    # Process input
    if (send_clicked or st.session_state.pending_input) and (user_input or st.session_state.pending_input):
        final_input = user_input or st.session_state.pending_input
        st.session_state.pending_input = ""

        st.session_state.chat_history.append({"role": "user", "content": final_input})

        with st.spinner(f"{AGENT_NAME} is thinking..."):
            try:
                from chatbot import get_response
                response = get_response(
                    st.session_state.agent,
                    final_input,
                    st.session_state.chat_history[:-1],
                )
            except Exception as e:
                response = f"I encountered an error: {str(e)}. Please try again."

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Clear chat
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PROPERTIES MANAGER
# ═══════════════════════════════════════════════════════════════════════════════
elif "🏘️ Properties" in page:
    st.markdown("### 🏘️ Property Listings Manager")
    st.caption("Add, edit, or remove properties. Changes are saved to `data/properties.csv`.")

    df = load_properties()

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{len(df)}</div>
            <div class='metric-label'>Total Properties</div></div>""", unsafe_allow_html=True)
    with c2:
        avail = len(df[df["status"] == "Available"]) if not df.empty else 0
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{avail}</div>
            <div class='metric-label'>Available</div></div>""", unsafe_allow_html=True)
    with c3:
        types = df["type"].nunique() if not df.empty else 0
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{types}</div>
            <div class='metric-label'>Property Types</div></div>""", unsafe_allow_html=True)
    with c4:
        cities = df["city"].nunique() if not df.empty else 0
        st.markdown(f"""<div class='metric-card'>
            <div class='metric-value'>{cities}</div>
            <div class='metric-label'>Cities</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 View & Edit", "➕ Add Property", "📤 Import / Export"])

    with tab1:
        if df.empty:
            st.info("No properties found. Add some properties first.")
        else:
            edited = st.data_editor(
                df,
                use_container_width=True,
                num_rows="dynamic",
                key="prop_editor",
                column_config={
                    "price": st.column_config.NumberColumn("Price (₹)", format="₹%d"),
                    "area_sqft": st.column_config.NumberColumn("Area (sq.ft)"),
                    "status": st.column_config.SelectboxColumn(
                        "Status", options=["Available", "Sold", "Pending", "Reserved"]
                    ),
                    "type": st.column_config.SelectboxColumn(
                        "Type", options=["Apartment", "Villa", "Plot", "Commercial", "Studio", "Penthouse"]
                    ),
                },
            )
            if st.button("💾 Save Changes", type="primary", key="save_props"):
                edited.to_csv(PROPERTIES_CSV, index=False)
                st.success("✅ Properties saved successfully!")
                st.session_state.agent = None  # rebuild agent with new data

    with tab2:
        st.markdown("#### Add New Property")
        with st.form("add_property_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_name     = st.text_input("Property Name *")
                p_type     = st.selectbox("Type *", ["Apartment", "Villa", "Plot", "Commercial", "Studio", "Penthouse"])
                p_location = st.text_input("Locality *")
                p_city     = st.text_input("City *")
                p_price    = st.number_input("Price (₹) *", min_value=0, step=100000)
            with c2:
                p_beds  = st.number_input("Bedrooms", min_value=0, max_value=20, value=2)
                p_baths = st.number_input("Bathrooms", min_value=0, max_value=20, value=2)
                p_area  = st.number_input("Area (sq.ft)", min_value=0, step=50)
                p_status = st.selectbox("Status", ["Available", "Sold", "Pending", "Reserved"])
                p_amenities = st.text_input("Amenities (comma separated)")
            p_desc = st.text_area("Description")

            if st.form_submit_button("➕ Add Property", type="primary"):
                if p_name and p_city and p_location:
                    existing = load_properties()
                    new_id = f"P{len(existing)+1:03d}" if not existing.empty else "P001"
                    new_row = pd.DataFrame([{
                        "id": new_id, "name": p_name, "type": p_type,
                        "location": p_location, "city": p_city, "price": p_price,
                        "bedrooms": p_beds, "bathrooms": p_baths, "area_sqft": p_area,
                        "amenities": p_amenities, "status": p_status,
                        "description": p_desc, "image_url": "",
                    }])
                    updated = pd.concat([existing, new_row], ignore_index=True)
                    updated.to_csv(PROPERTIES_CSV, index=False)
                    st.session_state.agent = None
                    st.success(f"✅ Property '{p_name}' added with ID {new_id}!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")

    with tab3:
        col_imp, col_exp = st.columns(2)
        with col_imp:
            st.markdown("#### 📥 Import CSV")
            uploaded = st.file_uploader("Upload properties CSV", type=["csv"])
            if uploaded:
                imported = pd.read_csv(uploaded)
                st.dataframe(imported.head())
                if st.button("✅ Confirm Import"):
                    imported.to_csv(PROPERTIES_CSV, index=False)
                    st.session_state.agent = None
                    st.success(f"Imported {len(imported)} properties!")
                    st.rerun()
        with col_exp:
            st.markdown("#### 📤 Export CSV")
            if not df.empty:
                csv_data = df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Properties CSV",
                    data=csv_data,
                    file_name="properties.csv",
                    mime="text/csv",
                )
            st.markdown("#### 📋 Template")
            template = pd.DataFrame(columns=[
                "id","name","type","location","city","price","bedrooms",
                "bathrooms","area_sqft","amenities","status","description","image_url"
            ])
            st.download_button(
                "⬇️ Download Template",
                data=template.to_csv(index=False).encode("utf-8"),
                file_name="properties_template.csv",
                mime="text/csv",
            )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: LEADS / CRM
# ═══════════════════════════════════════════════════════════════════════════════
elif "📋 Leads" in page:
    st.markdown("### 📋 Leads & Bookings CRM")
    st.caption("All site visit requests and consultation bookings from the chatbot.")

    leads_df = load_leads()

    # Stats
    c1, c2, c3, c4 = st.columns(4)
    total = len(leads_df)
    visits = len(leads_df[leads_df["inquiry_type"] == "Site Visit"]) if not leads_df.empty else 0
    consults = len(leads_df[leads_df["inquiry_type"] == "Consultation"]) if not leads_df.empty else 0
    new_leads = len(leads_df[leads_df["status"] == "New"]) if not leads_df.empty else 0

    for col, val, label in zip(
        [c1, c2, c3, c4],
        [total, visits, consults, new_leads],
        ["Total Leads", "Site Visits", "Consultations", "New (Action Needed)"],
    ):
        with col:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-value'>{val}</div>
                <div class='metric-label'>{label}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if leads_df.empty:
        st.info("🎉 No leads yet! Start chatting to generate leads.")
    else:
        # Filters
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            type_filter = st.multiselect(
                "Filter by Type",
                options=leads_df["inquiry_type"].unique().tolist(),
            )
        with fc2:
            status_filter = st.multiselect(
                "Filter by Status",
                options=leads_df["status"].unique().tolist(),
            )
        with fc3:
            search_q = st.text_input("🔍 Search by name/email", placeholder="Search...")

        filtered = leads_df.copy()
        if type_filter:
            filtered = filtered[filtered["inquiry_type"].isin(type_filter)]
        if status_filter:
            filtered = filtered[filtered["status"].isin(status_filter)]
        if search_q:
            mask = (
                filtered["name"].str.lower().str.contains(search_q.lower(), na=False) |
                filtered["email"].str.lower().str.contains(search_q.lower(), na=False)
            )
            filtered = filtered[mask]

        st.dataframe(
            filtered,
            use_container_width=True,
            column_config={
                "status": st.column_config.SelectboxColumn(
                    "Status", options=["New", "Contacted", "Scheduled", "Completed", "Lost"]
                ),
            },
        )

        col_dl, col_clr = st.columns([2, 1])
        with col_dl:
            st.download_button(
                "⬇️ Export Leads CSV",
                data=filtered.to_csv(index=False).encode("utf-8"),
                file_name=f"leads_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary",
            )
        with col_clr:
            if st.button("🗑️ Clear All Leads", type="secondary"):
                if st.session_state.get("confirm_clear"):
                    pd.DataFrame(columns=leads_df.columns).to_csv(LEADS_CSV, index=False)
                    st.success("Leads cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm deletion.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif "⚙️ Settings" in page:
    st.markdown("### ⚙️ Settings & Configuration")

    tab1, tab2 = st.tabs(["🔑 API & Model", "🏢 Embed on Website"])

    with tab1:
        st.markdown("#### Groq API Configuration")
        st.info("Update your `.env` file with these settings for permanent configuration.")

        with st.expander("📄 .env File Reference", expanded=True):
            st.code("""
# ── Required ──────────────────────
GROQ_API_KEY=your_groq_api_key_here

# ── Model (optional) ──────────────
GROQ_MODEL=llama-3.3-70b-versatile
# Other options:
# GROQ_MODEL=mixtral-8x7b-32768
# GROQ_MODEL=gemma2-9b-it

# ── Company Branding ──────────────
APP_TITLE=LuxeEstate AI Assistant
COMPANY_NAME=LuxeEstate Realty
AGENT_NAME=Aria
COMPANY_PHONE=+91-9876543210
COMPANY_EMAIL=info@luxeestate.com
COMPANY_WEBSITE=https://luxeestate.com
            """, language="bash")

        if st.button("🔄 Reinitialize Agent", type="primary"):
            st.session_state.agent = None
            if init_agent():
                st.success("✅ Agent reinitialized successfully!")
            else:
                st.error("❌ Failed to initialize. Check your API key.")

    with tab2:
        st.markdown("#### 🌐 Embed on Any Website")
        st.markdown("Deploy your chatbot and embed it using an iframe:")

        st.markdown("**Step 1 – Deploy to Streamlit Cloud**")
        st.code("""
# 1. Push your project to GitHub
# 2. Go to https://share.streamlit.io
# 3. Connect your GitHub repo
# 4. Add GROQ_API_KEY in Secrets section
# 5. Deploy and copy your app URL
        """, language="bash")

        st.markdown("**Step 2 – Embed with iframe**")
        app_url = st.text_input("Your Streamlit App URL", placeholder="https://your-app.streamlit.app")
        if app_url:
            embed_code = f"""<!-- Real Estate Chatbot Widget -->
<div id="realestate-chatbot" style="position:fixed; bottom:20px; right:20px; z-index:9999;">
  <button onclick="toggleChat()" style="
    background: linear-gradient(135deg, #0f3460, #1a1a2e);
    color: #e8d5b0; border: none; border-radius: 50%;
    width: 60px; height: 60px; font-size: 1.5rem;
    cursor: pointer; box-shadow: 0 4px 20px rgba(0,0,0,0.3);">
    🏠
  </button>
  <iframe id="chat-iframe"
    src="{app_url}?embedded=true"
    style="display:none; position:fixed; bottom:90px; right:20px;
           width:400px; height:600px; border:none;
           border-radius:16px; box-shadow:0 8px 40px rgba(0,0,0,0.3);">
  </iframe>
</div>
<script>
  function toggleChat() {{
    var iframe = document.getElementById('chat-iframe');
    iframe.style.display = iframe.style.display === 'none' ? 'block' : 'none';
  }}
</script>"""
            st.code(embed_code, language="html")
            st.download_button(
                "⬇️ Download Embed Code",
                data=embed_code,
                file_name="chatbot_embed.html",
                mime="text/html",
            )

        st.markdown("**Step 3 – Custom Domain (Optional)**")
        st.code("""
# Using nginx reverse proxy:
location /chatbot {
    proxy_pass http://localhost:8501;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
        """, language="nginx")
