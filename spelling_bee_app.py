import streamlit as st
import pandas as pd
from collections import Counter
from streamlit_gsheets import GSheetsConnection

st.title("🐝 Bee is for Bunny")

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(
    worksheet="Words", 
    ttl="1m"
)
df.drop(['Category'], axis=1,inplace=True)

df_lower = df.map(lambda x: x.lower() if isinstance(x, str) else x)

tab1, tab2 = st.tabs(["Word Groups", "Solver"])

def is_pangram (target_chars, word): 
    return set(target_chars).issubset(word)

def prettify_output(df): 
    s = ''
    if isinstance(df, pd.DataFrame):
        for _, row in df.iterrows():
            for value in row:
                if pd.notna(value):  # Include only non-NaN values
                    s += " - " + str(value)
            s += "\n"
    if isinstance(df, list): 
        for i in df:
            s += "- " + i + "\n"
    st.markdown(s)

def find_word_group(df, target_word): 
    return df[df.isin([target_word]).any(axis=1)]

with tab1:
    target_word = st.text_input("Search for a word").lower().strip()
    if target_word != "": 
        # Search for words in Daddy's word list
        rows_with_value = find_word_group(df_lower, target_word) 
        if rows_with_value.empty: 
            st.write ("No words found using only the letters in '" + target_word + "'")
        else: 
            st.write("Word groups using only the letters in '" + target_word + "'")
            prettify_output(rows_with_value)

        # Search for words that contain letters in your word
        rows_containing_value = df_lower[df_lower.apply(
            lambda row: row.astype(str).str.contains(target_word, case=False, na=False).any(), axis=1)]
        if rows_containing_value.empty: 
            st.write ("No words found containing the letters in '" + target_word + "'")
        else: 
            st.write("Word groups containing the letters in '" + target_word + "'")        
            prettify_output(rows_containing_value)


# what's going on with "none"
def get_score(word, target_characters): 
    if len(word) == 4: 
        return 1
    elif len(word) > 4: 
        score = len(word)
        if is_pangram(target_characters, word): 
            score -= 7 #Normally this would be +=7 for a pangram, but since all pangrams are appended with space**(PANGRAM)**space, which adds 14 points already, we need to subtract 7 to get to the += 7
        return score
    return 0

def show_analytics(df, target_characters): 
    total_words = len(df)
    total_points = sum(get_score(word, target_characters) for word in df)

    st.write ("Number of words: " + str(total_words))
    st.write ("Total points: " + str(total_points))

def filter_words(target_string, golden_letter, df_lower):
    target_characters = set(target_string)
    filtered_words = []
    for column in df_lower.columns:
        for word in df_lower[column]:
            if pd.notna(word):
                has_golden_letter = golden_letter in word
                contains_target_chars = all(char in target_characters for char in word)
                if has_golden_letter and contains_target_chars:
                    if is_pangram(target_characters, word): 
                        filtered_words.append(word + " **(PANGRAM)**")
                    else:
                        filtered_words.append(word)

    return filtered_words

# for any string of letters (even if not a proper word), 
# we could see all the words that are possible from it 
with tab2: 
    target_string = st.text_input("Search for a list of letters").lower().strip()
    golden_letter = st.text_input ("[Optional] Enter the golden letter").strip()

    target_characters = set(target_string)
    if target_string != "": 
        if golden_letter not in target_string: 
            target_string += golden_letter
        # target_string has to have the golden letter AND all of the letters in the target word have to be in the string of letters 
        df_lower_filtered = sorted(filter_words(target_string, golden_letter, df_lower))
        show_analytics(df_lower_filtered, target_characters)
        prettify_output(df_lower_filtered)
