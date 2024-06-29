from datetime import datetime
import pandas as pd

# Function to parse date from various formats
def parse_date(date_str):
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%B %d, %Y'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

# Function to extract sentences containing "Notice of Intent"
def extract_noi_sentences(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    noi_sentences = [sentence for sentence in sentences if 'notice of intent' in sentence.lower()]
    return noi_sentences

# Function to find dates in the sentences
def find_dates_in_sentences(sentences):
    date_patterns = [
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{4}-\d{1,2}-\d{1,2})',
        r'\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\b \d{1,2}, \d{4}'
    ]
    dates = []
    for sentence in sentences:
        for pattern in date_patterns:
            matches = re.findall(pattern, sentence, re.IGNORECASE)
            for match in matches:
                try:
                    dates.append(datetime.strptime(match, '%m/%d/%Y'))
                except ValueError:
                    try:
                        dates.append(datetime.strptime(match, '%Y-%m-%d'))
                    except ValueError:
                        try:
                            dates.append(datetime.strptime(match, '%B %d, %Y'))
                        except ValueError:
                            continue
    return dates

# Function to calculate review times using extracted NOI dates and Federal Register dates
def calculate_review_times_with_noi_federal_register(dataset, num_samples=100):
    project_data = []

    for i, example in enumerate(dataset['train']):
        if len(project_data) >= num_samples:
            break
        
        project_title = example['Project Title']
        if "environmental impact statement" not in project_title.lower():
            continue
        
        documents = example['Documents']
        
        # Extract and aggregate NOI dates
        noi_dates = []
        total_pages = 0
        for doc in documents:
            page_texts = [page['Page Text'] for page in doc['Pages'] if 'Page Text' in page]
            full_text = " ".join(page_texts).lower()
            
            if 'notice of intent' in full_text:
                noi_sentences = extract_noi_sentences(full_text)
                noi_dates.extend(find_dates_in_sentences(noi_sentences))
            
            # Count the number of pages
            total_pages += len(doc['Pages'])
        
        # Get the earliest NOI date
        if noi_dates:
            noi_date = min(noi_dates)
        else:
            continue  # Skip if no NOI date found
        
        # Collect and parse Federal Register dates
        register_dates = example.get('Federal Register Date', [])
        federal_register_dates = [parse_date(date) for date in register_dates if parse_date(date)]
        
        # Use the latest Federal Register date as the ROD proxy
        if federal_register_dates:
            rod_date = max(federal_register_dates)
        else:
            continue  # Skip if no ROD date found
        
        # Calculate the review time
        review_time = (rod_date - noi_date).days
        if review_time > 0:  # Ensure positive review time
            project_data.append({
                "Project Title": project_title,
                "NOI Date": noi_date,
                "ROD (Federal Register) Date": rod_date,
                "Review Time (days)": review_time,
                "Total Pages": total_pages
            })

    return project_data

# Load the dataset in streaming mode
data = load_dataset("PolicyAI/NEPATEC1.0", streaming=True)

# Calculate review times using the extracted NOI dates and Federal Register dates
review_times_with_noi_and_federal_register = calculate_review_times_with_noi_federal_register(data, num_samples=100)

# Convert to DataFrame for easier viewing and manipulation
review_times_df = pd.DataFrame(review_times_with_noi_and_federal_register)

# Display the first few rows to verify
print(review_times_df.head())

# Save the review times data for further analysis
review_times_df.to_csv("nepatec_eis_review_times_with_noi_and_federal_register.csv", index=False)

print(f"Review times using extracted NOI dates and Federal Register dates for EIS projects have been processed and saved.")
