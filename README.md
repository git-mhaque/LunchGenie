# LunchGenie

**LunchGenie** is an agentic lunch recommendation system powered by OpenAI and Python agent orchestration (LangChain).  
It finds local places for team lunch based on cuisine, ratings, proximity, review analysis, and more, using LLM-based multi-criteria reasoning and modular data lookup plugins.

## Key Features

- Multi-criteria search: cuisine, rating, distance, atmosphere, review safety.
- Secure configuration via .env and strict secrets handling.
- Extensible plugin/tools framework for multiple restaurant data sources.
- LLM-based analysis for subjective criteria and review filtering.
- Python-based (LangChain, OpenAI SDK).

## Setup

1. Clone this repository
2. Create and activate a Python virtual environment:
    ```
    python3 -m venv venv
    ```

    ```
    source venv/bin/activate
    ```
3. Install dependencies:
    ```
    pip install -r requirements.txt
    ```
4. Copy the example environment file to the project root and rename it:
    ```
    cp configs/.env.example .env
    ```
   Then edit `.env` and fill in your API keys.

   **Required:**
    - `OPENAI_API_KEY`: Your OpenAI API key (see below)

   **Restaurant Data Providers:**
    - `YELP_API_KEY`: For Yelp restaurant search
    - `GOOGLE_PLACES_API_KEY`: For Google Places restaurant search

   **Default Location (optional):**
    - `DEFAULT_LATITUDE`, `DEFAULT_LONGITUDE`: Set these to control the geographic center point for all searches (e.g., your office or city center). If not specified by the user, these defaults are used for location-based recommendations.

## Obtaining an OpenAI API Key

LunchGenie uses OpenAI's GPT-3.5 or GPT-4 for review and recommendation logic. You'll need an OpenAI API key to run the app:

1. Sign up at [OpenAI](https://platform.openai.com/signup) if you don't have an account.
2. Visit your [OpenAI API Keys page](https://platform.openai.com/api-keys).
3. Click "Create new secret key" and copy it.
4. Set `OPENAI_API_KEY` in your `.env` file to this key.

The key is required even if you only use Google or Yelp for place data, since all intelligent ranking and review analysis uses the LLM.


## Development structure

- `lunchgenie/` — Core package: agent, orchestrator, config.
- `tools/` — Modular plugin data-adapters.
- `tests/` — Test suite.
- `configs/` — Configuration and reference files.

## Security

- No secrets or API keys should be hardcoded.
- Uses `.env` for sensitive fields, loaded and validated at runtime.

## Restaurant Provider Selection

LunchGenie can use either **Yelp** or **Google Places** as the data provider for restaurant search and reviews. The provider is selected via environment variable in your `.env` file:

```
RESTAURANT_PROVIDER=yelp   # Use Yelp (default)
RESTAURANT_PROVIDER=google # Use Google Places
```

You must provide a valid API key for the selected provider:
- For Yelp: `YELP_API_KEY`
- For Google Places: `GOOGLE_PLACES_API_KEY`

Be sure to set the appropriate variable(s) in your `.env` file. If both are set, the value of `RESTAURANT_PROVIDER` determines which source is used.

### Data and Feature Notes

- Yelp provides detailed business reviews. Google Places returns reviews and ratings but feature detail/format may differ.
- Both plugins normalize restaurant data for consistent use (name, address, rating, etc.).
- Advanced review summaries depend on available text from the provider.

## Usage

To run LunchGenie and get lunch recommendations:

1. Make sure your Python virtual environment is active and all dependencies are installed.
2. Run the app from the root of the project using Python's module syntax:

    ```
    python -m lunchgenie.agent recommend
    ```

   This is the recommended way to run LunchGenie. It will search for suitable restaurants and print the top recommendations based on your criteria.

Sample output: 
```
Found 17 high-rated options. Analyzing reviews...
Analyzing reviews for Cha Ching (5).
Analyzing reviews for Tian38 (5).
Analyzing reviews for Bamboo House Chinese Restaurant Melbourne (5).
Analyzing reviews for Miss Mi Restaurant & Bar (5).
Analyzing reviews for Nelayan Restaurant (5).
Analyzing reviews for Jom (5).
Analyzing reviews for Blue Chillies (5).
Analyzing reviews for Tazio (5).
Analyzing reviews for Nan Yang Express Chinatown (5).
Analyzing reviews for Ho Liao Melbourne (5).
Analyzing reviews for Lim Kopi (5).
Analyzing reviews for Mint & Co. (5).
Analyzing reviews for Pondok Rempah (5).
Analyzing reviews for Achelya Restaurant, Cafe and Bar. (5).
Analyzing reviews for Kedai Satay in King St (5).
Analyzing reviews for ILoveIstanbul (5).
Analyzing reviews for Kan Eang by Thai Culinary (5).

Recommended team lunch places (clean reviews, high rating, short walk):

- Jom (restaurant, point_of_interest, food, establishment)
  Rating: 4.9 from 857 reviews; 448m from point.
  Address: 378 Lonsdale St, Melbourne VIC 3000, Australia
  More: https://maps.google.com/?cid=2882563165016363395
  Review summary: Overall, the reviews do not mention any food safety, hygiene, or customer mistreatment issues. The restaurant seems safe based on the feedback provided.

- Cha Ching (restaurant, point_of_interest, food, establishment)
  Rating: 4.7 from 2164 reviews; 196m from point.
  Address: 348 Flinders Ln, Melbourne VIC 3000, Australia
  More: https://maps.google.com/?cid=15116040731015528848
  Review summary: Overall, the reviews do not mention any food safety, hygiene, or customer mistreatment issues. The restaurant seems safe based on the feedback provided.

- Blue Chillies (restaurant, point_of_interest, food, establishment)
  Rating: 4.7 from 396 reviews; 2186m from point.
  Address: 182 Brunswick St, Fitzroy VIC 3065, Australia
  More: https://maps.google.com/?cid=676553577094659346
  Review summary: It seems safe. Customers had positive experiences with the food, service, and atmosphere of the restaurant.

- Mint & Co. (restaurant, point_of_interest, food, establishment)
  Rating: 4.7 from 7658 reviews; 1985m from point.
  Address: 62 University St, Carlton VIC 3053, Australia
  More: https://maps.google.com/?cid=18180350769342393265
  Review summary: It seems safe based on the customer reviews. The restaurant received positive feedback on the food quality, service, and atmosphere.

- Kan Eang by Thai Culinary (restaurant, point_of_interest, food, establishment)
  Rating: 4.7 from 1534 reviews; 275m from point.
  Address: 306 Flinders Ln, Melbourne VIC 3000, Australia
  More: https://maps.google.com/?cid=11719064961553893173
  Review summary: Overall, the reviews are very positive with customers praising the food, service, and ambiance of the restaurant. No red flags related to food safety, hygiene, or customer mistreatment were mentioned.
```

To test LLM connectivity only (diagnostic), use:
```
python -m lunchgenie.agent
```

## Future Enhancements

- **Walking distance instead of point-to-point distance:**  
  Integrate Google Directions API to report true walking distance for each restaurant, replacing current straight-line ("as-the-crow-flies") calculations. This will further improve accuracy of proximity recommendations for users traveling on foot.

- **Refine ReviewAnalyzer tool:**  
  Enhance the ReviewAnalyzer module for more nuanced sentiment analysis, greater detection of subtle issues from text data, and improved LLM prompt engineering for summarizing feedback in a way that is more sensitive to safety, quality, and current trends.

- **Expanded Test Coverage:**  
  Build out comprehensive automated tests (unit and integration) to verify core agent logic, plugin adapters, and review analysis. Ensure robustness through high test coverage and continuous integration support.

- **Containerization:**  
  Add Docker support for consistent, reproducible local development and deployment. Provide ready-to-use Dockerfiles for easy container-based usage.

- **Cloud deployment/hosting:**  
  Support deployment to major cloud providers (such as AWS, Azure, or Google Cloud), including guides and scripts for running LunchGenie in production environments.
