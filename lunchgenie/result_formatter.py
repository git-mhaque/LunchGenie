"""
Result formatting and printing utilities for LunchGenie.
"""

def print_recommendations(places):
    """
    Print formatted list of recommended places and their details.
    """
    if not places:
        print("All matched places have review red flags or could not be verified as safe.")
        return
    print("\nRecommended team lunch places (clean reviews, high rating, short walk):\n")
    for p in places:
        print(f"- {p['name']} ({', '.join(p['categories'])})")
        print(f"  Rating: {p['rating']} from {p['review_count']} reviews; {p['distance_m']}m from point.")
        print(f"  Address: {p['address']}")
        print(f"  More: {p['url']}")
        if "review_summary" in p:
            print(f"  Review summary: {p['review_summary']}")
        print("")
