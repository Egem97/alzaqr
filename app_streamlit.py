import streamlit as st
from router.core import pages

def main():    
    st.set_page_config(
        page_title="PACKING TOOL",
        page_icon="src/assets/logo.jpg",
        layout="wide",
    )

    # Show logo
    st.logo("./src/assets/logo.jpg")    

    # Show main navigation
    pg = st.navigation(pages())
    pg.run()

if __name__ == "__main__":
    main()







    













