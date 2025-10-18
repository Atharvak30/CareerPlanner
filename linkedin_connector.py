import urllib.parse
import requests


def build_linkedin_search_url(job_title, location, start=0):
    """
    Constructs a properly formatted LinkedIn job search URL.

    Args:
        job_title: Job title to search for (e.g., "Software Engineer")
        location: Location to search in (e.g., "San Francisco, CA" or "remote")
        start: Pagination offset (0, 25, 50, etc.)

    Returns:
        Properly formatted and URL-encoded LinkedIn job search URL
    """
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    params = {
        "keywords": job_title,
        "location": location,
        "start": start
    }

    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


def test_linkedin_connection(url):
    """
    Tests HTTP connectivity to LinkedIn job search URL.

    Args:
        url: The URL to test

    Returns:
        Tuple of (status_code, response_length)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.linkedin.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.status_code, len(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LinkedIn: {e}")
        return None, 0


if __name__ == "__main__":
    # Test with Data Scientist and remote location
    url = build_linkedin_search_url("Data Scientist", "remote")
    print(f"Generated URL: {url}\n")

    status, length = test_linkedin_connection(url)

    if status:
        print(f"Status Code: {status}")
        print(f"Response Length: {length} characters")

        # Verify expectations
        if status == 200 and length > 1000:
            print("\n✓ Connection test passed!")
        else:
            print(f"\n✗ Connection test failed - Status: {status}, Length: {length}")
    else:
        print("✗ Connection failed")
