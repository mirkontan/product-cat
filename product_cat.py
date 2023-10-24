import streamlit as st
import pandas as pd
import base64
import io
import jieba
from collections import Counter


product_cat_dict = {
    '炖': 'Stew Pot',
    "多士炉": "Toaster",
    "咖啡机": "Coffee Machine",
    "咖啡杯": "Coffee Cup",
    "热水壶": "Kettle",
    '炖锅': "Cooking Pot",
    '杯盖子底座': 'Coaster',
    '保温杯': 'Thermos',
    '奶泡': 'Milk Frother',
    '平底炒锅':'Flat Pan',
    '烧水壶': 'Kettle',
    '球琅锅': 'Stew Pot',
    '平底锅': 'Stew Pot',
    '不粘锅': 'Stew Pot',
    '搅拌机': 'Blender',
    '锅具': 'Pot Set',
    '厨师机': 'Stand Mixer',
    '料理机': 'Stand Mixer',
    '木砧板': 'Cutting Board',
    '咖啡磨豆机': 'Coffee Grinder',
    '冰箱': 'Fridge',
    '咖啡载杯': 'Travel Cup',
    '随行杯': 'Travel Cup',
    '咖啡配套': 'Coffee Kit',
    '汁机': 'Juicer',
    '磨豆机': 'Cofee Grinder',
    '咖啡豆研磨机': 'Cofee Grinder',
    '咖啡磨粉机': 'Cofee Grinder',
    '搅拌榨汁': 'Blender',
    '油烟机': 'Range Hood',
    "燃气灶": "Gas Stove",
    "家用灶具": "Gas Stove",
    '挂烫机': 'Steamer',
    '餐具': 'Tableware Set',
    "食品加工机": 'Food Processor',
    '打蛋器': 'Whisk',
    '破壁': 'Blender',
    '烤面包机': 'Toaster',
    '压面器': 'Rolling Machine',
    '榨汁': 'Juicer',
    '刀具': 'Knives Set',
    '泡茶': 'Kettle',
    '搅拌器': 'Blender',
    '过滤器': 'Filter',
    '磁炉': 'Oven',
    '真空机': 'Vacuum Machine',
    '手动真空': 'Vacuum Machine'
}

#平底锅

# Set page config at the beginning
st.set_page_config(page_title="CATEGORIZZAZIONE PRODOTTO", page_icon="📂")

# Define the function to process the uploaded Excel files
def process_files(uploaded_files, product_cat_dict):
    merged_dfs = []
    
    for file in uploaded_files:
        df = pd.read_excel(file)
        merged_df = pd.DataFrame()
        
        if 'ITEM_ID' in df.columns:
                merged_df['ITEM_ID'] = df['ITEM_ID']
        else:
                merged_df['ITEM_ID'] = df['Item ID']

        merged_df['TITLE'] = df['TITLE'] 
        
        if 'IMAGE_URL' in df.columns:
                merged_df['IMAGE_URL'] = df['IMAGE_URL']
        else:
                merged_df['IMAGE_URL'] = df['Image Url']

        if 'PRODUCT_CATEGORY' in df.columns:
                merged_df['PRODUCT_CATEGORY'] = df['PRODUCT_CATEGORY']
        else:
                merged_df['PRODUCT_CATEGORY'] = df['Product Category']
        
        
        def map_category(title):
            for keyword, category in product_cat_dict.items():
                if keyword in title:
                    return category
            return '-'
        
        merged_df['PRODUCT_CATEGORY_SUGGESTED'] = merged_df['TITLE'].apply(map_category)
        merged_dfs.append(merged_df)


        # GESTIONE ECCEZIONI
        # Function to check if both terms are present in the TITLE
        def has_breakfast_kit(title):
            return '水壶' in title and '多士炉' or '吐司' in title

        # Update the 'PRODUCT_CATEGORY_SUGGESTED' column based on the condition
        merged_df['PRODUCT_CATEGORY_SUGGESTED'] = merged_df.apply(
            lambda row: 'Breakfast Kit' if has_breakfast_kit(row['TITLE']) else row['PRODUCT_CATEGORY_SUGGESTED'],
            axis=1
        )
        
        # Count the number of rows with '-' in PRODUCT_CATEGORY_SUGGESTED
        no_categorization_count = (merged_df['PRODUCT_CATEGORY_SUGGESTED'] == '-').sum()
        # Total number of rows in the DataFrame
        total_rows = len(merged_df)
        # Display the message
        st.sidebar.write(f"{no_categorization_count} out of {total_rows} products have no categorization.")

        #------------------------------------------------------------------------------------
        #                                       WORDS CLOUD
        #------------------------------------------------------------------------------------



        # Filter rows with '-' in 'PRODUCT_CATEGORY_SUGGESTED'
        filtered_df = merged_df[merged_df['PRODUCT_CATEGORY_SUGGESTED'].str.contains('-')]
        # Extract the "TITLE" column from the filtered DataFrame
        title_column = filtered_df["TITLE"]
        # Combine all titles into a single string
        all_titles = " ".join(title_column)
        # Tokenize the text using jieba
        words = list(jieba.cut(all_titles))
        # Define the desired n-gram size (e.g., bigrams)
        n = 2
        # Generate n-grams
        ngrams = [tuple(words[i:i + n]) for i in range(len(words) - n + 1)]

        # Count the occurrences of each n-gram
        ngram_counts = Counter(ngrams)

        # Sort the n-grams by occurrence in descending order
        sorted_ngram_counts = sorted(ngram_counts.items(), key=lambda x: x[1], reverse=True)

        st.sidebar.write('Words Pairs most commonly used in TITLE of uncategorized listings')

        # Display the most common n-grams and their counts
        for ngram, count in sorted_ngram_counts:
            if all(len(word) >= 2 for word in ngram):  # Filter out n-grams with single-character words
                st.sidebar.write(f"{' '.join(ngram)}: {count}")

        #------------------------------------------------------------------------------------
        #                    
        #------------------------------------------------------------------------------------




    return merged_dfs

# Define the Streamlit app
st.title('Excel File Processor')

uploaded_files = st.file_uploader("Upload one or multiple XLSX files", type=["xlsx"], accept_multiple_files=True)

if uploaded_files:
    merged_dfs = process_files(uploaded_files, product_cat_dict)

    st.write("Merged DataFrame with Suggested Categories:")

    for idx, df in enumerate(merged_dfs):
        st.write(f"DataFrame {idx + 1}:")
        st.write(df)


    # Search box for filtering by 'TITLE'
    search_term = st.text_input("Search by TITLE", "")

    # Filter the DataFrame based on the search term
    if search_term:
        for idx, df in enumerate(merged_dfs):
            df_filtered = df[df['TITLE'].str.contains(search_term, case=False)]
            st.write(f"Filtered DataFrame {idx + 1}:")
            st.write(df_filtered)


    # Download the data as XLSX
    for idx, df in enumerate(merged_dfs):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=f'DataFrame_{idx + 1}', index=False)
        b64 = base64.b64encode(output.getvalue()).decode()
        st.markdown(f"Download DataFrame {idx + 1} as XLSX: [DataFrame_{idx + 1}.xlsx](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64})", unsafe_allow_html=True)

# Run the Streamlit app
if __name__ == '__main__':
    st.set_option('deprecation.showfileUploaderEncoding', False)
    st.write('Upload one or multiple XLSX files to begin.')
