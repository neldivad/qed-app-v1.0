import streamlit as st
import streamlit.components.v1 as components
from streamlit_player import st_player
from streamlit_option_menu import option_menu

import pandas as pd

# Custom imports 
from pages import sf

st.set_page_config(
     page_title="QED Finance | Finance Quite Easily Demonstrated",
     page_icon="https://www.qed-insights.com/content/images/2021/04/qed-mark-black---600.png",
     layout="wide",
     initial_sidebar_state="expanded",
 )

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
def main():
    st.markdown(hide_st_style, unsafe_allow_html=True)
    st.image('./assets/qed-finance.png')
    # Removing and add pages
    pages = {
        'Fundamentals': sf_fundamental,
    }

    st.sidebar.write(' ')
    with st.sidebar:
        st.title('App Navigation')
        page = option_menu("", tuple(pages.keys()), 
            menu_icon="list", default_index=0)

        st.write('---')
        st.title('Resources')
        st.markdown('#### Find me on Twitter')
        components.html("""
        <a href="https://twitter.com/just_neldivad" class="twitter-follow-button" data-show-screen-name="true" data-show-count="true">Follow @just_neldivad</a>
        <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
        """, height=30,)
        st.markdown('#### Or join my discord community.')
        components.html("""
        <iframe src="https://discord.com/widget?id=749377367482433677&theme=dark" width="280" height="380" allowtransparency="true" frameborder="0" sandbox="allow-popups allow-popups-to-escape-sandbox allow-same-origin allow-scripts"></iframe>
        """, height=400)
    pages[page]()

    with st.sidebar.expander('About this app'):
        st.markdown("""
        **Sponsored by:** Zer Platform Ltd
        **Data provider**: [Simfin](https://simfin.com/)
        """)
        

    with st.sidebar:
        st.markdown('''[Make a donation](https://buy.stripe.com/dR6dSreL929i9bycMO)''')
        st.markdown('''<small>QED Finance</small>''', unsafe_allow_html=True)
        st.markdown('''<small>dl.eeee.nv@gmail.com</small>''', unsafe_allow_html=True)

#-------------------
# Page functions
#--------------------
def sf_fundamental():
    sf.sf_fundamentals()


if __name__ == "__main__":
    main()
