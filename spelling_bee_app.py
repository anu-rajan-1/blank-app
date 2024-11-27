import streamlit as st
import pandas as pd
from collections import Counter

st.title("🐝 Bee is for Bunny")

file_path = 'SpellingBee_Nov24.csv'
df = pd.read_csv ('SpellingBee_Nov24.csv')
df_lower = df.map(lambda x: x.lower() if isinstance(x, str) else x)

tab1, tab2, tab3 = st.tabs(["Word Groups", "Solver", "Add Words"])

def is_pangram (target_chars, word): 
    return set(target_chars).issubset(word)

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


# load in unique and unique_4 sheets 
# what's going on with "none"
# allow daddy to add new word groups, add to an existing word group, or add unique words


# for any string of letters (even if not a proper word), 
# we could see all the words that are possible from it 
with tab2: 
    target_string = st.text_input("Search for a list of letters").lower().strip()
    golden_letter = st.text_input ("[Optional] Enter the golden letter").strip()

    if target_string != "": 
        if golden_letter not in target_string: 
            target_string += golden_letter
        # target_string has to have the golden letter AND all of the letters in the target word have to be in the string of letters 
        df_lower_filtered = sorted(filter_words(target_string, golden_letter, df_lower))
        prettify_output(df_lower_filtered)

def insert_word_if_not_exists(df, row_index, word):
    """
    Inserts a word into a specific row of a Pandas DataFrame only if the word doesn't already exist in that row.

    :param df: The Pandas DataFrame.
    :param row_index: The index of the row where the word should be inserted.
    :param word: The word to insert.
    :return: Updated DataFrame.
    """
    # Get the row as a list of strings (excluding NaN values)
    row_values = df.loc[row_index].dropna().tolist()

    # Check if the word already exists in the row
    if word not in row_values:
        # Find the first empty column index
        empty_cols = df.columns[df.loc[row_index].isna()]
        if not empty_cols.empty:
            df.loc[row_index, empty_cols[0]] = word
    return df

with tab3: 
    changelog_file_path = 'dictionary_changelog.csv'
    # Read the single-column CSV into a DataFrame
    changelog_df = pd.read_csv(changelog_file_path, header=None, names=["Column"])


    target_word = st.text_input("Enter the word you want to add").lower().strip()
    if target_word != "": 
        target_letters = set(target_word)
        
        # Iterate through rows and update where the set of letters matches
        # Get all words in the row, ignoring NaN values
        # Iterate through rows
        within_case = False

        for index, row in df_lower.iterrows():
            row_words = row.dropna().tolist()
            if target_word in row_words: #Word is already present 
                st.write ("Word is already present in this word group:")
                st.markdown(row_words)
                within_case = True

            # Check if any word in the row matches the target letters
            elif any(set(word) == target_letters for word in row_words): #Add to an existing word group
                # Find the first empty column in the row
                empty_cols = df_lower.columns[row.isna()]
                if not empty_cols.empty:
                    # Assign the target_word to the first empty column
                    df_lower.loc[index, empty_cols[0]] = target_word
                    st.write ("Added word to an existing word group: ")
                    st.markdown (df_lower.loc[index].dropna().tolist())
                    within_case = True

                    # Append the new value as a new row
                    changelog_df.loc[len(changelog_df)] = target_word
                    st.write(changelog_df)
                    
        if not within_case: #New word group
            new_row = [target_word] + [None] * (len(df_lower.columns) - 1)
            df_lower.loc[len(df_lower)] = new_row
            st.write ("Added " + target_word + " to form new word group")
            
            changelog_df.loc[len(changelog_df)] = target_word

        # Save the updated DataFrame back to the CSV
        df_lower.to_csv(file_path, index=False)

        changelog_df.to_csv(changelog_file_path, index=False, header=False)



# Test CSV reading 

# Define the specific number of columns you want to check for
#row_counts = data_dictionary.notna().sum(axis=1)

# target_column_count = 1

# Count the rows with the exact number of non-null columns
# rows_with_target_columns = (row_counts == target_column_count).sum()

# Debug print to inspect row_counts
# st.write("Row counts (non-null values per row):")
# st.write(row_counts)
# st.write(f"Number of rows with {target_column_count} columns: {rows_with_target_columns}")